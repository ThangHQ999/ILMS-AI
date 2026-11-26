# Điểm cần xác nhận

Không hỏi lại những gì đã chốt trong decisions.md. Các điểm dưới chưa ngăn tạo tài liệu, nhưng có thể ngăn một phần triển khai.

| Điểm | Ảnh hưởng | Cách xử lý trước mắt |
|---|---|---|
| Người dùng xác nhận ba bảng chưa tạo; MySQL phiên bản và DDL thực message/session chưa đối chiếu | FK, CHECK, UUID và migration | Đã cung cấp 001 tạo mới + 002 ALTER để người dùng tự áp dụng |
| knowledge_entity_id của heatmap cũ chứa loại mã nào, bên nào đang cập nhật | Tránh hai bảng điểm độc lập | Chốt mapping/backfill/lớp đọc tương thích trước P5 |
| Cạnh nối thực tế, kiểu properties, owner_id và scope trong Neo4j | Repository đúng dữ liệu người dùng | Lấy mẫu schema/export đã lược dữ liệu nhạy cảm; không đoán tên cạnh |
| Quy tắc xuất bản nội dung từ ingestion cho chat | Có dùng bản nháp/bị từ chối không | Chat đọc qua contract; không tự định nghĩa workflow duyệt |
| Topic trùng giữa chunk có được gom ở ingestion không | Xếp hạng và giữ Topic | Hỗ trợ nhiều ứng viên; không tự merge dữ liệu nguồn |
| FE hỗ trợ Mermaid hay schema sơ đồ nào, có renderer artifact chưa | Hợp đồng diagram_ready | Thiết kế backend trước, chốt schema trước P6 |
| Mức độ trễ/chi phí mong muốn và model triển khai | Cache, escalation và ngân sách context | Không hứa thời gian cụ thể; cung cấp cấu hình và cách đo |
| Quy tắc điểm mastery và mục tiêu theo từng môn | Báo cáo năng lực đáng tin | Giữ NULL khi chưa đủ dữ liệu; chưa chốt công thức phần trăm |
| Chính sách xóa hội thoại có giữ bằng chứng/tiến độ dài hạn không | FK CASCADE và khả năng truy vết | Rà soát SQL nháp trước migration; không coi thiết kế xóa đã chốt |
