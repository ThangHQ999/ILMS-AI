"""Source-preserving chunk construction and deterministic integrity checks."""
import hashlib
import math
import re
from uuid import uuid5

from app.schema.ingestion_contracts import (
    BlockSpan, ChunkManifest, ChunkProposal, IntegrityReport, ParsedDocument, ValidationIssue,
)
from app.service.ingestion.config import IngestionSettings
from app.service.ingestion.document_parser import IngestionError


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


class TokenCounter:
    def __init__(self, encoding: str):
        import tiktoken
        self.encoding = tiktoken.get_encoding(encoding)
        self.name = encoding

    def count(self, text: str) -> int:
        # Documents may contain literal tokenizer special-token strings.
        return len(self.encoding.encode(text, disallowed_special=()))


def _prefix_end(text: str, start: int, budget: int, counter: TokenCounter) -> int:
    """Find a fitting character boundary; never decode truncated UTF-8 tokens."""
    # Bound tokenizer work for very large blocks; fitting the largest possible
    # prefix is not required, preserving source and enforcing the cap is.
    low, high, best = start + 1, min(len(text), start + budget * 16), start
    while low <= high:
        middle = (low + high) // 2
        if counter.count(text[start:middle]) <= budget:
            best, low = middle, middle + 1
        else:
            high = middle - 1
    if best == start:
        raise IngestionError('TOKEN_BUDGET_TOO_SMALL', 'A source character cannot fit the token budget')
    if best < len(text):
        newline = text.rfind('\n', start, best)
        if newline >= start + (best - start) // 2 and counter.count(text[start:newline + 1]) <= budget:
            best = newline + 1
    return best


