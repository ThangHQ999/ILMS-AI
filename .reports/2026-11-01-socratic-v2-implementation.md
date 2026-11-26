# Socratic V2 — đợt triển khai đầu

## Quyền và phạm vi

Người dùng đã yêu cầu triển khai từng plan. Sau đó xác nhận ba bảng chưa tạo và sẽ tự áp dụng SQL. Không có yêu cầu chạy thử; agent không chạy ứng dụng/test/migration/seed hay gọi DB/LLM.

## Đã viết code

- P0/P1: migration ba bảng đầy đủ và ALTER message/ngộ nhận; ORM Topic/state/evaluation/progress; DTO nội bộ; nhận lượt, lease, fingerprint/replay, finalize transaction và projection sidebar cũ.
- P2: graph read adapter có scope/cạnh cấu hình; entity collection cosine; fixed embedding provider; seed explicit entity/chunk; Topic suy từ các chunk; cache theo scope và bộ nguồn giới hạn.
- P3: intent, rubric/tiêu chí tạm, evaluation có trích đoạn kiểm chứng, policy Python, state/return stack.
- P4: prompt V2 riêng; SSE progress/heartbeat/artifact, protocol cũ/mới; phản hồi buffered trước commit/phát; không fallback provider sau nội dung đầu.
- P5: evidence aggregation không gán numeric mastery, history tiêu chí, ngộ nhận có bằng chứng; endpoint progress để heatmap đổi nguồn đọc.
- P6: đọc Exercise/ExerciseStep; hỗ trợ câu hỏi phụ không tự hoàn thành bước; sinh bài ngắn có model review; concept_graph_2d nodes/edges với validator cấu trúc.
- P7: env mẫu và operator guide có thứ tự SQL/backfill, request mẫu, scenario tự kiểm tra và giới hạn.

## Giới hạn còn cần nghiệm thu/hoàn thiện

- Chưa xác nhận schema/cạnh/version thực. Tên cạnh có cấu hình, ExerciseStep lookup theo exercise_id. Rubric absent có nhánh fallback; không triển khai ingestion/admin workflow.
- Chưa có notification cache invalidation từ ingestion, chỉ TTL/bypass khi phản biện. Pending dùng snapshot lịch sử; thu hồi nội dung tức thì cần contract publication/revocation từ ingestion.
- Chưa có solver chuyên biệt hoặc xác nhận ý nghĩa sơ đồ bằng công cụ; model check không bảo đảm lời giải đúng.
- Summary là metadata ngắn của lượt, chưa là semantic summary hội thoại dài.
- Công thức mastery chưa chốt; numeric để NULL, chỉ thể hiện evidence. Chỉ tiêu chí được quan sát nhiều lần có thể đánh dấu demonstrated, không chứng nhận toàn concept/objective.
- Progress endpoint đã có, nhưng FE/Gateway và mapping heatmap cũ không ở repo này, chưa tự thay đổi nguồn ở hệ thống khác.
- Câu hỏi/nguồn được kiểm tra hình thức trước phát; không có lời hứa ngăn tuyệt đối mọi lỗi tri thức/hallucination.
- Disconnect hủy lượt chưa commit, không có background durable runner. Tiến trình SSE tức thời, nội dung chỉ chia đoạn sau validate/commit; không gọi đó là live provider-token stream.
- Số call phụ thuộc intent/question/artifact: một lượt có thể dùng intent + evaluation + question + response (4), thêm artifact/review khi yêu cầu. Chưa đạt mục tiêu tối ưu 1–2 call ở tất cả đường tiếp nối; không có benchmark.
- Không có pipeline chấm lại revision cho evaluation cũ; correction được phản hồi và chấm mới có kiểm soát, không tự cộng/trừ lại lịch sử.

## Kiểm tra đã làm

Parse AST tĩnh 101 file Python, không lỗi cú pháp tại thời điểm kiểm tra; không import/execute ứng dụng. Kiểm tra đường dẫn import local ở phần V2 không thiếu file. Rà tay fingerprint/replay, transaction, pending question, public/private và vòng đời stream. Static review không thay runtime/test.

## File vận hành

- migrations/001_socratic_v2_tables.sql: ba bảng tạo mới đã có lease.
- migrations/002_socratic_v2_turns.sql: nâng message/ngộ nhận, áp dụng một lần.
- migrations/003_upgrade_early_draft_state.sql: chỉ dành schema nháp cũ, người dùng hiện không cần.
- .docs/socratic-operator-guide.md và .docs/socratic.env.example.

V2 mặc định tắt tới khi người dùng tự áp dụng schema/backfill và bật cấu hình. Các cột mới của model legacy cũng yêu cầu 002 trước chạy code mới. Không thay đổi các file bị xóa/src và sửa đổi cũ của người dùng.
