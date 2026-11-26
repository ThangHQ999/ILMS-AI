# Quyết định hiện hành

Cập nhật 2026-11-02. Đây là quyết định thiết kế từ cuộc trao đổi, không chứng minh đã triển khai.

| ID | Quyết định | Trạng thái |
|---|---|---|
| D01 | Ưu tiên giải thích khái niệm; hỗ trợ đa môn, độ sâu điều chỉnh qua tương tác | Đã chốt hướng |
| D02 | Topic do ingestion tự trích xuất theo chunk; chat tự suy ra, FE không phải biết Topic | Đã chốt |
| D03 | Hỗ trợ tăng dần, giải thích ngắn, ví dụ tương tự; không giải hộ bài đang làm | Đã chốt |
| D04 | Dùng ba bảng learning_state, turn_evaluations, concept_progress | Người dùng xác nhận đã có đủ bảng; agent chưa kiểm chứng DB |
| D05 | Canonical code là định danh tri thức liên hệ các kho | Thiết kế đề xuất được dùng làm cơ sở; kiểm tra mapping dữ liệu cũ trước triển khai |
| D06 | Có thể mở rộng Neo4j bằng ConceptRubric/ConceptCriterion; chat hoạt động khi chưa có rubric bằng tiêu chí tạm | Thiết kế; việc thêm node thuộc kho tri thức, chưa triển khai |
| D07 | Giáo viên/admin có quyền rà soát nội dung AI sinh; luồng tạo/duyệt thuộc ingestion/quản trị | Đã chốt ranh giới |
| D08 | Chat không chờ duyệt để trả lời, không tự ghi tiêu chí tạm thành rubric chuẩn | Đã thống nhất hướng |
| D09 | SSE status theo công việc thật; token cho phản hồi; artifact hoàn chỉnh qua event riêng | Đã chốt hướng; payload là đề xuất |
| D10 | Người dùng tự chạy thử; agent chưa triển khai code trước khi duyệt kế hoạch | Yêu cầu hiện hành |
| D11 | Người dùng đã yêu cầu triển khai các gói blueprint; người dùng tự quản lý SQL | Được phép viết code/migration, không áp dụng DB/test |
| D12 | student_misconceptions dùng misconception_status (SUSPECTED/CONFIRMED/RESOLVED), bỏ is_resolved/review_status; session_id nullable ON DELETE SET NULL | Đã chốt DDL và cho phép đồng bộ code; người dùng xác nhận đủ bảng |
| D13 | Người dùng yêu cầu trải nghiệm trạng thái tác vụ và chữ sinh dần kiểu ChatGPT: protocol 2 live delta, hậu kiểm có thể sửa bằng content_replace, done sau commit; protocol 1 giữ buffer | Đã viết backend/contract; FE ngoài repo, chưa chạy thử |
| D14 | Người dùng yêu cầu bỏ service cũ, dùng một SocraticChatService, bỏ cờ bật/tên phiên bản trong runtime, chuẩn hóa SOCRATIC_* và seed_tutoring | Đã viết; giữ hợp đồng API/SSE và lịch sử dữ liệu/migration; chưa chạy thử |
| D15 | Người dùng duyệt sửa ca AI tự hoàn tất bao đóng: policy giới hạn SINGLE_STEP, câu hỏi phụ một tiêu chí, kiểm tra mức tiết lộ trước khi phát nhánh gợi ý | Đã viết, không chạy thử; nhánh này ưu tiên không lộ đáp án hơn live draft chưa kiểm tra |
| D16 | Ingestion mặc định chỉ lấy tài liệu; bổ sung phải opt-in, nguồn ngoài có URL/trích dẫn, AI tự sinh gắn nhãn riêng; giáo viên/admin duyệt graph | Người dùng xác nhận; chưa triển khai pipeline theo thiết kế mới |
| D17 | Giới hạn định dạng/quy mô/concurrency ingestion cấu hình qua env | Người dùng yêu cầu; đã có mẫu đề xuất, chưa nối Settings hoặc sửa env thật |
| D18 | Schema ingestion dùng bốn bảng mới material_versions/ingestion_jobs/knowledge_graph_drafts/material_publications và chunks theo version, CREATE hoàn chỉnh trong BE | Đã viết migration theo yêu cầu; chưa chạy DB hoặc nâng Entity/reader |
| D19 | Người dùng duyệt triển khai kế hoạch ingestion theo gói, yêu cầu file nhận đường dẫn file máy để tự kiểm tra từng bước | Bắt đầu nền tảng tiền xử lý và runner; chưa chạy thử, chưa hoàn tất workflow production |
| D20 | Hoãn OCR và giới hạn đợt triển khai ở văn bản trích được trực tiếp từ tài liệu | Người dùng xác nhận ngày 2026-11-03 |
| D21 | Ingestion gửi toàn văn text khi đủ giới hạn; agent sau kiểm tra có nguồn, tự gom topic và tự nối chunk; tự lưu draft trên server; chat chỉ đọc publication hiện hành; duyệt theo phiên bản | Đã chốt nghiệp vụ, kế hoạch kỹ thuật mới chờ duyệt |

Code đợt đầu đã thêm theo D11, xem report triển khai. D04 đã được người dùng xác nhận có bảng; D06 chưa xác nhận graph thực tế. Agent không trực tiếp kiểm chứng DB. D10 về điều kiện duyệt đã được đáp ứng cho phạm vi blueprint; yêu cầu tự chạy thử vẫn giữ.

D14 thay thế các quyết định rollout hai service trước đây. Migration/báo cáo có ngày giữ tên lịch sử. Tên collection vật lý giữ nguyên giá trị để không trỏ nhầm index.

## Các phương án đã được thay thế

- Đề xuất dùng heatmap thay student_concept_progress đã được thay bằng lựa chọn ba bảng của người dùng. Cách di chuyển/đọc tương thích heatmap cũ còn phải chốt.
- Đề xuất nhét state vào session đã được thay bằng bảng socratic_learning_state riêng.
- Đề xuất đưa workflow duyệt rubric vào phạm vi chat đã được rút lại theo người dùng. Chat chỉ cần contract đọc dữ liệu.
- Sáu mục tiêu không phải sáu bước bắt buộc cho mọi khái niệm.

## Quy tắc thay đổi quyết định

Khi người dùng điều chỉnh: cập nhật quyết định hiện hành, ghi điều đã thay thế và các file bị ảnh hưởng. Không tự suy ra đã cho phép code từ một câu đồng ý về thiết kế.


## 2026-11-08 — Quản trị đồ thị

Người dùng duyệt triển khai BE và AI theo kế hoạch knowledge-graph-api-plan.md và xác nhận RBAC có ADMIN/USER, vai trò lớp có OWNER/TEACHER/STUDENT. Module mới đọc permission trực tiếp từ DB, kiểm membership ACTIVE cho phạm vi tài liệu, tái dùng service cho các route ingestion cũ. Mặc định giảng viên tự duyệt học liệu mình upload khi còn dạy khóa học. OWNER quản lý nội dung dùng chung khi sở hữu toàn bộ các lớp ACTIVE liên kết. Có một migration mới cho audit/idempotency/generation và permission của module. Đây là thay đổi schema bổ sung của tính năng quản trị, tách khỏi quyết định trước về giữ nguyên bảng khi chỉ thêm projection draft Neo4j.
