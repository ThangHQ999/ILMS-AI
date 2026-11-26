"""Synchronize immutable MySQL draft revisions into a Neo4j editing projection."""
import json
from uuid import UUID

from sqlalchemy import text

from app.core.config import settings
from app.db.mysql import mysql_manager
from app.db.neo4j import neo4j_manager
from app.service.ingestion.drafts.projection import project


SELECT_REVISION = """
    SELECT d.id, d.job_id, d.revision_number, d.payload_hash, d.graph_payload,
           CASE WHEN p.status IN ('PUBLISHED', 'SUPERSEDED') THEN p.status ELSE 'DRAFT' END AS status
    FROM knowledge_graph_drafts d
    JOIN ingestion_jobs j ON j.id=d.job_id
    LEFT JOIN material_publications p ON p.draft_id=d.id AND p.job_id=d.job_id
"""
SYNCED_NUMBER = "COALESCE(CAST(JSON_UNQUOTE(JSON_EXTRACT(j.checkpoint,'$.neo4j_draft_revision')) AS UNSIGNED),0)"


async def ensure_projection(row):
    revision_id = str(UUID(bytes=row['id']))
    payload = row['graph_payload']
    graph = json.loads(payload) if isinstance(payload, (str, bytes)) else payload
    metadata = {
        'id': revision_id, 'job_id': str(UUID(bytes=row['job_id'])),
        'revision': row['revision_number'], 'payload_hash': row['payload_hash'], 'status': row['status'],
    }

    async def write(tx):
        cursor = await tx.run("""
            MERGE (r:IngestionGraphRevision {id:$metadata.id})
            ON CREATE SET r = $metadata
            SET r.status=CASE
                WHEN r.status='SUPERSEDED' THEN r.status
                WHEN r.status='PUBLISHED' AND $metadata.status='DRAFT' THEN r.status
                ELSE $metadata.status END
            RETURN r.payload_hash AS hash, coalesce(r.projected, false) AS projected
        """, metadata=metadata)
        state = await cursor.single(strict=True)
        if state['hash'] != metadata['payload_hash']:
            raise ValueError('Draft revision payload changed')
        if state['projected']:
            return
        nodes, edges = project(revision_id, graph)
        cursor = await tx.run("""
            MATCH (r:IngestionGraphRevision {id:$id})
            UNWIND $nodes AS node
            MERGE (n:IngestionDraftNode {id:node.id})
            SET n = node, n.graph_revision_id=$id
            MERGE (r)-[:HAS_DRAFT_NODE]->(n)
        """, id=revision_id, nodes=nodes)
        await cursor.consume()
        cursor = await tx.run("""
            UNWIND $edges AS edge
            MATCH (a:IngestionDraftNode {id:edge.source, graph_revision_id:$id}),
                  (b:IngestionDraftNode {id:edge.target, graph_revision_id:$id})
            MERGE (a)-[link:DRAFT_LINK {kind:edge.kind}]->(b)
            SET link.description=edge.description
        """, id=revision_id, edges=edges)
        await cursor.consume()
        cursor = await tx.run("""
            MATCH (r:IngestionGraphRevision {id:$id}) SET r.projected=true
        """, id=revision_id)
        await cursor.consume()

    async with neo4j_manager.driver.session(database=settings.NEO4J_DATABASE) as session:
        await session.execute_write(write)


async def sync_next_revision():
    async with mysql_manager.session_factory() as db:
        row = (await db.execute(text(SELECT_REVISION + f"""
            WHERE d.revision_number = {SYNCED_NUMBER} + 1
               OR (p.status IN ('PUBLISHED','SUPERSEDED') AND d.revision_number <= {SYNCED_NUMBER}
                   AND p.status <> COALESCE(JSON_UNQUOTE(JSON_EXTRACT(j.checkpoint,'$.neo4j_publication_status')), ''))
            ORDER BY d.created_at, d.id LIMIT 1
        """))).mappings().first()
    if row is None:
        return False

    await ensure_projection(row)
    async with mysql_manager.session_factory() as db, db.begin():
        await db.execute(text(f"""
            UPDATE ingestion_jobs j
            SET checkpoint=JSON_SET(COALESCE(checkpoint, JSON_OBJECT()),
                '$.neo4j_draft_revision', GREATEST({SYNCED_NUMBER}, :revision))
            WHERE j.id=:job
        """), {'revision': row['revision_number'], 'job': row['job_id']})
        if row['status'] != 'DRAFT':
            await db.execute(text("""
                UPDATE ingestion_jobs j JOIN material_publications p ON p.job_id=j.id
                SET j.checkpoint=JSON_SET(COALESCE(j.checkpoint, JSON_OBJECT()),
                    '$.neo4j_publication_status', :status)
                WHERE j.id=:job AND p.status=:status
            """), {'status': row['status'], 'job': row['job_id']})
    return True


async def get_graph(job_id, revision_id):
    async with mysql_manager.session_factory() as db:
        row = (await db.execute(text(SELECT_REVISION + " WHERE d.job_id=:job AND d.id=:revision"),
                                {'job': job_id.bytes, 'revision': revision_id.bytes})).mappings().first()
    if row is None:
        return None
    await ensure_projection(row)
    async with neo4j_manager.driver.session(database=settings.NEO4J_DATABASE) as session:
        result = await session.run("""
            MATCH (r:IngestionGraphRevision {id:$id})
            OPTIONAL MATCH (r)-[:HAS_DRAFT_NODE]->(n:IngestionDraftNode)
            RETURN collect(n { .id, .kind, .path, .label }) AS nodes
        """, id=str(revision_id))
        nodes = (await result.single(strict=True))['nodes']
        result = await session.run("""
            MATCH (r:IngestionGraphRevision {id:$id})-[:HAS_DRAFT_NODE]->(a)-[e:DRAFT_LINK]->(b)
            WHERE b.graph_revision_id=$id
            RETURN a.id AS source, b.id AS target, e.kind AS kind
        """, id=str(revision_id))
        edges = await result.data()
    return {'revision_id': str(revision_id), 'status': row['status'], 'nodes': nodes, 'edges': edges}
