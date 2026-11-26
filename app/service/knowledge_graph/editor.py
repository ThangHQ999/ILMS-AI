"""Apply graph edits atomically in memory and validate the resulting snapshot."""
from copy import deepcopy
from uuid import uuid4

from app.service.ingestion.publication.records import SEMANTIC_RELATIONS, stable_id
from app.service.knowledge_graph.document import (
    GraphInputError, NODE_FIELDS, PARENT_COLLECTION, inventory, normalize_document,
)


def check_fields(kind, fields):
    if kind not in NODE_FIELDS or set(fields) - NODE_FIELDS[kind]:
        raise GraphInputError('Unsupported node kind or attribute')
    for key, value in fields.items():
        if value is None:
            continue
        if key == 'step_number':
            if type(value) is not int or value < 1:
                raise GraphInputError('Step number must be positive')
        elif key in {'conditions', 'exceptions', 'concepts_included'}:
            if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
                raise GraphInputError('Conditions and exceptions must be string arrays')
        elif not isinstance(value, str) or len(value) > 100_000:
            raise GraphInputError('Invalid text attribute')
        elif key in {'name', 'title'} and len(value) > 255:
            raise GraphInputError('Name or title exceeds 255 characters')


def attach(graph, refs, kind, parent_id, node):
    expected, field = PARENT_COLLECTION[kind]
    if expected is None:
        if parent_id:
            raise GraphInputError('Top-level node cannot have a parent')
        graph[field].append(node)
        return
    parent = refs.get(parent_id)
    if parent is None or parent.kind != expected:
        raise GraphInputError('Parent type does not match the node')
    if field == 'definition':
        if parent.data.get(field):
            raise GraphInputError('Concept already has a definition')
        parent.data[field] = node
    else:
        parent.data.setdefault(field, []).append(node)


def edit_document(base, operations, context, replacement=None):
    graph = deepcopy(base if replacement is None else replacement)
    mappings = {}
    if replacement is not None and operations:
        raise GraphInputError('Choose operations or a replacement document')
    for operation in operations:
        operation = operation.model_copy(update={
            field: mappings.get(getattr(operation, field), getattr(operation, field))
            for field in ('nodeId', 'parentId', 'newParentId', 'fromNodeId', 'toNodeId')
        })
        refs = inventory(graph)
        op = operation.op
        node = refs.get(operation.nodeId)
        if op == 'CREATE_NODE':
            check_fields(operation.kind, operation.fields)
            identifier = str(uuid4())
            if operation.nodeId:
                if operation.nodeId in refs or operation.nodeId in mappings:
                    raise GraphInputError('New node alias is already in use')
                mappings[operation.nodeId] = identifier
            attach(graph, refs, operation.kind, operation.parentId, {
                'id': identifier, **operation.fields, 'origin': 'TEACHER_EDITED',
                'source_claim_ids': [],
            })
            normalize_document(graph, **context, previous=base)
        elif op == 'UPDATE_NODE':
            if node is None:
                raise GraphInputError('Node does not exist in this revision')
            check_fields(node.kind, operation.fields)
            if node.kind == 'KNOWLEDGE_ENTITY' and 'name' in operation.fields:
                old_name = node.data.get('name')
                for topic in graph['topics']:
                    topic['concepts_included'] = [
                        operation.fields['name'] if name == old_name else name
                        for name in topic.get('concepts_included', [])
                    ]
            if node.kind == 'DEFINITION' and 'content' in operation.fields:
                parent = refs[node.parent].data
                if not parent.get('description') or parent.get('description') == node.data.get('content'):
                    parent['description'] = operation.fields['content']
            node.data.update(operation.fields)
            node.data['origin'] = 'TEACHER_EDITED'
        elif op == 'MOVE_NODE':
            if node is None or PARENT_COLLECTION[node.kind][0] is None:
                raise GraphInputError('Node cannot be moved')
            node.remove()
            attach(graph, inventory(graph), node.kind, operation.newParentId, node.data)
        elif op == 'DELETE_NODE':
            if node is None:
                raise GraphInputError('Node does not exist in this revision')
            descendants = {operation.nodeId}
            for candidate_id, candidate in refs.items():
                if candidate.parent in descendants:
                    descendants.add(candidate_id)
            if len(descendants) > 1 and not operation.cascade:
                raise GraphInputError('Node has children; move them or request cascade')
            if node.kind == 'DEFINITION':
                parent = refs[node.parent].data
                if parent.get('description') == node.data.get('content'):
                    parent['description'] = ''
            node.remove()
            graph['knowledge_relations'] = [edge for edge in graph['knowledge_relations']
                if edge.get('source_id') not in descendants and edge.get('target_id') not in descendants]
            if node.kind == 'KNOWLEDGE_ENTITY':
                for topic in graph['topics']:
                    topic['concepts_included'] = [name for name in topic.get('concepts_included', [])
                                                  if name != node.data.get('name')]
            for candidate in inventory(graph).values():
                for field in ('process_id', 'process_step_id'):
                    if candidate.data.get(field) in descendants:
                        candidate.data[field] = None
        elif op in {'CREATE_EDGE', 'UPDATE_EDGE', 'DELETE_EDGE'}:
            edges = graph['knowledge_relations']
            existing = next((edge for edge in edges if edge['id'] == operation.edgeId), None)
            if op == 'DELETE_EDGE':
                if existing is None:
                    raise GraphInputError('Only semantic edges can be deleted; use move for ownership')
                edges.remove(existing)
                continue
            if op == 'UPDATE_EDGE' and existing is None:
                raise GraphInputError('Semantic edge does not exist')
            if set(operation.fields) - {'description'}:
                raise GraphInputError('Unsupported relation attribute')
            description = operation.fields.get('description')
            if description is not None and (not isinstance(description, str) or len(description) > 100_000):
                raise GraphInputError('Invalid relation description')
            kind = operation.kind or (existing or {}).get('kind')
            source = operation.fromNodeId or (existing or {}).get('source_id')
            target = operation.toNodeId or (existing or {}).get('target_id')
            if kind not in SEMANTIC_RELATIONS or source == target or any(
                endpoint not in refs or refs[endpoint].kind != 'KNOWLEDGE_ENTITY'
                for endpoint in (source, target)
            ):
                raise GraphInputError('Invalid semantic relation')
            edge = {'id': existing['id'] if existing else str(uuid4()), 'kind': kind,
                    'source_id': source, 'target_id': target,
                    'description': (existing or {}).get('description', ''),
                    **operation.fields, 'origin': 'TEACHER_EDITED'}
            edge['description'] = edge.get('description') or ''
            if existing:
                edges.remove(existing)
            edges.append(edge)
        elif op in {'LINK_TOPIC_CHUNK', 'UNLINK_TOPIC_CHUNK'}:
            if node is None or node.kind != 'TOPIC' or operation.chunkId is None:
                raise GraphInputError('Topic and chunk IDs are required')
            chunk_id = str(operation.chunkId)
            ids = node.data.setdefault('chunk_ids', [])
            if op == 'LINK_TOPIC_CHUNK' and chunk_id not in ids:
                ids.append(chunk_id)
            if op == 'UNLINK_TOPIC_CHUNK' and chunk_id in ids:
                ids.remove(chunk_id)

    normalize_document(graph, **context, previous=base)
    before, after = inventory(base), inventory(graph)
    for node_id, node in after.items():
        check_fields(node.kind, {key: value for key, value in node.data.items() if key in NODE_FIELDS[node.kind]})
        old = before.get(node_id)
        if old and old.kind != node.kind:
            raise GraphInputError('A node ID cannot change kind')
        node.data['source_claim_ids'] = old.data.get('source_claim_ids', []) if old else []
        node.data['origin'] = 'TEACHER_EDITED' if old is None or old.data != node.data else old.data.get('origin', 'DOCUMENT')
    # Review flags are inherited from the persisted snapshot, never from a browser.
    for field in ('issues', 'requires_evidence_review', 'source_hash', 'source_links'):
        graph[field] = deepcopy(base.get(field))
    return graph, mappings


