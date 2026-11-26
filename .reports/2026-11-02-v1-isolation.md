# Cách ly kiểm tra UUID V2 khỏi V1

Người dùng báo V1 dừng hoạt động sau khi thêm V2, POST stream HTTP 422. Qua đọc code, controller dùng chung gọi resolver users bắt buộc trước khi chọn luồng service. Đây là hồi quy do thay đổi mới, kể cả SOCRATIC_V2_ENABLED=false.

Đã sửa: chỉ resolve UUID và copy request khi cờ V2 bật. Khi cờ tắt, giữ nguyên request tới V1. Helper cho list/delete cũng trả nguyên student_id khi V1, không truy vấn users qua resolver mới. Endpoint vẫn await controller async. Không bỏ khóa ngoại DB và không thay schema. V2 giữ xử lý lỗi và đối chiếu UUID hiện tại.

protocol_version=1 chỉ là lựa chọn SSE; không có tác dụng chọn V1. DI chọn V1 khi SOCRATIC_V2_ENABLED=false. Không chỉnh .env của người dùng.

Kiểm tra tĩnh syntax và đường gọi, không chạy test/app/DB theo yêu cầu. Sửa này loại bỏ chặn 422 do resolver V2 trên V1; không phải xác nhận mọi phần của V1 đã chạy thành công. Các thay đổi chung trước đó như model ngộ nhận và LLM vẫn còn; nếu phát sinh lỗi khác cần traceback cụ thể.
