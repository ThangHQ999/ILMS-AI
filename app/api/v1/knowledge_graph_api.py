"""Internal graph APIs. Spring Boot authorizes actors before calling these routes."""
from fastapi import APIRouter, HTTPException, Request

from app.api.v1.ingestion_api import require_worker
from app.schema.graph_repair import AiGraphRepairRequest, AiGraphRepairResponse
from app.schema.knowledge_graph import (
    ConceptCatalogRequest, ConceptCatalogResponse, GraphEditRequest, GraphViewRequest,
)
from app.service.knowledge_graph.ai_repair_service import repair_knowledge_graph_with_ai
from app.service.knowledge_graph.concept_catalog import load_concept_catalog
from app.service.knowledge_graph.document import GraphInputError
from app.service.knowledge_graph.service import change_graph, graph_view

router = APIRouter(prefix='/internal/knowledge-graphs', tags=['internal-knowledge-graphs'])


@router.post('/changes')
async def changes(body: GraphEditRequest, request: Request):
    require_worker(request)
    try:
        result = await change_graph(body)
    except (GraphInputError, KeyError, TypeError) as exc:
        raise HTTPException(422, 'INVALID_GRAPH_CHANGE') from exc
    if result is None:
        raise HTTPException(404, 'GRAPH_REVISION_NOT_FOUND')
    return result


@router.post('/view')
async def view(body: GraphViewRequest, request: Request):
    require_worker(request)
    try:
        result = await graph_view(body)
    except (GraphInputError, KeyError, TypeError) as exc:
        raise HTTPException(422, 'INVALID_GRAPH_VIEW') from exc
    if result is None:
        raise HTTPException(404, 'GRAPH_REVISION_NOT_FOUND')
    return result


@router.post('/concept-catalog', response_model=ConceptCatalogResponse)
async def concept_catalog(body: ConceptCatalogRequest, request: Request):
    require_worker(request)
    try:
        result = await load_concept_catalog(body)
    except ValueError as exc:
        raise HTTPException(422, 'INVALID_PUBLISHED_CONCEPT_GRAPH') from exc
    if result is None:
        raise HTTPException(404, 'CONCEPT_CATALOG_PUBLICATION_NOT_FOUND')
    return result


@router.post('/ai-repair', response_model=AiGraphRepairResponse)
async def ai_repair(body: AiGraphRepairRequest, request: Request):
    require_worker(request)
    try:
        return await repair_knowledge_graph_with_ai(body)
    except Exception as exc:
        raise HTTPException(500, f'AI_REPAIR_FAILED: {exc}') from exc


@router.post('/generate-questions')
async def generate_questions(body: dict, request: Request):
    require_worker(request)
    from app.service.knowledge_graph.question_generator_service import generate_questions_with_ai
    try:
        return await generate_questions_with_ai(body)
    except Exception as exc:
        raise HTTPException(500, f'AI_QUESTION_GEN_FAILED: {exc}') from exc


