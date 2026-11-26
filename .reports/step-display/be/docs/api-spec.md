# API SPEC — ILMS

> **Status: PROPOSED CONTRACT.** Written from the PRD so the frontend can start. Replace with the real backend/OpenAPI spec as soon as it exists. Agents: if an endpoint is missing or differs from the real backend, **ask — never invent fields**.

## 1. Conventions
- Base URL: `NEXT_PUBLIC_API_URL` (ví dụ: `http://localhost:8080/api/v1`)
- Format: JSON, UTF-8. Dates: ISO 8601 UTC strings. IDs: UUID strings.
- Auth: Custom JWT. Gửi qua Header `Authorization: Bearer <token>` (Hoặc lấy từ Cookie tùy cấu hình frontend). Unauthenticated → `401`, forbidden → `403`.
- Locale: send `Accept-Language: vi|en`.

### Success envelope (Khớp với `ApiResponse<T>`)
```json
{ 
  "status": 0, 
  "message": "Thành công", 
  "data": { }, 
  "timestamp": "2026-10-10T09:32:45.547Z" 
}
```
### Paginated data (matches `PaginatedResponse<T>`)
```json
{ 
  "status": 0, 
  "message": "string", 
  "data": { 
    "items": [], 
    "pageNumber": 0, 
    "pageSize": 10, 
    "totalElements": 0, 
    "totalPages": 0, 
    "last": true 
  },
  "timestamp": "2026-10-10T09:32:45.547Z"
}
```
Query: `?page=1&pageSize=10&sort=createdAt:desc&search=...`

### Error envelope (becomes `ApiError`)
```json
{ 
  "status": 40001, 
  "message": "Tên khóa học đã tồn tại", 
  "data": null,
  "timestamp": "2026-10-10T09:32:45.547Z"
}
```
Field errors use i18n keys so the UI can translate them.

### Common error codes
| HTTP | code | Meaning |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Invalid input (`details.fieldErrors`) |
| 401 | `UNAUTHENTICATED` | Missing/expired session |
| 403 | `FORBIDDEN` | Not allowed |
| 404 | `NOT_FOUND` | Resource missing |
| 409 | `CONFLICT` | Duplicate/invalid state (e.g. already enrolled) |
| 422 | `BUSINESS_RULE` | Rule violated (e.g. delete course with enrollments) |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error |

## 2. Auth

| Method | Path | Purpose | Request Body | Response `data` Object |
|---|---|---|---|---|
| POST | `/auth/login` | Xác thực người dùng (Login) | `{ "email": "...", "password": "..." }` | `UserProfile` |
| POST | `/auth/register` | Đăng ký tài khoản mới | `{ "email": "...", "password": "...", "firstName": "...", "middleName": "...", "lastName": "..." }` | `UserProfile` |
| POST | `/auth/logout` | Đăng xuất (Clear session) | | Xóa Cookie |
| GET | `/auth/me` | Lấy thông tin user hiện tại | | `UserProfile` |

### Schema Model: `UserProfile`
Đây là cục dữ liệu nằm bên trong trường `data` của `ApiResponse<T>` (áp dụng cho `/auth/login` và `/auth/me`).

