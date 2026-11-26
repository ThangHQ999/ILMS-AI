package com.example.ilms.exception;

import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
public enum ErrorCode {
    SOCRATIC_STREAM_FAILED(HttpStatus.BAD_GATEWAY, "Kết nối gia sư AI bị gián đoạn. Vui lòng thử lại."),
    // Auth
    USER_EXISTED(HttpStatus.CONFLICT, "Tên tài khoản đã tồn tại"),
    EMAIL_EXISTED(HttpStatus.CONFLICT, "Email đã được đăng ký"),
    USER_NOT_FOUND(HttpStatus.NOT_FOUND, "Không tìm thấy người dùng"),
    ROLE_NOT_FOUND(HttpStatus.NOT_FOUND, "Vai trò người dùng không tồn tại"),
    PASSWORD_INCORRECT(HttpStatus.UNAUTHORIZED, "Mật khẩu không chính xác"),
    PASSWORD_CANNOT_BE_OLD_PASSWORD(HttpStatus.UNAUTHORIZED, "Mật khẩu mới không được trùng với mật khẩu cũ"),
    UNAUTHORIZED(HttpStatus.UNAUTHORIZED, "Yêu cầu xác thực tài khoản"),
    INVALID_TOKEN(HttpStatus.UNAUTHORIZED, "Token không hợp lệ hoặc đã hết hạn"),
    INVALID_CREDENTIALS(HttpStatus.UNAUTHORIZED, "Email hoặc mật khẩu không chính xác"),
    USER_DISABLED(HttpStatus.FORBIDDEN, "Tài khoản của bạn đã bị khóa"),
    // Class
    CLASS_NOT_FOUND(HttpStatus.NOT_FOUND, "Không tìm thấy lớp học"),
    CLASS_MEMBER_NOT_FOUND(HttpStatus.NOT_FOUND, "Không tìm thấy thành viên trong lớp học"),
    CLASS_CODE_NOT_FOUND(HttpStatus.NOT_FOUND, "Mã lớp học không tồn tại"),
    CLASS_CODE_INACTIVE(HttpStatus.FORBIDDEN, "Mã lớp học hiện không hoạt động"),
    ALREADY_CLASS_MEMBER(HttpStatus.CONFLICT, "Bạn đã là thành viên của lớp học"),
    CLASS_ACCESS_DENIED(HttpStatus.FORBIDDEN, "Bạn không có quyền thực hiện thao tác này"),
    CLASS_MEMBER_NOT_PENDING(HttpStatus.CONFLICT, "Thành viên không ở trạng thái chờ duyệt"),
    CLASS_OWNER_ROLE_CANNOT_CHANGE(HttpStatus.CONFLICT, "Không thể thay đổi vai trò của chủ sở hữu lớp học"),
    CLASS_OWNER_CANNOT_BE_REMOVED(HttpStatus.CONFLICT, "Không thể xóa chủ sở hữu khỏi lớp học"),
    CLASS_MEMBER_CANNOT_LEAVE(HttpStatus.CONFLICT, "Giảng viên hoặc chủ sở hữu không thể tự rời lớp học"),
    // Invitation
    INVITATION_NOT_FOUND(HttpStatus.NOT_FOUND, "Không tìm thấy lời mời"),
    INVITATION_ALREADY_EXISTS(HttpStatus.CONFLICT, "Lời mời đang chờ xử lý đã tồn tại"),
    INVITATION_ALREADY_PROCESSED(HttpStatus.CONFLICT, "Lời mời này đã được xử lý"),
    INVITATION_EXPIRED(HttpStatus.GONE, "Lời mời đã hết hạn"),
    INVITATION_EMAIL_MISMATCH(HttpStatus.FORBIDDEN, "Lời mời này không dành cho tài khoản hiện tại"),
    INVALID_INVITATION_ROLE(HttpStatus.BAD_REQUEST, "Vai trò trong lời mời không hợp lệ"),
    //    TOKEN
    INVALID_OR_EXPIRED_TOKEN(HttpStatus.UNAUTHORIZED, "Mã không hợp lệ hoặc đã hết hạn"),
    TOKEN_EXPIRED(HttpStatus.UNAUTHORIZED, "Mã đã hết hạn"),

    // Course
    COURSE_NOT_FOUND(HttpStatus.NOT_FOUND, "Không tìm thấy môn học"),

    // AI Chat Session
    AI_CHAT_SESSION_NOT_FOUND(HttpStatus.NOT_FOUND, "Không tìm thấy phiên trò chuyện AI"),
    AI_CHAT_SESSION_ACCESS_DENIED(HttpStatus.FORBIDDEN, "Bạn không có quyền truy cập phiên trò chuyện này"),

    // AI Chat Message
    AI_CHAT_MESSAGE_NOT_FOUND(HttpStatus.NOT_FOUND, "Không tìm thấy tin nhắn"),
    INVALID_MESSAGE_TYPE(HttpStatus.BAD_REQUEST, "Loại tin nhắn không hợp lệ (hỗ trợ USER, ASSISTANT, SYSTEM)"),

    // Upload Module
    FILE_EMPTY(HttpStatus.BAD_REQUEST, "Tệp tải lên không được để trống"),
    INVALID_FILE_FORMAT(HttpStatus.BAD_REQUEST, "Định dạng tệp không được hỗ trợ"),
    FILE_SIZE_EXCEEDED(HttpStatus.PAYLOAD_TOO_LARGE, "Kích thước tệp vượt quá giới hạn cho phép"),
    FILE_UPLOAD_FAILED(HttpStatus.INTERNAL_SERVER_ERROR, "Tải tệp lên thất bại"),
    FILE_DELETE_FAILED(HttpStatus.INTERNAL_SERVER_ERROR, "Xóa tệp thất bại"),

    // OAuth Module
    OAUTH_AUTHENTICATION_FAILED(HttpStatus.UNAUTHORIZED, "Xác thực OAuth thất bại"),
    OAUTH_EMAIL_NOT_FOUND(HttpStatus.BAD_REQUEST, "Không tìm thấy email từ tài khoản OAuth"),
    UNSUPPORTED_OAUTH_PROVIDER(HttpStatus.BAD_REQUEST, "Nhà cung cấp OAuth không được hỗ trợ"),

    // Role & Permission Module
    ROLE_CODE_EXISTED(HttpStatus.CONFLICT, "Mã vai trò đã tồn tại"),
    ROLE_CANNOT_BE_DELETED(HttpStatus.CONFLICT, "Không thể xóa vai trò hệ thống hoặc vai trò đang có người dùng"),
    PERMISSION_NOT_FOUND(HttpStatus.NOT_FOUND, "Không tìm thấy quyền hạn"),
    PERMISSION_CODE_EXISTED(HttpStatus.CONFLICT, "Mã quyền hạn đã tồn tại"),
    PERMISSION_IN_USE(HttpStatus.CONFLICT, "Không thể xóa quyền hạn đang được gán cho các vai trò");

    private final HttpStatus status;
    private final String message;

    ErrorCode(HttpStatus status, String message) {
        this.status = status;
        this.message = message;
    }
}