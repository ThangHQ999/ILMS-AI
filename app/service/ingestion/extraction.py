"""Whole-document extraction and bounded fallback with source provenance."""
import asyncio
from collections import defaultdict
import json

from openai import BadRequestError, LengthFinishReasonError
from pydantic import BaseModel

from app.agents.extractor_agent import run_extractor
from app.service.ingestion.document_parser import IngestionError


class Claim(BaseModel):
    text: str
    quote: str
    block_id: str


class Extraction(BaseModel):
    claims: list[Claim]


EXTRACTION_INSTRUCTION = (
    'Extract atomic claims, definitions, conditions and explicit steps. '
    'Include explicit relations between named concepts and explicitly stated arguments. '
    'Extract named process headings as separate claims. Keep each numbered process step as a separate claim. Preserve its number, full explanation and conditions. '
    'Extract each exercise statement and each supplied solution step separately. '
    'Never emit a standalone exercise heading as a claim. For an exercise, '
    'quote the actual question including its givens, starting after the heading. '
    'Include the exercise label and its stated problem context when available. '
    'Distinguish a worked solution for a specific exercise from a general process. '
    'Keep parenthetical examples. Do not promote a '
    'step or example into an independent process. Copy the exact supporting '
    'excerpt including punctuation and parentheses. For numbered steps, start '
    'the quote at the source step marker and include only that step. '
    'If the quote cannot be copied faithfully, still return the correct block_id. '
    'Use neighboring text only to identify the subject of the current span.'
)


def block_span(block, start=0, end=None):
    return {'block_id': block.block_id, 'locator': block.locator, 'start': start,
            'heading_path': block.heading_path, 'text': block.text[start:end]}


def window_payload(chunks, blocks, previous_tail):
    intervals = defaultdict(list)
    for chunk in chunks:
        for ref in chunk.block_refs:
            intervals[ref.block_id].append((ref.start, ref.end))
    spans = []
    for block_id, offsets in intervals.items():
        merged = []
        for start, end in sorted(offsets):
            if merged and start <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], end)
            else:
                merged.append([start, end])
        spans.extend(block_span(blocks[block_id], start, end) for start, end in merged)
    return {'current_spans': spans, 'previous_tail': previous_tail}


def locate(claim, spans, *, allow_span_fallback=False):
    if not claim.text.strip():
        return None
    matching = [span for span in spans if span['block_id'] == claim.block_id]
    quote = claim.quote.strip()
    for span in matching:
        variants = [quote, quote[:-1] + ','] if len(quote) > 1 and quote.endswith('.') else [quote]
        for candidate in variants:
            offset = span['text'].find(candidate) if candidate else -1
            if offset >= 0:
                return span['start'] + offset, candidate
    if allow_span_fallback and len(matching) == 1:
        return matching[0]['start'], matching[0]['text']
    return None


def exceeds_model_budget(error):
    return isinstance(error, LengthFinishReasonError) or (
        isinstance(error, BadRequestError) and error.code == 'context_length_exceeded'
    )


