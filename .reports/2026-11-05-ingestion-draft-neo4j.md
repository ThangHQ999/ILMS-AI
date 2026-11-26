# Đồ thị nháp Neo4j theo revision

- MySQL giữ bản lưu có thẩm quyền, hash, quyền, audit và con trỏ xuất bản. Mỗi bản tự lưu thành một revision bất biến. Worker đồng bộ các revision sang Neo4j qua checkpoint của ingestion_jobs. Neo4j lỗi thì checkpoint không tiến. Mở trình sửa sẽ đồng bộ đúng revision theo yêu cầu nếu worker chưa xử lý.
- Neo4j lưu IngestionGraphRevision, IngestionDraftNode, HAS_DRAFT_NODE và DRAFT_LINK. Node thuộc riêng graph_revision_id. Trạng thái trên root được đồng bộ từ MySQL dưới dạng DRAFT, PUBLISHED hoặc SUPERSEDED. Chat chỉ dùng graph publication và con trỏ MySQL. Bản xuất bản mang graph_revision_id để truy về revision đã duyệt.
- /materials đọc graph qua Spring Boot có kiểm tra quyền truy cập job. Giảng viên xem quan hệ, chọn nút để sửa trường văn bản, chuyển bài tập sang khái niệm khác và tự lưu như trước. Sửa nâng cao giữ editor JSON cho thao tác chưa có trong giao diện. Không ghi đè revision Neo4j trực tiếp từ trình duyệt.
- Dùng schema MySQL hiện hành. Các constraint mới của Neo4j nằm trong thiết lập startup. Không chạy migration, DB, app, test hoặc build trong đợt này. Đã kiểm tra AST 112 file Python và cú pháp ba file TypeScript.

## Kiểm tra thủ công

1. Upload tài liệu và mở job tại /materials. Chọn một nút, sửa text, đợi báo Đã lưu rồi mở lại trên thiết bị khác.
2. Chuyển một bài tập sang khái niệm khác. Chờ revision mới và kiểm tra đồ thị hiển thị cạnh mới. Neo4j vẫn giữ cạnh cũ trong revision trước.
3. Duyệt và chờ job COMPLETED. Kiểm tra root revision chuyển PUBLISHED sau đồng bộ và graph công khai cùng graph_revision_id. Trong khi chuẩn bị, chat vẫn chỉ đọc publication hiện hành.
4. Ngắt Neo4j trong môi trường kiểm tra. Lưu revision trên FE vẫn theo MySQL. Khôi phục Neo4j và mở lại graph để kiểm tra đồng bộ bù.
