# SQL ingestion và duyệt graph

Đã viết SQL theo thiết kế người dùng yêu cầu; chưa áp dụng hoặc kiểm chứng trên DB.

- 004 tạo material_versions, ingestion_jobs, knowledge_graph_drafts; version tài liệu, quyền nguồn ngoài, idempotency/lease/checkpoint/publication progress và review theo revision/hash. Job chọn draft thuộc đúng job qua FK ghép.
- 005 thêm materials.published_version_id và chunks.material_version_id, FK ghép bảo đảm đúng tài liệu; index mới hỗ trợ nhiều version nhưng khóa unique cũ còn giữ đến cutover.
- 006 backfill version 1 cho chunks cũ, giữ nguyên UUID chunk/topic links; hash và source snapshot chưa biết để NULL; không tự phê duyệt hoặc chọn bản xuất bản.
- 007 chốt NOT NULL và bỏ unique cũ chỉ khi code đã hỗ trợ version và dữ liệu kiểm tra hợp lệ. Code hiện chưa được đổi theo schema, không chạy toàn bộ ngay.

Đã đối chiếu tên bảng/cột/index từ migration BE, đọc ràng buộc và thứ tự phụ thuộc, kiểm tra tĩnh số bảng và trùng/độ dài constraint names. Không chạy SQL/app/test/DB/LLM, không chỉnh Flyway cũ hay tạo migration tự chạy trong BE. FK mới dùng RESTRICT để tránh vô tình mất lịch sử, có thể chặn các cascade xóa vật lý hiện có; giải thích trong guide.

Guide: `.docs/ingestion-database-migration.md`. CHECK và FK không thay thế kiểm tra quyền giáo viên, state transition, hash canonical JSON hoặc publication giữa ba kho. Legacy published_version_id cố ý còn NULL; cần quyết định review/publish trước khi bật version-filter cho chat.
