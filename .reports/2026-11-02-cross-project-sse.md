# Tích hợp luồng SSE qua Spring Boot và Next.js

Người dùng yêu cầu đọc và sửa hai dự án đã thêm. Đã đọc AGENTS/TASKS/rules liên quan, giữ giới hạn không chạy thử từ cuộc trao đổi hiện hành. Không có git worktree khả dụng ở các thư mục ngoài, nên bảo toàn nội dung bằng hash thay vì reset/checkouts.

BE: thêm protocol_version (mặc định 1), client_request_id, expected_state_version và forced_action vào DTO. Không thay nguồn student_id xác thực. SseEmitter chuyển tiếp event/data/comment/id/retry, xử lý cancel trước khi subscribe và khi FE đóng kết nối. Lỗi upstream dùng ObjectMapper và ErrorCode, không nhét raw exception vào JSON.

FE: gửi protocol 2 với UUID request mới mỗi explicit send; parse status/content_replace; xử lý frame CRLF, dữ liệu nhiều dòng và UTF-8 qua ranh giới chunk; bỏ cơ chế biến stream đứt thành done giả. Cập nhật đúng assistant bubble; lời AI sinh tới đâu hiển thị tới đó; done thay toàn bộ nội dung, không nối lặp. Có nhãn incomplete khi stop/error/EOF. Trạng thái tác vụ dùng bản dịch vi/en trong bubble, không thêm một bubble typing trùng. Hủy stream khi đổi phiên; không để finally của lượt cũ xóa controller lượt mới.

Đã chuẩn bị bản sửa trong .reports/sse-integration, xin và nhận quyền filesystem để ghi hai thư mục ngoài workspace. Script kiểm tra hash toàn bộ bản gốc trước khi ghi. Đã áp dụng 17 file và đọc lại xác nhận target khớp staging. Không sửa config/env/dependency/migration.

Đã kiểm tra syntax 6 TS/TSX files bằng Babel parser có sẵn trong Next, JSON hợp lệ và stage keys ở cả hai ngôn ngữ. Attempt dùng TypeScript package API không khả dụng, đã đổi parser; không tuyên bố typecheck pass. Chưa compile Java/typecheck/lint/test/build hay chạy app/DB/LLM theo yêu cầu. Không triển khai automatic retry/resume hoặc artifact renderer trong đợt này.

Report tại hai repo: reports/2026-11-02-socratic-live-sse-integration.md. TASKS và docs/api-spec trong từng repo đã cập nhật. Bước tiếp theo: người dùng khởi động lại các service và nghiệm thu request protocol 2, status, live token, replacement và ngắt kết nối.
