# Danh mục khái niệm cho câu hỏi và bản đồ nhiệt

Ngày 25/11/2026

ILMS-AI thêm API nội bộ `POST /api/v1/internal/knowledge-graphs/concept-catalog`. Spring Boot chọn các bản xuất bản mà người gọi được xem và truyền `courseId`, `publicationIds`. API đối chiếu liên kết tài liệu, bài học, chương và môn, trạng thái xuất bản hiện hành và hash của payload đã duyệt. Cả lô trả 404 nếu bất kỳ bản xuất bản nào đã đổi hoặc không thuộc môn. [Router](../app/api/v1/knowledge_graph_api.py) · [Truy vấn và phép chiếu](../app/service/knowledge_graph/concept_catalog.py)

Danh mục trả các cặp `canonicalCode`, `label`. Bản nhập JSON dùng mã đã lưu. Với bản ingestion cũ thiếu mã trong payload, danh mục tái dùng phép tính của publisher với phạm vi đoạn nguồn đầu tiên của đúng phiên bản. Các phần đánh giá chính thức, điểm và tổng hợp bằng chứng thuộc Spring Boot. [Hợp đồng API](../.docs/knowledge-graph-api-guide.md#internal-concept-catalog-for-assessments) · [Phép tính mã](../app/service/ingestion/publication/records.py)

Đã kiểm tra AST của 6 tệp Python và chạy lại 4 ca unit test SQLAlchemy trên SQLite trong bộ nhớ. Các ca bao gồm mã legacy so với publisher, nhận dạng trường `nodes[].code` của đồ thị cũ, loại trừ bản ngoài môn và bản sai hash, loại trừ bài học đã xóa, chống trả kết quả một phần trong lô, dedupe và giới hạn đầu vào. [Unit tests](../tests/test_concept_catalog.py)

Đã chạy router FastAPI và Spring Boot với MariaDB cục bộ. Router từ chối yêu cầu thiếu worker header và publication ở môn khác. Spring Boot nhập một đồ thị tổng hợp, gọi FastAPI lấy đúng mã và nhãn cho giảng viên, từ chối sinh viên gọi danh mục và đưa khái niệm vào heatmap với trạng thái chưa có bằng chứng. Luồng này chỉ cần API nội bộ và MySQL/MariaDB, nên đợt nghiệm thu dùng hai thành phần đó.
