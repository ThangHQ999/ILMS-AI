"""Document-only orchestration of the four ingestion agents."""
from collections import Counter
import unicodedata
from typing import Literal

from pydantic import BaseModel


from app.agents.expert_agent import run_expert
from app.agents.validator_agent import run_validator
from app.agents.reviewer_agent import run_reviewer
from app.service.ingestion.extraction import extract_document
from app.service.ingestion.graph_assembly import assemble_graph


class OrganizedClaim(BaseModel):
    claim_id: str
    concept: str
    topic: str
    kind: Literal['DEFINITION', 'CONDITION', 'EXCEPTION', 'PROCESS', 'PROCESS_CONTEXT', 'PROCESS_STEP',
                  'EXERCISE', 'EXERCISE_STEP', 'EXAMPLE', 'RELATION', 'ARGUMENT', 'OTHER']
    parent_claim_id: str | None
    step_number: int | None
    parent_title: str
    related_concept: str | None = None
    relation_type: Literal['REQUIRES', 'DEPENDS_ON', 'IS_A', 'PART_OF', 'CONTRASTS_WITH',
                           'USES', 'APPLIES_TO'] | None = None


class Organization(BaseModel):
    items: list[OrganizedClaim]


class Verdict(BaseModel):
    claim_id: str
    supported: bool
    reason: str


class Validation(BaseModel):
    verdicts: list[Verdict]


class ReviewNote(BaseModel):
    claim_id: str
    note: str


class StepRepair(BaseModel):
    claim_id: str
    parent_claim_id: str
    step_number: int
    reason: str


class Review(BaseModel):
    notes: list[ReviewNote]
    step_repairs: list[StepRepair]


def require_ids(actual, expected):
    if sorted(actual) != sorted(expected):
        missing = list((Counter(expected) - Counter(actual)).elements())
        extra = list((Counter(actual) - Counter(expected)).elements())
        raise ValueError(f'Agent claim ID mismatch. Missing: {missing}. Extra or duplicated: {extra}')


