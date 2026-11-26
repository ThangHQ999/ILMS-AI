import asyncio
import inspect
from app.core.config import settings
from app.db.chroma import chroma_manager


def embedding_identity():
    provider = settings.EMBEDDING_PROVIDER
    model = settings.OPENAI_EMBEDDING_MODEL if provider == 'openai' else settings.GEMINI_EMBEDDING_MODEL
    return f'{provider}:{model}:{settings.active_embedding_dimension}'


async def invoke(obj, method, **kwargs):
    fn = getattr(obj, method)
    if inspect.iscoroutinefunction(fn):
        return await fn(**kwargs)
    value = await asyncio.to_thread(fn, **kwargs)
    return await value if inspect.isawaitable(value) else value


class EntityVectorRepository:
    async def collection(self):
        # Create the entity index lazily; startup does not mutate it.
        client = chroma_manager._async_client or chroma_manager._sync_client
        if client is None:
            raise RuntimeError('Chroma client is not initialized')
        identity = embedding_identity()
        collection = await invoke(client, 'get_or_create_collection',
            name=settings.SOCRATIC_ENTITY_COLLECTION,
            metadata={'hnsw:space': 'cosine', 'embedding_identity': identity})
        metadata = collection.metadata or {}
        if metadata.get('hnsw:space') != 'cosine' or metadata.get('embedding_identity') != identity:
            raise ValueError('Entity collection embedding identity or metric mismatch; rebuild a versioned collection')
        return collection

    async def search(self, embedding, subject=None):
        query = {'query_embeddings': [embedding], 'n_results': settings.SOCRATIC_RETRIEVAL_K,
                 'include': ['documents', 'metadatas', 'distances']}
        if subject:
            query['where'] = {'subject': subject.strip().upper()}
        raw = await invoke(await self.collection(), 'query', **query)
        results = []
        for code, meta, distance in zip((raw.get('ids') or [[]])[0],
                (raw.get('metadatas') or [[]])[0], (raw.get('distances') or [[]])[0]):
            if distance is not None and 1 - distance >= settings.SOCRATIC_MIN_SIMILARITY:
                results.append({'canonical_code': code, **(meta or {})})
        return results

    async def upsert(self, entities, embeddings):
        if not entities:
            return
        await invoke(await self.collection(), 'upsert',
            ids=[e['canonical_code'] for e in entities], embeddings=embeddings,
            documents=[f"{e['canonical_code']} | {e['name']} ({e['subject']}): {e.get('description', '')}" for e in entities],
            metadatas=[{'name': e['name'], 'subject': e['subject']} for e in entities])
