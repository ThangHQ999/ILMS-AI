from datetime import datetime, timezone
from typing import Annotated, Any, Generic, TypeVar
import uuid
from pydantic import AfterValidator, BaseModel, ConfigDict, Field
from app.model.enums import OwnerRoleEnum, ScopeEnum

T = TypeVar("T")


def utc_now_iso_z() -> str:
    """Sinh chuỗi thời gian UTC chuẩn ISO-8601 có mili-giây và hậu tố 'Z' (VD: 2026-10-10T09:32:45.547Z)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def validate_uuid_str(value: str | uuid.UUID | bytes) -> str:
    """
    Chuẩn hóa UUID từ string 36 ký tự, đối tượng UUID hoặc bytes(16) (BinaryUUID từ MySQL)
    về định dạng chuỗi UUID v4 chuẩn (lowercase, 36 ký tự).
    """
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, bytes):
        if len(value) == 16:
            return str(uuid.UUID(bytes=value))
        value = value.decode("utf-8")
    try:
        return str(uuid.UUID(str(value).strip()))
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"Giá trị '{value}' không phải là UUID hợp lệ.") from exc


UUIDStr = Annotated[str, AfterValidator(validate_uuid_str)]


class ORMBaseSchema(BaseModel):
    """Base schema cấu hình sẵn from_attributes=True để đọc trực tiếp từ SQLAlchemy ORM model."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class TimestampSchemaMixin(BaseModel):
    """Mixin ánh xạ 2 cột created_at và updated_at từ TimestampMixin của MySQL."""

    created_at: datetime
    updated_at: datetime


class SpringBootCallerContext(BaseModel):
    """
    Thông tin ngữ cảnh người dùng được Spring Boot đính kèm khi gọi sang FastAPI
    (thông qua Headers hoặc phần tử xác thực nội bộ).
    """

    user_id: UUIDStr = Field(..., description="UUID của người dùng hiện tại (Admin, Teacher hoặc Student)")
    role: OwnerRoleEnum = Field(..., description="Vai trò người dùng đã được Spring Boot xác thực")
    teacher_id: UUIDStr | None = Field(
        default=None,
        description="UUID của giáo viên phụ trách lớp (dùng khi học sinh truy vấn kiến thức scope=TEACHER)",
    )

    @property
    def effective_scope_for_write(self) -> ScopeEnum:
        """Nếu người tạo là ADMIN/SYSTEM thì mặc định ghi bản chuẩn GLOBAL, ngược lại là TEACHER."""
        if self.role in (OwnerRoleEnum.ADMIN, OwnerRoleEnum.SYSTEM):
            return ScopeEnum.GLOBAL
        return ScopeEnum.TEACHER


class PaginationParams(BaseModel):
    """
    Tham số phân trang chuẩn đồng bộ 100% với Spring Data Pageable (pageNumber bắt đầu từ 0).
    Hỗ trợ cả alias `page` và `page_size` để tương thích ngược.
    """

    model_config = ConfigDict(populate_by_name=True)

    pageNumber: int = Field(
        default=0,
        ge=0,
        alias="page",
        description="Chỉ số trang hiện tại (bắt đầu từ 0 theo chuẩn Spring Boot)",
    )
    pageSize: int = Field(
        default=10,
        ge=1,
        le=100,
        alias="page_size",
        description="Số bản ghi tối đa trên mỗi trang",
    )

    @property
    def offset(self) -> int:
        return self.pageNumber * self.pageSize


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Cấu trúc trả về danh sách có phân trang từ FastAPI, khớp 100% với `PaginatedResponse<T>` bên Spring Boot BE:
    {
      "items": [],
      "pageNumber": 0,
      "pageSize": 10,
      "totalElements": 0,
      "totalPages": 0,
      "last": true
    }
    """

    model_config = ConfigDict(populate_by_name=True)

    items: list[T] = Field(default_factory=list)
    pageNumber: int = Field(default=0, ge=0, description="Trang hiện tại (0-indexed)")
    pageSize: int = Field(default=10, ge=1, description="Kích thước trang")
    totalElements: int = Field(default=0, ge=0, description="Tổng số bản ghi")
    totalPages: int = Field(default=0, ge=0, description="Tổng số trang")
    last: bool = Field(default=True, description="True nếu đây là trang cuối cùng")


class ApiResponse(BaseModel, Generic[T]):
    """
    Khuôn mẫu JSON phản hồi chuẩn từ FastAPI về cho Spring Boot, khớp 100% với `ApiResponse<T>` bên Spring Boot BE:
    {
      "status": 0,
      "message": "Thành công",
      "data": { },
      "timestamp": "2026-10-10T09:32:45.547Z"
    }
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",  # Tự động bỏ qua tham số thừa như `success=True` ở các controller cũ
    )

    status: int = Field(default=0, description="0 = Thành công (khớp chuẩn ApiResponse<T> của Spring Boot)")
    message: str = Field(default="Thành công", description="Thông báo trạng thái")
    data: T | None = Field(default=None, description="Payload dữ liệu trả về")
    timestamp: str = Field(
        default_factory=utc_now_iso_z,
        description="Thời gian phản hồi chuẩn ISO-8601 UTC (VD: 2026-10-10T09:32:45.547Z)",
    )