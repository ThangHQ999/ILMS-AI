# Workflow làm việc

## Đọc và lập kế hoạch

1. Đọc AGENTS.md, TASK.md và quyết định hiện hành.
2. Kiểm tra Git và các file liên quan; không đọc secret để lập tài liệu.
3. Lần theo đường gọi thực tế. Phân biệt file được nối, file thử nghiệm và schema do người dùng cung cấp.
4. Mô tả vấn đề, hành vi mong muốn, nguồn trạng thái chính, contract thay đổi và giới hạn.
5. Hỏi thông tin còn thiếu; phần độc lập tiếp tục được làm.
6. Ghi kế hoạch cụ thể để người dùng duyệt. Không tự chuyển từ kế hoạch sang triển khai.

## Triển khai sau khi được duyệt

1. Ghi phạm vi và bằng chứng duyệt vào TASK.md.
2. Đọc lại file vì repo có thể đã thay đổi từ lần khảo sát.
3. Thay đổi theo gói nhỏ; bảo toàn API cũ bằng mapping rõ ràng nếu cần.
4. Ghi migration thành artifact nếu được phép; không tự áp dụng lên DB.
5. Không chạy thử theo yêu cầu hiện hành của người dùng. Review file/diff và cung cấp kịch bản tự kiểm tra.
6. Cập nhật kiến trúc/contract tương ứng, viết report và bàn giao giới hạn.

## Review Socratic Chat

- Câu trả lời ngắn có gắn đúng câu hỏi chờ không?
- Topic/concept có bị đổi chỉ vì một lượt truy hồi nhiễu không?
- Đánh giá có câu hỏi, tiêu chí, nguồn và mức hỗ trợ không?
- Xin hỗ trợ, chưa rõ và lỗi vận hành có bị tính là sai không?
- Ôn nền có trở về đúng mục tiêu không?
- Retry/stream lỗi có ghi trùng hoặc nhảy tiến độ không?
- Status có phản ánh tác vụ thật và tránh lộ tiêu chí/đáp án nội bộ không?
- Điểm tiến độ có truy vết tới evaluation và phân biệt chưa đánh giá không?

## Bàn giao

Nêu kết quả, file, cách kiểm tra đã làm, phần chưa kiểm tra, câu hỏi mở và bước tiếp theo. Chỉ ghi trạng thái được bằng chứng hỗ trợ.
