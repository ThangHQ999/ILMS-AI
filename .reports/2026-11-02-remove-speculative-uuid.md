# Gỡ thay đổi UUID không có căn cứ

Ảnh dữ liệu xác nhận UUID chuẩn; log startup xác nhận runtime chọn ilms nhưng .env là ilms_db. Resolver chuẩn/swap đã thêm trước khi có bằng chứng không giải quyết sai database, còn gây hồi quy HTTP 422 ở V1.

Đã gỡ file resolver, các import/call và helper ở controller/API. Stream chuyển nguyên request; list/delete/progress/turn result dùng nguyên student_id. Không thay đổi dữ liệu, khóa ngoại hay BinaryUUID. Giữ kiểm tra user và phân loại IntegrityError riêng trong coordinator V2; không lan sang V1. Giữ đường dẫn .env tuyệt đối và log database để chẩn đoán.

Kiểm tra môi trường agent không có MYSQL_DATABASE ở Process/User/Machine; không tìm thấy launch.json/compose/script khởi chạy trong repo. Không thể xác định nơi biến được đặt trong tiến trình backend của người dùng từ môi trường agent. Không tự đổi ưu tiên env/.env trên toàn ứng dụng hoặc hardcode database. Không thể tuyên bố đã khắc phục runtime khi chưa chạy lại đúng cấu hình.

Kiểm tra tĩnh syntax và tìm tham chiếu resolver còn sót; không chạy app/test/DB. Các report resolver trước đây giữ làm lịch sử, quyết định hiện hành ở TASK và data-contracts.
