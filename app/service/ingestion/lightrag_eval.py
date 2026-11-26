"""Isolated LightRAG SDK experiment with the same chunks as ILMS."""
from importlib.metadata import PackageNotFoundError, version
from uuid import uuid4
from app.service.ingestion.benchmark_usage import record_openai_usage


async def extract_native(manifest, directory):
    try:
        installed = version('lightrag-hku')
    except PackageNotFoundError as exc:
        raise RuntimeError('Install requirements-lightrag-eval.txt first') from exc
    if installed != '1.4.9':
        raise RuntimeError(f'Expected lightrag-hku==1.4.9, found {installed}')

    import numpy as np
    from lightrag import LightRAG
    from lightrag.base import GRAPH_FIELD_SEP
    from lightrag.kg.shared_storage import initialize_pipeline_status
    from lightrag.utils import EmbeddingFunc, compute_mdhash_id
    from openai import AsyncOpenAI

    from app.core.config import settings
    from app.service.llm_service import LLMService

    if not settings.OPENAI_API_KEY:
        raise RuntimeError('The LightRAG experiment requires the configured OpenAI API key')
    calls = {'llm_requests': 0, 'embedding_batches': 0, 'reported_llm_tokens': 0}
    chunks = manifest.chunks
    source_map = {}
    for chunk in chunks:
        source_id = compute_mdhash_id(chunk.content, prefix='chunk-')
        source_map.setdefault(source_id, []).append(str(chunk.chunk_id))

    def same_chunks(*_):
        return [{'tokens': chunk.token_count, 'content': chunk.content, 'chunk_order_index': index}
                for index, chunk in enumerate(chunks)]

    async with LLMService(quiet=True).managed() as embeddings, AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL,
        timeout=settings.LLM_REQUEST_TIMEOUT, max_retries=settings.LLM_MAX_RETRIES,
    ) as client:
        async def embed(texts):
            calls['embedding_batches'] += 1
            return np.asarray(await embeddings.embed_texts(texts), dtype=np.float32)

        async def complete(prompt, system_prompt=None, history_messages=None, **_):
            calls['llm_requests'] += 1
            messages = [{'role': 'system', 'content': system_prompt}] if system_prompt else []
            messages.extend(history_messages or [])
            messages.append({'role': 'user', 'content': prompt})
            result = await client.chat.completions.create(
                model=settings.OPENAI_EXTRACTION_MODEL, messages=messages,
            )
            record_openai_usage(settings.OPENAI_EXTRACTION_MODEL, result.usage)
            if result.usage:
                calls['reported_llm_tokens'] += result.usage.total_tokens
            if not result.choices or not result.choices[0].message.content:
                raise ValueError('Empty LightRAG extraction response')
            return result.choices[0].message.content

        rag = LightRAG(
            working_dir=str(directory), workspace=uuid4().hex,
            kv_storage='JsonKVStorage', graph_storage='NetworkXStorage',
            vector_storage='NanoVectorDBStorage', doc_status_storage='JsonDocStatusStorage',
            chunking_func=same_chunks, llm_model_func=complete,
            llm_model_name=settings.OPENAI_EXTRACTION_MODEL,
            embedding_func=EmbeddingFunc(embedding_dim=settings.active_embedding_dimension, func=embed),
            llm_model_max_async=3, enable_llm_cache=False, enable_llm_cache_for_entity_extract=False,
        )
        await rag.initialize_storages()
        try:
            await initialize_pipeline_status()
            document_id = f'doc-{manifest.source_hash}'
            await rag.ainsert('\n\n'.join(chunk.content for chunk in chunks), ids=document_id)
            status = (await rag.aget_docs_by_ids(document_id)).get(document_id)
            state = status.get('status') if isinstance(status, dict) else getattr(status, 'status', None)
            if state != 'processed':
                raise RuntimeError(f'LightRAG document status is {state!s}, expected processed')
            graph = (await rag.get_knowledge_graph('*')).model_dump(mode='json')
        finally:
            await rag.finalize_storages()
    return {
        **graph, 'source_hash': manifest.source_hash, 'sdk_version': installed,
        'chunk_id_map': source_map, 'usage': calls,
        'source_id_separator': GRAPH_FIELD_SEP,
        'llm_model': settings.OPENAI_EXTRACTION_MODEL,
    }


def candidate_hints(graph, counter, budget=2200):
    """Keep suggestions small and retain only candidates with mapped source chunks."""
    import json

    hints = []
    remaining = budget
    for kind, records in (('entity', graph['nodes']), ('relation', graph['edges'])):
        for record in records:
            props = record.get('properties', {})
            source_ids = str(props.get('source_id') or '').split(graph['source_id_separator'])
            chunks = sorted({chunk for source in source_ids for chunk in graph['chunk_id_map'].get(source, [])})
            if not chunks:
                continue
            hint = {
                'kind': kind, 'id': record['id'], 'chunk_ids': chunks,
                'description': str(props.get('description') or '')[:400],
            }
            if kind == 'relation':
                hint.update(source=record.get('source'), target=record.get('target'))
            else:
                hint['entity_type'] = props.get('entity_type')
            cost = counter.count(json.dumps(hint, ensure_ascii=False)) + 4
            if cost <= remaining:
                hints.append(hint)
                remaining -= cost
    return hints
