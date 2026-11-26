# Kế hoạch ingestion chi tiết

Ngày: 2026-11-02. Phạm vi: tài liệu thiết kế, không triển khai runtime.

## Đầu ra

- `.docs/ingestion-implementation-plan.md`: hiện trạng, kiến trúc đích, MySQL/Neo4j/Chroma/object storage, Topic–Chunk n–n, DTO/API, từng stage nghiệp vụ, review/hash, publication/recovery, sửa reader chat và các gói triển khai P0–P8.
- `.docs/ingestion.env.example`: giới hạn file/parse/chunk/token, concurrency/lease/retry, model, opt-in nguồn ngoài, ngân sách, publication gate và artifacts. Đây là key đề xuất chưa có Settings đọc.
- TASK và decisions cập nhật trạng thái cùng yêu cầu người dùng vừa xác nhận.

## Những điểm cần duyệt khi triển khai

BE sở hữu mutation workflow MySQL; worker lấy lease qua API nội bộ. Graph có KnowledgeEntityRevision theo publication. Vector record ID ghép publication/định danh, đọc UUID chunk từ metadata. Topic/mapping canonical theo manifest publication để không ghi đè dữ liệu khi chạy lại cùng version. Các lựa chọn này chưa được coi là người dùng đã duyệt code.

## Kiểm tra và giới hạn

Đọc lại AGENTS/TASK/ARCHITECTURE/decisions/workflow và schema guide; đối chiếu pipeline, extraction schema, graph reader, retrieval service và dependency Kafka của BE. Đã review tĩnh cấu trúc tài liệu và các key cấu hình; chưa chạy ứng dụng/test/build/DB/Flyway/seed/LLM hoặc sửa BE/FE/.env thật. Không xác nhận năng lực parser/OCR/provider hay chất lượng ingestion bằng tài liệu kế hoạch.
