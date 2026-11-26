# Đưa schema ingestion vào migration BE

Người dùng yêu cầu sửa trực tiếp CREATE TABLE trong migration BE và không dùng ALTER. Đã hỏi về vòng FK của đề xuất ban đầu; người dùng chọn thêm material_publications. Quyền sửa migration gốc đến từ yêu cầu trực tiếp này, không suy ra từ quy tắc repo.

Đã thêm V20260922170941..44 tạo material_versions, ingestion_jobs, knowledge_graph_drafts, material_publications; thứ tự sau materials và trước material_chunks. FK ghép kiểm tra material/version/job/draft cùng nguồn. Không có FK ngược từ materials sang versions hoặc jobs sang drafts. Publication hiện tại dùng UNIQUE(material_id,is_current), NULL ở các row không hiện hành; một publication attempt mỗi job.

Đã sửa CREATE materials gom index vào bảng; CREATE chunks yêu cầu material_version_id và unique(version,index). Seed migration cũng được chỉnh trực tiếp để 12 chunk có version fixture hợp lệ; không đổi biểu thức ID/content/owner và không tự tạo approval/publication. Không in dữ liệu seed nhạy cảm.

Đã chuẩn bị staging, kiểm tra toàn bộ thứ tự CREATE/FK theo migration filename, không có ALTER/disabled FK checks trong DDL thay đổi, không trùng constraint, số trường seed khớp và 12 row giữ nguyên các biểu thức gốc. Áp dụng 11 file BE bằng script có approval và hash guard, đọc lại target khớp staging. Không chạy SQL/Flyway/app/test/Gradle/DB, không reset/repair checksum.

Đây là schema tạo mới, không tự nâng cấp DB đã áp dụng các migration bị sửa. Chưa cập nhật application Entity/ingestion/publisher/reader; không tuyên bố workflow đã chạy. Guide hiện hành ở .docs/ingestion-database-migration.md; đề xuất SQL 004-007 trước đó không dùng kết hợp bộ CREATE BE mới.
