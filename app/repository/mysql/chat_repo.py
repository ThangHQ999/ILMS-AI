from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.model.mysql.socratic_chat_message import SocraticChatMessage
from app.model.mysql.socratic_chat_session import SocraticChatSession
from app.model.neo4j.nodes import normalize_canonical_code
from app.schema.chat_sse_schema import SocraticChatSessionUpdate, SocraticMessageFeedbackRequest


class SocraticChatRepository:
    """Session management and message feedback. Turn writes belong to TurnCoordinator."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_session_by_id(
        self,
        session_id: str,
        include_messages: bool = False,
        student_id: str | None = None,
    ) -> SocraticChatSession | None:
        """
        Lấy thông tin phiên chat theo ID.
        Hỗ trợ lọc kèm `student_id` để chống truy cập trái phép (IDOR) khi gọi từ API chi tiết phiên.
        """
        stmt = select(SocraticChatSession).where(SocraticChatSession.id == session_id)
        if student_id is not None:
            stmt = stmt.where(SocraticChatSession.student_id == student_id)
        if include_messages:
            stmt = stmt.options(selectinload(SocraticChatSession.messages))

        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_student_sessions_sidebar(
        self,
        student_id: str,
        subject: str | None = None,
        is_completed: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[SocraticChatSession], int]:
        """
        Lấy danh sách phiên chat của học sinh hiển thị ở Sidebar UI,
        tối ưu theo index `idx_student_sidebar (student_id, updated_at)`.
        """
        filters = [SocraticChatSession.student_id == student_id]
        if subject:
            filters.append(SocraticChatSession.subject == subject.strip().upper())
        if is_completed is not None:
            filters.append(SocraticChatSession.is_completed.is_(is_completed))

        count_stmt = select(func.count()).select_from(SocraticChatSession).where(*filters)
        total_result = await self._session.execute(count_stmt)
        total = int(total_result.scalar_one() or 0)

        safe_size = max(1, min(page_size, 100))
        offset = (max(page, 1) - 1) * safe_size
        stmt = (
            select(SocraticChatSession)
            .where(*filters)
            .order_by(SocraticChatSession.updated_at.desc(), SocraticChatSession.id.desc())
            .offset(offset)
            .limit(safe_size)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all()), total

    async def update_session(
        self,
        session_id: str,
        update_in: SocraticChatSessionUpdate,
        student_id: str | None = None,
    ) -> SocraticChatSession | None:
        """Cập nhật các trường trạng thái của phiên Socratic từ API quản lý phiên."""
        db_session = await self.get_session_by_id(session_id, student_id=student_id)
        if db_session is None:
            return None

        update_data = update_in.model_dump(exclude_unset=True)
        if "active_canonical_code" in update_data and update_data["active_canonical_code"]:
            update_data["active_canonical_code"] = normalize_canonical_code(
                update_data["active_canonical_code"]
            )
        if "subject" in update_data and update_data["subject"]:
            update_data["subject"] = update_data["subject"].strip().upper()

        for field_name, value in update_data.items():
            if hasattr(db_session, field_name):
                setattr(db_session, field_name, value)

        await self._session.commit()
        await self._session.refresh(db_session)
        return db_session

    async def delete_session(self, session_id: str, student_id: str) -> bool:
        """Xóa phiên chat của học sinh (tự động cascade xóa messages & misconceptions của phiên)."""
        stmt = delete(SocraticChatSession).where(
            SocraticChatSession.id == session_id,
            SocraticChatSession.student_id == student_id,
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return bool(result.rowcount and result.rowcount > 0)

    async def update_message_feedback(
        self,
        message_id: str,
        feedback_in: SocraticMessageFeedbackRequest,
    ) -> SocraticChatMessage | None:
        """Cập nhật đánh giá (`user_feedback`, `feedback_rating`) của học sinh cho 1 câu gợi ý."""
        stmt = select(SocraticChatMessage).where(SocraticChatMessage.id == message_id)
        result = await self._session.execute(stmt)
        db_msg = result.scalar_one_or_none()
        if db_msg is None:
            return None

        if feedback_in.user_feedback is not None:
            db_msg.user_feedback = feedback_in.user_feedback
        if feedback_in.feedback_rating is not None:
            db_msg.feedback_rating = feedback_in.feedback_rating

        await self._session.commit()
        await self._session.refresh(db_msg)
        return db_msg
