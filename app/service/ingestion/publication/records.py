"""Build the graph and index plan from one approved draft."""
from collections import defaultdict
import json
import unicodedata
from uuid import UUID, uuid5


SEMANTIC_RELATIONS = frozenset({
    'REQUIRES', 'DEPENDS_ON', 'IS_A', 'PART_OF', 'CONTRASTS_WITH', 'USES', 'APPLIES_TO',
})
IDENTITY_NAMESPACE = UUID('a62900a9-f03c-46f3-94ba-9a7b3b7766ae')


def stable_id(*parts):
    return str(uuid5(IDENTITY_NAMESPACE, json.dumps(parts, ensure_ascii=False)))


def normalize(value):
    return ' '.join(unicodedata.normalize('NFC', value).split()).casefold()


def ingested_canonical_code(owner: str, subject: str, scope: str, name: str) -> str:
    namespace = owner if scope == 'TEACHER' else 'GLOBAL'
    return f'INGESTION_{stable_id(namespace, subject, normalize(name))}'


def build_records(publication_id, draft, evidence, chunks, owner, subject, scope):
    by_chunk = {row['id']: row for row in chunks}
    codes_by_chunk = defaultdict(set)
    nodes, edges, vectors, topics = [], [], [], []
    namespace = owner if scope == 'TEACHER' else 'GLOBAL'
    codes = {}
    roots = {}
    claims = {claim['claim_id']: claim for claim in evidence.get('claims', [])}

    def source_chunks(item):
        return sorted({
            chunk_id for claim_id in item.get('source_claim_ids', [])
            for claim in [claims.get(claim_id, {})]
            for chunk_id in claim.get('chunk_ids', [claim.get('chunk_id')])
            if chunk_id in by_chunk
        })

    def vector(kind, key, content):
        vectors.append((stable_id(publication_id, kind, key), content, {
            'publication_id': publication_id, 'kind': kind, 'item_id': key, 'subject': subject,
        }))

    def node(kind, key, fields, parent=None, edge=None):
        identifier = stable_id(publication_id, kind, key)
        nodes.append({
            'id': identifier, 'publication_id': publication_id, 'node_kind': kind,
            'owner_id': owner, 'scope': scope, 'subject': subject,
            **{field: value for field, value in fields.items() if value is not None},
        })
        if parent:
            edges.append({'parent': parent, 'child': identifier, 'kind': edge})
        return identifier

    def steps(items, parent, kind, action_key, owner_key):
        numbers = set()
        for item in items:
            number = item['step_number']
            action = item['action'].strip()
            if type(number) is not int or number < 1 or number in numbers or not action:
                raise ValueError('Invalid step in approved draft')
            numbers.add(number)
            process_step = item.get('process_step_id')
            node(kind, item['id'], {'step_number': number, action_key: action, owner_key: parent,
                                     'source_chunk_ids': source_chunks(item),
                                     **{key: item.get(key) for key in ('hint_prompt', 'expected_outcome',
                                         'socratic_question', 'common_mistake')},
                                     'process_step_id': stable_id(publication_id, 'ProcessStep', process_step) if process_step else None},
                 parent, 'HAS_STEP')

    for entity in draft['entities']:
        name = entity['name'].strip()
        key = normalize(name)
        if not key or key in codes:
            raise ValueError('Missing or duplicate concept name')
        code = entity.get('canonical_code') or ingested_canonical_code(owner, subject, scope, name)
        codes[key] = code
        description = entity.get('description') or ''
        entity_chunks = source_chunks(entity)
        root = node('KnowledgeEntitySnapshot', entity['id'],
                    {'name': name, 'canonical_code': code, 'description': description,
                     'source_chunk_ids': entity_chunks})
        roots[entity['id']] = root
        for chunk_id in entity_chunks:
            codes_by_chunk[chunk_id].add(code)
        definition_text = (entity.get('definition') or {}).get('content', '')
        vector('entity', code, f'{name}\n{description}\n{definition_text}')
        if definition := entity.get('definition'):
            node('Definition', entity['id'], {k: definition.get(k) for k in
                 ('content', 'conditions', 'exceptions')}, root, 'HAS_DEFINITION')
        for index, example in enumerate(entity.get('examples', [])):
            node('Example', f"{entity['id']}:{index}", {k: example.get(k) for k in
                 ('title', 'explanation', 'code_snippet')}, root, 'HAS_EXAMPLE')
        for argument in entity.get('arguments', []):
            node('Argument', argument['id'], {
                'hypothesis': argument.get('hypothesis'), 'evidence': argument['evidence'],
                'conclusion': argument.get('conclusion'), 'source_chunk_ids': source_chunks(argument),
            }, root, 'HAS_ARGUMENT')
        for process in entity.get('processes', []):
            parent = node('Process', process['id'], {k: process.get(k) for k in
                          ('name', 'description')}, root, 'HAS_PROCESS')
            steps(process['steps'], parent, 'ProcessStep', 'action', 'process_id')
        for exercise in entity.get('exercises', []):
            if not exercise['content'].strip():
                raise ValueError('Exercise statement is empty')
            process_id = exercise.get('process_id')
            parent = node('Exercise', exercise['id'], {
                **{k: exercise.get(k) for k in ('title', 'content', 'difficulty')},
                'process_id': stable_id(publication_id, 'Process', process_id) if process_id else None,
            }, root, 'HAS_EXERCISE')
            steps(exercise.get('exercise_steps', []), parent, 'ExerciseStep', 'instruction', 'exercise_id')

    for edge in draft.get('knowledge_relations', []):
        kind = edge['kind']
        source = roots.get(edge['source_id'])
        target = roots.get(edge['target_id'])
        if kind not in SEMANTIC_RELATIONS or not source or not target or source == target:
            raise ValueError('Invalid semantic relation')
        edges.append({'parent': source, 'child': target, 'kind': kind,
                      'description': edge['description'], 'source_chunk_ids': source_chunks(edge)})

    node_ids = {n['id'] for n in nodes}
    for item in nodes:
        for field, kind in (('process_id', 'USES_PROCESS'), ('process_step_id', 'FOLLOWS_PROCESS_STEP')):
            target = item.get(field)
            applicable = (field == 'process_id' and item['node_kind'] == 'Exercise') or (
                field == 'process_step_id' and item['node_kind'] == 'ExerciseStep'
            )
            if applicable and target and target in node_ids:
                edges.append({'parent': item['id'], 'child': target, 'kind': kind})

    seen_topics = set()
    for topic in draft['topics']:
        name = topic['name'].strip()
        key = normalize(name)
        concepts = sorted({codes[normalize(name)] for name in topic['concepts_included']})
        chunk_ids = sorted(set(topic['chunk_ids']))
        if not key or len(name) > 255 or not concepts or not chunk_ids or not set(chunk_ids) <= by_chunk.keys():
            raise ValueError('Invalid topic or topic chunk')
        topic_id = stable_id(namespace, subject, key, concepts)
        if topic_id in seen_topics:
            raise ValueError('Duplicate topic in approved draft')
        seen_topics.add(topic_id)
        summary = topic['summary'].strip()
        topics.append({'id': topic_id, 'name': name, 'summary': summary, 'codes': concepts, 'chunks': chunk_ids})
        node('TopicSnapshot', topic_id, {'topic_id': topic_id, 'name': name, 'description': summary,
                                        'source_chunk_ids': chunk_ids})
        vector('topic', topic_id, f'{name}\n{summary}')

    for chunk in chunks:
        vector('chunk', chunk['id'], chunk['content'])
    if not nodes or len({row['id'] for row in nodes}) != len(nodes):
        raise ValueError('Missing graph or duplicate node ID')
    return nodes, edges, vectors, topics, codes_by_chunk
