# Gói đầu ingestion: kiểm tra tiền xử lý cục bộ

Người dùng đã duyệt triển khai kế hoạch theo gói và yêu cầu file điền đường dẫn file để tự kiểm tra. Phạm vi gói đầu: nền tảng DTO/config và phần parse/chunk của P2, độc lập workflow BE P1; chưa nhận là hoàn tất P0/P1/P2 production.

## Thay đổi

- `run_ingestion.py`: FILE_PATH sửa trực tiếp hoặc nhận positional path/file URI; --stop-after snapshot/parse/chunk/check, --env-file, --output, --material-id, --version-id.
- `ingestion_contracts.py`: contracts nguồn, blocks, spans, chunks, facts/evidence, policy/status và integrity report. Các DTO job/review/publication production còn lại chưa triển khai.
- Config tiền xử lý riêng: không import settings chat hoặc yêu cầu DB/LLM credentials; đọc subset INGESTION_* có validation. Mẫu env phân biệt key hoạt động và đề xuất tương lai.
- Parser TXT/MD/code, PDF, DOCX, PPTX với giới hạn file/pages/slides/expanded archive/chars và locators; không dùng loader cũ có tuyên bố giữ cấu trúc hoàn hảo.
- Chunk theo token target, giữ nguyên ký tự nguồn và spans; ID xác định theo version/index/content hash, overlap trong block dài có giới hạn để tiến về trước.
- Integrity kiểm tra hash/token/UUID/version/index/spans/reconstruction/coverage; không chứng minh completeness của parser hoặc ngữ nghĩa.
- Artifact riêng mỗi run: snapshot, parsed/chunks/integrity JSON, chunks.txt, REPORT.md, status/events/error, config và hashes.
- Bổ sung dependency tiktoken; không cài hoặc chạy nó trong đợt này.

## Chưa triển khai / giới hạn

Không sửa pipeline bốn agent cũ, chat runtime, BE/FE hoặc DB. Chưa có claim/lease/checkpoint production, agent calls, outside sources, canonical/topic graph draft, teacher review, graph/vector publisher hoặc publication-aware retrieval. Không có HTTP endpoint nhận đường dẫn file tùy ý trên server; đây chỉ là CLI cục bộ.

OCR chưa có; bật option OCR bị từ chối. DOCX/PPTX/PDF có cảnh báo extraction limitations. Parser timeout/process isolation và chunking AST theo ngôn ngữ chưa có. Các key liên quan gói tương lai trong env sample chưa được runner dùng. Encoding tokenizer lần đầu có thể cần tải dữ liệu cache; không đồng nghĩa LLM call.

## Kiểm chứng

Chỉ review source và parse AST các file Python thay đổi; không import/chạy module ứng dụng, không test/build/server/DB/LLM/Flyway/seed. Người dùng tự chạy theo `.docs/ingestion-local-guide.md`; chưa xác nhận kết quả runtime hoặc chất lượng parser trên học liệu thật.
