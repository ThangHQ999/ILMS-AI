import uuid
from sqlalchemy import Boolean, Index, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.model.mysql.base import Base, BinaryUUID, TimestampMixin

class SocraticChatSession(Base, TimestampMixin):
    """
    Bảng lưu trữ và quản lý phiên hội thoại Socratic Chat của học sinh.
    - Hợp nhất cả thông tin UI (Sidebar) lẫn trạng thái tiến trình thuật toán Socratic.
    - Không yêu cầu khai báo Model User trong Python nhưng vẫn sinh ForeignKey đúng chuẩn DDL.
    """

    __tablename__ = "socratic_chat_sessions"

    id: Mapped[str] = mapped_column(
        BinaryUUID,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="UUID v4 Binary(16) đại diện cho Session",
    )
    student_id: Mapped[str] = mapped_column(
        BinaryUUID,
        nullable=False,
        comment="ID học sinh từ Spring Boot (FK tới bảng users)",
    )
    teacher_id: Mapped[str | None] = mapped_column(
        BinaryUUID,
        nullable=True,
        comment="ID giáo viên phụ trách để lọc scope=TEACHER trong Neo4j",
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Phiên tư vấn Socratic",
        comment="Tiêu đề hiển thị ở Sidebar UI",
    )
    subject: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Môn học (VD: MATHEMATICS, PHYSICS)",
    )
    active_canonical_code: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        comment="Mã khái niệm đang học trong Neo4j",
    )
    active_process_id: Mapped[str | None] = mapped_column(
        BinaryUUID,
        nullable=True,
        comment="ID Node :Process dẫn dắt quy trình giải",
    )
    active_exercise_id: Mapped[str | None] = mapped_column(
        BinaryUUID,
        nullable=True,
        comment="ID Node :Exercise bài tập đang giải",
    )
    current_step_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="Bước gợi ý hiện tại trong :ProcessStep",
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="1: Đã hoàn thành, 0: Đang giải",
    )
    stuck_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    parent_canonical_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    messages = relationship(
        "SocraticChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="SocraticChatMessage.created_at.asc()",
    )

    __table_args__ = (
        Index("idx_student_sidebar", "student_id", "updated_at"),
        Index("idx_student_subject_active", "student_id", "subject", "active_canonical_code"),
    )