from enum import Enum
import json
from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator
from app.model.enums import MessageRoleEnum
from app.schema.common import ORMBaseSchema, TimestampSchemaMixin, UUIDStr
from app.schema.tutoring_contracts import StepProgress

# Định nghĩa các giá trị hợp lệ cho cột feedback_rating trong bảng socratic_chat_messages
FeedbackRatingLiteral = Literal["LIKE", "DISLIKE", "1", "2", "3", "4", "5"]


# ============================================================================
# PHẦN 1: SCHEMA QUẢN LÝ PHIÊN CHAT & TIN NHẮN (KHỚP 100% BẢNG MYSQL CỦA BẠN)
# - Bảng `socratic_chat_sessions`
# - Bảng `socratic_chat_messages`
# ============================================================================


class SocraticChatSessionUpdate(BaseModel):
    """Schema cập nhật trạng thái phiên học hoặc đổi tiêu đề Sidebar."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    teacher_id: UUIDStr | None = None
    subject: str | None = Field(default=None, max_length=100)
    active_canonical_code: str | None = Field(default=None, max_length=128)
    active_process_id: UUIDStr | None = None
    active_exercise_id: UUIDStr | None = None
    current_step_number: int | None = Field(default=None, ge=1)
    is_completed: bool | None = None


class SocraticChatSessionSidebarItem(ORMBaseSchema, TimestampSchemaMixin):
    """
    Schema gọn nhẹ trả về danh sách phiên chat cho Sidebar UI
    (tối ưu theo index `idx_student_sidebar (student_id, updated_at)`).
    """

    id: UUIDStr
    student_id: UUIDStr
    teacher_id: UUIDStr | None = None
    title: str
    subject: str | None = None
    active_canonical_code: str | None = None
    current_step_number: int
    is_completed: bool


class SocraticChatMessageResponse(ORMBaseSchema, TimestampSchemaMixin):
    """
    Schema ánh xạ 1-1 với bảng `socratic_chat_messages` trong MySQL.
    """

    id: UUIDStr
    session_id: UUIDStr
    role: MessageRoleEnum | str = Field(..., description="USER, ASSISTANT, SYSTEM")
    content: str
    step_number_at_turn: int | None = None
    step_progress: StepProgress | None = None
    referenced_chunk_ids: list[str] | None = Field(default_factory=list)
    referenced_node_ids: list[str] | None = Field(default_factory=list)
    user_feedback: str | None = None
    feedback_rating: str | None = None
    turn_id: UUIDStr | None = None
    turn_status: str | None = None
    content_status: str | None = None
    artifacts: list[dict[str, Any]] = Field(default_factory=list)


class SocraticChatSessionDetailResponse(SocraticChatSessionSidebarItem):
    """Schema chi tiết 1 phiên Socratic Chat bao gồm cả cấu hình quy trình và lịch sử tin nhắn."""

    active_process_id: UUIDStr | None = None
    active_exercise_id: UUIDStr | None = None
    messages: list[SocraticChatMessageResponse] = Field(default_factory=list)


class SocraticMessageFeedbackRequest(BaseModel):
    """
    Schema để học sinh đánh giá 1 câu trả lời gợi mở của AI (`socratic_chat_messages`).
    """

    user_feedback: str | None = Field(
        default=None,
        max_length=2000,
        description="Phản hồi bằng lời của học sinh về gợi ý của Socratic Tutor",
    )
    feedback_rating: FeedbackRatingLiteral | None = Field(
        default=None,
        description="Đánh giá nhanh: 'LIKE', 'DISLIKE' hoặc số sao từ '1' đến '5'",
    )


# ============================================================================
# PHẦN 2: SCHEMA REQUEST & SỰ KIỆN STREAM SSE (FE -> SPRING BOOT -> FASTAPI)
# ============================================================================
class SocraticChatStreamRequest(BaseModel):
    """
    Payload do Spring Boot gửi sang FastAPI để bắt đầu nhận luồng SSE trả lời học sinh.
    """

    session_id: UUIDStr | None = Field(
        default=None,
        description="UUID của phiên chat hiện tại; nếu None FastAPI sẽ tạo mới SocraticChatSession",
    )
    student_id: UUIDStr = Field(..., description="UUID của học sinh đang chat")
    teacher_id: UUIDStr | None = Field(
        default=None,
        description="UUID giáo viên phụ trách (để ưu tiên truy vấn đồ thị Neo4j có scope=TEACHER)",
    )
    message: str = Field(..., min_length=1, description="Câu hỏi hoặc câu trả lời từng bước của học sinh")
    subject: str | None = Field(default=None, max_length=100, description="Môn học (VD: MATHEMATICS, PHYSICS)")
    material_ids: list[UUIDStr] | None = Field(
        default=None,
        description="Giới hạn phạm vi truy xuất RAG trong các học liệu cụ thể (nếu có)",
    )
    active_canonical_code: str | None = Field(
        default=None,
        max_length=128,
        description="Ép tập trung vào 1 khái niệm :KnowledgeEntity cụ thể (nếu học sinh bấm từ bài học)",
    )
    active_process_id: UUIDStr | None = Field(
        default=None,
        description="Ép đi theo 1 :Process cụ thể",
    )
    active_exercise_id: UUIDStr | None = Field(
        default=None,
        description="Ép giải 1 :Exercise cụ thể",
    )
    forced_action: str | None = None
    client_request_id: UUIDStr | None = None
    expected_state_version: int | None = Field(default=None, ge=0)
    protocol_version: Literal[1, 2] = 2

    @field_validator('message')
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()
        if not value or len(value) > 20000:
            raise ValueError('Tin nhắn phải có nội dung và không vượt quá 20000 ký tự.')
        return value


class SSEEventTypeEnum(str, Enum):
    """Các loại sự kiện phát qua dòng chảy Server-Sent Events (SSE)."""

    SESSION_INIT = "session_init"      # Phát ngay đầu stream: trả về session_id, message_id, bước hiện tại
    STEP_UPDATE = "step_update"        # Phát khi học sinh trả lời đúng bước hiện tại và được nâng lên bước kế tiếp
    CONTEXT_REF = "context_ref"        # Phát danh sách referenced_chunk_ids và referenced_node_ids đã dùng
    TOKEN = "token"                    # Phát từng cụm từ (delta token) của câu phản hồi Socratic
    DONE = "done"                      # Phát khi hoàn tất câu trả lời và đã lưu vào bảng socratic_chat_messages
    ERROR = "error"                    # Phát khi có lỗi trong quá trình stream
    STATUS = 'status'
    CONTENT_REPLACE = 'content_replace'
    DIAGRAM_READY = 'diagram_ready'
    EXERCISE_READY = 'exercise_ready'


class SSESessionInitData(BaseModel):
    """Dữ liệu của sự kiện `session_init`."""

    session_id: UUIDStr
    user_message_id: UUIDStr
    assistant_message_id: UUIDStr
    title: str
    active_canonical_code: str | None = None
    active_process_id: str | None = None
    active_exercise_id: str | None = None
    current_step_number: int = 1
    step_progress: StepProgress | None = None


class SSEStepUpdateData(BaseModel):
    """Dữ liệu của sự kiện `step_update` khi tiến trình Socratic chuyển bước."""

    previous_step_number: int
    current_step_number: int
    step_progress: StepProgress | None = None
    total_steps: int | None = None
    current_step_action: str | None = None
    is_completed: bool = False
    did_backtrack: bool = False
    active_canonical_code: str | None = None

class SSEContextRefData(BaseModel):
    """Dữ liệu của sự kiện `context_ref` phục vụ truy vết RAG (Chroma + MySQL + Neo4j)."""

    referenced_chunk_ids: list[str] = Field(default_factory=list)
    referenced_node_ids: list[str] = Field(default_factory=list)
    matched_canonical_codes: list[str] = Field(default_factory=list)
    active_strategy: str | None = None
    frustration_level: str | None = None


class SSETokenData(BaseModel):
    """Dữ liệu của sự kiện `token`."""

    delta: str = Field(..., description="Mảnh văn bản vừa sinh ra từ LLM")


class SSEDoneData(BaseModel):
    """Dữ liệu của sự kiện `done` kết thúc lượt trả lời."""

    session_id: UUIDStr
    assistant_message_id: UUIDStr
    full_content: str
    step_number_at_turn: int | None = None
    step_progress: StepProgress | None = None
    is_completed: bool
    referenced_chunk_ids: list[str] = Field(default_factory=list)
    referenced_node_ids: list[str] = Field(default_factory=list)
    active_strategy: str | None = None
    

class SSEErrorData(BaseModel):
    """Dữ liệu của sự kiện `error`."""

    code: str
    message: str
    recoverable: bool = True


class SocraticSSEEvent(BaseModel):
    """
    Khuôn mẫu đóng gói 1 khung truyền (frame) SSE chuẩn từ FastAPI về Spring Boot -> FE.
    """

    event: SSEEventTypeEnum
    data: (
        SSESessionInitData
        | SSEStepUpdateData
        | SSEContextRefData
        | SSETokenData
        | SSEDoneData
        | SSEErrorData
        | dict[str, Any]
    )

    def to_sse_frame(self) -> str:
        """
        Định dạng thành chuỗi chuẩn giao thức text/event-stream:
        event: <event_name>\n
        data: <json_payload>\n\n
        """
        if isinstance(self.data, BaseModel):
            json_str = self.data.model_dump_json()
        else:
            json_str = json.dumps(self.data, ensure_ascii=False)
        return f"event: {self.event.value}\ndata: {json_str}\n\n"