async def run_pipeline(document, manifest, stop_after, status, save, *, repair_quotes=True,
                       parallel_chunks=1, quiet=False, graph_hints=None, config=None, counter=None):
    if config is not None and counter is None:
        raise ValueError('Production extraction requires a token counter')
    status('extract', 'STARTED')
    from app.service.llm_service import LLMService

    async with LLMService(quiet=quiet).managed() as llm:
        batches, evidence_rejections, window_issues, extraction_mode = await extract_document(
            llm, document, manifest, save, config=config, counter=counter,
            parallel_chunks=parallel_chunks, repair_quotes=repair_quotes,
        )
        status('extract', 'COMPLETED')
        if stop_after == 'extract':
            return

        status('organize', 'STARTED')
        facts = [fact for batch in batches for fact in batch]
        expert_ids = {str(index): fact['claim_id'] for index, fact in enumerate(facts, 1)}
        instruction = (
            'First identify the parent claims across the whole document: a PROCESS is the source claim '
            'introducing a general procedure, and an EXERCISE is the actual question to solve. '
            'Then classify their children. A PROCESS_STEP points directly to a PROCESS; an EXERCISE_STEP '
            'points directly to an EXERCISE whose specific question the step answers. A step is never a parent. '
            'If the parent cannot be identified from the source, return null. '
            'Assign a consistent owning concept and broad topic across the document. '
            'Keep concept names in the source language. Reuse the underlying defined concept '
            'for its definition, process, examples and exercises. Never use labels such as '
            'Definition, Example, Exercise 1 or process titles as owning concepts. '
            'Classify by the meaning and surrounding text, in any language. A task statement is EXERCISE. A step in a '
            'worked solution is EXERCISE_STEP. A heading alone is OTHER. '
            'For PROCESS_STEP and EXERCISE_STEP provide parent_claim_id of the matching PROCESS or EXERCISE claim. '
            'Use exactly one PROCESS claim for each distinct procedure. Classify its heading or introduction '
            'that refers to the same procedure as PROCESS_CONTEXT with parent_claim_id pointing to that PROCESS. '
            'A definition of the owning concept remains DEFINITION. A sentence announcing the number of steps '
            'is context, not a step. An exercise title or difficulty is OTHER. The actual question with givens '
            'is EXERCISE, and only actions in the worked answer are EXERCISE_STEP. '
            'Read the surrounding source to distinguish a generic procedure from a worked solution. '
            'A heading such as Lời giải bài tập 1 identifies exercise 1 even after the statement of exercise 2. '
            'Read explicit step numbers in any language, including unaccented or misspelled labels. '
            'Keep the original number; use null if the source has no clear number. '
            'For PROCESS or EXERCISE use parent_title for the explicit name or exercise label. '
            'For all other kinds return an empty parent_title. '
            'Use null step_number for all non-step kinds. Only steps and PROCESS_CONTEXT have a parent_claim_id. '
            'Return exactly one item for every supplied short claim_id, including OTHER. '
            'Copy IDs as strings and use the same short IDs for parent_claim_id. Do not invent claims.'
            + (' Optional graph_candidates are unverified hints. Use them only to reconcile names '
               'and identify possible parent links supported by the actual claims. Never use a '
               'candidate as evidence or create claims from it.' if graph_hints else '')
            + ' For an explicit concept relation use RELATION and specify related_concept and relation_type. '
              'Do not infer a relation from proximity. For ARGUMENT keep the source reasoning together. '
              'When neighboring_claims is provided use it only for context or parent IDs, '
              'and return verdicts only for claims.'
        )
        entries = [{**fact, 'claim_id': short_id} for short_id, fact in zip(expert_ids, facts)]
        batch_size = config.expert_batch_claims if config is not None else len(entries)
        organization_items = []
        unknown_expert_ids = set()
        for offset in range(0, len(entries), batch_size):
            batch = entries[offset:offset + batch_size]
            neighbors = entries[max(0, offset - 16):offset] + entries[offset + batch_size:offset + batch_size + 16]
            result = await run_expert(
                llm, instruction,
                {'claims': batch,
                 **({'neighboring_claims': neighbors} if neighbors else {}),
                 **({'graph_candidates': graph_hints} if graph_hints else {})},
                Organization, config=config,
            )
            allowed = {entry['claim_id'] for entry in batch}
            organization_items.extend(item for item in result.items if item.claim_id in allowed)
            unknown_expert_ids.update(item.claim_id for item in result.items if item.claim_id not in allowed)
        save('06-organization-raw.json', Organization(items=organization_items).model_dump())
        counts = Counter(item.claim_id for item in organization_items)
        organization_issues = [
            {'code': 'UNRESOLVED_ORGANIZATION', 'claim_id': original_id,
             'response_count': counts[short_id]}
            for short_id, original_id in expert_ids.items() if counts[short_id] != 1
        ]
        organization_issues.extend({'code': 'UNKNOWN_EXPERT_ID', 'response_id': response_id}
                                   for response_id in sorted(unknown_expert_ids))
        by_id = {}
        for item in organization_items:
            if counts[item.claim_id] != 1:
                continue
            original_id = expert_ids[item.claim_id]
            by_id[original_id] = {
                **item.model_dump(), 'claim_id': original_id,
                'parent_claim_id': expert_ids.get(item.parent_claim_id),
            }
        if organization_issues:
            save('06-organization-issues.json', organization_issues)
        if not by_id:
            raise ValueError('Expert returned no usable classifications')
        organized = [[{**fact, **by_id[fact['claim_id']]} for fact in batch
                      if fact['claim_id'] in by_id] for batch in batches]
        organized_items = [item for batch in organized for item in batch]
        if config is not None:
            organized = [organized_items[i:i + batch_size] for i in range(0, len(organized_items), batch_size)]
        organized_by_id = {item['claim_id']: item for item in organized_items}
        expected_parent_kinds = {
            'PROCESS_STEP': 'PROCESS', 'PROCESS_CONTEXT': 'PROCESS', 'EXERCISE_STEP': 'EXERCISE',
        }
        invalid_links = {}
        for item in organized_items:
            expected = expected_parent_kinds.get(item['kind'])
            if expected is None:
                continue
            parent = organized_by_id.get(item['parent_claim_id'])
            actual = parent['kind'] if parent else None
            if actual != expected:
                invalid_links[item['claim_id']] = {
                    'code': 'INVALID_PARENT_KIND', 'claim_id': item['claim_id'],
                    'parent_claim_id': item['parent_claim_id'],
                    'expected_parent_kind': expected, 'actual_parent_kind': actual,
                }
        if invalid_links:
            organization_issues.extend(invalid_links.values())
            save('06-organization-issues.json', organization_issues)
        save('06-organization.json', organized)
        status('organize', 'COMPLETED')
        if stop_after == 'organize':
            return

        status('validate', 'STARTED')
        accepted = []
        verdicts = []
        for batch_index, items in enumerate(organized):
            if not items:
                continue
            # Use short local IDs to avoid model transcription errors on UUIDs.
            id_map = {str(index): item['claim_id'] for index, item in enumerate(items, 1)}
            payload = []
            for local_id, item in zip(id_map, items):
                parent = organized_by_id.get(item['parent_claim_id'])
                payload.append({
                    **item, 'claim_id': local_id,
                    'invalid_parent_link': item['claim_id'] in invalid_links,
                    'parent': {key: parent[key] for key in ('kind', 'text', 'quote', 'context_before')}
                    if parent else None,
                })
            result = await run_validator(llm,
                'For each claim, decide whether the quote supports its wording and concept '
                'assignment. Reject unsupported inference or missing conditions. For RELATION, '
                'check both named endpoints, direction and relation type explicitly. Account for '
                'every claim without rewriting it or adding new facts. Check the proposed parent and '
                'step number against both excerpts. Reject a wrong parent or wrong step number. '
                'An EXERCISE must contain the actual task and its givens. A heading is insufficient. '
                'An EXERCISE_STEP parent must be an EXERCISE, and explicit source exercise '
                'numbers must agree between the question and solution. '
                'A PROCESS_STEP or PROCESS_CONTEXT parent must be a PROCESS. '
                'Return supported=false for any item marked invalid_parent_link. '
                'Return exactly one verdict per top-level claim_id. Copy its short ID as a string. '
            'Check that a step is an action in a procedure or worked solution. Titles, difficulty, '
            'question statements and announcements of step counts are not steps. Check that '
            'PROCESS_CONTEXT describes the same procedure as its parent. '
                'Leave unresolved links for human review if the claim itself has source evidence.',
                payload, Validation, config=config,
            )
            save(f'validate-{batch_index:04d}-raw.json', result.model_dump())
            counts = Counter(v.claim_id for v in result.verdicts)
            if config is None:
                require_ids(list(v.claim_id for v in result.verdicts), list(id_map))
            else:
                for short_id, original_id in id_map.items():
                    if counts[short_id] != 1:
                        organization_issues.append({'code': 'MISSING_VALIDATOR_VERDICT', 'claim_id': original_id})
                result.verdicts = [
                    verdict for verdict in result.verdicts
                    if verdict.claim_id in id_map and counts[verdict.claim_id] == 1
                ]
            for verdict in result.verdicts:
                verdict.claim_id = id_map[verdict.claim_id]
                if verdict.claim_id in invalid_links:
                    verdict.supported = False
                    verdict.reason = 'Parent is missing or its type does not match the child type.'
            approved = {v.claim_id for v in result.verdicts if v.supported}
            accepted.append([item for item in items if item['claim_id'] in approved])
            verdicts.extend(v.model_dump() for v in result.verdicts)
        save('07-validation.json', verdicts)
        status('validate', 'COMPLETED')
        if stop_after == 'validate':
            return

        status('review', 'STARTED')
        notes = []
        claims = []
        repaired_ids = set()
        repairs = []
        parents = {
            item['claim_id']: item for batch in accepted for item in batch
            if item['kind'] in {'PROCESS', 'EXERCISE'}
        }
        for original_items, items in zip(organized, accepted):
            candidates = {
                item['claim_id']: item for item in original_items
                if item['claim_id'] in invalid_links
                and item['kind'] in {'PROCESS_STEP', 'EXERCISE_STEP'}
            }
            if not items and not candidates:
                continue
            allowed_parents = parents if candidates else {}
            result = await run_reviewer(llm,
                'Flag ambiguous concept names, dubious statements and incomplete sequences '
                'for teacher review. Flag possible duplicates only when they have the same '
                'meaning. Similar names alone are insufficient. Preserve distinct concepts '
                'and keep examples attached to their parent concept. '
                'For unresolved_steps only, propose a step_repair when the source shows both an '
                'explicit positive number and an unambiguous parent among validated_parents. '
                'A general procedure can be repaired to a PROCESS parent even if originally labeled '
                'EXERCISE_STEP. An exercise parent must be the specific problem being solved. '
                'Never repair a heading, introduction or exercise statement as a step. '
                'Explain the source evidence in reason. Leave uncertain links unresolved.',
                {'accepted': items, 'unresolved_steps': list(candidates.values()),
                 'validated_parents': list(allowed_parents.values())}, Review, config=config,
            )
            valid_ids = {item['claim_id'] for item in items} | candidates.keys()
            notes.extend(note.model_dump() for note in result.notes if note.claim_id in valid_ids)
            claims.extend(items)
            repair_counts = Counter(repair.claim_id for repair in result.step_repairs)
            for repair in result.step_repairs:
                item = candidates.get(repair.claim_id)
                parent = allowed_parents.get(repair.parent_claim_id)
                if (item is None or parent is None or repair_counts[repair.claim_id] != 1
                        or repair.step_number < 1 or not repair.reason.strip()
                        or item['step_number'] not in (None, repair.step_number)):
                    continue
                claims.append({
                    **item, 'kind': f"{parent['kind']}_STEP", 'concept': parent['concept'],
                    'topic': parent['topic'], 'parent_claim_id': parent['claim_id'],
                    'step_number': repair.step_number,
                })
                repaired_ids.add(repair.claim_id)
                repairs.append(repair.model_dump())
        if repairs:
            save('08-review-repairs.json', repairs)
        organization_issues = [issue for issue in organization_issues
                               if issue.get('claim_id') not in repaired_ids]
        topics = {}
        topic_names = {}
        for claim in claims:
            name = ' '.join(unicodedata.normalize('NFC', claim['topic']).split())
            if name and claim['kind'] != 'OTHER':
                name = topic_names.setdefault(name.casefold(), name)
                claim['topic'] = name
                topics.setdefault(name, set()).update(claim['chunk_ids'])
        organization_issues.extend(window_issues)
        rejected_ids = {
            verdict['claim_id'] for verdict in verdicts
            if not verdict['supported'] and verdict['claim_id'] not in repaired_ids
        }
        rejected_ids.update(issue['claim_id'] for issue in organization_issues if 'claim_id' in issue)
        save('08-draft.json', {
            'schema_version': 'local-claims-draft-1',
            'status': 'DRAFT',
            'source_policy': 'DOCUMENT_ONLY',
            'extraction_mode': extraction_mode,
            'source_hash': document.source_hash,
            'material_version_id': str(document.material_version_id),
            'claims': claims,
            'claims_requiring_review': [fact for fact in facts if fact['claim_id'] in rejected_ids],
            'validation_verdicts': verdicts,
            'topics': [{'name': name, 'chunk_ids': sorted(ids)} for name, ids in topics.items()],
            'review_notes': notes,
            'review_repairs': repairs,
            'organization_issues': organization_issues,
            'evidence_rejections': evidence_rejections,
            'requires_evidence_review': bool(evidence_rejections or organization_issues),
            'rejected_claim_count': sum(not verdict['supported'] and verdict['claim_id'] not in repaired_ids
                                        for verdict in verdicts),
        })
        status('review', 'COMPLETED')
        status('graph', 'STARTED')
        if not claims:
            raise ValueError('No validated claims to build a graph draft')
        graph = assemble_graph(claims, document, topics)
        graph['issues'].extend(organization_issues)
        if config is not None:
            graph['issues'].extend(
                {'code': 'UNSUPPORTED_CLAIM', 'claim_id': verdict['claim_id']}
                for verdict in verdicts
                if not verdict['supported'] and verdict['claim_id'] not in repaired_ids
                and verdict['claim_id'] not in invalid_links
            )
        graph['review_notes'] = notes
        graph['review_repairs'] = repairs
        graph['requires_evidence_review'] = bool(evidence_rejections or graph['issues'] or
                                                 any(not verdict['supported'] and verdict['claim_id'] not in repaired_ids
                                                     for verdict in verdicts))
        save('09-graph-draft.json', graph)
        status('graph', 'COMPLETED')
