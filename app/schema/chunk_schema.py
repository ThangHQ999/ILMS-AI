from typing import Any
from pydantic import BaseModel, Field, field_validator
from app.model.enums import ExtractionStatusEnum, ScopeEnum
from app.model.neo4j.nodes import normalize_canonical_code
from app.schema.common import ORMBaseSchema, TimestampSchemaMixin, UUIDStr


class MaterialChunkBase(ORMBaseSchema):
    """Các trường dữ liệu cơ bản của bảng `material_chunks`."""

    material_id: UUIDStr = Field(..., description="UUID tài liệu gốc từ bảng materials (Spring Boot)")
    owner_id: UUIDStr = Field(..., description="UUID của Admin hoặc Giáo viên sở hữu tài liệu")
    scope: ScopeEnum = Field(default=ScopeEnum.GLOBAL, description="Phạm vi hiển thị: GLOBAL hoặc TEACHER")
    subject: str = Field(..., min_length=1, max_length=100, description="Môn học (VD: MATHEMATICS, PHYSICS)")
    chunk_index: int = Field(default=0, ge=0, description="Thứ tự của chunk trong tài liệu gốc (0, 1, 2...)")
    content: str = Field(..., min_length=1, description="Nội dung văn bản thô của chunk")
    token_count: int = Field(default=0, ge=0, description="Số lượng token ước tính của chunk")
    char_start: int | None = Field(default=None, ge=0, description="Vị trí ký tự bắt đầu trong tài liệu gốc")
    char_end: int | None = Field(default=None, ge=0, description="Vị trí ký tự kết thúc trong tài liệu gốc")
    extra_metadata: dict[str, Any] | None = Field(
        default_factory=dict,
        description="Metadata bổ sung (số trang, chương, mục...)",
    )

    @field_validator("subject")
    @classmethod
    def normalize_subject(cls, v: str) -> str:
        return v.strip().upper()


class MaterialChunkCreate(MaterialChunkBase):
    """Schema tạo mới 1 bản ghi `MaterialChunk` trong MySQL và đồng bộ sang ChromaDB."""

    id: UUIDStr | None = Field(
        default=None,
        description="Tùy chọn truyền sẵn UUID; nếu để trống hệ thống tự sinh UUID v4",
    )
    canonical_codes: list[str] = Field(
        default_factory=list,
        description="Danh sách canonical_code gắn sẵn (nếu có)",
    )

    @field_validator("canonical_codes")
    @classmethod
    def normalize_codes(cls, codes: list[str]) -> list[str]:
        return [normalize_canonical_code(c) for c in codes if c and c.strip()]


class RawMaterialIngestRequest(BaseModel):
    """
    Schema để Spring Boot gửi toàn bộ nội dung văn bản của 1 học liệu (`materials`) sang FastAPI
    nhằm tự động cắt nhỏ (chunking), lưu vào bảng `material_chunks`, tạo vector vào ChromaDB
    và (tùy chọn) kích hoạt AI bóc tách đồ thị tri thức vào Neo4j.
    """

    material_id: UUIDStr = Field(..., description="ID tài liệu gốc từ bảng materials")
    owner_id: UUIDStr = Field(..., description="ID của Admin hoặc Giáo viên tải tài liệu")
    scope: ScopeEnum = Field(default=ScopeEnum.GLOBAL)
    subject: str = Field(..., min_length=1, max_length=100)
    raw_text: str = Field(..., min_length=10, description="Toàn bộ văn bản thô đã trích xuất từ file học liệu")
    chunk_size_tokens: int = Field(default=512, ge=100, le=4000, description="Kích thước mục tiêu của mỗi chunk")
    chunk_overlap_tokens: int = Field(default=64, ge=0, le=1000, description="Số token gối đầu giữa 2 chunk liên tiếp")
    auto_extract_kg: bool = Field(
        default=True,
        description="True: Sau khi lưu chunk và vector sẽ tự động chạy AI trích xuất Knowledge Graph vào Neo4j",
    )
    extra_metadata: dict[str, Any] | None = Field(default_factory=dict)

    @field_validator("subject")
    @classmethod
    def normalize_subject(cls, v: str) -> str:
        return v.strip().upper()


class MaterialChunkUpdate(BaseModel):
    """Schema cập nhật trạng thái bóc tách KG hoặc nội dung của `MaterialChunk`."""

    content: str | None = Field(default=None, min_length=1)
    token_count: int | None = Field(default=None, ge=0)
    canonical_codes: list[str] | None = None
    extraction_status: ExtractionStatusEnum | None = None
    extraction_error: str | None = None
    extra_metadata: dict[str, Any] | None = None

    @field_validator("canonical_codes")
    @classmethod
    def normalize_codes(cls, codes: list[str] | None) -> list[str] | None:
        if codes is None:
            return None
        return [normalize_canonical_code(c) for c in codes if c and c.strip()]


class MaterialChunkResponse(MaterialChunkBase, TimestampSchemaMixin):
    """
    Schema trả về thông tin đầy đủ của 1 `MaterialChunk` từ MySQL (`material_chunks`).
    """

    id: UUIDStr
    canonical_codes: list[str] | None = Field(default_factory=list)
    extraction_status: ExtractionStatusEnum
    extraction_error: str | None = None


class ChunkSemanticSearchRequest(BaseModel):
    """
    Schema tìm kiếm ngữ nghĩa trên ChromaDB kết hợp lấy dữ liệu chi tiết từ bảng `material_chunks`.
    """

    query_text: str = Field(..., min_length=1, description="Câu hỏi của học sinh hoặc từ khóa cần tìm")
    subject: str | None = Field(default=None, max_length=100, description="Lọc theo môn học")
    teacher_id: UUIDStr | None = Field(
        default=None,
        description="Nếu có teacher_id sẽ tìm trên cả tài liệu GLOBAL của Admin và TEACHER của giáo viên đó",
    )
    material_ids: list[UUIDStr] | None = Field(
        default=None,
        description="Giới hạn tìm kiếm trong danh sách học liệu cụ thể (nếu có)",
    )
    top_k: int = Field(default=5, ge=1, le=30, description="Số lượng chunks tương đồng nhất cần lấy")


class ChunkSemanticSearchResult(BaseModel):
    """Kết quả 1 chunk trả về từ tìm kiếm kết hợp ChromaDB + MySQL."""

    chunk: MaterialChunkResponse
    distance: float = Field(..., description="Khoảng cách vector (càng nhỏ càng sát nghĩa với cosine distance)")
    similarity_score: float = Field(..., description="Điểm tương đồng quy đổi (0.0 -> 1.0)")