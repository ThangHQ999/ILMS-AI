"""Prepare Neo4j and Chroma, then activate the approved publication in MySQL."""
import json
from uuid import UUID, uuid4

from sqlalchemy import text

from app.core.config import settings
from app.db.mysql import mysql_manager
from app.db.neo4j import neo4j_manager
from app.repository.chroma.entity_vector_repo import embedding_identity, invoke
from app.repository.chroma.publication_vectors import publication_collection
from app.service.ingestion.config import IngestionSettings
from app.service.ingestion.publication.records import build_records
from app.service.ingestion.publication.lifecycle import PublicationConflict, check_base, published_event
from app.service.knowledge_graph.editor import validation_issues
from app.service.knowledge_graph.document import normalize_document
from app.service.llm_service import LLMService


class InvalidApprovedDraft(ValueError):
    pass


def uid(value):
    return str(UUID(bytes=value))


async def publish(job_id):
    lease = uuid4().bytes
    key = job_id.bytes
    async with mysql_manager.session_factory() as db, db.begin():
        claimed = await db.execute(text("""
            UPDATE ingestion_jobs SET lease_token=:lease,
              lease_expires_at=DATE_ADD(CURRENT_TIMESTAMP(6), INTERVAL 15 MINUTE),
              current_stage='PREPARING_INDEXES'
            WHERE id=:job AND status='PUBLISHING'
              AND (lease_token IS NULL OR lease_expires_at < CURRENT_TIMESTAMP(6))
        """), {'lease': lease, 'job': key})
        if claimed.rowcount != 1:
            return False
    try:
        await prepare_and_activate(key, lease)
    except InvalidApprovedDraft:
        # Only input validation uses this path, before touching either index.
        async with mysql_manager.session_factory() as db, db.begin():
            await db.execute(text("""
                UPDATE knowledge_graph_drafts d
                JOIN material_publications p ON p.draft_id=d.id
                JOIN ingestion_jobs j ON j.id=p.job_id
                SET d.review_status='CHANGES_REQUESTED'
                WHERE j.id=:job AND j.lease_token=:lease AND p.status='PREPARING'
            """), {'job': key, 'lease': lease})
            await db.execute(text("""
                UPDATE ingestion_jobs j JOIN material_publications p ON p.job_id=j.id
                SET j.status='FAILED',j.error_code='INVALID_APPROVED_GRAPH',j.current_stage='PUBLICATION_FAILED',
                  j.lease_token=NULL,j.lease_expires_at=NULL,p.status='FAILED'
                WHERE j.id=:job AND j.lease_token=:lease AND p.status='PREPARING'
            """), {'job': key, 'lease': lease})
        raise
    except Exception as failure:
        async with mysql_manager.session_factory() as db, db.begin():
            await db.execute(text("""
                UPDATE ingestion_jobs j JOIN material_publications p ON p.job_id=j.id
                SET j.status='FAILED', j.error_code=:code,
                    j.current_stage='PUBLICATION_FAILED', j.lease_token=NULL,
                    j.lease_expires_at=NULL, p.status='FAILED'
                WHERE j.id=:job AND j.lease_token=:lease AND p.status='PREPARING'
            """), {'job': key, 'lease': lease,
                     'code': 'PUBLICATION_CONFLICT' if isinstance(failure, PublicationConflict) else 'PUBLICATION_FAILED'})
        raise
    return True


async def prepare_and_activate(job, lease):
    async with mysql_manager.session_factory() as db:
        row = (await db.execute(text("""
            SELECT p.id, p.material_id, p.material_version_id, v.version_number,
                   d.id AS draft_id, d.graph_payload, d.source_manifest, d.validation_report, d.reviewed_by
            FROM material_publications p
            JOIN material_versions v ON v.id=p.material_version_id
            JOIN knowledge_graph_drafts d ON d.id=p.draft_id AND d.job_id=p.job_id
            WHERE p.job_id=:job AND p.status='PREPARING' AND d.review_status='APPROVED'
              AND d.reviewed_payload_hash=d.payload_hash
        """), {'job': job})).mappings().one()
        source = (await db.execute(text("""
            SELECT id, content, owner_id, subject, scope FROM material_chunks
            WHERE material_version_id=:version ORDER BY chunk_index
        """), {'version': row['material_version_id']})).mappings().all()

    if not source:
        raise ValueError('Approved version has no chunks')
    first = source[0]
    identity = (first['owner_id'], first['subject'], first['scope'])
    if any((chunk['owner_id'], chunk['subject'], chunk['scope']) != identity for chunk in source):
        raise ValueError('Inconsistent source scope')
    publication = uid(row['id'])
    try:
        draft = json.loads(row['graph_payload'])
        normalize_document(draft, uid(row['material_version_id']), uid(first['owner_id']),
                           first['subject'].strip().upper(), first['scope'])
        report = json.loads(row['validation_report']) if isinstance(row['validation_report'], (str, bytes)) else row['validation_report'] or {}
        acknowledged = set(report.get('acknowledgedIssueIds', []))
        for issue in validation_issues(draft, {uid(chunk['id']) for chunk in source}):
            if issue['severity'] == 'BLOCKER' or issue['id'] not in acknowledged:
                raise ValueError('Draft contains unresolved validation issues')
        nodes, edges, vectors, topics, codes = build_records(
            publication, draft, json.loads(row['source_manifest'] or '{}'),
            [{'id': uid(chunk['id']), 'content': chunk['content']} for chunk in source],
            uid(first['owner_id']), first['subject'].strip().upper(), first['scope'],
        )
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        raise InvalidApprovedDraft('Approved graph does not match the publication contract') from exc
    revision_id = uid(row['draft_id'])
    for node in nodes:
        node['graph_revision_id'] = revision_id
    await store_graph(nodes, edges)
    await store_vectors(vectors)
    await activate(row, job, lease, topics, codes)


