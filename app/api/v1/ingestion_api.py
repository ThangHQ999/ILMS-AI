"""Authenticated binary upload from the Spring Boot ingestion worker."""
import asyncio
import hashlib
import secrets
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request

from app.core.config import settings
from app.schema.ingestion_contracts import SourceSnapshot
from app.service.ingestion.benchmark_usage import collect_usage
from app.service.ingestion.config import IngestionSettings
from app.service.ingestion.document_parser import IngestionError, parse_document, validate_source
from app.service.ingestion.multi_agent import run_pipeline
from app.service.ingestion.preprocessing import (
    TokenCounter, build_chunks, semantic_boundaries, semantic_units, verify_chunks,
)

router = APIRouter(prefix='/internal/ingestion', tags=['internal-ingestion'])
_processing = asyncio.Semaphore(2)


def require_worker(request):
    expected = settings.INTERNAL_API_KEY
    supplied = request.headers.get(settings.INTERNAL_API_KEY_HEADER, '')
    if not expected or not secrets.compare_digest(supplied.encode(), expected.encode()):
        raise HTTPException(403, 'Invalid service identity')


@router.post('/publications/{job_id}')
async def publish_approved_draft(job_id: UUID, request: Request):
    require_worker(request)
    from app.service.ingestion.publication.service import publish

    try:
        return {'published': await publish(job_id)}
    except Exception as exc:
        raise HTTPException(502, 'PUBLICATION_FAILED') from exc


@router.post('/draft-graphs/sync')
async def sync_draft_graph(request: Request):
    require_worker(request)
    from app.service.ingestion.drafts.service import sync_next_revision

    return {'synchronized': await sync_next_revision()}


@router.get('/draft-graphs/{job_id}/{revision_id}')
async def read_draft_graph(job_id: UUID, revision_id: UUID, request: Request):
    require_worker(request)
    from app.service.ingestion.drafts.service import get_graph

    graph = await get_graph(job_id, revision_id)
    if graph is None:
        raise HTTPException(404, 'DRAFT_NOT_FOUND')
    return graph


@router.post('/draft')
async def create_draft(request: Request, material_id: UUID, version_id: UUID,
                       filename: str, source_hash: str):
    require_worker(request)
    config = IngestionSettings()
    body = bytearray()
    limit = config.max_file_mb * 1024**2
    async with _processing:
        async for part in request.stream():
            if len(body) + len(part) > limit:
                raise HTTPException(413, 'FILE_LIMIT_EXCEEDED')
            body.extend(part)
        content = bytes(body)
        path = Path(filename)
        try:
            validate_source(path, content, config)
            digest = hashlib.sha256(content).hexdigest()
            if digest != source_hash:
                raise IngestionError('SOURCE_HASH_MISMATCH', 'Upload hash differs')
            snapshot = SourceSnapshot(
                material_id=material_id, material_version_id=version_id,
                source_name=path.name, source_hash=digest,
                size_bytes=len(content), extension=path.suffix.lower(),
            )
            document = await asyncio.to_thread(parse_document, snapshot, config, content=content)
            counter = await asyncio.to_thread(TokenCounter, config.tokenizer_encoding)
            if config.chunk_strategy == 'semantic':
                units = await asyncio.to_thread(lambda: list(semantic_units(document, config, counter)))
                similarities = await semantic_boundaries(units, quiet=True)
                manifest = build_chunks(document, config, counter, units=units, similarities=similarities)
            else:
                manifest = build_chunks(document, config, counter)
            if not verify_chunks(document, manifest, counter).passed:
                raise IngestionError('CHUNK_INTEGRITY_FAILED', 'Chunk verification failed')
            result = {}

            def keep_result(name, value):
                if name == '08-draft.json':
                    result['evidence'] = value
                elif name == '09-graph-draft.json':
                    result['graph'] = value

            with collect_usage() as usage:
                await run_pipeline(
                    document, manifest, 'review', lambda *_: None, keep_result,
                    repair_quotes=False, parallel_chunks=config.api_parallel_chunks, quiet=True,
                    config=config, counter=counter,
                )
            return {**result, 'source_hash': digest, 'parser_version': document.parser_version,
                    'chunker_version': manifest.chunker_version,
                    'chunks': [chunk.model_dump(mode='json') for chunk in manifest.chunks],
                    'parser_warnings': document.warnings, 'usage': usage}
        except IngestionError as exc:
            raise HTTPException(422, exc.code) from exc
        except Exception as exc:
            raise HTTPException(502, 'INGESTION_PROCESSING_FAILED') from exc
