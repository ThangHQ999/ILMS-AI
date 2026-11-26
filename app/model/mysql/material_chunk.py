import uuid
from typing import Any
from sqlalchemy import Enum as SqlEnum, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.model.enums import ExtractionStatusEnum, ScopeEnum
from app.model.mysql.base import Base, BinaryUUID, TimestampMixin


class MaterialChunk(Base, TimestampMixin):
    """
    Bảng lưu trữ các đoạn văn bản (chunks) được cắt nhỏ từ tài liệu gốc (materials).
    """

    __tablename__ = "material_chunks"

    id: Mapped[str] = mapped_column(
        BinaryUUID,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="UUID v4 dạng Binary(16) tương ứng 36-char string bên ChromaDB/Neo4j",
    )
    material_id: Mapped[str] = mapped_column(
        BinaryUUID,
        ForeignKey("materials.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="ID tài liệu gốc từ Spring Boot (FK tới bảng materials)",
    )
    material_version_id: Mapped[str] = mapped_column(BinaryUUID, nullable=False)
    owner_id: Mapped[str] = mapped_column(
        BinaryUUID,
        nullable=False,
        comment="ID của Admin hoặc Giáo viên sở hữu tài liệu",
    )
    scope: Mapped[ScopeEnum] = mapped_column(
        SqlEnum(ScopeEnum, native_enum=False, length=20),
        nullable=False,
        default=ScopeEnum.GLOBAL,
        comment="GLOBAL hoặc TEACHER",
    )
    subject: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Môn học (VD: MATHEMATICS, PHYSICS)",
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Thứ tự của chunk trong tài liệu gốc",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Nội dung văn bản thô của chunk",
    )
    token_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Số lượng token ước tính",
    )
    char_start: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Vị trí ký tự bắt đầu trong tài liệu gốc",
    )
    char_end: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Vị trí ký tự kết thúc trong tài liệu gốc",
    )
    canonical_codes: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True,
        default=list,
        comment="Danh sách canonical_code dạng JSON array",
    )
    extraction_status: Mapped[ExtractionStatusEnum] = mapped_column(
        SqlEnum(ExtractionStatusEnum, native_enum=False, length=20),
        nullable=False,
        default=ExtractionStatusEnum.PENDING,
        index=True,
        comment="PENDING, PROCESSING, COMPLETED, FAILED",
    )
    extraction_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Chi tiết lỗi nếu trích xuất KG thất bại",
    )
    extra_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
        comment="Metadata bổ sung (trang, chương...)",
    )
    
    __table_args__ = (
        Index("uq_chunk_version_index", "material_version_id", "chunk_index", unique=True),
        Index("idx_chunk_scope_owner_subject", "scope", "owner_id", "subject"),
    )