def validation_issues(graph, chunk_ids):
    refs = inventory(graph)
    issues = []

    def issue(code, target, message, severity='BLOCKER'):
        issues.append({'id': stable_id(code, target), 'code': code, 'targetId': target,
                       'severity': severity, 'message': message})

    names, numbers, edges, edge_ids = set(), set(), set(), set()
    for node_id, node in refs.items():
        required = {'KNOWLEDGE_ENTITY': 'name', 'TOPIC': 'name', 'DEFINITION': 'content',
                    'EXERCISE': 'content', 'PROCESS': 'name', 'PROCESS_STEP': 'action',
                    'EXERCISE_STEP': 'action', 'EXAMPLE': 'explanation', 'ARGUMENT': 'evidence'}[node.kind]
        if not str(node.data.get(required) or '').strip():
            issue('MISSING_REQUIRED_FIELD', node_id, f'{required} is required')
        if node.kind == 'KNOWLEDGE_ENTITY':
            name = str(node.data.get('name') or '').strip().casefold()
            if name in names:
                issue('DUPLICATE_CONCEPT_NAME', node_id, 'Concept names must be distinct')
            names.add(name)
        if node.kind.endswith('_STEP'):
            number = node.data.get('step_number')
            if type(number) is not int or number < 1 or (node.parent, number) in numbers:
                issue('INVALID_STEP_NUMBER', node_id, 'Step numbers must be positive and unique within their parent')
            numbers.add((node.parent, number))
        if node.kind == 'TOPIC':
            links = node.data.get('chunk_ids', [])
            concepts = node.data.get('concepts_included', [])
            if not isinstance(links, list) or any(chunk not in chunk_ids for chunk in links):
                raise GraphInputError('Topic chunk belongs to another source version')
            if not links or not concepts:
                issue('EMPTY_TOPIC', node_id, 'Topic requires a concept and source chunk')
            if not isinstance(concepts, list) or any(
                name not in {n.data.get('name') for n in refs.values() if n.kind == 'KNOWLEDGE_ENTITY'}
                for name in concepts
            ):
                raise GraphInputError('Topic refers to an unknown concept')
        for field, expected in (('process_id', 'PROCESS'), ('process_step_id', 'PROCESS_STEP')):
            target = node.data.get(field)
            if target and (target not in refs or refs[target].kind != expected):
                raise GraphInputError('Invalid process reference')
    for edge in graph['knowledge_relations']:
        if not isinstance(edge.get('description', ''), str) or edge['id'] in edge_ids:
            raise GraphInputError('Invalid relation description or duplicate edge ID')
        edge_ids.add(edge['id'])
        pair = (edge.get('source_id'), edge.get('target_id'), edge.get('kind'))
        if (pair in edges or pair[0] == pair[1] or pair[2] not in SEMANTIC_RELATIONS
                or any(key not in refs or refs[key].kind != 'KNOWLEDGE_ENTITY' for key in pair[:2])):
            raise GraphInputError('Invalid or duplicate semantic relation')
        edges.add(pair)
    if not graph['entities']:
        issue('EMPTY_GRAPH', 'graph', 'At least one concept is required')
    for index, original in enumerate(graph.get('issues') or []):
        issue('SOURCE_REVIEW', str(index), str(original), severity='WARNING')
    if graph.get('requires_evidence_review'):
        issue('SOURCE_REVIEW', 'graph', 'Review the original extraction evidence', severity='WARNING')
    return issues
