from pydantic import BaseModel, Field, field_validator
from app.model.enums import DifficultyEnum, RelationLabel, ScopeEnum
from app.model.neo4j.nodes import normalize_canonical_code
from app.schema.common import ORMBaseSchema, UUIDStr


# ============================================================================
# 1. :KnowledgeEntity — Tâm chung bất biến đại diện cho 1 khái niệm khoa học
# ============================================================================
class KnowledgeEntityBase(ORMBaseSchema):
    canonical_code: str = Field(
        ...,
        min_length=2,
        max_length=128,
        description="Khóa duy nhất chuẩn hóa UPPER_SNAKE_CASE (VD: PYTHAGORAS_THEOREM)",
    )
    name: str = Field(..., min_length=1, max_length=255, description="Tên hiển thị của khái niệm khoa học")
    subject: str = Field(..., min_length=1, max_length=100, description="Môn học (VD: MATHEMATICS, PHYSICS)")

    @field_validator("canonical_code")
    @classmethod
    def validate_canonical_code(cls, v: str) -> str:
        code = normalize_canonical_code(v)
        if not code:
            raise ValueError("canonical_code không được rỗng sau khi chuẩn hóa.")
        return code

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v: str) -> str:
        return v.strip().upper()


class KnowledgeEntityCreate(KnowledgeEntityBase):
    source_chunk_id: UUIDStr | None = Field(
        default=None,
        description="UUID của bản ghi material_chunks đã sinh ra khái niệm này",
    )


class KnowledgeEntityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    subject: str | None = Field(default=None, min_length=1, max_length=100)


class KnowledgeEntityResponse(KnowledgeEntityBase):
    source_chunk_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


# ============================================================================
# 2. :Definition — Định nghĩa / Diễn giải lý thuyết
# ============================================================================
class DefinitionBase(ORMBaseSchema):
    content: str = Field(..., min_length=1, description="Nội dung định nghĩa hoặc diễn giải lý thuyết")
    conditions: list[str] = Field(
        default_factory=list,
        description="Danh sách các điều kiện áp dụng định nghĩa/định lý",
    )
    exceptions: list[str] = Field(
        default_factory=list,
        description="Các trường hợp ngoại lệ không thỏa mãn",
    )
    owner_id: UUIDStr = Field(..., description="UUID của Admin hoặc Giáo viên sở hữu")
    scope: ScopeEnum = Field(default=ScopeEnum.GLOBAL, description="GLOBAL hoặc TEACHER")


class DefinitionCreate(DefinitionBase):
    canonical_code: str = Field(
        ...,
        description="canonical_code của :KnowledgeEntity mà định nghĩa này thuộc về",
    )
    source_chunk_id: UUIDStr | None = None

    @field_validator("canonical_code")
    @classmethod
    def normalize_code(cls, v: str) -> str:
        return normalize_canonical_code(v)


class DefinitionUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1)
    conditions: list[str] | None = None
    exceptions: list[str] | None = None
    scope: ScopeEnum | None = None


class DefinitionResponse(DefinitionBase):
    id: UUIDStr
    source_chunk_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


# ============================================================================
# 3 & 4. :Process & :ProcessStep — Phương pháp giải và Chuỗi bước gợi ý Socratic
# ============================================================================
class ProcessStepBase(ORMBaseSchema):
    step_number: int = Field(..., ge=1, description="Thứ tự bước giải (1, 2, 3...)")
    action: str = Field(..., min_length=1, description="Hành động hoặc thao tác giải chi tiết tại bước này")
    hint_prompt: str = Field(
        ...,
        min_length=1,
        description="Câu hỏi gợi mở Socratic để dẫn dắt học sinh tự suy nghĩ ở bước này",
    )


class ProcessStepCreate(ProcessStepBase):
    pass


class ProcessStepUpdate(BaseModel):
    step_number: int | None = Field(default=None, ge=1)
    action: str | None = Field(default=None, min_length=1)
    hint_prompt: str | None = Field(default=None, min_length=1)


class ProcessStepResponse(ProcessStepBase):
    id: UUIDStr
    process_id: str | None = None
    created_at: str | None = None


class ProcessBase(ORMBaseSchema):
    name: str = Field(..., min_length=1, max_length=255, description="Tên phương pháp / quy trình giải dạng bài")
    owner_id: UUIDStr = Field(..., description="UUID của Admin hoặc Giáo viên")
    scope: ScopeEnum = Field(default=ScopeEnum.GLOBAL, description="GLOBAL hoặc TEACHER")


class ProcessCreate(ProcessBase):
    canonical_code: str = Field(
        ...,
        description="canonical_code của :KnowledgeEntity gắn với quy trình này",
    )
    steps: list[ProcessStepCreate] = Field(
        default_factory=list,
        description="Danh sách các bước :ProcessStep theo thứ tự",
    )
    source_chunk_id: UUIDStr | None = None

    @field_validator("canonical_code")
    @classmethod
    def normalize_code(cls, v: str) -> str:
        return normalize_canonical_code(v)


class ProcessUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    scope: ScopeEnum | None = None
    steps: list[ProcessStepCreate] | None = Field(
        default=None,
        description="Nếu truyền vào sẽ thay thế chuỗi các bước giải của quy trình",
    )


class ProcessResponse(ProcessBase):
    id: UUIDStr
    steps: list[ProcessStepResponse] = Field(default_factory=list)
    source_chunk_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


