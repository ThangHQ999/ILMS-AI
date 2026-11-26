import secrets
from fastapi import Depends, Header, HTTPException, status
from app.core.config import settings
from app.model.enums import OwnerRoleEnum
from app.schema.common import SpringBootCallerContext


async def verify_internal_api_key(
    x_internal_api_key: str = Header(
        ...,
        alias="X-Internal-Api-Key",
        description="Secret key nội bộ do Spring Boot đính kèm khi gọi sang FastAPI",
    ),
) -> str:
    """
    Xác thực request thực sự được gọi từ Spring Boot Backend thông qua `X-Internal-Api-Key`.
    Sử dụng `secrets.compare_digest` để chống tấn công timing attack.
    """
    if not secrets.compare_digest(x_internal_api_key, settings.INTERNAL_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Internal-Api-Key không hợp lệ. Từ chối kết nối ngoài Spring Boot.",
        )
    return x_internal_api_key


async def get_caller_context(
    _: str = Depends(verify_internal_api_key),
    x_user_id: str = Header(
        ...,
        alias="X-User-Id",
        description="UUID của người dùng hiện tại đã được Spring Boot xác thực JWT",
    ),
    x_user_role: OwnerRoleEnum = Header(
        default=OwnerRoleEnum.STUDENT,
        alias="X-User-Role",
        description="Vai trò người dùng: ADMIN, TEACHER, STUDENT hoặc SYSTEM",
    ),
    x_teacher_id: str | None = Header(
        default=None,
        alias="X-Teacher-Id",
        description="UUID của giáo viên phụ trách lớp (nếu học sinh đang học theo lớp riêng)",
    ),
) -> SpringBootCallerContext:
    """
    Trích xuất ngữ cảnh người dùng (`user_id`, `role`, `teacher_id`) từ bộ Header do Spring Boot chuyển tiếp.
    """
    return SpringBootCallerContext(
        user_id=x_user_id,
        role=x_user_role,
        teacher_id=x_teacher_id,
    )


async def require_admin_or_teacher(
    caller: SpringBootCallerContext = Depends(get_caller_context),
) -> SpringBootCallerContext:
    """Chỉ cho phép ADMIN, SYSTEM hoặc TEACHER thực hiện thao tác ghi/cập nhật học liệu và đồ thị."""
    if caller.role not in (OwnerRoleEnum.ADMIN, OwnerRoleEnum.TEACHER, OwnerRoleEnum.SYSTEM):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Admin hoặc Giáo viên mới có quyền chỉnh sửa Đồ thị Tri thức và Học liệu.",
        )
    return caller


async def require_admin(
    caller: SpringBootCallerContext = Depends(get_caller_context),
) -> SpringBootCallerContext:
    """Chỉ cho phép ADMIN hoặc SYSTEM chuẩn hóa Node tâm :KnowledgeEntity."""
    if caller.role not in (OwnerRoleEnum.ADMIN, OwnerRoleEnum.SYSTEM):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Hệ thống hoặc Admin mới có quyền chuẩn hóa trực tiếp :KnowledgeEntity.",
        )
    return caller