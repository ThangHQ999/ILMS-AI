from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from src.schemas.tutor.TutorChatRequest import TutorChatRequest
from src.services.tutoring import TutorService

router = APIRouter(prefix="/tutor", tags=["AI Tutor Controller"])

@router.post("/chat/stream")
async def chat_stream_controller(
    request: TutorChatRequest,
    service: TutorService = Depends()
):
    """
    Tiếp nhận request từ Spring Boot và stream token về theo chuẩn text/event-stream.
    """
    return StreamingResponse(
        service.stream_tutor_response(request),
        media_type="text/event-stream"
    )