# ============================================================================
# 5. :Example — Ví dụ minh họa / Đoạn code mẫu
# ============================================================================
class ExampleBase(ORMBaseSchema):
    title: str = Field(..., min_length=1, max_length=255, description="Tiêu đề ví dụ minh họa")
    code_snippet: str | None = Field(
        default=None,
        description="Đoạn code mẫu, công thức hoặc lời giải biểu diễn ngắn gọn",
    )
    explanation: str = Field(..., min_length=1, description="Lời giải thích chi tiết cho ví dụ")
    owner_id: UUIDStr = Field(..., description="UUID của Admin hoặc Giáo viên")
    scope: ScopeEnum = Field(default=ScopeEnum.GLOBAL)


class ExampleCreate(ExampleBase):
    canonical_code: str = Field(..., description="canonical_code của :KnowledgeEntity được minh họa")
    source_chunk_id: UUIDStr | None = None

    @field_validator("canonical_code")
    @classmethod
    def normalize_code(cls, v: str) -> str:
        return normalize_canonical_code(v)


class ExampleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    code_snippet: str | None = None
    explanation: str | None = Field(default=None, min_length=1)
    scope: ScopeEnum | None = None


class ExampleResponse(ExampleBase):
    id: UUIDStr
    source_chunk_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


# ============================================================================
# 6. :Exercise — Bài tập rèn luyện
# ============================================================================
class ExerciseBase(ORMBaseSchema):
    title: str = Field(..., min_length=1, max_length=255, description="Tiêu đề bài tập")
    content: str = Field(..., min_length=1, description="Đề bài chi tiết")
    difficulty: DifficultyEnum = Field(default=DifficultyEnum.MEDIUM, description="EASY, MEDIUM, HARD, ADVANCED")
    owner_id: UUIDStr = Field(..., description="UUID của Admin hoặc Giáo viên")
    scope: ScopeEnum = Field(default=ScopeEnum.GLOBAL)


class ExerciseCreate(ExerciseBase):
    canonical_code: str = Field(..., description="canonical_code của :KnowledgeEntity mà bài tập rèn luyện")
    process_id: UUIDStr | None = Field(
        default=None,
        description="Tùy chọn nối bài tập này với 1 :Process cụ thể qua cạnh [:USES_PROCESS]",
    )
    source_chunk_id: UUIDStr | None = None

    @field_validator("canonical_code")
    @classmethod
    def normalize_code(cls, v: str) -> str:
        return normalize_canonical_code(v)


class ExerciseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = Field(default=None, min_length=1)
    difficulty: DifficultyEnum | None = None
    scope: ScopeEnum | None = None


class ExerciseResponse(ExerciseBase):
    id: UUIDStr
    source_chunk_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


# ============================================================================
# 7. :Argument — Lập luận logic / Chứng minh
# ============================================================================
class ArgumentBase(ORMBaseSchema):
    hypothesis: str = Field(..., min_length=1, description="Giả thiết xuất phát")
    evidence: str = Field(..., min_length=1, description="Luận cứ / Dẫn chứng / Các bước biến đổi")
    conclusion: str = Field(..., min_length=1, description="Kết luận được chứng minh")
    owner_id: UUIDStr = Field(..., description="UUID của Admin hoặc Giáo viên")
    scope: ScopeEnum = Field(default=ScopeEnum.GLOBAL)


class ArgumentCreate(ArgumentBase):
    canonical_code: str = Field(..., description="canonical_code của :KnowledgeEntity")
    source_chunk_id: UUIDStr | None = None

    @field_validator("canonical_code")
    @classmethod
    def normalize_code(cls, v: str) -> str:
        return normalize_canonical_code(v)


class ArgumentUpdate(BaseModel):
    hypothesis: str | None = Field(default=None, min_length=1)
    evidence: str | None = Field(default=None, min_length=1)
    conclusion: str | None = Field(default=None, min_length=1)
    scope: ScopeEnum | None = None


class ArgumentResponse(ArgumentBase):
    id: UUIDStr
    source_chunk_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


# ============================================================================
# 8. Quan hệ giữa các :KnowledgeEntity (22 nhãn RelationLabel) & Subgraph
# ============================================================================
class EntityRelationCreate(ORMBaseSchema):
    """Schema tạo cạnh nối giữa 2 :KnowledgeEntity theo đúng 22 nhãn RelationLabel."""

    source_canonical_code: str = Field(..., description="canonical_code của thực thể nguồn")
    relation_label: RelationLabel = Field(..., description="1 trong 22 nhãn quan hệ thuộc RelationLabel")
    target_canonical_code: str = Field(..., description="canonical_code của thực thể đích")
    description: str | None = Field(default=None, description="Giải thích ngắn gọn mối quan hệ")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source_chunk_id: UUIDStr | None = None
    owner_id: str = Field(default="SYSTEM")
    scope: ScopeEnum = Field(default=ScopeEnum.GLOBAL)

    @field_validator("source_canonical_code", "target_canonical_code")
    @classmethod
    def normalize_codes(cls, v: str) -> str:
        return normalize_canonical_code(v)


class EntityRelationResponse(EntityRelationCreate):
    target_name: str | None = None
    created_at: str | None = None


class KnowledgeEntitySubgraphResponse(BaseModel):
    """
    Toàn bộ cụm tri thức xoay quanh 1 :KnowledgeEntity (đã lọc theo quyền GLOBAL + TEACHER).
    Dùng để cung cấp ngữ cảnh có cấu trúc cho Socratic Tutor hoặc hiển thị đồ thị trên FE.
    """

    entity: KnowledgeEntityResponse
    definitions: list[DefinitionResponse] = Field(default_factory=list)
    processes: list[ProcessResponse] = Field(default_factory=list)
    examples: list[ExampleResponse] = Field(default_factory=list)
    exercises: list[ExerciseResponse] = Field(default_factory=list)
    arguments: list[ArgumentResponse] = Field(default_factory=list)
    outgoing_relations: list[EntityRelationResponse] = Field(default_factory=list)
    incoming_relations: list[EntityRelationResponse] = Field(default_factory=list)