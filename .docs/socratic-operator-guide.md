# Socratic — áp dụng và tự kiểm tra

Dự án chỉ có một SocraticChatService. Không còn cờ bật hoặc chọn phiên bản; mọi request dùng cùng luồng cải tiến. Chưa chạy app/test/DB/LLM theo yêu cầu người dùng. Không coi tài liệu này là kết quả pass.

Cấu hình chat dùng SOCRATIC_*; .env trong dự án đã được đổi tên key và giữ giá trị. Nếu launcher/container của bạn đặt các key phiên bản cũ, cần đổi tương ứng. Tên collection vật lý đang có dữ liệu giữ nguyên; không chạy seed/migration lại chỉ vì đổi tên code.

## 1. Trạng thái SQL hiện tại

Người dùng đã xác nhận có đủ bảng ngày 2026-11-01. Không chạy lại các script tạo bảng/ALTER dưới đây trên DB đã dùng DDL cuối. Agent chưa truy cập DB để kiểm chứng. `student_misconceptions` hiện dùng duy nhất `misconception_status`, không còn `is_resolved`/`review_status`; `session_id` nullable với ON DELETE SET NULL. Chi tiết ở [data-contracts.md](data-contracts.md).

Ba bảng đầy đủ nằm ở [001_socratic_v2_tables.sql](../migrations/001_socratic_v2_tables.sql). Đây là bản tạo mới, đã có lease vận hành, không cần chạy 003.

[002_socratic_v2_turns.sql](../migrations/002_socratic_v2_turns.sql) chỉ dành cho message schema cũ thiếu cột lượt chat. Bản hiện hành đã bỏ ALTER ngộ nhận lỗi thời. Nếu đã tạo message bằng DDL cuối, bỏ qua 002.

Chỉ dùng [003_upgrade_early_draft_state.sql](../migrations/003_upgrade_early_draft_state.sql) nếu đã tạo learning_state từ SQL nháp cũ chưa có lease. Không chạy cả 001-fresh và 003.

Yêu cầu bảng users/topics/material_chunks/session/message hiện có, kiểu FK BINARY(16) thống nhất. UUID theo uuid.UUID.bytes, không byte-swap. CREATE IF NOT EXISTS không nâng cấp schema có sẵn. Hãy kiểm tra version, DDL/cột/index thực trước áp dụng; migration không tự chạy ở startup.

State được tạo khi đọc session cũ. Câu hỏi cũ không được giả lập rubric hoặc chấm lại tự động. Learning state là nguồn chính; cột session được chiếu lại để sidebar đọc.

## 2. Cấu hình và vector

Tham khảo [socratic.env.example](socratic.env.example). Không ghi API key vào repo. Runtime cần Python >=3.11 và dependency hiện có. Model theo task có thể cấu hình, không cần dùng model extraction nặng cho mọi đánh giá.

Chọn collection chunk MỚI, cosine và embedding provider/model/dimension cố định. Không dùng mock embeddings. Chạy thủ công từ root repo nếu bạn muốn nạp chỉ mục:

```powershell
python -m app.seed_tutoring --target entities
python -m app.seed_tutoring --target chunks
```

Các lệnh có gọi DB/LLM và tốn chi phí embedding; agent chưa thực hiện. Seed chunk chỉ gắn identity lên collection rỗng, từ chối collection khác mô hình không rỗng. Seed không xóa vector cũ; thay đổi/xóa dữ liệu nguồn cần upsert/delete từ ingestion hoặc rebuild tên collection mới. Cache có TTL và theo scope; chưa có notification invalidation liên tiến trình từ ingestion.

## 3. Graph adapter

Đọc KnowledgeEntity trực tiếp; satellite theo cạnh cấu hình. Rubric chỉ đọc trạng thái nằm trong SOCRATIC_RUBRIC_STATUSES (mặc định ACTIVE/APPROVED). Không có rubric thì dùng tiêu chí tạm, không tạo node mới.

ExerciseStep được đọc theo property exercise_id và step_number, không đòi một tên cạnh step cụ thể. Node riêng giáo viên cần owner_id đúng giáo viên; owner_role không đủ xác định cá nhân. Thiếu scope không được mặc định công khai.

Nếu tên cạnh khác mặc định, cấu hình trong Settings. Không có UI/schema publication của ingestion trong gói chat. Không giả teacher-reviewed khi chỉ qua model review.

## 4. Gửi một lượt

Giữ route POST /api/v1/chat/socratic/stream và internal key như API cũ. Ví dụ payload (thay UUID theo dữ liệu thật):

```json
{
  "session_id": "11111111-1111-4111-8111-111111111111",
  "client_request_id": "22222222-2222-4222-8222-222222222222",
  "student_id": "33333333-3333-4333-8333-333333333333",
  "message": "Khóa ứng viên khác siêu khóa như thế nào?",
  "protocol_version": 2
}
```

FE không cần topic_id. Mỗi tin nhắn mới cấp request ID mới; retry giữ nguyên ID và nội dung/context. Backend có thể tạo session ID từ student/request nếu chưa gửi session_id. Khi retry lượt đầu vẫn giữ nguyên payload, không thêm session_id khác vào request cũ (fingerprint sẽ khác).

Protocol 1 giữ các event cũ, không phát status/artifact event mới; done vẫn có nội dung và artifacts. Protocol 2 thêm turn_id/sequence và status/diagram_ready/exercise_ready. FE cần renderer concept_graph_2d schema v1 (nodes/edges), label là plain text, không render HTML tùy ý.

Lấy lại kết quả: GET /api/v1/chat/socratic/turns/{session_id}/{turn_id}?student_id=...

Tiến độ cho heatmap: GET /api/v1/chat/socratic/progress/{student_id}. Nguồn mới là student_concept_progress; code không dual-write student_knowledge_heatmaps. Gateway/UI cần đổi nguồn đọc, mapping legacy chưa được tự áp dụng.

## 5. Streaming và độ trễ

Status được phát trong lúc tác vụ thật chạy; có heartbeat. Protocol 1 giữ buffer/kiểm tra/commit rồi phát đoạn token. Protocol 2 hiện chuyển delta ngay từ provider (DRAFT), có thể content_replace sau hậu kiểm; done.full_content là bản cuối sau commit. FE cần hiển thị status, nối token ngay, thay nội dung theo content_replace/done và đánh dấu INCOMPLETE khi error hoặc mất kết nối trước done. Không hiển thị suy luận nội bộ. Chi tiết ở [sse-contract.md](sse-contract.md).

Một session chỉ có một lượt đang xử lý. TURN_IN_PROGRESS/STALE_STATE yêu cầu đợi/lấy lại phiên. Disconnect hủy phần đang chạy nếu chưa commit; retry cùng ID. Nếu đã commit trước ngắt, endpoint kết quả trả bản hoàn tất. Không có worker nền tiếp tục bảo đảm sau khi ngắt.

## 6. Hành vi nghiệp vụ cần thử

1. Hỏi định nghĩa: giải thích trước, không ép kiểm tra.
2. Yêu cầu “kiểm tra em hiểu chưa”: nhận câu hỏi có tiêu chí; trả lời ngắn được gắn pending.
3. Đúng một phần: công nhận ý đúng, hỏi phần thiếu; xin hỗ trợ không tăng failed_attempts.
4. COMPARE hai concept: nguồn cả hai, không đổi Topic máy móc.
5. Phản biện AI: bypass cache, không ghi người học sai tự động.
6. Nhiều lần mắc ở cùng nền: chỉ backtrack qua cạnh REQUIRES/DEPENDS_ON có thật; return stack phục hồi câu cũ.
7. REQUEST_EXERCISE: bài có sẵn trước; nếu sinh mới thì private solution chỉ trong state, không nằm public artifact/message API.
8. REQUEST_DIAGRAM: event nodes/edges hoàn chỉnh; lỗi artifact fallback văn bản.
9. Retry cùng ID: một pair message, một evaluation mỗi mục tiêu, không tăng counter hai lần.
10. Hai tab cùng session: conflict rõ; hai session cùng concept không mất update.
11. LLM/Chroma/Neo4j lỗi: không biến lỗi thành đánh giá sai; không fallback embedding qua provider khác.
12. Kiểm tra DB: state pending text khớp câu hỏi cuối response; score numeric vẫn NULL, objective evidence được cập nhật.

## 7. Giới hạn cần theo dõi

- Chưa có kết quả runtime/performance/quality; syntax review không chứng minh SQL/SDK chạy được.
- Tự kiểm tra bài tập bằng LLM không phải chứng minh đáp án toán học; chưa có executor/solver chuyên biệt.
- Summary hiện là metadata tóm tắt mục tiêu/hành động, không phải tóm tắt ngữ nghĩa toàn bộ cuộc trò chuyện; history gần và pending giữ phần quan trọng.
- Công thức mastery numeric chưa chốt, không ghi số đoán. Mốc independent successes là cấu hình ban đầu, không chứng nhận thành thạo toàn concept.
- Rà soát rubric thuộc ingestion/admin. Không thêm node hoặc workflow duyệt từ chat.
- Xóa session hiện cascade evaluation; progress vẫn còn counters nhưng last_evaluation có thể null. Nếu cần bằng chứng dài hạn sau xóa hội thoại, phải đổi chính sách retention trước dùng production.
- API internal vẫn dựa Gateway về danh tính; gói này không làm lại phân quyền Gateway như người dùng đã giới hạn phạm vi.
