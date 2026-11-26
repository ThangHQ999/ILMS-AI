# ILMS-AI

Chạy FastAPI từ thư mục gốc của repo.

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

`requirements.txt` dùng cho FastAPI và bộ unit test hiện tại. Khi chạy benchmark LightRAG, cài thêm `requirements-lightrag-eval.txt` theo [hướng dẫn benchmark](.docs/lightrag-comparison-plan.md).

## GitHub Actions và VPS

[Workflow](.github/workflows/deploy.yml) cài dependency, kiểm tra cú pháp, chạy unit test và thử import `app.main` khi có pull request hoặc push vào `main` hay `test`. Push vào `test` triển khai nếu kiểm tra đạt. Để triển khai thủ công, chọn **Run workflow** trên nhánh `main` hoặc `test` trong tab **Actions** sau khi file workflow có trên nhánh mặc định.

Khai báo ba GitHub Secrets trong repo ILMS-AI cùng tên với BE và FE gồm `VPS_HOST`, `VPS_USERNAME` và `SSH_PRIVATE_KEY`. Có thể thêm `VPS_SSH_FINGERPRINT` để xác minh host SSH.

| GitHub Actions variable | Mặc định |
| --- | --- |
| `ILMS_AI_DEPLOY_PATH` | `/var/www/ilms-ai/ILMS-AI` |
| `ILMS_AI_PYTHON` | `python3.12` |
| `ILMS_AI_PORT` | `8000` |

Trên VPS, đặt sẵn Git clone của ILMS-AI tại đường dẫn đã cấu hình. Tài khoản SSH cần đọc được remote `origin` và có Python với module `venv`, PM2 và `curl`. Workflow dùng tên PM2 `ilms-ai` cho tiến trình nó quản lý. Nếu VPS đã dùng tên đó cho lệnh khởi động khác, xử lý tên tiến trình cũ trước lần chạy workflow đầu tiên. Đặt cấu hình ứng dụng trong `.env` trên VPS theo [mẫu cấu hình](.docs/socratic.env.example). FastAPI lắng nghe trên loopback để Spring Boot cùng máy gọi qua `fastapi.base-url`.

Job deploy chuẩn bị môi trường Python riêng trước khi chuyển commit và khởi động lại tiến trình `ilms-ai`. Khi `/health` trả thành công, workflow lưu trạng thái PM2. Nếu khởi động hoặc kiểm tra sức khỏe thất bại, workflow phục hồi commit và môi trường Python trước đó của lần deploy đã được quản lý.
