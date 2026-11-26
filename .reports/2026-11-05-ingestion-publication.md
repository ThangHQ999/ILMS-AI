# Ingestion text và xuất bản học liệu

Ngày 2026-11-05. Triển khai dựa trên .docs/ingestion-text-publication-plan.md.

## Đường chạy

- FE /materials tải tài liệu qua Spring Boot, liệt kê 50 job gần nhất mà tài khoản có quyền, mở nháp đã lưu và tự lưu JSON sau 800 ms. Server kiểm tra baseRevisionId và baseHash. FE chỉ báo đã lưu sau ACK, giữ nội dung cục bộ nếu có xung đột.
- Review APPROVED tạo publication PREPARING và chuyển job PUBLISHING trong một transaction. Worker Spring Boot gọi FastAPI qua khóa nội bộ. Job đã duyệt lưu chính xác ID revision. Retry publication dùng lại ID cũ.
- app/service/ingestion/publication/records.py kiểm tra và dựng graph/records. service.py ghi Neo4j, upsert các vector còn thiếu ở Chroma, sau đó chuyển con trỏ MySQL và cập nhật topics/topic_chunks trong một transaction. Khi bước ngoài MySQL lỗi, current cũ vẫn giữ. Draft sai cấu trúc phát hiện trước khi ghi index thì đưa về sửa.
- Neo4j dùng nhãn IngestedKnowledge với node_kind và publication_id. Cạnh INGESTED_RELATION mang loại cạnh. Đường này tách graph ingestion đang chuẩn bị khỏi các repository graph cũ. MySQL vẫn dùng schema BE hiện hành.
- Chroma dùng collection riêng ilms-publications-1, ghi chunk/entity/topic theo batch. Cấu hình tại mẫu ingestion.env.example. Reader và writer khóa cùng provider/model/dimension. Muốn đổi embedding identity cần collection tên mới và tái tạo index.
- Chat lấy danh sách publication hiện hành từ MySQL dựa trên học liệu và quyền người dùng. Học liệu TEACHER được kiểm qua chủ sở hữu hoặc lớp có môn tương ứng và thành viên ACTIVE. teacher_id chỉ thu hẹp phạm vi. Neo4j và Chroma chỉ nhận danh sách publication đã lọc. Định danh cũ riêng ngoài ingestion vẫn theo luồng legacy.
- Expert chia lô, nhận claim lân cận để tìm cha. Bước không đánh số có thể lấy thứ tự nguồn nếu toàn bộ các bước cùng cha đều không đánh số. Quan hệ ngữ nghĩa dùng allowlist. Bốn agent tái dùng một đường gọi và cache prompt.

## Phạm vi còn giới hạn

- UI sửa JSON và xem bằng chứng. Chưa có trình sửa đồ thị trực quan. Danh sách job giới hạn 50 mục. Trang truy cập qua /materials.
- Gom topic dùng khóa chuẩn hóa theo owner/scope, subject, tên và tập mã khái niệm. Topic diễn đạt khác tên và khái niệm legacy chưa tự hợp nhất theo ngữ nghĩa. Canonical code mới có namespace riêng. Quan hệ cha cách xa ngữ cảnh lân cận vẫn có thể cần giảng viên sửa.
- Argument giữ đoạn bằng chứng. Các trường hypothesis và conclusion chỉ được xuất bản khi có trong draft. Workflow upload hiện hành vẫn text-only và dùng source policy mặc định DOCUMENT_ONLY.
- Schema Flyway hiện hành phải có material_versions, ingestion_jobs, knowledge_graph_drafts, material_publications và material_chunks.material_version_id. Fixture cũ chưa xuất bản sẽ không xuất hiện trong truy xuất chunk; cần đưa qua quy trình duyệt/xuất bản có chủ đích.
- Chưa triển khai upload replay idempotency từ FE, bổ sung nguồn ngoài và dọn publication lịch sử. Chưa chạy ứng dụng, API, DB, LLM hoặc migration. Đã kiểm tra AST 110 file Python và cú pháp 3 file TypeScript. Chưa build Spring Boot hoặc typecheck toàn FE.

## Kiểm tra thủ công

1. Mở /materials bằng tài khoản giảng viên có quyền quản lý khóa học. Upload một tài liệu text và chờ AWAITING_REVIEW.
2. Mở cùng job trên hai thiết bị. Sửa và lưu máy A, sau đó sửa bản cũ ở máy B để xác minh 409. Kiểm tra mở lại thấy revision mới nhất.
3. Trước khi duyệt, chat thử với khái niệm đặc trưng của file để kiểm tra không có nguồn nháp. Duyệt revision và chờ COMPLETED.
4. Kiểm tra material_publications PUBLISHED/is_current=1, topics/topic_chunks có mapping, Neo4j có graph đúng publication_id, Chroma có cả ba kind. Kiểm tra chat với tài khoản trong lớp và ngoài lớp.
5. Mô phỏng lỗi index trên môi trường kiểm tra. Job publish phải báo lỗi, bản hiện hành vẫn giữ. Khôi phục index và retry để kiểm tra không tạo vector hoặc node trùng.
