"""Assemble a reviewable graph from verified claims without calling a model."""
from uuid import uuid5


def assemble_graph(claims, document, topics):
    entities = {}
    parents = {}
    issues = []
    source_links = []
    relation_claims = []
    version = document.material_version_id

    def entity_for(name):
        key = name.strip().casefold()
        if key not in entities:
            entities[key] = {
                'id': str(uuid5(version, f'entity:{key}')),
                'name': name.strip(), 'type': 'Concept', 'description': '',
                'embedding': None, 'definition': None, 'processes': [],
                'exercises': [], 'examples': [], 'arguments': [], 'source_claim_ids': [],
            }
        return entities[key]

    for claim in claims:
        kind = claim['kind']
        if kind.endswith('_STEP') or kind in {'PROCESS_CONTEXT', 'OTHER'}:
            continue
        if not claim['concept'].strip():
            issues.append({'code': 'MISSING_CONCEPT', 'claim_id': claim['claim_id']})
            continue
        if kind == 'RELATION':
            relation_claims.append(claim)
            continue
        entity = entity_for(claim['concept'])
        claim_id = claim['claim_id']
        entity['source_claim_ids'].append(claim_id)
        text = claim['text']
        if kind in {'DEFINITION', 'CONDITION', 'EXCEPTION'}:
            definition = entity['definition']
            if definition is None:
                definition = entity['definition'] = {'content': '', 'conditions': [], 'exceptions': []}
            if kind == 'DEFINITION':
                definition['content'] = '\n\n'.join(filter(None, (definition['content'], text)))
                entity['description'] = definition['content']
            else:
                definition['conditions' if kind == 'CONDITION' else 'exceptions'].append(text)
        elif kind == 'ARGUMENT':
            entity['arguments'].append({'id': str(uuid5(version, f'argument:{claim_id}')),
                                        'evidence': claim['quote'], 'source_claim_ids': [claim_id]})
        elif kind == 'EXAMPLE':
            entity['examples'].append({'title': '', 'explanation': text, 'code_snippet': ''})
        elif kind in {'PROCESS', 'EXERCISE'}:
            node_id = str(uuid5(version, f'parent:{claim_id}'))
            label = claim['parent_title'].strip() or text
            if kind == 'PROCESS':
                node = {'id': node_id, 'name': label, 'description': text, 'steps': []}
                entity['processes'].append(node)
            else:
                # Expert may return the entire statement as the display title.
                # A distinct, verified source excerpt can still supply the body.
                if text.strip().casefold() == label.strip().casefold():
                    text = claim['quote'].strip()
                if not text or text.casefold() == label.strip().casefold():
                    issues.append({'code': 'MISSING_EXERCISE_STATEMENT', 'claim_id': claim_id})
                    continue
                node = {'id': node_id, 'title': label, 'content': text,
                        'difficulty': None, 'solution_steps': [], 'exercise_steps': []}
                entity['exercises'].append(node)
            parents[claim_id] = (kind, node)
            source_links.append({'entity_id': entity['id'], 'node_id': node_id, 'claim_ids': [claim_id]})

    for claim in claims:
        if claim['kind'] != 'PROCESS_CONTEXT':
            continue
        parent = parents.get(claim['parent_claim_id'])
        if not parent or parent[0] != 'PROCESS':
            issues.append({'code': 'UNRESOLVED_PROCESS_CONTEXT', 'claim_id': claim['claim_id'],
                           'parent_claim_id': claim['parent_claim_id']})
            continue
        node = parent[1]
        node.setdefault('context', []).append({'text': claim['text'], 'claim_id': claim['claim_id']})
        source_links.append({'node_id': node['id'], 'claim_ids': [claim['claim_id']]})

    grouped_steps = {}
    pending_steps = {}
    block_order = {block.block_id: index for index, block in enumerate(document.blocks)}
    for claim in claims:
        kind = claim['kind']
        if kind not in {'PROCESS_STEP', 'EXERCISE_STEP'}:
            continue
        parent_id = claim['parent_claim_id']
        parent = parents.get(parent_id)
        if not parent or parent[0] != kind.removesuffix('_STEP'):
            issues.append({'code': 'UNRESOLVED_PARENT', 'claim_id': claim['claim_id'],
                           'parent_claim_id': parent_id})
        else:
            pending_steps.setdefault(parent_id, []).append(claim)

    for parent_id, candidates in pending_steps.items():
        implicit = all(item['step_number'] is None for item in candidates)
        if implicit:
            candidates = sorted(candidates, key=lambda item: (
                block_order.get(item['block_id'], len(block_order)), item['start'], item['end'],
            ))
        for ordinal, claim in enumerate(candidates, 1):
            number = ordinal if implicit else claim['step_number']
            if not number or number < 1:
                issues.append({'code': 'UNVERIFIED_STEP_NUMBER', 'claim_id': claim['claim_id'],
                               'step_number': number})
                continue
            grouped_steps.setdefault(parent_id, {}).setdefault(number, []).append({
                **claim, 'step_order_origin': 'SOURCE_POSITION' if implicit else 'SOURCE_NUMBER',
            })

    for parent_id, steps in grouped_steps.items():
        kind, node = parents[parent_id]
        for number, candidates in sorted(steps.items()):
            ids = [item['claim_id'] for item in candidates]
            if len({item['quote'].strip() for item in candidates}) != 1:
                issues.append({'code': 'CONFLICTING_STEP_NUMBER', 'parent_claim_id': parent_id,
                               'step_number': number, 'claim_ids': ids})
                continue
            step_id = str(uuid5(version, f'step:{parent_id}:{number}'))
            action = candidates[0]['quote']
            step = {'id': step_id, 'step_number': number, 'action': action, 'source_claim_ids': ids,
                    'step_order_origin': candidates[0]['step_order_origin']}
            node['steps' if kind == 'PROCESS' else 'exercise_steps'].append(step)
            if kind == 'EXERCISE':
                node['solution_steps'].append(action)
            source_links.append({'node_id': step_id, 'parent_id': node['id'], 'claim_ids': ids})

    for parent_id, (kind, node) in parents.items():
        if kind == 'PROCESS' and not node['steps']:
            issues.append({'code': 'PROCESS_WITHOUT_VERIFIED_STEPS', 'claim_id': parent_id})

    relations = []
    for claim in relation_claims:
        source = entities.get(claim['concept'].strip().casefold())
        target = entities.get((claim.get('related_concept') or '').strip().casefold())
        label = claim.get('relation_type')
        if not source or not target or source == target or not label:
            issues.append({'code': 'UNRESOLVED_CONCEPT_RELATION', 'claim_id': claim['claim_id']})
            continue
        relations.append({'source_id': source['id'], 'target_id': target['id'], 'kind': label,
                          'description': claim['quote'], 'source_claim_ids': [claim['claim_id']]})

    topic_rows = []
    for name, chunk_ids in topics.items():
        concepts = {
            entities[key]['name']
            for claim in claims if claim['topic'] == name
            if (key := claim['concept'].strip().casefold()) in entities
        }
        descriptions = [
            entity['description'] for entity in entities.values()
            if entity['name'] in concepts and entity['description']
        ]
        topic_rows.append({'name': name, 'summary': '\n\n'.join(descriptions)[:2400],
                           'concepts_included': sorted(concepts),
                           'chunk_ids': sorted(chunk_ids)})
    return {
        'schema_version': 'local-graph-draft-2',
        'status': 'DRAFT',
        'source_hash': document.source_hash,
        'metadata': {'domain': '', 'main_topic': topic_rows[0]['name'] if topic_rows else ''},
        'topic': topic_rows[0] if topic_rows else None,
        'topics': topic_rows,
        'entities': list(entities.values()),
        'knowledge_relations': relations,
        'source_links': source_links, 'issues': issues,
        'evidence_artifact': '08-draft.json',
    }
