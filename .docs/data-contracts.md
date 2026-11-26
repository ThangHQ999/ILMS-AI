# Contract dữ liệu — thiết kế

Chưa xác nhận schema DB thực. Người dùng cho biết ba bảng chưa tạo. Migration tạo mới 001 và ALTER 002 đã được viết trong migrations/ theo contract dưới đây, có thêm lease/message metadata; người dùng tự áp dụng, agent chưa chạy.

## Định danh

- MySQL UUID theo BinaryUUID hiện có; không tự đổi byte order.
- canonical_code là mã ổn định UPPER_SNAKE_CASE, dự kiến VARCHAR(128) ascii_bin ở ba bảng mới. Không sinh mã từ tên rồi mặc định đã tồn tại.
- ID Neo4j nghiệp vụ là property id hoặc canonical_code theo loại node; không dùng internal ID.
- Một lượt cần turn_id/idempotency key, thứ tự và trạng thái RUNNING/COMPLETED/FAILED. Chỗ lưu và tương thích request cũ còn mở trong P0.

## Ba bảng được người dùng chọn

| Bảng | Khóa và dữ liệu chính | Quy tắc |
|---|---|---|
| socratic_learning_state | PK/FK session_id; Topic, concept, mode, objective, pending_question_message_id, process/exercise/step ID, hint_level, failed_attempts, assessment_context, return_stack, summary, state_version | Một phiên một state; chuyển concept phải bỏ process/step cũ nếu không còn phù hợp |
| socratic_turn_evaluations | id; session/student_message/question_message; concept/objective; verdict; rubric ID/version/snapshot; criteria_results/evidence; hint_level; model/prompt version | Unique message+concept+objective cho kết quả chính thức ban đầu; chấm lại cần revision rõ |
| student_concept_progress | id; unique user+concept; mastery nullable; status; assessment_count; independent_success_count; objective_progress; last_evaluation; scoring/version/timestamps | Dữ liệu tổng hợp từ evaluation; không ghi tăng lặp khi retry |

Các JSON phải có schema được validate ở service. Null nghĩa chưa biết/không áp dụng; mảng rỗng không tự có nghĩa đã hoàn tất.

assessment_context dự kiến chứa schema_version, rubric reference/snapshot và nguồn. return_stack là danh sách frame: topic, concept, objective, câu hỏi, process/exercise/step và mức hỗ trợ để phục hồi.

evidence chứa trích đoạn trả lời và ID nguồn liên quan, không lưu suy luận nội bộ dài. objective_progress lưu trạng thái và số quan sát từng mục tiêu. Mastery không được gọi là xác suất đã hiệu chuẩn.

FK chỉ đảm bảo tồn tại: service kiểm tra message thuộc session và role phù hợp. Không có FK xuyên MySQL–Neo4j. Chốt chính sách xóa trước khi dùng CASCADE của SQL nháp.

## Nguồn ingestion cung cấp

- Topic: id/name/summary/concepts_included; topic_chunks liên kết nguồn. concepts_included phải thống nhất canonical code, trong khi schema extraction hiện mô tả tên entity.
- KnowledgeEntity: canonical_code/name/subject/description theo người dùng.
- Definition, Process, ProcessStep, Exercise, ExerciseStep, Example, Argument theo schema người dùng; tên cạnh phải xác nhận mẫu thực tế.
- ExerciseStep có instruction/expected_outcome/socratic_question/common_mistake, liên hệ exercise/process_step. Không đưa expected_outcome ra event cho FE.
- ConceptRubric/ConceptCriterion là mở rộng tùy ingestion. Chat đọc nguồn được phép sử dụng; origin và review status là hai thuộc tính khác nhau.
- Có thể dùng tiêu chí tạm theo câu hỏi khi thiếu rubric; lưu snapshot, không ghi thành tri thức chuẩn.

## Tiến độ và tương thích

Session cũ giữ metadata hội thoại, state mới quản lý học. Heatmap cũ chuyển sang đọc progress hoặc mapping đã chốt, không hai bộ tính điểm độc lập. Chưa có công thức mastery chính thức; chưa đủ dữ liệu giữ NULL.

Trạng thái rubric đã duyệt không có nghĩa từng đánh giá AI đã được người duyệt xác nhận. Không tự nâng mức xác nhận cho evaluation cũ khi rubric được duyệt sau.
# Bổ sung đã chốt: student_misconceptions (2026-11-01)

Cập nhật cuối 2026-11-02: ảnh dữ liệu xác nhận user lưu UUID bytes chuẩn, khớp BinaryUUID. Đã gỡ resolver tự đoán chuẩn/swap và kiểm tra user ở controller vì không có căn cứ dùng, làm thay đổi hành vi luồng cũ. Request giữ nguyên UUID; BinaryUUID thực hiện chuyển đổi tại ORM. Log runtime xác nhận kết nối ilms trong khi .env và dữ liệu người dùng ở ilms_db. Báo cáo request-uuid-resolution và session-list-regression trước đó là lịch sử, đã được thay thế bởi `.reports/2026-11-02-remove-speculative-uuid.md`.

Người dùng xác nhận đã có đủ bảng. Contract này thay thế đề xuất thêm `review_status` và giữ `is_resolved` trước đây.

- `id`: BINARY(16), khóa chính; `student_id`: BINARY(16), bắt buộc, FK users ON DELETE/UPDATE CASCADE.
- `session_id`: BINARY(16), nullable; FK phiên chat ON DELETE SET NULL, ON UPDATE CASCADE. Xóa phiên không xóa ký ức ngộ nhận.
- `canonical_code`: VARCHAR(128) ASCII/ascii_bin, bắt buộc, định danh khái niệm; `misconception_code`: cùng kiểu, nullable, định danh loại ngộ nhận.
- `misconception_summary`: TEXT bắt buộc; `evidence`: JSON nullable, chứa tham chiếu evaluation phát hiện/khắc phục.
- `misconception_status`: VARCHAR(24), NOT NULL DEFAULT SUSPECTED; CHECK giới hạn SUSPECTED/CONFIRMED/RESOLVED. Đây là mức xác nhận ngộ nhận, không phải duyệt nội dung bởi giáo viên.
- `created_at`, `updated_at`: DATETIME(6), NOT NULL; cập nhật thời gian theo DDL đã chốt.
- Index: student/concept/status/created_at; student/concept/misconception_code; session_id. Không UNIQUE theo loại ngộ nhận, cho phép tái xuất hiện sau khi đã giải quyết.

Socratic tạo SUSPECTED khi có bằng chứng sai hợp lệ, nâng CONFIRMED khi có evaluation khác củng cố, ghi RESOLVED khi đánh giá đúng đủ điều kiện hiện hành và chỉ rõ mã ngộ nhận được khắc phục. Bản ghi CONFIRMED không bị hạ xuống do thiếu evidence cũ. Nếu đã tồn tại nhiều bản ghi mở cùng mã, cập nhật bản mới nhất; tránh lỗi scalar khi truy vấn nhiều hàng. Bộ lọc `is_resolved` trong hàm phân trang repository là tham số tương thích, được ánh xạ sang status và không truy vấn cột cũ.

Chỉ TurnCoordinator cập nhật ngộ nhận theo evaluation và mã lỗi được phép; không còn nhánh đóng toàn bộ ngộ nhận khi hoàn thành quy trình của service cũ. JSON evidence không có FK: khi xóa session, evaluation có thể bị cascade nên tham chiếu lịch sử có thể không còn truy xuất được.

