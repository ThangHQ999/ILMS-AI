# GitHub Actions cho ILMS-AI

[Workflow](../.github/workflows/deploy.yml) dùng Python 3.12 để cài `requirements.txt`, kiểm tra cú pháp, chạy unit test và thử import `app.main` với cấu hình CI. Push vào `test` triển khai qua SSH và PM2 sau khi kiểm tra đạt. Nhánh `main` chạy kiểm tra khi push và hỗ trợ triển khai thủ công. Tùy chọn chạy thủ công cần file workflow có trên nhánh mặc định. [Tài liệu GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch)

Deploy chọn đúng commit đã kiểm tra, cài dependency vào môi trường Python riêng và khởi động `ilms-ai` với `app.main:app`. Workflow kiểm tra `/health` trước khi lưu PM2 và phục hồi phiên bản trước nếu khởi động hoặc health check thất bại. Tài khoản SSH, đường dẫn và cổng được mô tả trong [README](../README.md).

## Kiểm tra dependency

Đã rà import của 122 file Python trong `app/`, `tests/` và các script gốc theo cú pháp Python 3.12. Các dependency trên đường chạy FastAPI và unit test hiện tại có trong `requirements.txt` hoặc được cài kèm. `pydantic` là dependency của FastAPI và `pydantic-settings`. Benchmark LightRAG cài thêm `requirements-lightrag-eval.txt`. Một số module cũ còn tham chiếu `src/`, `schemas` và Pinecone, nằm ngoài các router đang được nạp từ `app.main`.

## Xác minh

Đã parse YAML, kiểm tra điều kiện kích hoạt và luồng phụ thuộc job, kiểm tra cú pháp script SSH và launcher bằng Bash. Chưa chạy GitHub Actions, bộ unit test hay kết nối VPS trong đợt này.
