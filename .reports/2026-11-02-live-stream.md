# Status tác vụ và phản hồi sinh dần

Người dùng yêu cầu trải nghiệm hiển thị như ChatGPT. Backend protocol 2 chuyển provider delta ngay qua callback on_delta của ResponseGenerator; không thêm luật lời chào. Giữ status tác vụ có thật, không hiển thị chain-of-thought hoặc kết luận chấm trước khi kiểm tra.

Content còn DRAFT cho đến commit. Sau hậu kiểm, nếu phản hồi giữ nguyên prefix thì nối phần câu hỏi do server chuẩn bị; nếu khác thì content_replace thay toàn bộ nháp. Không phát lại cả nội dung ở cuối gây lặp. done chứa FINAL/full_content sau transaction; replay cũng FINAL. Error chứa partial_response/INCOMPLETE; FE phải xử lý đóng stream chưa có done. Không commit evaluation/progress nếu generation/validation thất bại. Phản hồi live có thể đã hiển thị trước khi phát hiện lỗi citation; đây là giới hạn khác với buffer.

Protocol 1 giữ buffer như trước. Protocol 2 cần FE/Gateway giữ các event status/token/content_replace/done/error; repo không có package.json/tsx/vue/jsx để sửa UI. Không tuyên bố UI đã tích hợp.

Kiểm tra cú pháp tĩnh, đọc callback/emit/commit và call sites; không chạy tests/app/DB/LLM theo yêu cầu hiện hành. Hành vi realtime, disconnect, retry và tương thích Gateway cần người dùng chạy nghiệm thu.
