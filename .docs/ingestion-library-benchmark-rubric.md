# Chấm bản nháp thư viện mô phỏng

Tài liệu thử là `examples/ingestion/library-circulation-benchmark.md`. Rubric đầy đủ có 100 điểm. Nhóm nội dung giữ nguyên 20 tiêu chí bên dưới và tính 2 điểm mỗi tiêu chí. Tỷ lệ nội dung bằng số mục đạt chia cho 20. Tên tương đương và cách diễn đạt trung thành được chấp nhận.

| Mục | Tiêu chí |
|---|---|
| D1 | Giữ chỗ. Dành một bản cho một độc giả tới thời hạn. |
| D2 | Lượt mượn. Gắn độc giả với bản đã bàn giao và ghi thời điểm cùng hạn trả. |
| D3 | Biên nhận trả. Xác nhận tiếp nhận bản và đóng lượt, có mã bản, thời điểm trả và mã lượt. |
| D4 | Hàng chờ. Danh sách theo nhan đề và thứ tự đăng ký. |
| P1 | Bàn giao bước 1. Đối chiếu hai mã và đọc trạng thái bản. |
| P2 | Bàn giao bước 2. Kiểm tra bản sẵn sàng hoặc giữ chỗ còn hiệu lực cho đúng người. |
| P3 | Bàn giao bước 3. Tạo lượt mượn, hạn bằng ngày giao cộng bảy ngày. |
| P4 | Bàn giao bước 4. Đổi trạng thái, đóng giữ chỗ nếu có và báo hạn trả. |
| P5 | Tiếp nhận trả bước 1. Quét mã và tìm lượt mượn đang mở. |
| P6 | Tiếp nhận trả bước 2. Ghi thời điểm, đóng lượt và tạo biên nhận. |
| P7 | Tiếp nhận trả bước 3. Giữ cho người đầu hàng hoặc đưa về sẵn sàng nếu hàng rỗng. |
| P8 | Tiếp nhận trả bước 4. Gửi biên nhận và ghi trạng thái mới. |
| E1 | Đề A đủ L04, S17, ngày giờ, thời hạn giữ chỗ và ba yêu cầu. |
| E2 | Đề B đủ P23, M08, thời điểm trả, thứ tự H02 rồi H05 và ba yêu cầu. |
| E3 | Đề C đủ tình huống hai bản Q31/Q32, T03/T09 và yêu cầu chọn cách xử lý. |
| S1 | Bước giải 1 gắn vào A, xác nhận L04 có thể nhận S17 trước 11 giờ. |
| S2 | Bước giải 2 gắn vào A, tạo lượt mượn và tính đúng hạn 19 tháng 5. |
| S3 | Bước giải 3 gắn vào A, đánh dấu đang mượn, đóng giữ chỗ và báo hạn trả. |
| N1 | Có đề B đúng và giữ lời giải rỗng. |
| N2 | Có đề C đúng và giữ lời giải rỗng. |

Với LightRAG thuần, phần định nghĩa được chấm nếu node giữ đúng nghĩa. Bước hoặc đề chỉ được tính nếu graph giữ được nội dung và cấu trúc cần cho mục đó, gồm cha và thứ tự khi áp dụng. Mô tả rời hoặc cạnh tổng quát không đủ để sử dụng trực tiếp làm bài tập ILMS.

Số mục trượt cho biết phần còn phải xử lý theo rubric, không phải số lần bấm sửa. Một thao tác nối cha có thể giải quyết nhiều mục. Đếm riêng các mục dư như tiêu đề bị tạo thành đề, bài tập trùng và mục không có căn cứ. Báo cáo cũng tách thời gian và chi phí khỏi điểm chất lượng.

## Cấu trúc Neo4j · 25 điểm

