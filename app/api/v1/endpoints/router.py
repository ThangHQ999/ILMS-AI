from fastapi import APIRouter
from app.api.v1.endpoints.chat_api import router as chat_router
from app.api.v1.ingestion_api import router as ingestion_router
from app.api.v1.knowledge_graph_api import router as knowledge_graph_router
# from app.api.v1.endpoints.extraction_api import router as extraction_router
# from app.api.v1.endpoints.graph_api import router as graph_router

api_v1_router = APIRouter()

api_v1_router.include_router(chat_router)
api_v1_router.include_router(ingestion_router)
api_v1_router.include_router(knowledge_graph_router)
# api_v1_router.include_router(extraction_router)
# api_v1_router.include_router(graph_router)
