"""Stable business IDs and ownership for the nested ingestion graph format."""
from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid5

from app.service.ingestion.publication.records import ingested_canonical_code


NODE_FIELDS = {
    'KNOWLEDGE_ENTITY': {'name', 'description'},
    'DEFINITION': {'content', 'conditions', 'exceptions'},
    'PROCESS': {'name', 'description'},
    'PROCESS_STEP': {'step_number', 'action', 'hint_prompt'},
    'EXERCISE': {'title', 'content', 'difficulty', 'process_id'},
    'EXERCISE_STEP': {'step_number', 'action', 'expected_outcome', 'socratic_question',
                      'common_mistake', 'process_step_id'},
    'EXAMPLE': {'title', 'code_snippet', 'explanation'},
    'ARGUMENT': {'hypothesis', 'evidence', 'conclusion'},
    'TOPIC': {'name', 'summary', 'concepts_included'},
}
COLLECTIONS = {
    'processes': ('PROCESS', 'steps', 'PROCESS_STEP'),
    'exercises': ('EXERCISE', 'exercise_steps', 'EXERCISE_STEP'),
    'examples': ('EXAMPLE', None, None),
    'arguments': ('ARGUMENT', None, None),
}
PARENT_COLLECTION = {
    'KNOWLEDGE_ENTITY': (None, 'entities'), 'TOPIC': (None, 'topics'),
    'DEFINITION': ('KNOWLEDGE_ENTITY', 'definition'),
    'PROCESS': ('KNOWLEDGE_ENTITY', 'processes'),
    'EXERCISE': ('KNOWLEDGE_ENTITY', 'exercises'),
    'EXAMPLE': ('KNOWLEDGE_ENTITY', 'examples'),
    'ARGUMENT': ('KNOWLEDGE_ENTITY', 'arguments'),
    'PROCESS_STEP': ('PROCESS', 'steps'), 'EXERCISE_STEP': ('EXERCISE', 'exercise_steps'),
}


class GraphInputError(ValueError):
    pass


@dataclass
class NodeRef:
    kind: str
    data: dict[str, Any]
    parent: str | None
    container: dict | list
    key: str | None = None

    def remove(self):
        if isinstance(self.container, list):
            self.container.remove(self.data)
        else:
            self.container.pop(self.key, None)


def inventory(graph):
    result = {}

    def add(kind, value, parent, container, key=None):
        if not isinstance(value, dict) or not isinstance(value.get('id'), str):
            raise GraphInputError('Node requires a business ID')
        if value['id'] in result:
            raise GraphInputError('Duplicate node ID')
        result[value['id']] = NodeRef(kind, value, parent, container, key)

    for entity in graph['entities']:
        add('KNOWLEDGE_ENTITY', entity, None, graph['entities'])
        parent = entity['id']
        if entity.get('definition'):
            add('DEFINITION', entity['definition'], parent, entity, 'definition')
        for field, (kind, step_field, step_kind) in COLLECTIONS.items():
            for child in entity.get(field, []):
                add(kind, child, parent, entity[field])
                if step_field:
                    for step in child.get(step_field, []):
                        add(step_kind, step, child['id'], child[step_field])
    for topic in graph['topics']:
        add('TOPIC', topic, None, graph['topics'])
    return result


def normalize_document(graph, version_id, owner, subject, scope, *, previous=None):
    namespace = UUID(str(version_id))

    def identifier(value, key):
        if not isinstance(value, dict):
            raise GraphInputError('Node must be an object')
        value.setdefault('id', str(uuid5(namespace, key)))

    for field in ('entities', 'topics', 'knowledge_relations'):
        graph.setdefault(field, [])
        if not isinstance(graph[field], list):
            raise GraphInputError(f'{field} must be an array')
    for i, entity in enumerate(graph['entities']):
        identifier(entity, f'entity:{i}')
        if entity.get('definition'):
            identifier(entity['definition'], f"{entity['id']}:definition")
        for field, (_, steps, _) in COLLECTIONS.items():
            entity.setdefault(field, [])
            if not isinstance(entity[field], list):
                raise GraphInputError(f'{field} must be an array')
            for j, child in enumerate(entity[field]):
                identifier(child, f"{entity['id']}:{field}:{j}")
                if steps:
                    child.setdefault(steps, [])
                    if not isinstance(child[steps], list):
                        raise GraphInputError('Steps must be an array')
                    for k, step in enumerate(child[steps]):
                        identifier(step, f"{child['id']}:{steps}:{k}")
    for i, topic in enumerate(graph['topics']):
        identifier(topic, f'topic:{i}')
        topic.setdefault('concepts_included', [])
        topic.setdefault('chunk_ids', [])
    for i, edge in enumerate(graph['knowledge_relations']):
        identifier(edge, f'relation:{i}')
    refs = inventory(graph)
    old = inventory(previous) if previous is not None else {}
    for identifier_value, node in refs.items():
        if node.kind == 'KNOWLEDGE_ENTITY':
            existing = old.get(identifier_value)
            code = existing.data['canonical_code'] if existing else (
                node.data.get('canonical_code') if previous is None else None
            ) or ingested_canonical_code(owner, subject, scope, str(node.data.get('name') or ''))
            # Caller-supplied canonical codes never grant access to another concept.
            node.data['canonical_code'] = code
    return graph
