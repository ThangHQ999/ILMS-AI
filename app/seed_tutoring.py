"""Explicit operator command: rebuild Socratic indexes. Never imported/executed at startup.

python -m app.seed_tutoring --target entities
python -m app.seed_tutoring --target chunks
Use a NEW versioned CHROMA_COLLECTION_NAME for chunks; do not mix mock/legacy vectors.
"""
import argparse
import asyncio
from sqlalchemy import select
from app.core.config import settings
from app.db.chroma import chroma_manager
from app.db.mysql import mysql_manager
from app.db.neo4j import neo4j_manager
from app.model.mysql.material_chunk import MaterialChunk
from app.repository.neo4j.tutoring_repo import TutoringGraphRepository
from app.repository.chroma.entity_vector_repo import EntityVectorRepository, embedding_identity, invoke
from app.repository.chroma.vector_repo import ChromaVectorRepository
from app.service.llm_service import llm_service


async def seed(target):
    try:
        await chroma_manager.init_chroma()
        if target == 'entities':
            neo4j_manager.init_neo4j()
            graph, vectors, after = TutoringGraphRepository(), EntityVectorRepository(), ''
            while True:
                entities = await graph.all_entities(after, settings.EMBEDDING_BATCH_SIZE)
                if not entities:
                    break
                texts = [f"{e['canonical_code']} | {e['name']} ({e['subject']}): {e.get('description', '')}" for e in entities]
                embeddings = await llm_service.embed_texts(texts)
                await vectors.upsert(entities, embeddings)
                after = entities[-1]['canonical_code']
                print('Indexed entities through', after)
        else:
            mysql_manager.init_mysql()
            collection = chroma_manager.collection
            metadata = collection.metadata or {}
            identity = embedding_identity()
            if metadata.get('hnsw:space') != 'cosine':
                raise ValueError('Choose a new collection with CHROMA_DISTANCE_METRIC=cosine')
            if metadata.get('embedding_identity') != identity:
                if await invoke(collection, 'count'):
                    raise ValueError('Non-empty collection has unknown/different embeddings. Choose a NEW collection name.')
                await invoke(collection, 'modify', metadata=dict(metadata, embedding_identity=identity))
            vectors = ChromaVectorRepository(collection)
            after = None
            while True:
                async with mysql_manager.session_factory() as db:
                    stmt = select(MaterialChunk).order_by(MaterialChunk.id).limit(settings.EMBEDDING_BATCH_SIZE)
                    if after:
                        stmt = stmt.where(MaterialChunk.id > after)
                    chunks = (await db.execute(stmt)).scalars().all()
                    if not chunks:
                        break
                    embeddings = await llm_service.embed_texts([c.content for c in chunks])
                    await vectors.upsert_chunks(chunks, embeddings)
                    after = chunks[-1].id
                    print('Indexed chunks through', after)
    finally:
        await chroma_manager.close_chroma()
        await neo4j_manager.close_neo4j()
        await mysql_manager.close_mysql()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=['entities', 'chunks'], required=True)
    asyncio.run(seed(parser.parse_args().target))
