# Hợp nhất service chat Socratic

Yêu cầu: xóa luồng chat cũ, giữ bản cải tiến và chuẩn hóa tên trong dự án AI. Phạm vi chỉ D:/ILMS-AI; không sửa BE/FE, không chạy app/test/DB/LLM/seed/migration.

## Thay đổi

- Xóa app/service/socratic_chat_service.py cũ. Đổi app/service/tutoring/v2_service.py thành chat_service.py, class SocraticChatService. DI chỉ tạo service này, không mở thêm dependency chỉ phục vụ router/grader cũ.
- Bỏ cờ chọn service và các gate trên API turn/progress; PATCH title bảo vệ trạng thái học ở mọi request.
- Xóa các method repository tạo phiên/ghi tin/đánh giá/ngộ nhận chỉ được service cũ gọi. TurnCoordinator là nơi ghi lượt, state, evaluation, progress và ngộ nhận. Bỏ schema/export SocraticChatSessionCreate không còn dùng.
- Đưa bốn prompt đang dùng về app/prompts/tutoring. Xóa base rules/router prompt cũ. Bốn file strategies bị Windows từ chối quyền Delete, vẫn tồn tại nhưng không còn code nào đọc.
- Đổi SOCRATIC_V2_* thành SOCRATIC_*; xóa cờ ENABLED và cấu hình legacy không còn dùng. .env chỉ đổi tên key/bỏ key cũ, giữ giá trị còn dùng và physical collection. Không log secrets. Không giữ alias chọn hai service.
- Đổi lệnh thành python -m app.seed_tutoring --target chunks|entities. Default entity collection có tên trung tính; .env giữ collection đang được chọn trước hợp nhất để không mất liên kết với vector hiện có.
- Đổi tên operator guide, env example và blueprint, cập nhật link/tài liệu hiện hành. Migration và báo cáo có ngày giữ định danh lịch sử; evaluator_version mới là socratic-evaluator-1, không sửa evaluation đã lưu.
- Route /api/v1 và protocol_version 1/2 giữ hợp đồng BE/FE. Protocol chỉ điều khiển dạng truyền SSE, không tạo hai luồng nghiệp vụ. Default Python là 2; client gửi 1 vẫn có một service với buffer transport.

## Kiểm tra

- AST parse 97 file Python: không lỗi cú pháp.
- Không còn import service cũ/module v2_service hoặc cờ SOCRATIC_V2_* trong runtime.
- Tất cả settings SOCRATIC_* được tham chiếu đều có khai báo; bốn file prompt đang dùng tồn tại.
- .env không còn key SOCRATIC_V2_* hoặc key chat trùng; không in giá trị.
- Link file trong tài liệu hiện hành không hỏng.
- Chưa import/khởi động app, chạy test, gọi DB/provider hoặc seed. Chưa xác nhận runtime/hiệu năng.

## Vướng quyền filesystem

Windows trả WinError 5 cho việc xóa các file dưới đây; thử qua exec có approval và apply_patch đều bị từ chối. Attributes không readonly, nhưng ACL có thể không cấp quyền Delete cho identity đang chạy. Không tự thay ACL/ownership hoặc xóa cả thư mục để vượt quyền.

- app/prompts/tutoring/strategies/cognitive_metaphor.md
- app/prompts/tutoring/strategies/feynman_protege.md
- app/prompts/tutoring/strategies/misconception_autopsy.md
- app/prompts/tutoring/strategies/socratic_dialectic.md

Luồng chạy đã hợp nhất. Việc dọn file trên còn cần quyền Delete của Windows; không ảnh hưởng lựa chọn service vì không còn tham chiếu tới chúng. Nếu launcher/container đặt các biến SOCRATIC_V2_* bên ngoài .env của repo, người vận hành cần đổi sang SOCRATIC_* tương ứng. Không đổi database hoặc index vật lý vì tên code đổi.
