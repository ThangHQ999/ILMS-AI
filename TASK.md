# Công việc hiện hành

Cập nhật 2026-11-26.

## Yêu cầu mới nhất

2026-11-26 — Thêm GitHub Actions cho ILMS-AI theo mô hình SSH và PM2 của BE/FE. Kiểm tra Python trước deploy, tự deploy nhánh `test` và hỗ trợ chạy thủ công từ `main` hoặc `test`. Xem [cấu hình VPS](README.md) và [báo cáo kiểm tra workflow](.reports/2026-11-26-ai-deploy-workflow.md).

2026-11-25 — Người dùng yêu cầu triển khai các phần FE, BE và AI của luồng đánh giá. Phần AI đã thêm API nội bộ chỉ đọc mã và nhãn khái niệm của các bản xuất bản hiện hành theo môn. Đã đạt 4 ca unit test SQLite và kiểm tra Spring Boot gọi router FastAPI với MariaDB cục bộ. Xem [.reports/2026-11-25-assessment-concept-catalog.md](.reports/2026-11-25-assessment-concept-catalog.md).

2026-11-08 — Người dùng duyệt triển khai API quản trị đồ thị trên BE và AI với ADMIN/USER và class_members OWNER/TEACHER/STUDENT. Đã thêm controller/DTO/service/repository phân quyền, sửa graph theo revision, review, publish lại cùng file, withdraw, retry, audit và migration knowledge_graph_events + permission. Tài liệu nối API tại .docs/knowledge-graph-api-guide.md. Đã kiểm tra cú pháp, chưa chạy app/DB/LLM/test/migration theo chỉ dẫn người dùng. Báo cáo .reports/2026-11-08-knowledge-graph-api.md.

Đã lập kế hoạch API quản trị đồ thị tri thức tại .docs/knowledge-graph-api-plan.md. Phân quyền, API/DTO, chỉnh sửa theo revision, xuất bản lại cùng file và audit đang chờ duyệt triển khai.

Đã dọn runner ingestion cục bộ và luồng dual-track cũ. Đường vận hành là FE /materials và API Spring Boot/FastAPI. Giữ benchmark riêng và dữ liệu lịch sử. Xem .reports/2026-11-05-ingestion-api-cleanup.md.

Đã chuyển đường upload và runner chính sang ưu tiên đưa toàn văn text cho Extractor. Cửa sổ chỉ dùng khi vượt ngân sách. Logic extraction riêng trong app/service/ingestion/extraction.py. Đã bỏ chunker cũ không có caller. Xem .reports/2026-11-05-ingestion-full-document.md. Chưa chạy runtime.

Đã thêm đồng bộ đồ thị nháp Neo4j theo revision và trình sửa trực quan tại /materials. MySQL giữ bản lưu có thẩm quyền và con trỏ xuất bản. Xem .reports/2026-11-05-ingestion-draft-neo4j.md. Chưa kiểm chứng runtime.

Đã nối code upload → draft → autosave FE → review → Neo4j/Chroma → publication MySQL → chat. FE tại /materials, chỉnh sửa dạng JSON. Các giới hạn và hướng dẫn nghiệm thu xem .reports/2026-11-05-ingestion-publication.md. Chưa kiểm chứng runtime.

Đã duyệt triển khai kế hoạch ingestion text → publication. Đã sửa phần AI tạo draft: extraction theo cửa sổ, model theo agent, warning PDF, provenance và runner kiểm tra cùng pipeline. Publisher, auto-save FE và publication gate vẫn đang thiếu. Xem .reports/2026-11-05-ingestion-text-draft.md.

Đã lập kế hoạch ingestion text-only, bốn agent kiểm tra nối tiếp, tự gom topic, tự lưu draft qua nhiều thiết bị và chỉ cho chat đọc publication hiện hành. Xem .docs/ingestion-text-publication-plan.md. Đây là thiết kế chờ duyệt triển khai, chưa sửa ứng dụng hoặc migration.

Đã thêm runner thử nghiệm LightRAG SDK riêng để so bốn agent, LightRAG native và LightRAG gợi ý cho Expert. Plan và cách chạy tại `.docs/lightrag-comparison-plan.md`. Chưa chạy SDK/API LLM, không nối nhánh thử nghiệm vào upload.

API ingestion đã nối Spring Boot upload học liệu với FastAPI xử lý trong bộ nhớ. Worker lưu materials/version/job/chunks và draft revision vào MySQL; API hỗ trợ mở lại, sửa, duyệt và retry. Đường API bỏ artifact theo stage và chạy Extractor song song có giới hạn. Hướng dẫn `.docs/material-ingestion-api.md`. Publication Neo4j/Topic/Chroma và giao diện giảng viên còn lại; chưa chạy ứng dụng/DB/API.

Reviewer có thể đề xuất sửa liên kết cho bước bị sai loại cha dựa trên các cha đã qua Validator. Runner ghi đề xuất được áp dụng vào `08-review-repairs.json`; Python tiếp tục kiểm tra số bước và xung đột khi ráp graph. Người dùng cho phép tối đa 5 lượt chạy. Lượt OSI đầu dừng ở tải tokenizer do DNS; lượt chạy ngoài sandbox bị bộ duyệt tự động từ chối trước khi khởi động vì đích nhận nội dung tài liệu chưa được xác định rõ. Chưa có kết quả chạy LLM để so chất lượng.

