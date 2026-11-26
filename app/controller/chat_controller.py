import math
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from app.repository.mysql.chat_repo import SocraticChatRepository
from app.schema.chat_sse_schema import (
    SocraticChatMessageResponse,
    SocraticChatSessionDetailResponse,
    SocraticChatSessionSidebarItem,
    SocraticChatSessionUpdate,
    SocraticChatStreamRequest,
    SocraticMessageFeedbackRequest,
)
from app.schema.common import ApiResponse, PaginatedResponse, PaginationParams
from app.service.llm_service import ProviderType
from app.service.tutoring.chat_service import SocraticChatService


class SocraticChatController:
    """
    Controller điều phối luồng Socratic Tutor Chat SSE (trả về `StreamingResponse` chuẩn `text/event-stream`
    cho Spring Boot forward về FE) cùng các thao tác quản lý phiên học và đánh giá tin nhắn.
    """

    def __init__(
        self,
        chat_service: SocraticChatService,
        chat_repo: SocraticChatRepository,
    ) -> None:
        self._chat_service = chat_service
        self._chat_repo = chat_repo

    async def stream_socratic_chat(
        self,
        req: SocraticChatStreamRequest,
        preferred_provider: ProviderType | None = None,
    ) -> StreamingResponse:
        """
        Khởi tạo `StreamingResponse` chuẩn SSE (`text/event-stream`).
        Thiết lập bộ Header tắt bộ đệm (`X-Accel-Buffering: no`, `Cache-Control: no-cache`)
        để Spring Boot `WebClient` / `SseEmitter` nhận từng token ngay lập tức.
        """
        event_generator = self._chat_service.stream_socratic_chat(
            req=req,
            preferred_provider=preferred_provider,
        )

        return StreamingResponse(
            event_generator,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-transform",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    async def list_student_sessions(
        self,
        student_id: str,
        subject: str | None,
        pagination: PaginationParams,
    ) -> ApiResponse[PaginatedResponse[SocraticChatSessionSidebarItem]]:
        """
        Lấy danh sách phiên hội thoại cho Sidebar UI của học sinh.
        Trả về đúng cấu trúc `PaginatedResponse<T>` (`items`, `pageNumber`, `pageSize`, `totalElements`, `totalPages`, `last`)
        của Spring Boot BE để không cần map lại.
        """
        # Chuyển pageNumber (0-based của Spring Boot) sang page (1-based của repository)
        repo_page = pagination.pageNumber + 1
        sessions, total_elements = await self._chat_repo.list_student_sessions_sidebar(
            student_id=student_id,
            subject=subject,
            page=repo_page,
            page_size=pagination.pageSize,
        )
        total_pages = (
            math.ceil(total_elements / pagination.pageSize) if total_elements > 0 else 0
        )
        is_last = (total_pages == 0) or (pagination.pageNumber >= total_pages - 1)
        items = [SocraticChatSessionSidebarItem.model_validate(s) for s in sessions]

        return ApiResponse(
            status=0,
            message="Thành công",
            data=PaginatedResponse(
                items=items,
                pageNumber=pagination.pageNumber,
                pageSize=pagination.pageSize,
                totalElements=total_elements,
                totalPages=total_pages,
                last=is_last,
            ),
        )

    async def get_session_detail(
        self,
        session_id: str,
    ) -> ApiResponse[SocraticChatSessionDetailResponse]:
        """Lấy chi tiết phiên học kèm toàn bộ lịch sử tin nhắn `socratic_chat_messages`."""
        session = await self._chat_repo.get_session_by_id(
            session_id=session_id,
            include_messages=True,
        )
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy phiên hội thoại Socratic '{session_id}'.",
            )
        return ApiResponse(
            status=0,
            message="Thành công",
            data=SocraticChatSessionDetailResponse.model_validate(session),
        )

    async def update_session(
        self,
        session_id: str,
        update_in: SocraticChatSessionUpdate,
    ) -> ApiResponse[SocraticChatSessionSidebarItem]:
        """Cập nhật tiêu đề hoặc trạng thái bước giải của phiên hội thoại."""
        protected = {'active_canonical_code', 'active_process_id', 'active_exercise_id',
                     'current_step_number', 'is_completed', 'teacher_id', 'subject'}
        if update_in.model_fields_set & protected:
            raise HTTPException(409, 'Trạng thái học được quản lý qua lượt chat; PATCH này chỉ đổi tiêu đề.')
        updated = await self._chat_repo.update_session(session_id, update_in)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy phiên hội thoại '{session_id}'.",
            )
        return ApiResponse(
            status=0,
            message="Đã cập nhật phiên hội thoại.",
            data=SocraticChatSessionSidebarItem.model_validate(updated),
        )

    async def delete_session(
        self,
        session_id: str,
        student_id: str,
    ) -> ApiResponse[dict[str, bool]]:
        """Xóa phiên hội thoại của học sinh."""
        deleted = await self._chat_repo.delete_session(
            session_id=session_id,
            student_id=student_id,
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy phiên hội thoại hoặc không thuộc quyền sở hữu của học sinh.",
            )
        return ApiResponse(
            status=0,
            message="Đã xóa phiên hội thoại thành công.",
            data={"deleted": True},
        )

    async def update_message_feedback(
        self,
        message_id: str,
        feedback_in: SocraticMessageFeedbackRequest,
    ) -> ApiResponse[SocraticChatMessageResponse]:
        """Cập nhật `user_feedback` và `feedback_rating` cho 1 tin nhắn của Socratic Tutor."""
        msg = await self._chat_repo.update_message_feedback(
            message_id=message_id,
            feedback_in=feedback_in,
        )
        if msg is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy tin nhắn '{message_id}'.",
            )
        return ApiResponse(
            status=0,
            message="Đã ghi nhận phản hồi của học sinh.",
            data=SocraticChatMessageResponse.model_validate(msg),
        )
        
