from chromadb.api.models.AsyncCollection import AsyncCollection
from chromadb.api.models.Collection import Collection
from fastapi import Depends
from neo4j import AsyncSession as Neo4jAsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from app.controller.chat_controller import SocraticChatController
from app.controller.graph_controller import GraphController
# from app.controller.ingestion_controller import IngestionController
from app.db.chroma import get_chroma_collection
from app.db.mysql import get_mysql_session
from app.db.neo4j import get_neo4j_session
from app.repository.chroma.vector_repo import ChromaVectorRepository
from app.repository.mysql.chat_repo import SocraticChatRepository
from app.repository.mysql.chunk_repo import MaterialChunkRepository
from app.repository.neo4j.knowledge_entity_repo import KnowledgeEntityRepository
from app.repository.neo4j.pedagogy_node_repo import PedagogyNodeRepository
from app.repository.neo4j.process_repo import ProcessRepository
# from app.service.ingestion_service import MaterialIngestionService
# from app.service.kg_extraction_service import KnowledgeGraphExtractionService
from app.service.llm_service import llm_service
from app.service.tutoring.chat_service import SocraticChatService


# ============================================================================
# 1. REPOSITORY DEPENDENCIES
# ============================================================================
def get_chunk_repo(
    mysql_session: AsyncSession = Depends(get_mysql_session),
) -> MaterialChunkRepository:
    return MaterialChunkRepository(mysql_session)


def get_chat_repo(
    mysql_session: AsyncSession = Depends(get_mysql_session),
) -> SocraticChatRepository:
    return SocraticChatRepository(mysql_session)


def get_vector_repo(
    chroma_collection: AsyncCollection | Collection = Depends(get_chroma_collection),
) -> ChromaVectorRepository:
    return ChromaVectorRepository(chroma_collection)


def get_kg_entity_repo(
    neo4j_session: Neo4jAsyncSession = Depends(get_neo4j_session),
) -> KnowledgeEntityRepository:
    return KnowledgeEntityRepository(neo4j_session)


def get_pedagogy_repo(
    neo4j_session: Neo4jAsyncSession = Depends(get_neo4j_session),
) -> PedagogyNodeRepository:
    return PedagogyNodeRepository(neo4j_session)


def get_process_repo(
    neo4j_session: Neo4jAsyncSession = Depends(get_neo4j_session),
) -> ProcessRepository:
    return ProcessRepository(neo4j_session)


# ============================================================================
# 2. SERVICE DEPENDENCIES
# ============================================================================
# def get_ingestion_service(
#     chunk_repo: MaterialChunkRepository = Depends(get_chunk_repo),
#     vector_repo: ChromaVectorRepository = Depends(get_vector_repo),
# ) -> MaterialIngestionService:
#     return MaterialIngestionService(
#         chunk_repo=chunk_repo,
#         vector_repo=vector_repo,
#         ai_service=llm_service,
#     )


# def get_kg_extraction_service(
#     chunk_repo: MaterialChunkRepository = Depends(get_chunk_repo),
#     vector_repo: ChromaVectorRepository = Depends(get_vector_repo),
#     kg_repo: KnowledgeEntityRepository = Depends(get_kg_entity_repo),
# ) -> KnowledgeGraphExtractionService:
#     return KnowledgeGraphExtractionService(
#         chunk_repo=chunk_repo,
#         vector_repo=vector_repo,
#         kg_repo=kg_repo,
#         ai_service=llm_service,
#     )


def get_socratic_chat_service(
    vector_repo: ChromaVectorRepository = Depends(get_vector_repo),
) -> SocraticChatService:
    return SocraticChatService(llm_service, vector_repo)


# ============================================================================
# 3. CONTROLLER DEPENDENCIES
# ============================================================================
# def get_ingestion_controller(
#     ingestion_service: MaterialIngestionService = Depends(get_ingestion_service),
#     kg_extraction_service: KnowledgeGraphExtractionService = Depends(get_kg_extraction_service),
# ) -> IngestionController:
#     return IngestionController(
#         ingestion_service=ingestion_service,
#         kg_extraction_service=kg_extraction_service,
#     )


def get_graph_controller(
    kg_repo: KnowledgeEntityRepository = Depends(get_kg_entity_repo),
    pedagogy_repo: PedagogyNodeRepository = Depends(get_pedagogy_repo),
    process_repo: ProcessRepository = Depends(get_process_repo),
) -> GraphController:
    return GraphController(
        kg_repo=kg_repo,
        pedagogy_repo=pedagogy_repo,
        process_repo=process_repo,
    )


def get_chat_controller(
    chat_service: SocraticChatService = Depends(get_socratic_chat_service),
    chat_repo: SocraticChatRepository = Depends(get_chat_repo),
) -> SocraticChatController:
    return SocraticChatController(
        chat_service=chat_service,
        chat_repo=chat_repo,
    )