def _overlap_start(text: str, start: int, end: int, budget: int, counter: TokenCounter) -> int:
    if not budget:
        return end
    # At most half of a fragment is repeated, even for extremely compressible
    # whitespace. This guarantees useful forward progress under a token budget.
    low, high, best = max(start + 1, start + (end - start) // 2), end, end
    while low <= high:
        middle = (low + high) // 2
        if counter.count(text[middle:end]) <= budget:
            best, high = middle, middle - 1
        else:
            low = middle + 1
    return best


def semantic_units(document, config, counter):
    for block in document.blocks:
        boundaries = [0]
        if block.kind == 'TEXT':
            boundaries.extend(match.end() for match in re.finditer(r'\n[ \t]*\n+', block.text)
                              if match.end() < len(block.text))
        boundaries.append(len(block.text))
        for left, right in zip(boundaries, boundaries[1:]):
            paragraph = block.text[left:right]
            start = 0
            while start < len(paragraph):
                end = _prefix_end(paragraph, start, config.chunk_target_tokens, counter)
                yield block, left + start, left + end
                start = (_overlap_start(paragraph, start, end, config.chunk_overlap_tokens, counter)
                         if end < len(paragraph) else end)


async def semantic_boundaries(units, *, quiet=False):
    if len(units) < 2:
        return {}
    from app.service.llm_service import LLMService

    async with LLMService(quiet=quiet).managed() as service:
        texts = [block.text[start:end] for block, start, end in units]
        vectors = []
        for index in range(0, len(texts), 32):
            batch = texts[index:index + 32]
            result = await service.embed_texts(batch)
            if len(result) != len(batch):
                raise IngestionError('EMBEDDING_COUNT_MISMATCH', 'Semantic embeddings do not match source units')
            vectors.extend(result)
        norms = [math.hypot(*vector) for vector in vectors]
        if len({len(vector) for vector in vectors}) != 1 or any(
            not math.isfinite(norm) or norm <= 0 for norm in norms
        ):
            raise IngestionError('INVALID_EMBEDDINGS', 'Semantic embeddings have invalid dimensions or values')
        return {
            index: sum((a / norms[index - 1]) * (b / norms[index])
                       for a, b in zip(vectors[index - 1], vectors[index]))
            for index in range(1, len(vectors))
        }


def build_chunks(document: ParsedDocument, config: IngestionSettings, counter: TokenCounter,
                 *, units=None, similarities=None) -> ChunkManifest:
    chunks: list[ChunkProposal] = []
    pending: list[BlockSpan] = []
    pieces: list[str] = []
    headings: list[str] = []

    def flush():
        if not pending:
            return
        if len(chunks) >= config.max_chunks:
            raise IngestionError('CHUNK_LIMIT_EXCEEDED', 'Chunk count exceeds configured limit')
        content = '\n\n'.join(pieces)
        digest = text_hash(content)
        index = len(chunks)
        chunks.append(ChunkProposal(
            chunk_id=uuid5(document.material_version_id, f'chunk:{index}:{digest}'),
            material_version_id=document.material_version_id, chunk_index=index,
            content=content, content_hash=digest, token_count=counter.count(content),
            block_refs=list(pending), heading_path=list(headings),
        ))
        pending.clear()
        pieces.clear()

    def structural_units():
        for block in document.blocks:
            start = 0
            while start < len(block.text):
                end = _prefix_end(block.text, start, config.chunk_target_tokens, counter)
                yield block, start, end
                start = (_overlap_start(block.text, start, end, config.chunk_overlap_tokens, counter)
                         if end < len(block.text) else end)

    for index, (block, start, end) in enumerate(units if units is not None else structural_units()):
        piece = block.text[start:end]
        combined = '\n\n'.join([*pieces, piece])
        budget = config.chunk_max_tokens if similarities is not None else config.chunk_target_tokens
        semantic_break = (
            similarities is not None
            and similarities.get(index, 1.0) < config.semantic_min_similarity
            and counter.count('\n\n'.join(pieces)) >= config.semantic_min_chunk_tokens
        )
        if pending and (block.heading_path != headings or counter.count(combined) > budget
                        or semantic_break):
            flush()
        headings = list(block.heading_path)
        pending.append(BlockSpan(block_id=block.block_id, start=start, end=end))
        pieces.append(piece)
        if similarities is None and end < len(block.text):
            flush()
    flush()
    return ChunkManifest(
        material_version_id=document.material_version_id, source_hash=document.source_hash,
        chunker_version=f'{config.chunker_version}-semantic' if similarities is not None else config.chunker_version,
        tokenizer=counter.name,
        target_tokens=config.chunk_target_tokens, max_tokens=config.chunk_max_tokens,
        overlap_tokens=config.chunk_overlap_tokens, chunks=chunks,
    )


def verify_chunks(document: ParsedDocument, manifest: ChunkManifest, counter: TokenCounter) -> IntegrityReport:
    issues: list[ValidationIssue] = []

    def error(code: str, message: str, ref=None):
        issues.append(ValidationIssue(code=code, severity='ERROR', message=message, object_ref=ref))

    blocks = {block.block_id: block for block in document.blocks}
    coverage: dict[str, list[tuple[int, int]]] = {key: [] for key in blocks}
    if len(blocks) != len(document.blocks):
        error('DUPLICATE_BLOCK_ID', 'Block IDs must be unique')
    if manifest.material_version_id != document.material_version_id or manifest.source_hash != document.source_hash:
        error('SOURCE_IDENTITY_MISMATCH', 'Chunk manifest belongs to another document/version')
    if manifest.tokenizer != counter.name:
        error('TOKENIZER_MISMATCH', 'Integrity check must use the manifest tokenizer')
    if not manifest.chunks:
        error('NO_CHUNKS', 'Document has no chunks')
    seen = set()
    for index, chunk in enumerate(manifest.chunks):
        ref = str(chunk.chunk_id)
        if chunk.chunk_id in seen:
            error('DUPLICATE_CHUNK_ID', 'Chunk ID repeated', ref)
        seen.add(chunk.chunk_id)
        if chunk.chunk_index != index or chunk.material_version_id != document.material_version_id:
            error('CHUNK_IDENTITY_MISMATCH', 'Index/version does not match manifest', ref)
        if chunk.chunk_id != uuid5(document.material_version_id, f'chunk:{index}:{chunk.content_hash}'):
            error('CHUNK_IDENTITY_MISMATCH', 'Chunk ID differs from deterministic identity', ref)
        if text_hash(chunk.content) != chunk.content_hash:
            error('CONTENT_HASH_MISMATCH', 'Chunk content hash differs', ref)
        count = counter.count(chunk.content)
        if count != chunk.token_count or count > manifest.max_tokens:
            error('TOKEN_COUNT_MISMATCH', 'Token count differs or exceeds maximum', ref)
        pieces = []
        for span in chunk.block_refs:
            block = blocks.get(span.block_id)
            if block is None or span.end > len(block.text):
                error('INVALID_SOURCE_SPAN', 'Span is outside a known block', ref)
                continue
            pieces.append(block.text[span.start:span.end])
            coverage[span.block_id].append((span.start, span.end))
        if '\n\n'.join(pieces) != chunk.content:
            error('SOURCE_RECONSTRUCTION_MISMATCH', 'Chunk cannot be reconstructed from source spans', ref)
    covered = 0
    for block_id, spans in coverage.items():
        until = 0
        for start, end in sorted(spans):
            if start > until:
                break
            until = max(until, end)
        if until == len(blocks[block_id].text):
            covered += 1
        else:
            error('SOURCE_COVERAGE_GAP', 'Some parsed source characters are not covered by chunks', block_id)
    return IntegrityReport(
        passed=not issues, block_count=len(document.blocks), chunk_count=len(manifest.chunks),
        covered_nonempty_blocks=covered, issues=issues,
    )