*Lưu ý cho AI: Backend trả JWT Token ngầm qua `Set-Cookie: HttpOnly` header trong endpoint `/auth/login`, KHÔNG CÓ trường token trong body JSON. Axios interceptor cần được cấu hình `withCredentials: true` để tự động đính kèm cookie này cho các request sau.*

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "roleName": "ADMIN",
  "email": "user@example.com",
  "firstName": "Nguyễn",
  "middleName": "Văn",
  "lastName": "A"
}
```

## 3. AI Chat Sessions

Base path: `/api/v1/ai-chat-sessions`

| Method | Path | Purpose | Query / Request Body | Response `data` Object |
|---|---|---|---|---|
| POST | `/api/v1/ai-chat-sessions` | Tạo phiên chat mới | `{ "title": "optional string" }` | `AiChatSessionResponseDTO` |
| GET | `/api/v1/ai-chat-sessions` | Lấy danh sách phiên chat của user | `?search=&userId=&page=0&size=10&sort=lastUpdatedAt,desc` | `PageResponse<AiChatSessionResponseDTO>` |
| GET | `/api/v1/ai-chat-sessions/{id}` | Lấy chi tiết phiên chat kèm tin nhắn | None | `AiChatSessionDetailResponseDTO` |
| PUT | `/api/v1/ai-chat-sessions/{id}` | Đổi tiêu đề phiên chat | `{ "title": "required string" }` | `AiChatSessionResponseDTO` |
| DELETE | `/api/v1/ai-chat-sessions/{id}` | Xóa vĩnh viễn phiên chat (Hard delete) | None | `null` |

## 4. AI Chat Messages

Base path: `/api/v1/ai-chat-sessions/{sessionId}/messages`

| Method | Path | Purpose | Query / Request Body | Response `data` Object |
|---|---|---|---|---|
| POST | `/api/v1/ai-chat-sessions/{sessionId}/messages` | Gửi/tạo tin nhắn mới (tự update `lastUpdatedAt` của session) | `{ "content": "string", "messageType": "USER" }` | `AiChatMessageResponseDTO` |
| GET | `/api/v1/ai-chat-sessions/{sessionId}/messages` | Lấy danh sách tin nhắn trong session | `?page=0&size=20&sort=sentAt,asc` | `PageResponse<AiChatMessageResponseDTO>` |
| GET | `/api/v1/ai-chat-sessions/{sessionId}/messages/{messageId}` | Xem chi tiết một tin nhắn | None | `AiChatMessageResponseDTO` |
| PUT | `/api/v1/ai-chat-sessions/{sessionId}/messages/{messageId}` | Cập nhật nội dung tin nhắn | `{ "content": "updated content" }` | `AiChatMessageResponseDTO` |
| PATCH | `/api/v1/ai-chat-sessions/{sessionId}/messages/{messageId}/feedback` | Đánh giá phản hồi tin nhắn (LIKE/DISLIKE/sao + nhận xét) | `{ "feedbackRating": "LIKE", "userFeedback": "tốt" }` | `AiChatMessageResponseDTO` |
| DELETE | `/api/v1/ai-chat-sessions/{sessionId}/messages/{messageId}` | Xóa tin nhắn | None | `null` |

## 5. File Uploads (Cloudinary)

Base path: `/api/v1/uploads`

Content-Type: `multipart/form-data`

| Method | Path | Purpose | Query / Form-Data Body | Response `data` Object |
|---|---|---|---|---|
| POST | `/api/v1/uploads` | Tải lên tệp đa năng (tự động nhận diện ảnh/video) | `file`: MultipartFile (required), `folder`: string (optional) | `FileUploadResponseDTO` |
| POST | `/api/v1/uploads/image` | Tải lên hình ảnh (max 10MB, kiểm tra mime `image/*`) | `file`: MultipartFile (required), `folder`: string (optional) | `FileUploadResponseDTO` |
| POST | `/api/v1/uploads/video` | Tải lên video (max 100MB, kiểm tra mime `video/*`) | `file`: MultipartFile (required), `folder`: string (optional) | `FileUploadResponseDTO` |
| DELETE | `/api/v1/uploads` | Xóa tệp trên Cloudinary | `?publicId=xxx&resourceType=image` | `null` |

### Schema Model: `FileUploadResponseDTO`
```json
{
  "publicId": "ilms/images/avatars/sample123",
  "url": "http://res.cloudinary.com/.../sample123.jpg",
  "secureUrl": "https://res.cloudinary.com/.../sample123.jpg",
  "format": "jpg",
  "resourceType": "image",
  "bytes": 204850,
  "width": 1024,
  "height": 768,
  "duration": null,
  "createdAt": "2026-10-15T01:30:00Z",
  "originalFilename": "avatar.jpg"
}
```

## 6. OAuth2 Authentication (Google & GitHub)

Base path: `/api/v1/auth/oauth`

| Method | Path | Purpose | Query / Request Body | Response / Behavior |
|---|---|---|---|---|
| GET | `/api/v1/auth/oauth/{provider}/url` | Lấy URL đăng nhập OAuth (`google` hoặc `github`) | Path: `provider` | `OAuthUrlResponseDTO` (`{ provider, url }`) |
| GET | `/api/v1/auth/oauth/{provider}/login` | Chuyển hướng trực tiếp 302 sang trang đăng nhập của Provider | Path: `provider` | 302 Redirect Location Header |
| GET | `/api/v1/auth/oauth/google` | Callback Google OAuth2 | Query: `code` | 302 Redirect về frontend (`http://localhost:3000`), kèm Set-Cookie: `access-token`, `refresh-token` |
| GET | `/api/v1/auth/oauth/github` | Callback GitHub OAuth2 | Query: `code` | 302 Redirect về frontend (`http://localhost:3000`), kèm Set-Cookie: `access-token`, `refresh-token` |
| POST | `/api/v1/auth/oauth/{provider}` | SPA trao đổi mã ủy quyền (code exchange) trực tiếp | Path: `provider`<br>Body: `{ "code": "..." }` | 200 OK + `UserResponseDTO` kèm Set-Cookie: `access-token`, `refresh-token` |

### Flow hoạt động:
1. **Frontend / Browser**: Gọi `GET /api/v1/auth/oauth/{provider}/login` (hoặc lấy link từ `GET .../{provider}/url`) để người dùng ủy quyền qua Google/GitHub.
2. **Provider**: Chuyển hướng về Redirect URI đã cấu hình:
   - Google: `http://localhost:8080/api/v1/auth/oauth/google?code=...`
   - GitHub: `http://localhost:8080/api/v1/auth/oauth/github?code=...`
3. **Backend Callback**:
   - Trao đổi `code` lấy `access_token` từ Provider.
   - Lấy hồ sơ người dùng (`email`, `name`, `avatar`). Với GitHub nếu email ẩn, hệ thống tự động gọi API `/user/emails` để trích xuất primary verified email.
   - Tìm kiếm người dùng theo `email`:
     - Nếu đã tồn tại: kích hoạt tài khoản `ACTIVE` (nếu đang `PENDING`), cập nhật avatar (nếu trống).
     - Nếu chưa tồn tại: đăng ký người dùng mới với `ROLE_USER`, mật khẩu ngẫu nhiên an toàn, trạng thái `ACTIVE`.
   - Sinh bộ JWT token (`access-token`, `refresh-token`), đóng gói vào HttpOnly Cookie, chuyển hướng 302 về frontend (`http://localhost:3000`).

## 7. Roles & Permissions (Quản lý vai trò & quyền hạn)

> Yêu cầu xác thực: `@PreAuthorize("hasRole('ADMIN')")` cho toàn bộ endpoint.

### 7.1. Roles API

Base path: `/api/v1/roles`

| Method | Path | Purpose | Query / Request Body | Response `data` Object |
|---|---|---|---|---|
| GET | `/api/v1/roles` | Lấy danh sách vai trò | `?search=&all=false&page=0&size=10&sort=createdAt,desc` | `PageResponse<RoleResponseDTO>` (hoặc `List<RoleResponseDTO>` khi `all=true`) |
| GET | `/api/v1/roles/{id}` | Xem chi tiết vai trò kèm danh sách quyền | Path: `id` (UUID) | `RoleResponseDTO` |
| POST | `/api/v1/roles` | Tạo vai trò mới (tự chuẩn hóa tiền tố `ROLE_`) | `{ "code": "MANAGER", "name": "...", "description": "...", "permissionIds": [...] }` | `RoleResponseDTO` |
| PUT | `/api/v1/roles/{id}` | Cập nhật thông tin vai trò (chặn sửa code core role) | `{ "name": "...", "description": "..." }` | `RoleResponseDTO` |
| DELETE | `/api/v1/roles/{id}` | Xóa vai trò (chặn xóa ROLE_ADMIN, ROLE_USER và role có user) | Path: `id` (UUID) | `null` |
| PUT | `/api/v1/roles/{id}/permissions` | Gán / cập nhật lại toàn bộ quyền cho vai trò | `{ "permissionIds": ["...", "..."] }` | `RoleResponseDTO` |
| GET | `/api/v1/roles/{id}/permissions` | Lấy danh sách quyền hạn của vai trò | Path: `id` (UUID) | `List<PermissionResponseDTO>` |

### 7.2. Permissions API

Base path: `/api/v1/permissions`

| Method | Path | Purpose | Query / Request Body | Response `data` Object |
|---|---|---|---|---|
| GET | `/api/v1/permissions` | Lấy danh sách quyền hạn | `?search=&module=&all=false&page=0&size=20&sort=module,asc` | `PageResponse<PermissionResponseDTO>` (hoặc `List<PermissionResponseDTO>` khi `all=true`) |
| GET | `/api/v1/permissions/modules` | Lấy danh mục các phân hệ hiện có | None | `List<String>` |
| GET | `/api/v1/permissions/{id}` | Xem chi tiết quyền hạn | Path: `id` (UUID) | `PermissionResponseDTO` |
| POST | `/api/v1/permissions` | Tạo quyền hạn mới | `{ "code": "COURSE_CREATE", "name": "...", "module": "COURSE", "description": "..." }` | `PermissionResponseDTO` |
| PUT | `/api/v1/permissions/{id}` | Cập nhật thông tin quyền hạn | `{ "name": "...", "module": "COURSE", "description": "..." }` | `PermissionResponseDTO` |
| DELETE | `/api/v1/permissions/{id}` | Xóa quyền hạn (chặn xóa nếu quyền đang gán cho vai trò) | Path: `id` (UUID) | `null` |


## Socratic SSE protocol 2 (2026-11-02)

POST chat/socratic/stream accepts protocol_version (1 or 2), client_request_id (UUID) and optional expected_state_version. Spring derives student_id from the authenticated user. Protocol 1 remains the default for existing callers; the tutor UI sends 2. Each new explicit send gets a new request ID. Retry transport with the same payload/ID; automatic retry is not implemented by this change.

Forward event names and JSON unchanged, without buffering: session_init, status, token, content_replace, context_ref, step_update, diagram_ready, exercise_ready, done, error. Comments are heartbeats. Status contains stage/state/message and describes real tasks, never private chain-of-thought. The UI localizes stage labels. Tokens append provisional text; content_replace replaces the whole draft; done.full_content replaces text and confirms persistence. Error or EOF before done marks the draft incomplete, never successful. Unknown events are ignored; artifact rendering remains outside this change.


## Confirmed exercise step metadata (2026-11-02)

session_init/step_update/done and history messages can contain nullable step_progress: {step_id, exercise_id, number, total, instruction, completed}. Only this explicit metadata permits numbered step UI. Internal current_step_number is not display evidence. step_number_at_turn can be null. Missing metadata hides badges and the stepper, including old history; no frontend fallback total. Spring forwards metadata in historical DTOs and SSE pass-through.
