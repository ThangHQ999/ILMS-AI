# Ingestion toàn văn

- API upload và runner chính dùng cùng pipeline. Extractor nhận toàn bộ text đã parse theo thứ tự block và locator nếu payload vừa INGESTION_EXTRACTION_WINDOW_TOKENS. Mặc định 32000 token payload. Đây là ngân sách ứng dụng, không phải giới hạn context của model.
- Khi payload quá lớn hoặc SDK báo giới hạn context/output, dùng cửa sổ nhỏ hơn. Các cửa sổ thành công vẫn góp claims nếu cửa sổ khác lỗi. Evidence lưu FULL_DOCUMENT hoặc WINDOWED cùng danh sách lỗi, giữ các chunk ID giao với quote đã kiểm chứng.
- Chunk semantic vẫn được tạo cho topic–chunk và truy xuất. Expert, Validator và Reviewer xử lý tiếp claims. Review, đồng bộ revision Neo4j và xuất bản tiếp tục dùng đường hiện hành.
- Tách logic lập payload, kiểm quote và gom kết quả khỏi bộ điều phối agent. Bỏ app/service/ingestion/chunker.py vì không có caller và import src.* đã cũ. Giữ benchmark LightRAG và single-pass để so sánh. Runner chính dùng cấu hình production mặc định.
- Đã kiểm tra AST 114 file Python và đối chiếu caller. Chưa chạy app, DB, LLM hoặc benchmark.

Kiểm tra thủ công bằng python run_ingestion.py "D:\TaiLieu\bai-hoc.pdf" --stop-after review. Đối chiếu 08-draft.json và các lỗi coverage. Sau đó kiểm thử từ /materials để theo dõi review và publication.