async def extract_document(llm, document, manifest, save, *, config, counter,
                           parallel_chunks, repair_quotes):
    blocks = {block.block_id: block for block in document.blocks}
    chunks = manifest.chunks
    references = defaultdict(list)
    for chunk in chunks:
        for ref in chunk.block_refs:
            references[ref.block_id].append((ref.start, ref.end, str(chunk.chunk_id)))

    def fits(payload):
        return config is None or counter.count(
            json.dumps(payload, ensure_ascii=False)
        ) <= config.extraction_window_tokens

    async def extract(payload, key):
        spans = payload['current_spans']
        spans_by_id = defaultdict(list)
        for span in spans:
            spans_by_id[span['block_id']].append(span)
        result = await run_extractor(llm, EXTRACTION_INSTRUCTION, payload, Extraction, config=config)
        save(f'extract-{key}-raw.json', result.model_dump())
        facts, rejected = [], []
        for number, claim in enumerate(result.claims):
            evidence = locate(claim, spans_by_id[claim.block_id], allow_span_fallback=config is None)
            if evidence is None and repair_quotes:
                repaired = await run_extractor(
                    llm, 'Repair this claim with one exact source quote, or return no claims.',
                    {'claim': claim.model_dump(), 'current_spans': spans_by_id[claim.block_id]},
                    Extraction, config=config,
                )
                if len(repaired.claims) == 1:
                    claim = repaired.claims[0]
                    evidence = locate(claim, spans_by_id[claim.block_id], allow_span_fallback=config is None)
            if evidence is None:
                rejected.append({'window': key, 'reason': 'QUOTE_NOT_FOUND_IN_CURRENT_SPAN',
                                 'claim': claim.model_dump()})
                continue
            start, quote = evidence
            end = start + len(quote)
            linked = list(dict.fromkeys(
                chunk_id for lower, upper, chunk_id in references[claim.block_id]
                if lower < end and start < upper
            ))
            if not linked:
                rejected.append({'window': key, 'reason': 'QUOTE_WITHOUT_CHUNK',
                                 'claim': claim.model_dump()})
                continue
            facts.append({
                **claim.model_dump(), 'quote': quote,
                'claim_id': f'{linked[0]}:{key}:{number}', 'chunk_id': linked[0], 'chunk_ids': linked,
                'start': start, 'end': end,
                'context_before': blocks[claim.block_id].text[max(0, start - 1000):start],
            })
        facts.sort(key=lambda item: (block_order[item['block_id']], item['start'], item['end']))
        save(f'extract-{key}.json', facts)
        return facts, rejected

    block_order = {block_id: index for index, block_id in enumerate(blocks)}
    results = []
    issues = []
    attempted_whole = False
    if config is not None:
        full_payload = {'current_spans': [block_span(block) for block in document.blocks], 'previous_tail': ''}
        if fits(full_payload):
            attempted_whole = True
            try:
                results.append(await extract(full_payload, 'document'))
            except (LengthFinishReasonError, BadRequestError) as error:
                if not exceeds_model_budget(error):
                    raise

    windows_used = not results
    if windows_used:
        windows = []
        if config is None:
            windows = [(chunk,) for chunk in chunks]
        else:
            start, tokens = 0, 0
            for index, chunk in enumerate(chunks):
                cost = chunk.token_count + 32 * len(chunk.block_refs)
                if index > start and tokens + cost > config.extraction_window_tokens:
                    windows.append(chunks[start:index])
                    start, tokens = index, 0
                tokens += cost
            if start < len(chunks):
                windows.append(chunks[start:])
            if attempted_whole and len(windows) == 1 and len(chunks) > 1:
                midpoint = len(chunks) // 2
                windows = [chunks[:midpoint], chunks[midpoint:]]

        async def extract_window(window, key, previous_tail):
            payload = window_payload(window, blocks, previous_tail)
            if previous_tail and not fits(payload):
                payload['previous_tail'] = ''
            if fits(payload):
                try:
                    return [await extract(payload, key)], []
                except Exception as error:
                    if config is None:
                        raise
                    if not exceeds_model_budget(error):
                        return [], [window_issue(window, key)]
            if len(window) == 1:
                return [], [window_issue(window, key)]
            midpoint = len(window) // 2
            left, left_issues = await extract_window(window[:midpoint], f'{key}-a', previous_tail)
            right, right_issues = await extract_window(
                window[midpoint:], f'{key}-b', window[midpoint - 1].content[-1200:],
            )
            return left + right, left_issues + right_issues

        for offset in range(0, len(windows), parallel_chunks):
            group = await asyncio.gather(*(
                extract_window(windows[index], str(index),
                               windows[index - 1][-1].content[-1200:] if index else '')
                for index in range(offset, min(offset + parallel_chunks, len(windows)))
            ))
            for completed, failed in group:
                results.extend(completed)
                issues.extend(failed)

    batches, rejections, seen = [], [], set()
    for facts, rejected in results:
        unique = []
        for fact in facts:
            key = (fact['block_id'], fact['start'], fact['end'], fact['text'].strip().casefold())
            if key not in seen:
                seen.add(key)
                unique.append(fact)
        batches.append(unique)
        rejections.extend(rejected)
    save('05-extraction.json', batches)
    if rejections:
        save('05-evidence-rejections.json', rejections)
    if not any(batches):
        if not results and issues:
            raise IngestionError('EXTRACTION_WINDOWS_FAILED', 'No extraction window completed')
        raise IngestionError('NO_VERIFIED_CLAIMS', 'No extracted claim had verifiable source text')
    mode = 'FULL_DOCUMENT' if attempted_whole and not windows_used else 'WINDOWED'
    return batches, rejections, issues, mode


def window_issue(window, key):
    return {'code': 'EXTRACTION_WINDOW_FAILED', 'window': key,
            'chunk_ids': [str(chunk.chunk_id) for chunk in window]}
