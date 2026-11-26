"""Revision-specific editor projection, separate from the published retrieval graph."""
import json

from app.service.ingestion.publication.records import normalize, stable_id


def project(revision_id, graph):
    nodes, edges = [], []
    entities, names = {}, {}

    def items(parent, field):
        value = parent.get(field)
        if isinstance(value, list):
            yield from ((i, item) for i, item in enumerate(value) if isinstance(item, dict))

    def add(kind, path, fields, parent=None, relation='CONTAINS'):
        identifier = stable_id(revision_id, *path)
        nodes.append({
            'id': identifier, 'kind': kind, 'path': '/'.join(map(str, path)),
            'fields_json': json.dumps({
                key: value for key, value in fields.items()
                if key not in {'definition', 'processes', 'exercises', 'examples',
                               'arguments', 'steps', 'exercise_steps', 'solution_steps'}
            }, ensure_ascii=False),
            'label': next((fields[key] for key in ('name', 'title', 'content', 'action',
                           'explanation', 'evidence', 'summary') if isinstance(fields.get(key), str)
                           and fields[key].strip()), kind)[:160],
        })
        if parent:
            edges.append({'source': parent, 'target': identifier, 'kind': relation})
        return identifier

    for index, entity in items(graph, 'entities'):
        path = ['entities', index]
        root = add('KnowledgeEntity', path, entity)
        if isinstance(entity.get('id'), str):
            entities[entity['id']] = root
        if isinstance(entity.get('name'), str):
            names[normalize(entity['name'])] = root
        if isinstance(entity.get('definition'), dict):
            add('Definition', [*path, 'definition'], entity['definition'], root, 'HAS_DEFINITION')
        for field, kind in (('processes', 'Process'), ('exercises', 'Exercise'),
                            ('examples', 'Example'), ('arguments', 'Argument')):
            for child_index, child in items(entity, field):
                child_path = [*path, field, child_index]
                child_id = add(kind, child_path, child, root, f'HAS_{kind.upper()}')
                if field in ('processes', 'exercises'):
                    steps = 'steps' if field == 'processes' else 'exercise_steps'
                    for step_index, step in items(child, steps):
                        add(f'{kind}Step', [*child_path, steps, step_index], step, child_id, 'HAS_STEP')
    chunks = {}
    for index, topic in items(graph, 'topics'):
        topic_id = add('Topic', ['topics', index], topic)
        codes = topic.get('concepts_included')
        if isinstance(codes, list):
            for name in codes:
                if isinstance(name, str) and (entity_id := names.get(normalize(name))):
                    edges.append({'source': topic_id, 'target': entity_id, 'kind': 'COVERS'})
        chunk_ids = topic.get('chunk_ids')
        if isinstance(chunk_ids, list):
            for value in chunk_ids:
                if not isinstance(value, str):
                    continue
                if value not in chunks:
                    chunks[value] = add('Chunk', ['chunks', value], {'name': value})
                edges.append({'source': topic_id, 'target': chunks[value], 'kind': 'REFERENCES'})
    for _, relation in items(graph, 'knowledge_relations'):
        source, target = relation.get('source_id'), relation.get('target_id')
        if isinstance(source, str) and isinstance(target, str) and source in entities and target in entities:
            edges.append({'source': entities[source], 'target': entities[target],
                          'kind': str(relation.get('kind') or 'RELATED_TO'),
                          'description': relation.get('description') if isinstance(relation.get('description'), str) else None})
    return nodes, list({(edge['source'], edge['target'], edge['kind']): edge for edge in edges}.values())