Theo yêu cầu sửa lại luồng ingestion, runner gọi `multi_agent.py` và bốn module agent gốc đã cập nhật contract. Python ráp `09-graph-draft.json` theo ID cha và số bước nguồn. Đã bỏ luồng `draft_agents.py` và các lượt dựng/sửa graph bằng LLM. Chờ người dùng chạy lại ca OSI và bài tập.

Runner đã có bốn stage agent theo yêu cầu triển khai tiếp. Dùng `--stop-after review` để tạo bản nháp claims có nguồn và Topic–Chunk cục bộ. Workflow BE, canonical resolution toàn tài liệu và publication còn lại.

Ngày 2026-11-03, người dùng yêu cầu hoãn OCR. Các gói ingestion hiện hành chỉ xử lý văn bản trích được từ tài liệu. Kế hoạch, quyết định và mẫu cấu hình đã cập nhật theo phạm vi này.

Người dùng đã duyệt triển khai kế hoạch ingestion và yêu cầu làm theo gói, có file nhận đường dẫn file cục bộ để tự kiểm tra từng bước. Đã viết gói đầu: nền tảng contract/config và runner `run_ingestion.py`, snapshot → parse → chunk → integrity; hướng dẫn `.docs/ingestion-local-guide.md`, fixture `examples/ingestion/source-check.md`. Đã parse AST 6 file Python, không import/chạy ứng dụng hoặc test. Chưa nối workflow BE/bốn agent/review/publish; phần tiếp theo là job/lease/chunk commit và agent facts có evidence. Report `.reports/2026-11-02-ingestion-preprocessing.md`. Các gói còn lại giữ trong kế hoạch, không coi đã hoàn tất.

Người dùng yêu cầu kế hoạch ingestion chi tiết: luồng dữ liệu, DTO, các kho DB và logic nghiệp vụ. Đã viết `.docs/ingestion-implementation-plan.md` và cấu hình đề xuất `.docs/ingestion.env.example`; chưa triển khai ingestion hoặc sửa `.env` thật. Người dùng xác nhận nguồn ngoài có URL/trích dẫn, nội dung AI tự sinh gắn nhãn riêng; giới hạn file/quy mô cấu hình qua env. Các lựa chọn kỹ thuật mới trong plan còn chờ duyệt. Report `.reports/2026-11-02-ingestion-plan.md`.

Người dùng yêu cầu chuyển schema vào migration BE bằng CREATE TABLE hoàn chỉnh, sửa trực tiếp file gốc, không ALTER; đã chọn thêm material_publications để tránh vòng FK. Đã tạo bốn migration sau materials và trước chunks; sửa CREATE materials/chunks và seed cho 12 chunk, áp dụng tổng 11 file BE qua quyền filesystem, đối chiếu hash. Không chạy Flyway/DB/app/test/compile. Code ingestion/Entity/reader chưa cập nhật trong đợt SQL này. Guide `.docs/ingestion-database-migration.md` là nguồn hiện hành; SQL 004-007 ở repo AI là đề xuất đã được thay thế, không dùng cùng bộ CREATE mới.

Đợt trước đã sửa nhãn bước FE theo step_progress từ backend; report `.reports/2026-11-02-confirmed-step-display.md`, chưa chạy nghiệm thu. Các sửa SINGLE_STEP và luồng chat thống nhất giữ nguyên.

## Kết quả hiện tại

- Một service: app/service/tutoring/chat_service.py: SocraticChatService. DI chỉ phụ thuộc vector repo và tạo service này trực tiếp.
- Xóa service cũ, base rules/router prompt cũ; bốn prompt strategies bị Windows từ chối quyền xóa, không còn tham chiếu runtime.
- Prompt mới tại app/prompts/tutoring/{intent,evaluation,question,response}.md.
- Không còn cờ chọn phiên bản. Settings dùng SOCRATIC_*. .env đã đổi tên key, giữ dữ liệu nhạy cảm và tên collection vật lý nguyên trạng; không in giá trị.
- Seed: python -m app.seed_tutoring --target chunks|entities.
- Giữ route /api/v1, protocol_version 1/2 (một luồng nghiệp vụ, hai dạng truyền SSE). Mặc định Python protocol 2.
- Tài liệu hiện hành: ARCHITECTURE.md, .docs/socratic-operator-guide.md, .docs/socratic.env.example, .docs/sse-contract.md. Blueprint là thiết kế lịch sử; báo cáo/migration giữ nguyên định danh cũ.

## Kiểm chứng và phần còn lại

Sửa giới hạn tiết lộ: `.reports/2026-11-02-single-step-guidance.md`. Đã sửa intent/policy/rubric/response và prompt; nhánh SINGLE_STEP thêm kiểm tra bằng LLM trước khi hiển thị, có thể sinh lại một lần. Chưa chạy nghiệm thu; không bảo đảm tuyệt đối bằng kiểm tra mô hình. Không thêm bảng hoặc sửa BE/FE.

Đã kiểm tra tĩnh 97 file Python, import/config/prompt và doc links; chưa chạy ứng dụng hoặc DB. Báo cáo: `.reports/2026-11-02-single-chat-service.md`. Luồng chạy đã hợp nhất; dọn bốn file prompt strategies còn vướng quyền Delete của Windows. Không khẳng định chất lượng/hiệu năng bằng việc code đã viết.

Các đợt trước về live stream, tích hợp BE/FE, animation, schema ngộ nhận và DB đã ghi trong .reports/. Không reset những thay đổi có sẵn hoặc dọn module src/ingestion/thử nghiệm ngoài yêu cầu.
