# Điều phối hạt màu tại xưởng Meruva Talnek

## Trang 1 · Khái niệm và quy tắc

Meruva Talnek là một xưởng giả lập dùng để luyện đọc quy trình và quy tắc ưu tiên. Mỗi hạt màu được theo dõi bằng mã riêng, kể cả khi hai hạt có cùng màu. Đồng hồ xưởng tính theo nhịp. Các tên gọi và mã trong bài chỉ có ý nghĩa trong mô hình này.

**Thẻ Luvin** là quyền đưa một hạt vào buồng nhuộm dành cho người được ghi tên. Thẻ có hiệu lực đến hết nhịp ghi trên thẻ. Người đúng tên đến ở chính nhịp đó vẫn được dùng. Nếu sai tên hoặc đến muộn hơn, phải dừng trước khi mở hồ sơ. Thẻ chỉ được đóng khi hồ sơ mới đã được tạo.

**Hồ sơ Vask** ghi mã hạt, buồng đích, nhịp bắt đầu và hạn kiểm tra. Hạn thông thường là nhịp bắt đầu cộng 11 đối với màu lam, hoặc cộng 6 với các màu còn lại. Riêng buồng Z8 luôn dùng hạn cộng 3, bất kể màu. Phải kiểm tra buồng Z8 trước khi xét màu hạt.

**Biên dấu Rilen** xác nhận xưởng đã tiếp nhận hạt sau khi nhuộm. Nó ghi mã hạt, mã Hồ sơ Vask vừa đóng và nhịp tiếp nhận thực tế. Nếu không có hồ sơ đang mở tương ứng, xưởng chưa cấp biên dấu. Hạt bị đưa vào khay cách ly sau khi kiểm tra vẫn giữ biên dấu đã cấp.

Ví dụ minh họa: hạt lam được đưa tới Z8 ở nhịp 20 có hạn kiểm tra là 23, không phải 31. Ví dụ chỉ minh họa ngoại lệ của buồng, không cung cấp lời giải cho bài tập.

## Trang 2 · Quy trình vận hành

### Mở phiên nhuộm

Quy trình **Mở phiên nhuộm** thuộc khái niệm **Hồ sơ Vask**. Nhân viên cần mã hạt, tên người giao và buồng đích trước khi bắt đầu.

1. Đối chiếu mã hạt và tên trên Thẻ Luvin, rồi kiểm tra nhịp hiện tại không vượt quá giới hạn.
2. Tạo Hồ sơ Vask và ghi hạn kiểm tra. Nếu đích là Z8 thì cộng 3, còn lại mới xét quy tắc màu.
3. Đánh dấu hạt đang nhuộm và đóng Thẻ Luvin đã dùng sau khi hồ sơ được tạo thành công.

Lưu ý: nếu nhập sai mã buồng thì sửa dữ kiện trước khi lập hồ sơ. Đây là tình huống phát sinh, không phải bước thứ tư. Nhân viên không tự kéo dài thẻ cũ khi đổi buồng.

### Tiếp nhận hạt đã nhuộm

Quy trình **Tiếp nhận hạt đã nhuộm** thuộc khái niệm **Biên dấu Rilen**. Đây là quy trình riêng nên số thứ tự bắt đầu lại.

1. Quét mã hạt và tìm Hồ sơ Vask đang mở tương ứng.
2. Ghi nhịp tiếp nhận, đóng hồ sơ và cấp Biên dấu Rilen.
3. Kiểm tra bề mặt. Hạt rạn được đưa vào khay cách ly, hạt nguyên vẹn chuyển sang sẵn sàng.

Lưu ý: hạt ở khay cách ly vẫn được xác nhận là đã tiếp nhận. Việc cách ly chỉ ảnh hưởng tới khả năng dùng hạt cho phiên sau.

## Trang 3 · Bài tập và đáp án mẫu

### Bài K · Mở phiên cho hạt GN42

Người giao Mivo đến ở nhịp 47. Thẻ Luvin của hạt GN42 mang tên Mivo và có giới hạn nhịp 47. Hạt màu lam, buồng đích Z8. Hãy xác định Mivo có quyền mở phiên không, tính hạn kiểm tra và nêu trạng thái cuối của hạt cùng thẻ. Bài này vận dụng **Hồ sơ Vask**.

### Bài L · Tiếp nhận hạt MK16

Hạt MK16 trở về ở nhịp 81, có Hồ sơ Vask VS29 đang mở và bề mặt bị rạn. Hãy liệt kê ba trường cần ghi trên biên dấu, xác định trạng thái của hồ sơ và vị trí cuối của hạt. Bài này vận dụng **Biên dấu Rilen**. Tài liệu để người học tự giải bài L.

### Lời giải bài K

Lời giải dưới đây chỉ áp dụng cho bài K về hạt GN42. Đề bài L đứng gần hơn trên trang, nhưng không dùng chung lời giải.

1. Mivo có tên đúng và đến ở nhịp 47, đúng nhịp giới hạn. Thẻ còn hiệu lực nên có thể mở phiên.
2. Buồng Z8 dùng ngoại lệ cộng 3. Hạn kiểm tra là nhịp 50, dù hạt có màu lam.
3. Tạo hồ sơ, chuyển GN42 sang đang nhuộm và đóng Thẻ Luvin đã dùng.

Gợi ý tự kiểm tra: học sinh cần giải thích vì sao không cộng 11. Đoạn này chỉ nêu cách kiểm tra lập luận, không bổ sung bước giải thứ tư.
