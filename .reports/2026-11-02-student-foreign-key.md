# Sửa lỗi tạo phiên: khóa ngoại học sinh

Traceback do người dùng cung cấp cho thấy MySQL 1452 tại INSERT socratic_chat_sessions, constraint fk_socratic_chat_sessions_student. Không có users.id khớp student_id được bind bằng UUID bytes. Chưa truy cập DB để phân biệt ID không tồn tại, nhầm database hoặc khác quy ước lưu UUID.

Đã sửa TurnCoordinator: kiểm tra users trước khi tạo phiên; trả STUDENT_NOT_FOUND, recoverable=false nếu không có. Chỉ retry IntegrityError 1062 (duplicate key); 1452 được phân loại thành lỗi tham chiếu, không còn bị báo TURN_CONFLICT. Khóa ngoại vẫn xử lý trường hợp user bị xóa sau kiểm tra. SSE sử dụng recoverable của TurnError. Không tạo user giả, không đổi encoding UUID hay tắt constraint.

Người dùng cần gửi student_id thật từ hệ thống đăng nhập. Nếu ID đã có mà vẫn lỗi, đối chiếu đúng database và HEX(users.id) với UUID bỏ dấu gạch; BinaryUUID hiện dùng UUID.bytes, không byte-swap. Không tự đổi quy ước UUID trên dữ liệu hiện có.

Kiểm tra tĩnh cú pháp Python và đọc đường xử lý; không chạy app/test/DB/LLM theo yêu cầu hiện hành.
