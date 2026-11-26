# Sửa hồi quy kiểm tra user trên API đọc

Thay đổi resolver UUID đã mở rộng kiểm tra tồn tại users sang GET sessions, khiến truy vấn trước đây có thể trả danh sách rỗng nay trả HTTP 422. Response Spring Boot người dùng gửi không chứa detail FastAPI nên chưa chứng minh đây là nguyên nhân duy nhất, nhưng kiểm tra này là thay đổi hành vi không cần thiết do agent thêm.

Resolver có require_existing=False cho danh sách phiên, progress, lấy lại lượt và xóa phiên. Nếu không tìm thấy hoặc có hai cách lưu cùng khớp, dùng khóa chuẩn ban đầu để repository trả kết quả như trước; không đoán chọn user khác. Một khóa duy nhất vẫn được chuyển đổi. Tạo chat giữ kiểm tra tồn tại user vì FK thật yêu cầu điều đó.

Đã đọc lại call sites và kiểm tra cú pháp tĩnh. Không chạy app/test/DB. Lỗi MySQL 1452 khi INSERT phiên và lỗi GET sessions phải được phân biệt; không tự kết luận Spring Boot thiếu query từ access log.
