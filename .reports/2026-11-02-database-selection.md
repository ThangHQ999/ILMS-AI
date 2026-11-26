# Database runtime không khớp database đã kiểm tra

Ảnh người dùng xác nhận UUID user tồn tại ở ilms_db với HEX đúng UUID.bytes. Traceback tiếp theo vẫn ghi ilms.socratic_chat_sessions. Chưa có bằng chứng lỗi chuyển đổi UUID; hiện cần sửa lựa chọn database của tiến trình chạy.

Settings đọc .env từ đường dẫn tuyệt đối theo root dự án, tránh phụ thuộc working directory. MySQL verify_connectivity log SELECT DATABASE() và so sánh với cấu hình. Không log URI/password. Biến môi trường tiến trình vẫn ưu tiên hơn .env theo cơ chế Settings; cần kiểm tra launcher hoặc đặt MYSQL_DATABASE=ilms_db khi khởi động.

Kiểm tra syntax tĩnh; không khởi động backend, gọi DB, chạy test hoặc dừng tiến trình của người dùng.

Log mới vẫn có ilms.socratic_chat_sessions, nhưng không thấy log ứng dụng INFO. Đã dùng uvicorn.error để hiển thị database thực tế/cấu hình/giá trị MYSQL_DATABASE trong .env và PID khi verify kết nối. Cảnh báo khi cấu hình runtime khác .env; không log credential. Chưa có SELECT DATABASE() từ tiến trình thực tế, không loại trừ trường hợp view/trigger tham chiếu chéo schema.
