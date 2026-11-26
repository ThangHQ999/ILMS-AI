# Đối chiếu UUID đầu vào với khóa users

Người dùng yêu cầu backend tự chuyển đổi student_id thay vì yêu cầu client đổi payload.

Thêm user_identity_repo.resolve_student_key: chuẩn hóa UUID, truy vấn tham số hóa hai dạng bytes chuẩn và MySQL UUID_TO_BIN(uuid, 1). Chỉ chấp nhận đúng một khóa users.id. Chuyển khóa đã tìm thấy về biểu diễn nội bộ mà BinaryUUID bind lại đúng bytes. Không thay đổi BinaryUUID toàn cục vì session/message/chunk có quy ước riêng; không đổi dữ liệu hoặc tạo user.

Controller chuẩn hóa student_id cho cả V1/V2 trước khi tạo stream. Lấy lại lượt, đọc tiến độ, liệt kê/xóa phiên dùng cùng resolver. Danh sách phiên trả student_id theo request. Không có user hoặc có hai khóa ứng viên thì HTTP 422 trước khi mở SSE; không tự chọn một trong hai. Mỗi thao tác này thêm một truy vấn users. teacher_id và các ID khác không tự áp dụng swap theo student_id.

Giới hạn: các trường student_id đọc trực tiếp từ ORM trong API chi tiết/cập nhật phiên vẫn là biểu diễn khóa lưu trữ của BinaryUUID hiện hữu. Khi users lưu dạng swap, dùng ID đăng nhập làm nguồn định danh cho request, không lấy trường này làm ID đăng nhập. Việc thống nhất cách serialize toàn bộ UUID giữa các service cần contract chung; không tự đổi UUID của dữ liệu hiện có.

Kiểm tra: phân tích cú pháp tĩnh, đọc đường gọi async controller và route; không chạy ứng dụng/test/DB/LLM. Chưa xác nhận DB thật đang lưu UUID theo cách nào.
