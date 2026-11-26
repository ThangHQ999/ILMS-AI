from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from src.schemas.tutor import TutorChatRequest
from src.services.tutoring.tutor_service import TutorService

router = APIRouter(prefix="/tutor", tags=["AI Socratic Tutor"])

@router.post("/chat/stream")
async def chat_with_socratic_tutor(
    request: TutorChatRequest,
    service: TutorService = Depends(),
) -> StreamingResponse:
    return StreamingResponse(
        service.stream_socratic_chat(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )