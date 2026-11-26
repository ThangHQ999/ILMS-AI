import uuid
from sqlalchemy import CheckConstraint, Index, String, ForeignKey, Text, JSON
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.orm import Mapped, mapped_column
from app.model.mysql.base import Base, BinaryUUID, TimestampMixin

class StudentMisconception(Base, TimestampMixin):

    __tablename__ = "student_misconceptions"

    id: Mapped[str] = mapped_column(
        BinaryUUID,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="UUID v4 Binary(16) đại diện cho student_misconceptions",
    )
    student_id: Mapped[str] = mapped_column(
        BinaryUUID,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="ID học sinh từ Spring Boot (FK tới bảng users)",
    )
    session_id: Mapped[str | None] = mapped_column(
        BinaryUUID,
        ForeignKey("socratic_chat_sessions.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    canonical_code: Mapped[str] = mapped_column(
        VARCHAR(128, charset="ascii", collation="ascii_bin"),
        nullable=False,
        comment="Mã khái niệm đang học trong Neo4j",
    )
    misconception_summary: Mapped[str] = mapped_column(Text, nullable=False)
    misconception_code: Mapped[str | None] = mapped_column(VARCHAR(128, charset="ascii", collation="ascii_bin"), nullable=True)
    misconception_status: Mapped[str] = mapped_column(
        String(24), default="SUSPECTED", server_default="SUSPECTED", nullable=False
    )
    evidence: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("idx_student_concept_status", "student_id", "canonical_code", "misconception_status", "created_at"),
        Index("idx_student_concept_miscode", "student_id", "canonical_code", "misconception_code"),
        Index("idx_misconception_session", "session_id"),
        CheckConstraint("misconception_status IN ('SUSPECTED','CONFIRMED','RESOLVED')", name="chk_misconception_status"),
    )