async def store_graph(nodes, edges):
    async def write(tx):
        result = await tx.run("""
            UNWIND $nodes AS node
            MERGE (n:IngestedKnowledge {id:node.id})
            SET n = node
        """, nodes=nodes)
        await result.consume()
        result = await tx.run("""
            UNWIND $edges AS edge
            MATCH (p:IngestedKnowledge {id:edge.parent}), (c:IngestedKnowledge {id:edge.child})
            MERGE (p)-[r:INGESTED_RELATION {kind:edge.kind}]->(c)
            SET r.description=edge.description, r.source_chunk_ids=edge.source_chunk_ids
        """, edges=edges)
        await result.consume()

    async with neo4j_manager.driver.session(database=settings.NEO4J_DATABASE) as session:
        await session.execute_write(write)


async def store_vectors(vectors):
    config = IngestionSettings()
    collection = await publication_collection(config.publication_collection, create=True)
    async with LLMService(quiet=True).managed() as llm:
        for start in range(0, len(vectors), config.publication_embedding_batch):
            batch = vectors[start:start + config.publication_embedding_batch]
            ids, documents, metadata = map(list, zip(*batch))
            existing = await invoke(collection, 'get', ids=ids, include=[])
            ready = set(existing['ids'])
            missing = [i for i, item in enumerate(ids) if item not in ready]
            if not missing:
                continue
            texts = [documents[i] for i in missing]
            embeddings = await llm.embed_texts(texts, provider=settings.EMBEDDING_PROVIDER, allow_fallback=False)
            if any(len(vector) != settings.active_embedding_dimension for vector in embeddings):
                raise ValueError('Unexpected publication embedding dimension')
            await invoke(collection, 'upsert', ids=[ids[i] for i in missing], documents=texts,
                         embeddings=embeddings, metadatas=[metadata[i] for i in missing])


async def activate(row, job, lease, topics, codes):
    params = {'material': row['material_id'], 'job': job, 'lease': lease, 'draft': row['draft_id'],
              'id': row['id'], 'actor': row['reviewed_by'], 'version': row['material_version_id']}
    async with mysql_manager.session_factory() as db, db.begin():
        await db.execute(text('SELECT id FROM materials WHERE id=:material FOR UPDATE'), params)
        owned = (await db.execute(text("""
            SELECT j.id FROM ingestion_jobs j JOIN material_publications p ON p.job_id=j.id
            WHERE j.id=:job AND j.status='PUBLISHING' AND j.lease_token=:lease
              AND j.lease_expires_at >= CURRENT_TIMESTAMP(6) AND p.status='PREPARING'
            FOR UPDATE
        """), params)).first()
        if not owned:
            raise PublicationConflict('Publication lease was lost')
        await check_base(db, row, params)
        await db.execute(text("""
            DELETE tc FROM topic_chunks tc JOIN material_chunks c ON c.id=tc.chunk_id
            WHERE c.material_id=:material
        """), params)
        for topic in sorted(topics, key=lambda item: item['id']):
            topic_id = UUID(topic['id']).bytes
            await db.execute(text("""
                INSERT INTO topics(id,name,summary,concepts_included)
                VALUES(:id,:name,:summary,:codes)
                ON DUPLICATE KEY UPDATE id=topics.id
            """), {'id': topic_id, 'name': topic['name'], 'summary': topic['summary'],
                    'codes': json.dumps(topic['codes'])})
            await db.execute(text('INSERT INTO topic_chunks(topic_id,chunk_id) VALUES(:topic,:chunk)'),
                             [{'topic': topic_id, 'chunk': UUID(value).bytes} for value in topic['chunks']])
        await db.execute(text("""
            UPDATE material_chunks SET canonical_codes=JSON_ARRAY()
            WHERE material_version_id=:version
        """), params)
        if codes:
            await db.execute(text('UPDATE material_chunks SET canonical_codes=:codes WHERE id=:chunk'),
                             [{'chunk': UUID(key).bytes, 'codes': json.dumps(sorted(value))}
                              for key, value in codes.items()])
        await db.execute(text("""
            UPDATE material_publications SET status='SUPERSEDED', is_current=NULL,
              superseded_at=CURRENT_TIMESTAMP(6) WHERE material_id=:material AND is_current=1
        """), params)
        await db.execute(text("""
            UPDATE material_publications SET status='PUBLISHED', is_current=1,
              published_by=:actor, published_at=CURRENT_TIMESTAMP(6) WHERE id=:id
        """), params)
        await db.execute(text("""
            UPDATE ingestion_jobs SET status='COMPLETED', current_stage='PUBLISHED', error_code=NULL,
              lease_token=NULL, lease_expires_at=NULL, finished_at=CURRENT_TIMESTAMP(6),
              publication_state=:state
            WHERE id=:job
        """), {**params, 'state': json.dumps({'embedding_identity': embedding_identity()})})
        await published_event(db, params)
