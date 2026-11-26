"""Database-backed graph transformations used by the authenticated BE service."""
import json
from uuid import UUID

from sqlalchemy import text

from app.db.mysql import mysql_manager
from app.service.ingestion.publication.records import stable_id
from app.service.knowledge_graph.document import GraphInputError, inventory, normalize_document
from app.service.knowledge_graph.editor import edit_document, validation_issues


def decoded(value, default=None):
    if value is None:
        return default
    return json.loads(value) if isinstance(value, (str, bytes)) else value


async def load_revision(job_id, revision_id):
    async with mysql_manager.session_factory() as db:
        row = (await db.execute(text('''
            SELECT d.graph_payload, d.source_manifest, d.payload_hash,
                   v.material_id, v.id AS version_id, d.revision_number
            FROM knowledge_graph_drafts d JOIN ingestion_jobs j ON j.id=d.job_id
            JOIN material_versions v ON v.id=j.material_version_id
            JOIN materials m ON m.id=v.material_id
            WHERE d.id=:revision AND d.job_id=:job
        '''), {'revision': revision_id.bytes, 'job': job_id.bytes})).mappings().first()
        if row is None:
            return None
        chunks = (await db.execute(text('''
            SELECT id, scope, subject, owner_id FROM material_chunks
            WHERE material_version_id=:version ORDER BY chunk_index
        '''), {'version': row['version_id']})).mappings().all()
    if not chunks:
        raise GraphInputError('Revision has no source chunks')
    first = chunks[0]
    context = {
        'version_id': str(UUID(bytes=row['version_id'])),
        'owner': str(UUID(bytes=first['owner_id'])),
        'subject': first['subject'].strip().upper(), 'scope': first['scope'],
    }
    graph = normalize_document(decoded(row['graph_payload']), **context)
    claims = {claim['claim_id']: claim for claim in decoded(row['source_manifest'], {}).get('claims', [])}
    links = {link.get('node_id'): link.get('claim_ids', []) for link in graph.get('source_links') or []}
    refs = inventory(graph)
    for node_id, ref in refs.items():
        if 'source_claim_ids' in ref.data:
            continue
        selected = links.get(node_id, [])
        if ref.kind == 'DEFINITION':
            parent = refs[ref.parent].data
            selected = [claim_id for claim_id in parent.get('source_claim_ids', [])
                        if claims.get(claim_id, {}).get('kind') in {'DEFINITION', 'CONDITION', 'EXCEPTION'}]
        ref.data['source_claim_ids'] = selected
    return row, graph, context, {str(UUID(bytes=chunk['id'])) for chunk in chunks}


async def change_graph(request):
    source = await load_revision(request.jobId, request.revisionId)
    if source is None:
        return None
    row, base, context, chunks = source
    if request.graph is not None and len(json.dumps(request.graph)) > 8_000_000:
        raise GraphInputError('Graph document is too large')
    graph, mappings = edit_document(base, request.operations, context, request.graph)
    if len(json.dumps(graph)) > 8_000_000:
        raise GraphInputError('Graph document is too large')
    return {'graph': graph, 'baseHash': row['payload_hash'],
            'validationIssues': validation_issues(graph, chunks), 'idMappings': mappings}


