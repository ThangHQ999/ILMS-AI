# SSE — contract đề xuất

Socratic chưa được agent chạy thực tế. Giữ event session_init, step_update, context_ref, token, done, error. Protocol 1 giữ buffer/validate/commit trước khi chia đoạn token. Theo yêu cầu trải nghiệm stream của người dùng, protocol 2 phát status theo tác vụ thật và token ngay khi provider sinh; nội dung tạm thời cho đến done. Protocol 2 còn có content_replace, diagram_ready, exercise_ready.

## Envelope và thứ tự

Event mới có turn_id, sequence tăng trong lượt và payload. Event cũ cần mapping tương thích trước khi đổi shape. Hai trạng thái kết thúc của một stream là done hoặc error; không phát token sau trạng thái kết thúc.

```json
{
  "turn_id": "uuid",
  "sequence": 3,
  "stage": "connecting_concepts",
  "state": "running",
  "message": "Đang đối chiếu các khái niệm liên quan…"
}
```

Status stage dự kiến: understanding_request, retrieving_materials, connecting_concepts, evaluating_answer, preparing_explanation, generating_exercise, validating_exercise, generating_diagram. State: running/completed/failed.

Chỉ phát khi tác vụ thật diễn ra. Cache hit không giả vờ tìm kiếm; không phần trăm giả hoặc lộ suy luận nội bộ, đáp án hay expected_outcome. Backend dùng mẫu thông báo, không gọi LLM riêng để viết status.

## Nội dung và artifact

- session_init/step_update/done có `step_progress` nullable. Chỉ trả object khi state đang EXERCISE và step_id/exercise_id khớp một bước thật trong stored_exercise với thứ tự hợp lệ. Object gồm step_id, exercise_id, number, total, instruction, completed. Chat khái niệm, ôn nền, hoặc bài sinh chưa có bước rõ ràng trả null. Không dùng counter nội bộ mặc định 1 làm bằng chứng hiển thị.
- done.step_number_at_turn và cột message tương ứng là null khi không có bước được xác nhận. Lịch sử message trả step_progress từ turn_metadata.public; không suy lại từ phiên hiện tại. FE ẩn nhãn khi metadata thiếu, kể cả tin nhắn cũ có số bước không rõ nghĩa. Không backfill/đổi dữ liệu lịch sử.

- Token: delta phản hồi hiển thị, được tách khỏi status và khỏi lịch sử kỹ thuật.
- Protocol 2 token có content_status=DRAFT. FE nối delta ngay, không đợi done. Status hiển thị ở dòng riêng; chuyển sang trạng thái đang trả lời khi token đầu đến. Không gộp status thành nội dung hội thoại.
- content_replace (protocol 2): thay toàn bộ bong bóng hiện tại bằng full_content, không nối thêm. Dùng khi hậu kiểm điều chỉnh phần đã phát. Cần renderer hỗ trợ hoặc ít nhất thay bằng done.full_content khi hoàn tất.
- done: luôn lấy full_content làm nội dung cuối; content_status=FINAL chỉ sau commit thành công. Với replay chỉ có done, vẫn render được toàn bộ phản hồi.
- Context_ref: ID nguồn hợp lệ; danh sách nguồn không tự chứng minh mọi câu đều có căn cứ.
- Diagram_ready: artifact_id, loại/schema_version và payload đã kiểm tra cấu trúc; schema renderer cần chốt với FE.
- Exercise_ready: đề bài/mục tiêu/mức khó và nguồn gốc; không gửi lời giải nội bộ.
- Lỗi artifact có thể fallback văn bản; không báo đã kiểm tra nếu chưa có bước kiểm tra.

## Chậm, lỗi và retry

- Heartbeat chỉ giữ kết nối; không thay cho trạng thái tác vụ hoặc phép đo tốc độ.
- Fallback provider chỉ tự động trước token đầu tiên. Sau đó lỗi phải kết thúc rõ, không nối một câu trả lời mới vào nội dung cũ.
- Khóa retry chống tạo trùng message/evaluation/progress. Client reconnect tải kết quả đã hoàn tất; resume từng token chưa thuộc gói đầu.
- Câu hỏi pending chỉ được xác nhận từ phản hồi đã lưu hoàn tất. Ngắt kết nối hủy phần chưa commit; nếu đã commit trước ngắt, client lấy lại bản lưu qua API. Không có worker nền bền vững.
- Protocol 2 có thể đã hiển thị chữ trước lỗi. error có partial_response, content_status=INCOMPLETE và assistant_message_id; FE giữ phần nháp kèm trạng thái thất bại, không ghi nhận hoàn tất. Nếu kết nối đóng mà chưa có done/error thì cũng đánh dấu chưa hoàn tất. Retry cùng request ID phải reset bong bóng nháp thay vì nối lượt mới vào phần cũ.
- Ngoại lệ có chủ đích: lượt gợi ý SINGLE_STEP không phát nháp provider trước khi GuidanceCheck duyệt mức tiết lộ. Trong lúc đợi vẫn có status/heartbeat; chỉ nội dung được chấp nhận mới phát token. Lượt giải thích thông thường giữ live stream. Không dùng content_replace như cách thu hồi lời giải đã lộ.
- Cái giá của live stream: nội dung tạm có thể xuất hiện trước khi hậu kiểm citation/câu hỏi xong. Không tuyên bố mọi chữ đã được xác minh trước khi hiển thị. Hậu kiểm thất bại không commit evaluation/progress; trạng thái đã hiển thị không phải bằng chứng hoàn thành lượt.
- Đo riêng status đầu, token nội dung đầu và tổng thời gian; status nhanh không chứng minh suy luận nhanh.
