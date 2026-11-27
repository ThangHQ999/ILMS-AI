"""Pydantic v2 schemas for internal Spring Boot -> ILMS-AI chat endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _coerce_datetime(value: Any) -> datetime | None:
    """Accept ISO-8601 strings, datetime instances, or Jackson numeric arrays [Y,M,D,h,m,s,ns]."""
    if value is None or isinstance(value, datetime):
        return value
    if isinstance(value, (list, tuple)) and len(value) >= 5:
        try:
            year, month, day, hour, minute = (int(value[i]) for i in range(5))
            second = int(value[5]) if len(value) >= 6 else 0
            nano = int(value[6]) if len(value) >= 7 else 0
            microsecond = min(999_999, max(0, nano // 1000))
            return datetime(year, month, day, hour, minute, second, microsecond)
        except (TypeError, ValueError):
            return None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


class ChatSummarizeMessageItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    messageId: UUID | None = None
    senderName: str = "Thành viên"
    senderType: str = "USER"
    messageType: str = "TEXT"
    content: str = ""
    codeLanguage: str | None = None
    isRootMessage: bool = False
    createdAt: datetime | None = None

    @field_validator("senderName", mode="before")
    @classmethod
    def _default_sender_name(cls, v: Any) -> str:
        return v.strip()[:150] if isinstance(v, str) and v.strip() else "Thành viên"

    @field_validator("senderType", mode="before")
    @classmethod
    def _default_sender_type(cls, v: Any) -> str:
        return v.strip()[:30] if isinstance(v, str) and v.strip() else "USER"

    @field_validator("messageType", mode="before")
    @classmethod
    def _default_message_type(cls, v: Any) -> str:
        return v.strip()[:40] if isinstance(v, str) and v.strip() else "TEXT"

    @field_validator("content", mode="before")
    @classmethod
    def _default_content(cls, v: Any) -> str:
        return "" if v is None else str(v)

    @field_validator("isRootMessage", mode="before")
    @classmethod
    def _default_is_root(cls, v: Any) -> bool:
        return bool(v) if v is not None else False

    @field_validator("createdAt", mode="before")
    @classmethod
    def _parse_created_at(cls, v: Any) -> datetime | None:
        return _coerce_datetime(v)


class ChatSummarizeRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    conversationId: UUID
    threadRootId: UUID | None = None
    conversationType: str | None = Field(default=None, max_length=40)
    conversationName: str | None = Field(default=None, max_length=255)
    classId: UUID | None = None
    courseId: UUID | None = None
    courseTitle: str | None = Field(default=None, max_length=255)
    language: str = Field(default="vi", max_length=16)
    messages: list[ChatSummarizeMessageItem] = Field(default_factory=list, max_length=100)


class ChatSummarizeResponse(BaseModel):
    """Flat schema compatible with both OpenAI and Gemini structured outputs."""
    model_config = ConfigDict(extra="ignore")

    overview: str = Field(..., description="1-2 câu tổng quan ngắn gọn về nội dung thảo luận bằng tiếng Việt")
    mainTopics: list[str] = Field(default_factory=list, description="Tối đa 5 chủ đề chính đã thảo luận")
    keyConclusions: list[str] = Field(default_factory=list, description="Tối đa 5 kết luận hoặc lời giải đã chốt")
    openQuestions: list[str] = Field(default_factory=list, description="Tối đa 5 câu hỏi hoặc vấn đề còn bỏ ngỏ")
    actionItems: list[str] = Field(default_factory=list, description="Tối đa 5 đầu việc, bài tập hoặc deadline nhắc tới")


class GroupChatContextMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    senderName: str = "Thành viên"
    senderType: str = "USER"
    content: str = ""
    createdAt: datetime | None = None

    @field_validator("senderName", mode="before")
    @classmethod
    def _default_sender_name(cls, v: Any) -> str:
        return v.strip()[:150] if isinstance(v, str) and v.strip() else "Thành viên"

    @field_validator("senderType", mode="before")
    @classmethod
    def _default_sender_type(cls, v: Any) -> str:
        return v.strip()[:30] if isinstance(v, str) and v.strip() else "USER"

    @field_validator("content", mode="before")
    @classmethod
    def _default_content(cls, v: Any) -> str:
        return "" if v is None else str(v)

    @field_validator("createdAt", mode="before")
    @classmethod
    def _parse_created_at(cls, v: Any) -> datetime | None:
        return _coerce_datetime(v)


class SharedResourceMeta(BaseModel):
    model_config = ConfigDict(extra="ignore")

    resourceType: str | None = None
    resourceId: str | None = None
    title: str | None = None
    subtitle: str | None = None
    fileType: str | None = None
    url: str | None = None
    courseId: UUID | None = None
    classId: UUID | None = None
    conceptCode: str | None = None


class GroupChatAssistRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    conversationId: UUID
    classId: UUID | None = None
    courseId: UUID | None = None
    prompt: str = Field(..., min_length=1, max_length=6000)
    recentMessages: list[GroupChatContextMessage] = Field(default_factory=list, max_length=30)
    referencedResource: SharedResourceMeta | None = None


class GroupChatAssistResponse(BaseModel):
    """Flat schema compatible with both OpenAI and Gemini structured outputs."""
    model_config = ConfigDict(extra="ignore")

    answer: str = Field(..., description="Câu trả lời sư phạm ngắn gọn, chính xác bằng tiếng Việt")
    citedSources: list[str] = Field(default_factory=list, description="Danh sách nguồn học liệu được tham chiếu nếu có")
