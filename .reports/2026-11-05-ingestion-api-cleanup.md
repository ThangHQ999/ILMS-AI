# Dọn luồng ingestion dùng API

- Bỏ run_ingestion.py, local_runner.py, hướng dẫn chạy cục bộ và chức năng ghi snapshot/debug chỉ dùng bởi runner đó.
- Bỏ app/ingest.py và smart_chunk_document.py của đường dual-track cũ. API vẫn dùng parser và semantic chunking hiện hành.
- Bỏ hai bản staging Java sau khi đối chiếu hash với file ở repo Spring Boot.
- Giữ compare_ingestion.py, single_pass_ingestion.py và dữ liệu benchmark để so sánh ngoài production.
- Đường nghiệm thu hiện tại là /materials hoặc các API Spring Boot trong .docs/material-ingestion-api.md.
- Đã parse AST 111 file Python và rà tham chiếu đến các module bị bỏ. Chưa chạy ứng dụng, LLM, DB hoặc benchmark.
