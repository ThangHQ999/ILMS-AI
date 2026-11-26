"""Canonical identities from the exact current publications selected by Spring Boot."""

import json
from collections.abc import Iterator, Mapping
from uuid import UUID

from sqlalchemy import bindparam, text

from app.schema.knowledge_graph import ConceptCatalogRequest, ConceptCatalogResponse, PublishedConcept
from app.service.ingestion.publication.records import ingested_canonical_code


_PUBLICATIONS = text('''
    SELECT p.id AS publication_id, d.graph_payload, first_chunk.owner_id,
           first_chunk.subject, first_chunk.scope
    FROM material_publications p
    JOIN knowledge_graph_drafts d ON d.id = p.draft_id AND d.job_id = p.job_id
    JOIN materials m ON m.id = p.material_id
    LEFT JOIN lessons l ON l.id = m.lesson_id AND l.deleted_at IS NULL
    LEFT JOIN chapters c ON c.id = l.chapter_id AND c.deleted_at IS NULL
    JOIN courses course ON course.id = :course_id AND course.deleted_at IS NULL
    LEFT JOIN material_chunks first_chunk ON first_chunk.id = (
        SELECT mc.id FROM material_chunks mc
        WHERE mc.material_version_id = p.material_version_id
        ORDER BY mc.chunk_index, mc.id LIMIT 1
    )
    WHERE p.id IN :publication_ids
      AND p.status = 'PUBLISHED' AND p.is_current = 1
      AND d.review_status = 'APPROVED' AND d.reviewed_payload_hash = d.payload_hash
      AND (m.course_id IS NULL OR m.course_id = course.id)
      AND (m.lesson_id IS NULL OR c.course_id = course.id)
      AND COALESCE(m.course_id, c.course_id) = course.id
    ORDER BY p.published_at DESC, p.id
''').bindparams(bindparam('publication_ids', expanding=True))


def _clean_string(value: object) -> str:
    return value.strip() if isinstance(value, str) else ''


def _concepts_from_publication(row: Mapping[str, object]) -> Iterator[PublishedConcept]:
    payload = row['graph_payload']
    graph = json.loads(payload) if isinstance(payload, (str, bytes)) else payload
    if not isinstance(graph, dict) or not {'entities', 'nodes'}.intersection(graph):
        raise ValueError('Published graph has no concept collection')

    scope = _clean_string(row['scope'])
    subject = _clean_string(row['subject']).upper()
    owner_id = row['owner_id']
    for collection in ('entities', 'nodes'):
        nodes = graph.get(collection, [])
        if not isinstance(nodes, list):
            raise ValueError('Published graph concept collection must be a list')
        for node in nodes:
            if not isinstance(node, dict):
                raise ValueError('Published graph concept must be an object')
            raw_kind = node.get('kind') or node.get('nodeKind')
            if not raw_kind and collection == 'nodes':
                raw_kind = node.get('type')
            kind = _clean_string(raw_kind).upper().replace('_', '').replace('-', '')
            if kind and kind not in {'KNOWLEDGEENTITY', 'KNOWLEDGEENTITYSNAPSHOT', 'CONCEPT'}:
                continue
            attributes = node.get('attributes') if isinstance(node.get('attributes'), Mapping) else {}
            code = (_clean_string(node.get('canonical_code')) or _clean_string(node.get('canonicalCode'))
                    or _clean_string(attributes.get('canonical_code')) or _clean_string(attributes.get('canonicalCode')))
            if not code and collection == 'nodes' and kind == 'CONCEPT':
                code = _clean_string(node.get('code'))
            label = (_clean_string(node.get('name')) or _clean_string(node.get('label'))
                     or _clean_string(attributes.get('name')))
            if not code and collection == 'entities' and label and subject and scope in {'GLOBAL', 'TEACHER'} and owner_id:
                owner = str(UUID(bytes=bytes(owner_id)))
                code = ingested_canonical_code(owner, subject, scope, label)
            if code:
                yield PublishedConcept(canonicalCode=code, label=label or code)


async def load_concept_catalog(request: ConceptCatalogRequest) -> ConceptCatalogResponse | None:
    if not request.publicationIds:
        return ConceptCatalogResponse(courseId=request.courseId, concepts=[])

    from app.db.mysql import mysql_manager

    publication_ids = {publication_id.bytes for publication_id in request.publicationIds}
    async with mysql_manager.session_factory() as db:
        rows = (await db.execute(_PUBLICATIONS, {
            'course_id': request.courseId.bytes,
            'publication_ids': list(publication_ids),
        })).mappings().all()

    if {bytes(row['publication_id']) for row in rows} != publication_ids:
        return None

    by_code = {}
    for row in rows:
        for concept in _concepts_from_publication(row):
            by_code.setdefault(concept.canonicalCode, concept)
    return ConceptCatalogResponse(courseId=request.courseId,
                                  concepts=[by_code[code] for code in sorted(by_code)])
