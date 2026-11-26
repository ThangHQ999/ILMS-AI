# Đồng bộ schema ngộ nhận cuối

Người dùng yêu cầu cập nhật dự án và xác nhận đã có đủ bảng. Không áp dụng SQL lên DB.

- ORM bỏ is_resolved/review_status; dùng misconception_status, canonical_code bắt buộc ASCII phân biệt hoa thường, session_id nullable/SET NULL, FK user, index và CHECK theo DDL cuối.
- Repository V1 và coordinator V2 đọc/ghi status mới. Giữ tham số phân trang is_resolved để tương thích, ánh xạ sang status.
- V2 chọn bản ghi mở mới nhất khi có nhiều hàng cùng loại ngộ nhận; giữ CONFIRMED và chỉ nâng trạng thái khi có bằng chứng từ evaluation khác.
- Sửa hướng dẫn vận hành, TASK, quyết định và contract; bỏ ALTER review_status lỗi thời trong script 002. DB đã dùng DDL cuối không cần chạy lại các script.

Kiểm tra bằng đọc code, tìm tham chiếu cột cũ và phân tích cú pháp tĩnh Python; không import ứng dụng, chạy test, app, DB, migration hoặc LLM. Chưa xác nhận hành vi runtime. Các thay đổi có sẵn trong working tree được giữ nguyên.
