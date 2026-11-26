# Hiển thị bước học theo metadata backend

Người dùng báo FE luôn hiện Bước 1/2/3 trong hội thoại khái niệm. Đã xác định counter state mặc định 1 được dùng như số bước hiển thị; FE còn fallback totalSteps=3 và thanh grid ba cột.

## Sửa tại AI

- Thêm StepProgress và LearningStateService.step_progress: chỉ tạo metadata khi mode EXERCISE, exercise_id và step_id khớp stored exercise với danh sách step có ID duy nhất và thứ tự 1..N hợp lệ. Thiếu/không hợp lệ trả None, không đoán.
- session_init/step_update/done cung cấp step_progress nullable, chứa định danh, số bước, tổng thật, instruction và completed. Chat CONCEPT/REVIEW hoặc bài sinh chưa có ordered steps không có numbered progress.
- Public step_number_at_turn và giá trị lưu message nullable khi không có bước thực. Thêm property đọc step_progress từ turn_metadata.public cho history API; không thêm cột hay migration, không backfill số bước cũ không rõ nghĩa.

## Sửa tại Spring Boot và FE

- Spring DTO lịch sử giữ step_progress thay vì bỏ qua metadata mới. SSE đã pass-through nên không cần đổi relay.
- FE schema/types/hook nhận metadata, dùng cùng quy tắc cho live done và history. Không đóng dấu current_step_number từ session_init lên message mới vì event đó mô tả trạng thái đầu lượt.
- Badge chỉ dùng per-message step_progress; thiếu metadata thì ẩn dù step_number_at_turn cũ là 1.
- Stepper chỉ hiện khi có định danh và tổng hợp lệ, không fallback 3. Các thanh dùng flex theo số bước thật, không hardcode ba cột.
- Khi done trả null thì xóa tiến trình cũ. Status animation và nội dung stream giữ nguyên.

## Kiểm chứng và giới hạn

Đã parse cú pháp 97 file Python, parse 6 file TS/TSX bằng Babel parser sẵn có của Next; đọc luồng contract và xác nhận 13 file BE/FE đã áp dụng khớp staging. Ghi ngoài workspace qua permission được chấp thuận và kiểm tra hash bản gốc để không ghi đè thay đổi mới.

Không chạy app/tests/DB/LLM/Java compile/typecheck/build theo yêu cầu hiện hành. Chưa nghiệm thu thị giác/runtime. Các tin nhắn cũ không có metadata sẽ ẩn bước; không suy đoán bước lịch sử từ session hiện tại. Bài tự sinh không có ordered steps sẽ không có stepper cho đến khi backend có dữ liệu bước thật.

Người dùng cần khởi động lại Python, Spring Boot và FE, kiểm tra: hội thoại khái niệm không có badge/card; bài có ExerciseStep hiện đúng tổng thực; quay về concept xóa card; reload giữ đúng badge ở các message có metadata mới.