async def graph_view(request):
    source = await load_revision(request.jobId, request.revisionId)
    if source is None:
        return None
    row, graph, _, chunk_ids = source
    refs = inventory(graph)
    evidence = {claim['claim_id']: claim for claim in decoded(row['source_manifest'], {}).get('claims', [])}
    nodes, edges = [], []
    for node_id, ref in refs.items():
        if not request.includeSolutions and ref.kind in {'EXERCISE_STEP', 'ARGUMENT'}:
            continue
        fields = {key: value for key, value in ref.data.items() if key in {
            'name', 'description', 'title', 'content', 'conditions', 'exceptions', 'action',
            'step_number', 'explanation', 'code_snippet', 'summary',
        }}
        if request.includeSolutions:
            fields.update({key: value for key, value in ref.data.items() if key in {
                'expected_outcome', 'socratic_question', 'common_mistake', 'hypothesis', 'evidence', 'conclusion',
                'concepts_included', 'process_id', 'process_step_id', 'hint_prompt',
            }})
        sources = []
        if request.includeSolutions:
            for claim_id in ref.data.get('source_claim_ids', []):
                if claim_id in evidence:
                    claim = evidence[claim_id]
                    sources.append({
                        'materialId': str(UUID(bytes=row['material_id'])),
                        'chunkId': claim['chunk_id'], 'blockId': claim['block_id'],
                        'spanStart': claim['start'], 'spanEnd': claim['end'], 'excerpt': claim['quote'],
                    })
        nodes.append({'nodeId': node_id, 'kind': ref.kind, 'attributes': fields,
                      'canonicalCode': ref.data.get('canonical_code'), 'sourceRefs': sources})
        if ref.parent:
            edges.append({'edgeId': stable_id('ownership', ref.parent, node_id),
                          'fromNodeId': ref.parent, 'toNodeId': node_id, 'kind': 'HAS_' + ref.kind})
        for field, kind in (('process_id', 'USES_PROCESS'), ('process_step_id', 'FOLLOWS_PROCESS_STEP')):
            target = ref.data.get(field)
            if target and target in refs:
                edges.append({'edgeId': stable_id(kind, node_id, target), 'fromNodeId': node_id,
                              'toNodeId': target, 'kind': kind})
    for edge in graph['knowledge_relations']:
        edges.append({'edgeId': edge['id'], 'kind': edge['kind'],
                      'fromNodeId': edge['source_id'], 'toNodeId': edge['target_id'],
                      'attributes': {'description': edge.get('description', '')}})
    concepts = {ref.data.get('name'): node_id for node_id, ref in refs.items() if ref.kind == 'KNOWLEDGE_ENTITY'}
    for topic in graph['topics']:
        for name in topic.get('concepts_included', []):
            if name in concepts:
                target = concepts[name]
                edges.append({'edgeId': stable_id('covers', topic['id'], target), 'kind': 'COVERS',
                              'fromNodeId': topic['id'], 'toNodeId': target})
        if request.includeSolutions:
            for chunk in topic.get('chunk_ids', []):
                nodes.append({'nodeId': chunk, 'kind': 'CHUNK', 'attributes': {}, 'sourceRefs': []})
                edges.append({'edgeId': stable_id('references', topic['id'], chunk), 'kind': 'REFERENCES',
                              'fromNodeId': topic['id'], 'toNodeId': chunk})
    nodes = list({node['nodeId']: node for node in nodes}.values())
    selected = {node['nodeId'] for node in nodes}
    focus = request.nodeId
    if request.canonicalCode:
        focus = next((node['nodeId'] for node in nodes if node.get('canonicalCode') == request.canonicalCode), None)
        if focus is None:
            selected = set()
    if focus:
        if focus not in selected:
            raise GraphInputError('Node is not visible in this revision')
        selected = {focus}
        for _ in range(request.depth):
            frontier = {endpoint for edge in edges if edge['fromNodeId'] in selected or edge['toNodeId'] in selected
                        for endpoint in (edge['fromNodeId'], edge['toNodeId'])}
            selected.update(frontier)
    eligible = sorted((node for node in nodes if node['nodeId'] in selected), key=lambda node: node['nodeId'])
    if request.after:
        eligible = [node for node in eligible if node['nodeId'] > request.after]
    truncated = len(eligible) > request.limit
    page = eligible[:request.limit]
    page_ids = {node['nodeId'] for node in page}
    visible_edges = [edge for edge in edges if edge['fromNodeId'] in page_ids and edge['toNodeId'] in page_ids]
    return {'revisionId': str(request.revisionId), 'revisionNumber': row['revision_number'],
            'hash': row['payload_hash'] if request.includeSolutions else None,
            'nodes': page, 'edges': visible_edges, 'truncated': truncated,
            'validationIssues': validation_issues(graph, chunk_ids) if request.includeSolutions else [],
            'nextCursor': page[-1]['nodeId'] if truncated else None}