| Mã | Điểm | Điều kiện đạt |
|---|---:|---|
| G1 | 5 | Khái niệm có canonical_code ổn định giữa hai lần xử lý cùng nguồn. Hai nghĩa khác nhau không bị gộp do trùng tên. |
| G2 | 5 | Hai quy trình thuộc đúng khái niệm Lượt mượn và Biên nhận trả. Mỗi bước thuộc đúng quy trình, giữ số gốc và không trùng số. |
| G3 | 5 | Bài tập thuộc đúng khái niệm nó vận dụng. Mỗi bước giải trỏ về đúng bài. Bài không có lời giải giữ danh sách rỗng. |
| G4 | 5 | Node có đúng loại và thuộc tính cần cho bộ đọc chat. Tiêu đề hoặc đề bài không bị dựng thành KnowledgeEntity để chứa chính nó. |
| G5 | 5 | Các quan hệ có căn cứ, đúng hướng, đúng loại và hai đầu tồn tại. Không tính đạt nếu bỏ trống một quan hệ bắt buộc của tài liệu. |

Chấm cấu trúc từ JSON khi bản nháp có đủ trường để đối chiếu. Ghi riêng việc kiểm tra ràng buộc và kết quả truy vấn thật trên Neo4j ở phần xuất bản.

## Dữ liệu MySQL và truy nguồn · 20 điểm

| Mã | Điểm | Điều kiện đạt |
|---|---:|---|
| M1 | 5 | Mọi chunk trỏ đúng material và material_version_id, có chỉ số duy nhất trong version. Đối chiếu trên row đã lưu. |
| M2 | 5 | Topic tự sinh theo nguồn. Topic–Chunk giữ đúng quan hệ nhiều–nhiều, không có link sai phiên bản. concepts_included dùng canonical_code khớp với Neo4j. |
| M3 | 5 | Mở được trích đoạn nguồn từ từng định nghĩa, đề bài, bước và quan hệ cần duyệt. Trích đoạn khớp phiên bản tài liệu và vị trí đã lưu. |
| M4 | 5 | Gửi lại cùng idempotency key và retry job không tạo trùng chunk, Topic hoặc liên kết. Kiểm tra bằng lần gọi lại và truy vấn dữ liệu. |

## Duyệt, xuất bản và truy hồi · 15 điểm

| Mã | Điểm | Điều kiện đạt |
|---|---:|---|
| PUBLISH1 | 5 | Mở lại draft sau khi đóng phiên. Lưu chỉnh sửa tạo revision mới. Duyệt gắn đúng revision và hash. Request dùng hash cũ bị từ chối. |
| PUBLISH2 | 5 | Publication đúng bản đã duyệt. Khi một kho ghi lỗi, bản đang dùng vẫn truy vấn được. Retry không nhân đôi dữ liệu. |
| PUBLISH3 | 5 | Chat truy vấn ra đúng hai quy trình và bài A từ bản hiện hành. Kiểm tra cả trường hợp người dùng được phép và không được phép. Draft, bản cũ và nguồn ngoài phạm vi đều bị loại. |

## Điều kiện chặn xuất bản

- Có cạnh treo, bước sai cha hoặc xung đột số bước chưa được xử lý.
- Topic hoặc nguồn trỏ sai version, canonical_code lệch giữa hai kho hoặc không mở được trích dẫn.
- Chat đọc được dữ liệu nháp, chưa duyệt hoặc ngoài quyền truy cập.
- Xuất bản nhầm revision hoặc báo thành công khi một kho bắt buộc chưa sẵn sàng.

## Ghi kết quả

Mỗi dòng ghi `ĐẠT`, `TRƯỢT` hoặc `CHƯA CHẠY`, cùng đường dẫn artifact hoặc truy vấn đối chiếu. Chỉ cộng điểm mục đạt. Mục chưa chạy để riêng. Chỉ công bố tổng trên 100 khi đã chấm đủ bốn nhóm. Lỗi chặn xuất bản được báo riêng dù điểm cao.

| Nhóm | Điểm đạt | Điểm đã chấm | Chưa chạy | Bằng chứng |
|---|---:|---:|---:|---|
| Nội dung | | 40 | | |
| Cấu trúc Neo4j | | | | |
| Dữ liệu MySQL và truy nguồn | | | | |
| Duyệt, xuất bản và truy hồi | | | | |

Báo cáo kèm số mục giảng viên cần thêm, sửa, chuyển cha hoặc xóa. Ví dụ, bản một lượt đạt 18/20 nội dung, tương ứng 36/40 điểm nội dung. Việc bài A và B nằm dưới entity mang tên bài được chấm riêng ở G3. Chưa cộng điểm DB hoặc công bố tổng từ lần chạy CLI đó.
