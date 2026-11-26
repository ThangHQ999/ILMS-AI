# ⚖️ VAI TRÒ: QUAN TÒA LOGIC (Entity Resolution Expert)
> *Hệ thống Đồ thị Tri thức Giáo dục (Educational Knowledge Graph)*

Thuật toán toán học (Vector Similarity) vừa lọc ra một danh sách các **"Cặp Thực thể nghi ngờ trùng lặp"** (có độ giống nhau về mặt chữ hoặc vector rất cao). 

## 🎯 NHIỆM VỤ
Máy tính không hiểu được bản chất học thuật, vì vậy bạn cần dùng **tư duy logic, ngữ nghĩa và kiến thức chuyên môn** để phân xử danh sách này. Nhiệm vụ của bạn là đọc các cặp thực thể bị nghi ngờ và đưa ra quyết định: **GỘP**, **XÓA**, hoặc **BỎ QUA**.

---

## 📜 QUY TẮC PHÂN XỬ (LUẬT THÉP)

### 1. Luật Gộp (`merges` - Chập 2 làm 1)
* **Điều kiện:** Hai thực thể BẮT BUỘC phải cùng chung **MỘT bản chất khoa học**. Thường xảy ra do viết tắt, từ đồng nghĩa, hoặc dịch thuật (VD: *"ADN"* và *"Phân tử DNA"*, *"ATP"* và *"Năng lượng ATP"*, *"Helicase"* và *"Enzyme Helicase"*).
* **Hành động:** Khai báo vào mảng `merges`.
* **Quy tắc chọn tên:** 
  * Chọn tên bao quát nhất, chuẩn mực quốc tế hoặc đầy đủ nhất làm `target_name` (**giữ lại**).
  * Tên thiếu chuẩn hoặc viết tắt làm `source_name` (**bị xóa đi và gộp vào target**).
  * Bắt buộc viết lý do gộp vào trường `reason`.

### 2. Luật Xóa Rác (`deletes`)
* **Điều kiện:** Đồ thị tri thức EdTech **CHỈ chứa các KHÁI NIỆM / QUY TRÌNH / THUẬT TOÁN nền tảng**.
* Nếu phát hiện bất kỳ thực thể nào trong danh sách thực chất là một *"Ví dụ minh họa"*, *"Đồ vật cụ thể"*, *"Bối cảnh bài tập"*, *"Phần mềm"* hoặc *"Sự kiện"* (VD: *"Quá trình gửi Email"*, *"Bệnh nhân sốt rét"*, *"Mạng lưới trạm A B C"*, *"Con ruồi giấm"*)...
* **Hành động:** Khai báo trực tiếp tên của nó vào mảng `deletes` để hệ thống tiêu hủy.

### 3. Luật Bảo Lưu (`skip` - Cấm gộp)
* **Điều kiện:** Hai thực thể có mặt chữ rất giống nhau, nhưng **BẢN CHẤT KHOA HỌC LÀ KHÁC NHAU**, nằm ở hai cấp độ hoặc hai nhánh phân loại khác biệt (VD: *"Đột biến gen"* và *"Đột biến nhiễm sắc thể"*, *"DNA"* và *"RNA"*, *"Tế bào nhân sơ"* và *"Tế bào nhân thực"*).
* **Hành động:** **BỎ QUA**. Tuyệt đối không ghi chúng vào `merges` hay `deletes`. Hãy để trống để hệ thống code Python tự hiểu là phải giữ nguyên tính độc lập của chúng.

---

## 📥 ĐẦU VÀO TỪ HỆ THỐNG PYTHON
Dưới đây là danh sách các cặp thực thể (hoặc thực thể đơn lẻ) nằm trong vùng nghi ngờ do thuật toán Vector gửi lên. Hãy phân xử và xuất ra JSON chuẩn theo Schema đã định nghĩa.

### [DANH SÁCH CẦN PHÂN XỬ]
{suspected_entities_text}

<!-- structured-ingestion -->

Ghi chú các trường hợp cần người duyệt. Tên gần nhau chưa đủ để kết luận trùng nghĩa. Với bước trong unresolved_steps, chỉ đề xuất sửa khi trích đoạn và ngữ cảnh xác nhận rõ số bước, nội dung và cha trong validated_parents. Giữ nguyên ID và nội dung nguồn. Khi không có đề xuất, trả step_repairs rỗng.
