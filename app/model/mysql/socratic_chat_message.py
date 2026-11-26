import uuid
from sqlalchemy import ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.model.mysql.base import Base, BinaryUUID, TimestampMixin

class SocraticChatMessage(Base, TimestampMixin):
    """
    Bảng lưu vết chi tiết từng lượt tin nhắn trong phiên Socratic Chat.
    - `id` và `session_id` đều dùng BinaryUUID (BINARY(16) trong MySQL).
    - Lưu danh sách UUID chunks và Neo4j node IDs dạng JSON array để truy vết ngữ cảnh (RAG context).
    """

    __tablename__ = "socratic_chat_messages"

    id: Mapped[str] = mapped_column(
        BinaryUUID,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="UUID v4 dạng Binary(16) đại diện cho tin nhắn",
    )
    session_id: Mapped[str] = mapped_column(
        BinaryUUID,
        ForeignKey("socratic_chat_sessions.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="Khóa ngoại trỏ tới bảng socratic_chat_sessions",
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Loại người gửi: USER, ASSISTANT, SYSTEM",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Nội dung tin nhắn",
    )
    step_number_at_turn: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Ghi lại lượt chat này thuộc bước gợi ý thứ mấy (:ProcessStep.step_number)",
    )
    referenced_chunk_ids: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True,
        default=list,
        comment="Danh sách UUID chunks từ ChromaDB/MySQL dùng làm context",
    )
    referenced_node_ids: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True,
        default=list,
        comment="Danh sách ID Node Neo4j đã tham chiếu",
    )
    user_feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Phản hồi bằng lời của người dùng",
    )
    feedback_rating: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Đánh giá phản hồi: LIKE, DISLIKE hoặc số sao '1'..'5'",
    )

    turn_id: Mapped[str | None] = mapped_column(BinaryUUID, nullable=True)
    turn_status: Mapped[str | None] = mapped_column(String(24), nullable=True)
    content_status: Mapped[str | None] = mapped_column(String(16), nullable=True)
    turn_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    @property
    def artifacts(self) -> list[dict]:
        """Only public, already-validated artifact payloads are exposed by history APIs."""
        return (self.turn_metadata or {}).get('public', {}).get('artifacts', [])

    @property
    def step_progress(self) -> dict | None:
        """Per-turn display metadata; never infer exercise progress from a default counter."""
        return (self.turn_metadata or {}).get('public', {}).get('step_progress')

    session = relationship("SocraticChatSession", back_populates="messages")

    __table_args__ = (
        Index("idx_msg_session_created", "session_id", "created_at"),
        Index('uq_msg_session_turn_role', 'session_id', 'turn_id', 'role', unique=True),
    )
