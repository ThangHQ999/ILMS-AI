# Kế hoạch triển khai Socratic Chat

Trạng thái hiện tại: người dùng đã yêu cầu triển khai; code bản đầu đã được viết theo các gói, chưa chạy thực tế. Xem [báo cáo triển khai](../.reports/2026-11-01-socratic-v2-implementation.md) và [hướng dẫn vận hành](socratic-operator-guide.md). Các mục dưới giữ vai trò lộ trình thiết kế.

Bản triển khai đầy đủ: [Socratic Chat Socratic — blueprint](socratic-chat-implementation-blueprint.md). File này giữ lộ trình tóm tắt; blueprint mô tả thuật toán, chữ ký code, failure path và các gói nhỏ.

## Mục tiêu và phạm vi

AI giải thích đúng trọng tâm, giữ ngữ cảnh, kiểm tra mức độ hiểu bằng bằng chứng và điều chỉnh hỗ trợ. Ưu tiên CONCEPT; EXERCISE và REVIEW dùng chung state/policy. Không làm lại toàn bộ ingestion, UI quản trị hay bảo mật Gateway trong gói chat này.

## P0 — Khóa contract và đường chuyển đổi

- Đối chiếu DDL thực với ba bảng SQL nháp đã cung cấp; thống nhất UUID binary, canonical code và ID node.
- Chốt quyền sở hữu state mới; định nghĩa tương thích các cột session cũ và heatmap cũ.
- Chốt khóa lượt yêu cầu, trạng thái lượt và chống ghi lặp. Ba bảng mới chưa tự giải quyết đầy đủ idempotency của message/stream; cần chốt vị trí lưu turn_id trước khi code.
- Chốt contract đọc rubric và artifact; không triển khai workflow duyệt.
- Kết quả: schema/migration đề xuất, mapping cũ/mới, request/SSE/JSON cụ thể. Không áp dụng DB.

## P1 — Tầng dữ liệu

- Thêm model/repository Topic, topic_chunks và ba bảng mới.
- Dự kiến sửa app/model/mysql/, app/repository/mysql/, app/api/deps.py và schema chat.
- State là nguồn chính sau chuyển đổi; tạo state từ session cũ có quy tắc rõ, không mất tiến độ.
- Evaluation lưu snapshot tiêu chí, bằng chứng, nguồn, mức gợi ý, model/prompt version.
- Kết quả: data layer và đường chuyển đổi có thể review; chưa kết luận DB hoạt động.

## P2 — Ngữ cảnh và truy hồi

- Tách TopicContextService/ RetrievalService từ service chính.
- Tìm entity bằng mã, alias và vector; suy Topic qua topic_chunks. Giữ nhiều ứng viên khi mơ hồ.
- Tìm trong Topic trước, mở rộng môn khi thiếu; không lọc Topic sau một top-k toàn kho quá nhỏ.
- Hai collection chunk/entity; không fallback embedding qua không gian khác.
- Cache theo scope, teacher, concept, phiên bản/model; TTL/version invalidation có cấu hình.
- Kết quả: nguồn có ID và điểm xếp hạng; không tự chọn concept đầu tiên hay Topic chỉ từ tên.

## P3 — Đánh giá và trạng thái

- Lưu câu hỏi đang chờ; chỉ chấm khi có attempt phù hợp.
- Rubric nguồn nếu có, tiêu chí tạm nếu thiếu; kiểm tra bằng chứng rồi trả verdict có cấu trúc.
- Chính sách Python quyết định hỗ trợ/tiến mục tiêu; không để LLM trực tiếp cộng điểm.
- Chống state cũ ghi đè bằng version và thứ tự lượt; định nghĩa hành vi request đồng thời.
- Kết quả: PARTIAL/UNCLEAR/NOT_AN_ATTEMPT không bị gộp thành sai; chuyển concept xóa state không còn hợp lệ.

## P4 — Phản hồi và SSE

- Tách PromptBuilder, sửa prompt nền và chiến thuật theo tutoring-policy.md.
- Dùng nguồn có nhãn; giới hạn context theo nhiệm vụ, giữ summary và các lượt cần thiết.
- Thêm status theo tác vụ, giữ event cũ bằng mapping tương thích.
- Stream nội dung sau đánh giá; fallback chỉ trước token đầu tiên; lỗi có turn_id và trạng thái kết thúc rõ.
- Kết quả: không nối hai câu trả lời provider, không lộ expected_outcome qua status.

## P5 — Cá nhân hóa và ôn nền

- Ghi evaluation và cập nhật progress có transaction/idempotency.
- Điểm chưa đủ bằng chứng là NULL; tách mức hỗ trợ và các mục tiêu chưa kiểm tra.
- Ngộ nhận có mã, nguồn phát hiện/khắc phục; không đóng mọi lỗi vì xong một Process.
- Backtrack dựa thiếu hụt cụ thể, giới hạn stack, quay đúng câu hỏi dang dở.
- Kết quả: heatmap không ghi điểm độc lập; retry không tăng assessment_count hai lần.

## P6 — ExerciseStep và artifact

- Đọc ExerciseStep đúng schema DB thực, ưu tiên bài đã có.
- Sinh bài tạm theo concept/mục tiêu khi cần; kiểm tra dữ kiện/đáp án nội bộ, không tự nhập kho chuẩn.
- Tạo sơ đồ 2D theo contract FE, validate trước phát; fallback văn bản nếu lỗi. 3D để sau.
- Kết quả: artifact hoàn chỉnh, nguồn gốc rõ; không làm lộ lời giải bài đang học.

## P7 — Bàn giao để người dùng chạy

- Cung cấp file cấu hình mẫu không chứa secret, hướng dẫn migration/seed theo đúng phạm vi được duyệt và checklist nghiệm thu.
- Ghi rõ chưa chạy app/test/DB; không biến checklist thành kết quả pass.
- Các tình huống: định nghĩa mới; câu trả lời cụt; đúng một phần; xin trợ giúp; đổi concept cùng Topic; đổi Topic; ôn nền/quay lại; nguồn thiếu/mâu thuẫn; AI bị phản biện đúng; retry; stream ngắt; artifact lỗi.
- Người dùng đo thời gian truy hồi, đánh giá, token nội dung đầu tiên và hoàn tất; theo dõi cả lượt thường và chậm, số call/token. Chưa cam kết SLA.

## Điều kiện hoàn thành một gói

Phạm vi đã được duyệt, thay đổi có thể review, contract/tài liệu cập nhật, giới hạn nêu rõ và kịch bản tự kiểm tra được giao. Kết luận chạy thực tế chỉ được bổ sung khi có kết quả người dùng cung cấp hoặc yêu cầu kiểm thử mới.
