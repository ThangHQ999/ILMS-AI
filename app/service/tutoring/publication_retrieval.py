"""Retrieve published chunks and concept candidates through a scoped index."""
from app.core.config import settings
from app.repository.chroma.publication_vectors import publication_collection, search_publications
from app.service.ingestion.config import IngestionSettings


async def retrieve_published(topics, graph, embedding, publication_ids, access, *, resolve_entities):
    collection = await publication_collection(IngestionSettings().publication_collection)
    ranked = await search_publications(collection, embedding, publication_ids, 'chunk',
                                       settings.SOCRATIC_RETRIEVAL_K)
    ids = [meta['item_id'] for meta, distance in ranked if distance is not None
           and 1 - distance >= settings.SOCRATIC_MIN_SIMILARITY]
    hits = []
    if ids:
        rows = await topics.chunks(ids=ids, **access, limit=100)
        by_id = {row['id']: row for row in rows}
        hits = [by_id[item] for item in ids if item in by_id]
    if not hits:
        matches = await search_publications(collection, embedding, publication_ids, 'topic', 3)
        for meta, distance in matches:
            if distance is not None and 1 - distance >= settings.SOCRATIC_MIN_SIMILARITY:
                hits = await topics.chunks(topic_id=meta['item_id'], **access,
                                           limit=settings.SOCRATIC_RAG_TOP_K_CHUNKS)
                if hits:
                    break

    entities = {}
    if resolve_entities:
        matches = await search_publications(collection, embedding, publication_ids, 'entity', 5)
        for meta, distance in matches:
            code = meta['item_id']
            if distance is not None and 1 - distance >= settings.SOCRATIC_MIN_SIMILARITY and code not in entities:
                rows = await graph.published_entities(publication_ids, code=code)
                if rows:
                    entities[code] = rows[0]
    return hits, list(entities.values())
