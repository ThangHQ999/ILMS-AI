# Schema ingestion CREATE TABLE trong BE

Cập nhật 2026-11-02. Người dùng yêu cầu sửa trực tiếp migration gốc, không ALTER, và đã chọn thêm material_publications để loại bỏ vòng FK. Không dùng materials.published_version_id hoặc ingestion_jobs.selected_draft_id trong schema hiện hành.

## Migration hiện hành

Thư mục: C:/Users/Admin/OneDrive/Desktop/dang_ky_tin_chi/src/main/resources/db/migration/.

- V20260922170940__create_materials_table.sql: materials hiện hữu, index nằm trong CREATE TABLE.
- V20260922170941__create_material_versions_table.sql: phiên bản nguồn/parser, hash/snapshot/người tạo.
- V20260922170942__create_ingestion_jobs_table.sql: source policy, idempotency, checkpoint, lease và trạng thái các kho.
- V20260922170943__create_knowledge_graph_drafts_table.sql: graph revision, nguồn, validation và kết quả giảng viên duyệt.
- V20260922170944__create_material_publications_table.sql: liên kết chính xác material/version/job/draft và publication đang dùng.
- V20260922175725__create_material_chunks_table.sql: version bắt buộc, FK ghép đúng tài liệu và UNIQUE(version,chunk_index).

DDL trên chỉ dùng CREATE TABLE, không ALTER hoặc FOREIGN_KEY_CHECKS=0. topics/topic_chunks giữ nguyên. SQL 004-007 ở repo AI là đề xuất expand/backfill cũ, đã được thay thế; không dùng chung với bộ CREATE này.

## Publication và review

Một publication attempt mỗi job. is_current=1 chỉ dành cho PUBLISHED; các row lịch sử/PREPARING/FAILED dùng NULL. UNIQUE(material_id,is_current) chỉ cho một bản đang dùng trên mỗi tài liệu. FK ghép kiểm tra đúng material/version/job/draft, không tự chứng minh được quyền giáo viên hoặc trạng thái APPROVED.

Backend phải kiểm tra review và hash payload trước khi xuất bản. PREPARING không làm mất bản hiện hành. Sau khi các kho bắt buộc sẵn sàng, khóa row materials, đổi bản cũ thành SUPERSEDED/is_current=NULL và bản mới thành PUBLISHED/is_current=1 trong một transaction MySQL. Các kho Neo4j/Chroma phải lọc revision phù hợp; không có transaction chung ba kho.

Reader chọn material_publications với status=PUBLISHED và is_current=1, rồi nối version với chunks. Mỗi sửa graph tạo revision mới; không sửa nội dung đã duyệt tại chỗ. Nguồn ngoài mặc định DOCUMENT_ONLY; EXTERNAL_ALLOWED phải do giảng viên có quyền chọn, giữ provenance riêng.

## Seed, tương thích và kiểm chứng

Seed đã tạo version-1 fixture và gán version cho 12 chunk, giữ nguyên ID/nội dung và topic links. Không bịa hash/snapshot hoặc teacher approval/publication; dữ liệu fixture cần được kiểm tra trước khi bật reader mới.

Đây là schema tạo mới theo yêu cầu sửa migration lịch sử, không phải nâng cấp DB đã có checksum Flyway. Không reset, repair, drop hoặc chạy migration trong đợt này. Code Entity/ingestion/publisher/reader chưa được nâng cấp theo schema, SQL không tự làm workflow hoạt động. RESTRICT bảo vệ lịch sử và có thể chặn xóa vật lý material/course/user; cần archive/cleanup có chủ đích.

Đã kiểm tra tĩnh thứ tự CREATE/FK, tên constraint, số trường và nội dung biểu thức của 12 seed rows. Đã áp dụng 11 file BE qua quyền filesystem và đối chiếu target với staging. Chưa chạy Flyway/DB/app/test/compile/build. Report BE: reports/2026-11-02-ingestion-create-tables.md.
