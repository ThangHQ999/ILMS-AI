# Kế hoạch so sánh ingestion LightRAG HKU

Mục tiêu là xem LightRAG có giúp giảng viên sửa ít hơn ở những mục khó như quy trình, đề bài, lời giải và quan hệ tri thức. Đường thử nghiệm chạy cục bộ, dùng cùng học liệu và cùng manifest chunk trong một lần chạy.

## Các nhánh

| Nhánh | Xử lý | Đầu ra |
|---|---|---|
| A · agents | Bốn agent hiện tại và Python ráp đồ thị | Đồ thị nháp ILMS và claim có bằng chứng |
| B · lightrag | LightRAG HKU trích thực thể và cạnh bằng pipeline SDK | Graph gốc của LightRAG và ánh xạ chunk nguồn |
| C · hybrid | Chạy LightRAG một lần, đưa ứng viên thực thể và cạnh vào Expert của cùng luồng bốn agent | Đồ thị nháp ILMS và claim có bằng chứng |

B cho thấy cấu trúc tự nhiên của SDK. C trả lời câu hỏi LightRAG có giúp bốn agent tổ chức nội dung tốt hơn A hay không. Chạy cả ba nhánh chỉ index LightRAG một lần. Thời gian của C bao gồm chi phí LightRAG để so sánh như hai pipeline độc lập.

## Luồng dữ liệu

1. Đọc file, xác thực định dạng và hash, parse văn bản, tạo chunk bằng cấu hình ingestion hiện có. Kiểm tra integrity trước khi gọi agent. Dùng lại manifest cho A, B và C.
2. B dùng SDK được ghim phiên bản, callback chunk trả đúng nội dung trong manifest, kho JSON/NetworkX/vector cục bộ và thư mục riêng cho mỗi lượt thử. SDK có thể hợp nhất chunk trùng nội dung, vì vậy ghi ánh xạ từ ID chunk LightRAG sang mọi ID ILMS tương ứng.
3. Lấy graph native gồm node, edge, mô tả và ID nguồn. Ghi trạng thái bị cắt nếu SDK giới hạn kích thước graph. Đây là ứng viên tri thức cấp đoạn, không tự quy đổi chúng thành ExerciseStep hoặc bảo đảm cha đúng.
4. C thêm danh sách ứng viên có giới hạn vào prompt Expert. Một ứng viên chỉ được dùng khi tìm thấy claim và trích đoạn hỗ trợ. Extractor vẫn đọc nguồn, Validator kiểm tra nội dung và cha, Reviewer xử lý mơ hồ, Python ráp graph theo ID. Giữ cùng prompt cơ sở và cùng tham số trích xuất cho A và C.
5. Xuất ba đầu ra và một bảng so sánh. Lỗi một nhánh được báo riêng. Nếu LightRAG lỗi, C được đánh dấu bỏ qua vì thiếu đầu vào. Runner giữ kết quả của A nếu A hoàn thành.

## Cách chỉnh cho dữ liệu phức tạp

Đợt này tinh chỉnh prompt ở tầng Expert với gợi ý từ LightRAG. Chưa huấn luyện lại trọng số model. Graph native là tập thực thể và quan hệ. Một bài có đề, dữ kiện, lời giải và nhiều bước cần hợp đồng ILMS với ID cha, số bước và trích đoạn. Vì vậy dùng B để xem LightRAG tìm được khái niệm và cạnh nào, rồi dùng C để xem các gợi ý đó có cải thiện được đồ thị ILMS hay không.

Gợi ý có thể sai hoặc trùng. Expert dùng chúng để đối chiếu tên và mối liên hệ khi nguồn hỗ trợ. Python giữ nguyên cách gắn cha và kiểm tra của nhánh A. Nhánh hybrid hiện không chuyển cạnh LightRAG trực tiếp vào trường quan hệ ILMS.

## Nghiệm thu thủ công

Cài dependency thử nghiệm trong môi trường Python của dự án, ưu tiên môi trường riêng nếu đang dùng API production:

```powershell
python -m pip install -r requirements-lightrag-eval.txt
python compare_ingestion.py "D:\ILMS-AI\examples\ingestion\exercise-link-check.md"
```

Mặc định chạy cả ba nhánh. Dùng `--mode agents`, `--mode lightrag` hoặc `--mode hybrid` để chạy riêng. Hybrid luôn chạy LightRAG trước. Mỗi lần chạy in đường dẫn `REPORT.md` trong `data/ingestion-comparison`. Mở `agents-graph.json`, `lightrag-graph.json` và `hybrid-graph.json` để đối chiếu. `comparison.json` chứa số liệu và cấu hình model, còn `chunks.json` và hai file evidence giúp lần về văn bản. Thư mục `lightrag-storage` chứa dữ liệu index thử nghiệm của SDK. Chọn tài liệu được phép gửi tới provider đã cấu hình.

| Học liệu | Điều kiện đạt |
|---|---|
| OSI | Một thực thể OSI có một quy trình đủ bước 1–7. Đề LAN giữ nguyên dữ kiện và yêu cầu, không tách tiêu đề hoặc câu trả lời thành bài riêng. |
| Bao đóng thuộc tính | Một quy trình chung đủ 3 bước, hai đề đầy đủ, ba bước giải thuộc bài 1, bài 2 giữ danh sách lời giải rỗng. |
| DNA | Quy trình có đúng thứ tự từ nguồn. Đề giữ nguyên chuỗi nucleotide và yêu cầu. Kiểm tra từng cạnh cùng hai đầu và bằng chứng, nhất là cạnh nối sai loại. |

Chấm từng mục trên cùng nguồn. Đếm mục đúng, mục thiếu, mục cần đổi cha hoặc sửa nội dung và phát biểu không có căn cứ. Báo cáo tự động chỉ đếm cấu trúc, bằng chứng tham chiếu, cảnh báo và thời gian. Số node hoặc số bước cao hơn không đồng nghĩa chất lượng tốt hơn. Nên chạy lại khi kết quả sát nhau vì đầu ra LLM biến động.

## Phạm vi

Đây là runner so sánh bằng CLI. Kho thử nghiệm nằm trong thư mục kết quả cục bộ, tách khỏi Neo4j, MySQL và Chroma đang dùng. Sử dụng cùng cấu hình model trích xuất OpenAI cho SDK và agent khi agent cũng được cấu hình OpenAI. Nếu agent dùng Gemini hoặc fallback sang provider khác, kết quả có thêm biến model. Giữ nguyên cấu hình giữa các lượt so sánh. Người dùng chạy bằng thông tin kết nối LLM của dự án.

API SDK dùng callback chia chunk và graph export của bản ghim. Tham khảo [mã nguồn LightRAG v1.4.9](https://github.com/HKUDS/LightRAG/blob/v1.4.9/lightrag/lightrag.py).
