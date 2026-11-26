# Hướng dẫn agent — ILMS-AI

## Đọc trước khi làm

1. Đọc `TASK.md` để biết việc đang làm và phạm vi đã được cho phép.
2. Đọc `ARCHITECTURE.md` để phân biệt kiến trúc hiện tại và thiết kế đích.
3. Đọc `.docs/decisions.md`, rồi tài liệu liên quan trong `.docs/`.
4. Dùng `.agents/workflows.md` cho quy trình thực hiện và bàn giao.

Chỉ dẫn trực tiếp mới nhất của người dùng được ưu tiên. Nếu quyết định mới thay thế quyết định cũ, cập nhật tài liệu và ghi lý do; không âm thầm thay đổi lịch sử.

## Phạm vi và quyền thực hiện

- Người dùng đã yêu cầu hợp nhất thành một luồng Socratic duy nhất dựa trên bản cải tiến; được xóa service cũ, chuẩn hóa tên code/prompt/config. Không tự áp dụng DB hay chạy thử.
- Thiết kế đã thống nhất không đồng nghĩa đã cho phép triển khai. Chỉ sửa code ứng dụng, prompt chạy thực tế hoặc tạo migration triển khai sau khi người dùng duyệt phạm vi triển khai.
- Người dùng tự chạy thử. Không khởi động ứng dụng, gọi DB/LLM, chạy migration, seed, test hoặc benchmark trừ khi được yêu cầu lại. Có thể đọc file, diff và kiểm tra tính nhất quán tài liệu.
- Không tự tạo commit, push hay triển khai khi chưa có yêu cầu.
- Không tự dùng sub-agent; chỉ dùng khi người dùng yêu cầu rõ.
- Bảo toàn thay đổi có sẵn. Không reset hay hoàn tất việc chuyển `src/` sang `app/` ngoài phạm vi được giao. Việc xóa service chat cũ đã được người dùng cho phép; không mở rộng sang module khác.
- Khi thiếu dữ kiện, hỏi câu hỏi cụ thể và tiếp tục phần độc lập; không biến giả định thành quyết định đã chốt.

## Quy tắc cho AI Chat

- Ưu tiên giải thích khái niệm, hỗ trợ đa môn và điều chỉnh độ sâu theo tương tác.
- Topic được ingestion sinh theo chunk. Chat tự nhận diện qua entity/chunk/topic_chunks; không yêu cầu FE biết trước Topic.
- Giải thích ngắn khi người học chưa biết; dùng câu hỏi để kiểm tra đúng mục tiêu. Không ép mọi yêu cầu thành bài kiểm tra.
- Hỗ trợ tăng dần, ví dụ tương tự và phản ví dụ; không giải hộ bài tập đang làm.
- Phân biệt đúng một phần, chưa rõ, xin hỗ trợ và trả lời sai. Không tăng số lần sai do lỗi hệ thống.
- Việc tạo/duyệt rubric thuộc ingestion/quản trị. Chat chỉ đọc dữ liệu được phép dùng; có thể lập tiêu chí tạm theo câu hỏi khi chưa có rubric.
- SSE status mô tả tác vụ thật, không hiển thị suy luận nội bộ, đáp án nội bộ hoặc tiến độ giả.
- Không tự thay đổi các chính sách trên chỉ bằng sửa prompt; cập nhật quyết định và contract trước.

## Dữ liệu và báo cáo

- Dùng canonical_code làm khóa nghiệp vụ liên hệ tri thức; không dùng ID nội bộ Neo4j.
- Không ghi nội dung `.env`, secret, credential hay dữ liệu cá nhân thực vào tài liệu/báo cáo.
- Chỉ báo đã hoạt động khi có bằng chứng kiểm chứng tương ứng. Đọc code không xác nhận DB thực tế hoặc chất lượng học tập.
- Khi bàn giao: nêu thay đổi, cách kiểm tra, phần chưa chạy, giới hạn và bước tiếp theo.
- Cập nhật `TASK.md` khi trạng thái thay đổi; `.reports/` lưu kết quả từng đợt. Báo cáo cũ không thay thế trạng thái hiện hành.
