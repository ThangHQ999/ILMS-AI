# Ingestion text theo cửa sổ

2026-11-05. Phạm vi kế hoạch tại .docs/ingestion-text-publication-plan.md.

## Đã sửa

- API nội bộ tạo draft sử dụng pipeline bốn agent với cấu hình model/temperature cho từng vai trò. Temperature = 1 dùng GPT-6 Luna và bỏ trường temperature. Validator mặc định temperature = 0 với GPT-4o mini.
- Extractor nhận các chunk theo cửa sổ lớn hơn, hợp nhất span chồng lặp trong cửa sổ và đo token của payload. Claim phải có quote khớp nguồn. Các chunk giao với bằng chứng được lưu thành liên kết topic dự kiến. Topic trong cùng tài liệu được gom theo tên chuẩn hóa.
- Giữ issue có nguồn khi Validator trả thiếu hoặc trùng ID. Kết quả giữ metadata khi một cửa sổ extraction thất bại. API trả usage theo model nếu provider cung cấp.
- PDF có trang không trích được chữ vẫn giữ text ở các trang khác và trả danh sách trang thiếu. File không có text trả NO_EXTRACTABLE_TEXT.
- Dùng `python run_ingestion.py "D:\duong-dan\file.pdf" --stop-after review --api-pipeline` để tự kiểm tra pipeline tạo nháp. CLI ghi artifact phục vụ kiểm tra. API giữ kết quả trong bộ nhớ và trả cho BE.

## Còn thiếu

- Expert vẫn gom claims cả tài liệu vào một lượt. Chưa có chia batch riêng cho Expert và chưa kiểm chứng file lớn.
- Chưa hỗ trợ hết cấu trúc quan hệ ngữ nghĩa/Argument, chưa resolve canonical codes và chưa gom topic liên tài liệu.
- Chưa nối tự lưu FE, publication Neo4j/Chroma, chuyển con trỏ MySQL hoặc gate chat. Spring Boot và FE chưa sửa trong đợt này. Luồng đang dừng ở draft.
- Chưa chạy app, DB, LLM, test hoặc benchmark. Đã đọc và parse AST để kiểm tra cú pháp Python.
