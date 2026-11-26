from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from app.api.deps import get_chat_controller
from app.controller.chat_controller import SocraticChatController
from app.core.security import verify_internal_api_key
from app.schema.chat_sse_schema import (
    SocraticChatMessageResponse,
    SocraticChatSessionDetailResponse,
    SocraticChatSessionSidebarItem,
    SocraticChatSessionUpdate,
    SocraticChatStreamRequest,
    SocraticMessageFeedbackRequest,
)
from app.schema.common import ApiResponse, PaginatedResponse, PaginationParams, UUIDStr
from app.service.llm_service import ProviderType
from app.repository.mysql.topic_repo import TopicRepository
from app.service.tutoring.turn_coordinator import TurnCoordinator, TurnError

router = APIRouter(
    prefix="/chat/socratic",
    tags=["Socratic Tutor Chat SSE"],
    dependencies=[Depends(verify_internal_api_key)],
)


@router.get('/turns/{session_id}/{turn_id}', summary='Lấy lại kết quả lượt Socratic sau mất kết nối')
async def get_turn_result(session_id: UUIDStr, turn_id: UUIDStr, student_id: UUIDStr):
    try:
        return await TurnCoordinator().result(session_id, turn_id, student_id)
    except TurnError as exc:
        raise HTTPException(404, exc.message) from exc


@router.get('/progress/{student_id}', summary='Tiến độ evidence Socratic; thay nguồn đọc heatmap cũ')
async def get_concept_progress(student_id: UUIDStr):
    return {'data': await TopicRepository().progress(student_id)}


@router.post(
    "/stream",
    summary="Stream câu trả lời gợi mở Socratic theo thời gian thực qua SSE (Spring Boot gọi sang)",
    response_class=StreamingResponse,
)
async def stream_socratic_chat(
    req: SocraticChatStreamRequest,
    provider: ProviderType | None = Query(
        default=None,
        description="Tùy chọn chỉ định 'gemini' hoặc 'openai'; nếu để trống dùng LLM_DEFAULT_PROVIDER",
    ),
    controller: SocraticChatController = Depends(get_chat_controller),
) -> StreamingResponse:
    return await controller.stream_socratic_chat(req=req, preferred_provider=provider)


@router.get(
    "/sessions",
    response_model=ApiResponse[PaginatedResponse[SocraticChatSessionSidebarItem]],
    summary="Lấy danh sách phiên hội thoại Socratic cho Sidebar UI của học sinh (khớp PaginatedResponse<T> của Spring Boot)",
)
async def list_student_sessions(
    student_id: UUIDStr = Query(..., description="UUID của học sinh"),
    subject: str | None = Query(default=None, description="Lọc theo môn học"),
    pageNumber: int = Query(
        default=0,
        ge=0,
        alias="pageNumber",
        description="Chỉ số trang hiện tại (bắt đầu từ 0 theo chuẩn Spring Boot)",
    ),
    pageSize: int = Query(
        default=10,
        ge=1,
        le=100,
        alias="pageSize",
        description="Số bản ghi trên mỗi trang",
    ),
    controller: SocraticChatController = Depends(get_chat_controller),
) -> ApiResponse[PaginatedResponse[SocraticChatSessionSidebarItem]]:
    return await controller.list_student_sessions(
        student_id=student_id,
        subject=subject,
        pagination=PaginationParams(pageNumber=pageNumber, pageSize=pageSize),
    )


@router.get(
    "/sessions/{session_id}",
    response_model=ApiResponse[SocraticChatSessionDetailResponse],
    summary="Lấy chi tiết phiên hội thoại Socratic kèm lịch sử tin nhắn",
)
async def get_session_detail(
    session_id: UUIDStr,
    controller: SocraticChatController = Depends(get_chat_controller),
) -> ApiResponse[SocraticChatSessionDetailResponse]:
    return await controller.get_session_detail(session_id=session_id)


@router.patch(
    "/sessions/{session_id}",
    response_model=ApiResponse[SocraticChatSessionSidebarItem],
    summary="Cập nhật tiêu đề hoặc bước giải hiện tại của phiên Socratic",
)
async def update_session(
    session_id: UUIDStr,
    update_in: SocraticChatSessionUpdate,
    controller: SocraticChatController = Depends(get_chat_controller),
) -> ApiResponse[SocraticChatSessionSidebarItem]:
    return await controller.update_session(session_id=session_id, update_in=update_in)


@router.delete(
    "/sessions/{session_id}",
    response_model=ApiResponse[dict[str, bool]],
    summary="Xóa phiên hội thoại Socratic của học sinh",
)
async def delete_session(
    session_id: UUIDStr,
    student_id: UUIDStr = Query(..., description="UUID học sinh sở hữu phiên chat"),
    controller: SocraticChatController = Depends(get_chat_controller),
) -> ApiResponse[dict[str, bool]]:
    return await controller.delete_session(session_id=session_id, student_id=student_id)


@router.patch(
    "/messages/{message_id}/feedback",
    response_model=ApiResponse[SocraticChatMessageResponse],
    summary="Học sinh gửi đánh giá (LIKE/DISLIKE/1..5 sao & nhận xét) cho 1 câu gợi ý của AI",
)
async def submit_message_feedback(
    message_id: UUIDStr,
    feedback_in: SocraticMessageFeedbackRequest,
    controller: SocraticChatController = Depends(get_chat_controller),
) -> ApiResponse[SocraticChatMessageResponse]:
    return await controller.update_message_feedback(
        message_id=message_id,
        feedback_in=feedback_in,
    )
