"""Publication-scoped vectors shared by ingestion and tutoring."""
from app.db.chroma import chroma_manager
from app.repository.chroma.entity_vector_repo import embedding_identity, invoke


async def publication_collection(name, *, create=False):
    client = chroma_manager._async_client or chroma_manager._sync_client
    if client is None:
        raise RuntimeError('Chroma is unavailable')
    if create:
        collection = await invoke(client, 'get_or_create_collection', name=name,
                                  metadata={'embedding_identity': embedding_identity(), 'hnsw:space': 'cosine'})
    else:
        collection = await invoke(client, 'get_collection', name=name)
    metadata = collection.metadata or {}
    if metadata.get('embedding_identity') != embedding_identity() or metadata.get('hnsw:space') != 'cosine':
        raise ValueError('Publication embedding identity mismatch')
    return collection


async def search_publications(collection, vector, publication_ids, kind, limit):
    if not publication_ids:
        return []
    result = await invoke(collection, 'query', query_embeddings=[vector], n_results=limit,
                          where={'$and': [{'publication_id': {'$in': publication_ids}}, {'kind': kind}]},
                          include=['metadatas', 'distances'])
    return list(zip(result['metadatas'][0], result['distances'][0]))
