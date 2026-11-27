"""Internal Chat AI APIs (/api/v1/internal/chat/summarize, /group-assist)."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request

from app.api.v1.ingestion_api import require_worker
from app.schema.internal_chat import (
    ChatSummarizeRequest,
    ChatSummarizeResponse,
    GroupChatAssistRequest,
    GroupChatAssistResponse,
)
from app.service.internal_chat_service import (
    assist_group_chat_with_ai,
    summarize_conversation_with_ai,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal/chat", tags=["internal-chat"])


@router.post("/summarize", response_model=ChatSummarizeResponse)
async def summarize_chat(body: ChatSummarizeRequest, request: Request) -> ChatSummarizeResponse:
    require_worker(request)
    try:
        return await summarize_conversation_with_ai(body)
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning(
            "Internal chat summarize failed (conversationId=%s): %s",
            body.conversationId,
            exc,
        )
        raise HTTPException(status_code=502, detail="AI_SUMMARIZE_FAILED") from exc


@router.post("/group-assist", response_model=GroupChatAssistResponse)
async def group_assist(body: GroupChatAssistRequest, request: Request) -> GroupChatAssistResponse:
    require_worker(request)
    try:
        return await assist_group_chat_with_ai(body)
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning(
            "Internal chat group-assist failed (conversationId=%s): %s",
            body.conversationId,
            exc,
        )
        raise HTTPException(status_code=502, detail="AI_GROUP_ASSIST_FAILED") from exc
