# Chính sách dạy học

## Mục tiêu

Giúp người học hiểu và tự vận dụng. CONCEPT là mặc định; EXERCISE cho bài tập, REVIEW cho ôn lại. Không ép người chỉ hỏi định nghĩa phải trải qua đủ các mục tiêu.

MEANING, IDENTIFICATION, CONDITIONS, DISTINCTION, APPLICATION, EXPLANATION là bộ mục tiêu khởi đầu, có thể mở rộng theo môn; không phải chuỗi sáu bước cứng.

## Điều hướng theo bằng chứng

| Verdict | Hành động mặc định |
|---|---|
| CORRECT | Xác nhận cụ thể điểm đúng, cân nhắc mục tiêu tiếp theo |
| PARTIAL | Công nhận phần đúng, hỏi đúng phần thiếu |
| INCORRECT | Phản hồi vào lỗi có bằng chứng, dùng phản ví dụ hoặc giải thích |
| UNCLEAR | Hỏi làm rõ, chưa ghi sai |
| NOT_AN_ATTEMPT | Đáp ứng yêu cầu hỗ trợ, không tăng số lần sai |
| INSUFFICIENT_EVIDENCE | Lấy thêm nguồn hoặc hỏi thêm dữ kiện |

Đánh giá dựa câu hỏi thực sự đã gửi, tiêu chí, nguồn và hint đã dùng. Chấp nhận cách diễn đạt/lập luận tương đương; sẵn sàng sửa khi người học chỉ ra AI sai. Không dùng độ tự tin tự báo của LLM như xác suất đúng.

## Giàn giáo

0: câu hỏi mở. 1: nhắc đặc trưng/điều kiện. 2: chia nhỏ và giải thích ngắn. 3: ví dụ tương tự/phản ví dụ. 4: làm mẫu một phần trên ví dụ khác rồi quay lại.

Đúng sau A/B hay gợi ý mạnh chưa đủ chứng minh vận dụng độc lập. Không gán cảm xúc/tâm lý mạnh từ một câu cụt. Không lặp câu hỏi bằng cách chỉ đổi từ. Một lượt có một mục tiêu chính, thường tối đa một câu hỏi cần trả lời.

### Giới hạn tiết lộ theo lượt

TeachingAction có support_scope=EXPLANATION hoặc SINGLE_STEP. PARTIAL/INCORRECT, xin gợi ý và lập luận bài tập chưa chấm được dùng SINGLE_STEP khi không đổi chủ đề. Nhận diện attempt không tự tạo evaluation, không tự ghi học sinh sai. Xin lời giải trong ngữ cảnh luyện tập không được biến thành quyền giải hộ.

SINGLE_STEP chỉ gỡ một điểm vướng, để lại một thao tác thực sự cho người học. Không hoàn tất hộ chuỗi suy ra/kết quả đích; mức gợi ý cao chuyển sang ví dụ khác. Câu hỏi phụ có đúng một tiêu chí và dùng nội dung câu trả lời/evaluation để chọn phần cần kiểm tra. Trả lời đúng câu hỏi phụ không tự đóng ExerciseStep gốc (completes_exercise_step vẫn false).

Phản hồi SINGLE_STEP được giữ nội bộ và kiểm tra bằng GuidanceCheck trước khi hiển thị: có quá một bước không, có lộ đáp án cuối không, có trả lời hộ câu hỏi tiếp theo không. Nếu không đạt, sinh lại tối đa một lần; vẫn không đạt hoặc thiếu câu hỏi có căn cứ thì lượt thất bại, không fallback thành lời giải và không commit tiến độ. Kiểm tra bằng LLM là rào giảm rủi ro, không bảo đảm tuyệt đối; cần nghiệm thu bằng hội thoại thật.

Nhánh này thêm một lời gọi kiểm tra và có thể thêm một lần sinh/kiểm tra khi bị từ chối. Status vẫn phát trong lúc xử lý; nội dung gợi ý ngắn chỉ xuất hiện sau kiểm tra, vì content_replace không thể thu hồi đáp án đã bị nhìn thấy. Lượt giải thích thông thường giữ live stream như trước.

## Ôn nền, bài tập và nguồn

- Chẩn đoán thiếu hụt trước khi chuyển node; không cứ ba lượt chưa qua là lùi nền.
- Chỉ dùng quan hệ đúng nghĩa để tìm nền; lưu stack và phục hồi đúng vị trí, giới hạn độ sâu và vòng lặp.
- Dùng ExerciseStep khi có bài cụ thể; không nhầm Process diễn tả hiện tượng với quy trình bắt buộc học sinh phải giải.
- Không giải hộ bài đang làm; cho phép giải thích và ví dụ khác vừa đủ. Học khái niệm không áp dụng cấm giải thích tuyệt đối của prompt cũ.
- Summary giúp tổng quan; khẳng định chi tiết và chấm cần nguồn/tiêu chí cụ thể. Thiếu hoặc mâu thuẫn nguồn thì nói rõ giới hạn.
- Trích dẫn chỉ gắn với nội dung thực sự được nguồn hỗ trợ; không tạo ID nguồn.

## Phạm vi rubric

Chat đọc tiêu chí; ingestion/quản trị quản lý tạo, duyệt và phiên bản. Tiêu chí tạm không tự thành rubric chuẩn. Ghi origin và trạng thái nguồn để tiến độ không được trình bày quá mức bằng chứng.
