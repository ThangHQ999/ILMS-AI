# Sổ vận hành hệ thống giả lập Ordel Nuvarek

Tài liệu thử nghiệm gồm 30 trang quy ước. Mã vật, màu, tên quy trình và quy tắc dưới đây được đặt riêng cho mô hình giả lập. Mười quy trình và hai mươi đề bài được trình bày trước. Lời giải nằm ở phần cuối và chỉ dành cho mười bài có hậu tố A. Không suy diễn đáp án cho các bài có hậu tố B.

## Trang 1 · Hồ sơ Aven

**Hồ sơ Aven** là bản ghi điều phối cho một vật trong khu Aven. Bản ghi có mã vật, tên người thao tác, đích, nhịp mở và nhịp đến hạn. Với vật màu xanh lam, hạn thông thường bằng nhịp mở cộng 11. Riêng đích buồng Z11 dùng hạn bằng nhịp mở cộng 4, kể cả khi màu vật khớp quy tắc thông thường. Nhân viên áp dụng ngoại lệ của đích trước khi xét màu. Quy tắc của khu khác không được dùng cho Hồ sơ Aven.

Phiếu cấp quyền ghi tên người được phép và nhịp giới hạn. Trong khu Aven, người đúng tên vẫn được thao tác ở chính nhịp giới hạn. Nếu nhịp hiện tại lớn hơn giới hạn hoặc tên không khớp, dừng yêu cầu trước khi lập bản ghi. Quyền đã dùng chỉ đóng sau khi bản ghi được tạo thành công. Trạng thái hiển thị ở màn hình không thay thế việc kiểm tra mã vật và mã quyền.

### Mở hồ sơ Aven

Quy trình **Mở hồ sơ Aven** thuộc khái niệm **Hồ sơ Aven**. Đầu vào là mã vật, tên người, nhịp hiện tại và đích. Quy trình có đúng ba bước.

1. Đối chiếu mã vật và tên trên phiếu cấp quyền, rồi kiểm tra nhịp hiện tại không vượt giới hạn.
2. Lập Hồ sơ Aven. Nếu đích là buồng Z11, cộng 4 để tính hạn. Nếu đích khác và vật màu xanh lam, cộng 11.
3. Sau khi lưu bản ghi thành công, đánh dấu đang hiệu chỉnh, đóng quyền đã dùng và thông báo hạn cho người thao tác.

Lưu ý riêng của khu: Giá đỡ bị cong. Ghi hiện tượng vào phần nhận xét để ca sau đối chiếu. Đoạn này không phải bước thứ tư và không thay đổi công thức tính hạn. Ví dụ, vật màu xanh lam tới buồng Z11 ở nhịp 20 có hạn 24, không phải 31.

## Trang 2 · Phiếu Belor

**Phiếu Belor** là bản ghi điều phối cho một vật trong khu Belor. Bản ghi có mã vật, tên người thao tác, đích, nhịp mở và nhịp đến hạn. Với vật màu đỏ, hạn thông thường bằng nhịp mở cộng 9. Riêng đích kho R24 dùng hạn bằng nhịp mở cộng 2, kể cả khi màu vật khớp quy tắc thông thường. Nhân viên áp dụng ngoại lệ của đích trước khi xét màu. Quy tắc của khu khác không được dùng cho Phiếu Belor.

Phiếu cấp quyền ghi tên người được phép và nhịp giới hạn. Trong khu Belor, người đúng tên vẫn được thao tác ở chính nhịp giới hạn. Nếu nhịp hiện tại lớn hơn giới hạn hoặc tên không khớp, dừng yêu cầu trước khi lập bản ghi. Quyền đã dùng chỉ đóng sau khi bản ghi được tạo thành công. Trạng thái hiển thị ở màn hình không thay thế việc kiểm tra mã vật và mã quyền.

### Mở hồ sơ Belor

Quy trình **Mở hồ sơ Belor** thuộc khái niệm **Phiếu Belor**. Đầu vào là mã vật, tên người, nhịp hiện tại và đích. Quy trình có đúng ba bước.

1. Đối chiếu mã vật và tên trên phiếu cấp quyền, rồi kiểm tra nhịp hiện tại không vượt giới hạn.
2. Lập Phiếu Belor. Nếu đích là kho R24, cộng 2 để tính hạn. Nếu đích khác và vật màu đỏ, cộng 9.
3. Sau khi lưu bản ghi thành công, đánh dấu đang chuyển, đóng quyền đã dùng và thông báo hạn cho người thao tác.

Lưu ý riêng của khu: Tem bị rách. Ghi hiện tượng vào phần nhận xét để ca sau đối chiếu. Đoạn này không phải bước thứ tư và không thay đổi công thức tính hạn. Ví dụ, vật màu đỏ tới kho R24 ở nhịp 20 có hạn 22, không phải 29.

## Trang 3 · Sổ Cirva

**Sổ Cirva** là bản ghi điều phối cho một vật trong khu Cirva. Bản ghi có mã vật, tên người thao tác, đích, nhịp mở và nhịp đến hạn. Với vật màu trắng, hạn thông thường bằng nhịp mở cộng 15. Riêng đích trạm M08 dùng hạn bằng nhịp mở cộng 6, kể cả khi màu vật khớp quy tắc thông thường. Nhân viên áp dụng ngoại lệ của đích trước khi xét màu. Quy tắc của khu khác không được dùng cho Sổ Cirva.

Phiếu cấp quyền ghi tên người được phép và nhịp giới hạn. Trong khu Cirva, người đúng tên vẫn được thao tác ở chính nhịp giới hạn. Nếu nhịp hiện tại lớn hơn giới hạn hoặc tên không khớp, dừng yêu cầu trước khi lập bản ghi. Quyền đã dùng chỉ đóng sau khi bản ghi được tạo thành công. Trạng thái hiển thị ở màn hình không thay thế việc kiểm tra mã vật và mã quyền.

### Mở hồ sơ Cirva

Quy trình **Mở hồ sơ Cirva** thuộc khái niệm **Sổ Cirva**. Đầu vào là mã vật, tên người, nhịp hiện tại và đích. Quy trình có đúng ba bước.

1. Đối chiếu mã vật và tên trên phiếu cấp quyền, rồi kiểm tra nhịp hiện tại không vượt giới hạn.
2. Lập Sổ Cirva. Nếu đích là trạm M08, cộng 6 để tính hạn. Nếu đích khác và vật màu trắng, cộng 15.
3. Sau khi lưu bản ghi thành công, đánh dấu chờ tiếp nhận, đóng quyền đã dùng và thông báo hạn cho người thao tác.

Lưu ý riêng của khu: Cảm biến không phản hồi. Ghi hiện tượng vào phần nhận xét để ca sau đối chiếu. Đoạn này không phải bước thứ tư và không thay đổi công thức tính hạn. Ví dụ, vật màu trắng tới trạm M08 ở nhịp 20 có hạn 26, không phải 35.

## Trang 4 · Biên Doren

**Biên Doren** là bản ghi điều phối cho một vật trong khu Doren. Bản ghi có mã vật, tên người thao tác, đích, nhịp mở và nhịp đến hạn. Với vật màu vàng, hạn thông thường bằng nhịp mở cộng 12. Riêng đích buồng K19 dùng hạn bằng nhịp mở cộng 3, kể cả khi màu vật khớp quy tắc thông thường. Nhân viên áp dụng ngoại lệ của đích trước khi xét màu. Quy tắc của khu khác không được dùng cho Biên Doren.

Phiếu cấp quyền ghi tên người được phép và nhịp giới hạn. Trong khu Doren, người đúng tên vẫn được thao tác ở chính nhịp giới hạn. Nếu nhịp hiện tại lớn hơn giới hạn hoặc tên không khớp, dừng yêu cầu trước khi lập bản ghi. Quyền đã dùng chỉ đóng sau khi bản ghi được tạo thành công. Trạng thái hiển thị ở màn hình không thay thế việc kiểm tra mã vật và mã quyền.

### Mở hồ sơ Doren

Quy trình **Mở hồ sơ Doren** thuộc khái niệm **Biên Doren**. Đầu vào là mã vật, tên người, nhịp hiện tại và đích. Quy trình có đúng ba bước.

1. Đối chiếu mã vật và tên trên phiếu cấp quyền, rồi kiểm tra nhịp hiện tại không vượt giới hạn.
2. Lập Biên Doren. Nếu đích là buồng K19, cộng 3 để tính hạn. Nếu đích khác và vật màu vàng, cộng 12.
3. Sau khi lưu bản ghi thành công, đánh dấu đang kiểm định, đóng quyền đã dùng và thông báo hạn cho người thao tác.

Lưu ý riêng của khu: Vỏ có vết nứt. Ghi hiện tượng vào phần nhận xét để ca sau đối chiếu. Đoạn này không phải bước thứ tư và không thay đổi công thức tính hạn. Ví dụ, vật màu vàng tới buồng K19 ở nhịp 20 có hạn 23, không phải 32.

## Trang 5 · Mã Elvix

**Mã Elvix** là bản ghi điều phối cho một vật trong khu Elvix. Bản ghi có mã vật, tên người thao tác, đích, nhịp mở và nhịp đến hạn. Với vật màu tím, hạn thông thường bằng nhịp mở cộng 17. Riêng đích trạm P31 dùng hạn bằng nhịp mở cộng 7, kể cả khi màu vật khớp quy tắc thông thường. Nhân viên áp dụng ngoại lệ của đích trước khi xét màu. Quy tắc của khu khác không được dùng cho Mã Elvix.

Phiếu cấp quyền ghi tên người được phép và nhịp giới hạn. Trong khu Elvix, người đúng tên vẫn được thao tác ở chính nhịp giới hạn. Nếu nhịp hiện tại lớn hơn giới hạn hoặc tên không khớp, dừng yêu cầu trước khi lập bản ghi. Quyền đã dùng chỉ đóng sau khi bản ghi được tạo thành công. Trạng thái hiển thị ở màn hình không thay thế việc kiểm tra mã vật và mã quyền.

### Mở hồ sơ Elvix

Quy trình **Mở hồ sơ Elvix** thuộc khái niệm **Mã Elvix**. Đầu vào là mã vật, tên người, nhịp hiện tại và đích. Quy trình có đúng ba bước.

1. Đối chiếu mã vật và tên trên phiếu cấp quyền, rồi kiểm tra nhịp hiện tại không vượt giới hạn.
2. Lập Mã Elvix. Nếu đích là trạm P31, cộng 7 để tính hạn. Nếu đích khác và vật màu tím, cộng 17.
3. Sau khi lưu bản ghi thành công, đánh dấu đang lọc, đóng quyền đã dùng và thông báo hạn cho người thao tác.

Lưu ý riêng của khu: Niêm phong không khớp. Ghi hiện tượng vào phần nhận xét để ca sau đối chiếu. Đoạn này không phải bước thứ tư và không thay đổi công thức tính hạn. Ví dụ, vật màu tím tới trạm P31 ở nhịp 20 có hạn 27, không phải 37.

## Trang 6 · Thẻ Faren

**Thẻ Faren** là bản ghi điều phối cho một vật trong khu Faren. Bản ghi có mã vật, tên người thao tác, đích, nhịp mở và nhịp đến hạn. Với vật màu xám, hạn thông thường bằng nhịp mở cộng 10. Riêng đích kho H05 dùng hạn bằng nhịp mở cộng 5, kể cả khi màu vật khớp quy tắc thông thường. Nhân viên áp dụng ngoại lệ của đích trước khi xét màu. Quy tắc của khu khác không được dùng cho Thẻ Faren.

Phiếu cấp quyền ghi tên người được phép và nhịp giới hạn. Trong khu Faren, người đúng tên vẫn được thao tác ở chính nhịp giới hạn. Nếu nhịp hiện tại lớn hơn giới hạn hoặc tên không khớp, dừng yêu cầu trước khi lập bản ghi. Quyền đã dùng chỉ đóng sau khi bản ghi được tạo thành công. Trạng thái hiển thị ở màn hình không thay thế việc kiểm tra mã vật và mã quyền.

### Mở hồ sơ Faren

Quy trình **Mở hồ sơ Faren** thuộc khái niệm **Thẻ Faren**. Đầu vào là mã vật, tên người, nhịp hiện tại và đích. Quy trình có đúng ba bước.

1. Đối chiếu mã vật và tên trên phiếu cấp quyền, rồi kiểm tra nhịp hiện tại không vượt giới hạn.
2. Lập Thẻ Faren. Nếu đích là kho H05, cộng 5 để tính hạn. Nếu đích khác và vật màu xám, cộng 10.
3. Sau khi lưu bản ghi thành công, đánh dấu chờ cân, đóng quyền đã dùng và thông báo hạn cho người thao tác.

Lưu ý riêng của khu: Cân chưa được đặt về 0. Ghi hiện tượng vào phần nhận xét để ca sau đối chiếu. Đoạn này không phải bước thứ tư và không thay đổi công thức tính hạn. Ví dụ, vật màu xám tới kho H05 ở nhịp 20 có hạn 25, không phải 30.

## Trang 7 · Hồ sơ Givon

**Hồ sơ Givon** là bản ghi điều phối cho một vật trong khu Givon. Bản ghi có mã vật, tên người thao tác, đích, nhịp mở và nhịp đến hạn. Với vật màu lục, hạn thông thường bằng nhịp mở cộng 13. Riêng đích buồng N12 dùng hạn bằng nhịp mở cộng 4, kể cả khi màu vật khớp quy tắc thông thường. Nhân viên áp dụng ngoại lệ của đích trước khi xét màu. Quy tắc của khu khác không được dùng cho Hồ sơ Givon.

Phiếu cấp quyền ghi tên người được phép và nhịp giới hạn. Trong khu Givon, người đúng tên vẫn được thao tác ở chính nhịp giới hạn. Nếu nhịp hiện tại lớn hơn giới hạn hoặc tên không khớp, dừng yêu cầu trước khi lập bản ghi. Quyền đã dùng chỉ đóng sau khi bản ghi được tạo thành công. Trạng thái hiển thị ở màn hình không thay thế việc kiểm tra mã vật và mã quyền.

### Mở hồ sơ Givon

Quy trình **Mở hồ sơ Givon** thuộc khái niệm **Hồ sơ Givon**. Đầu vào là mã vật, tên người, nhịp hiện tại và đích. Quy trình có đúng ba bước.

1. Đối chiếu mã vật và tên trên phiếu cấp quyền, rồi kiểm tra nhịp hiện tại không vượt giới hạn.
2. Lập Hồ sơ Givon. Nếu đích là buồng N12, cộng 4 để tính hạn. Nếu đích khác và vật màu lục, cộng 13.
3. Sau khi lưu bản ghi thành công, đánh dấu chờ làm nguội, đóng quyền đã dùng và thông báo hạn cho người thao tác.

Lưu ý riêng của khu: Nhiệt kế không hiển thị. Ghi hiện tượng vào phần nhận xét để ca sau đối chiếu. Đoạn này không phải bước thứ tư và không thay đổi công thức tính hạn. Ví dụ, vật màu lục tới buồng N12 ở nhịp 20 có hạn 24, không phải 33.

## Trang 8 · Phiếu Havik

**Phiếu Havik** là bản ghi điều phối cho một vật trong khu Havik. Bản ghi có mã vật, tên người thao tác, đích, nhịp mở và nhịp đến hạn. Với vật màu cam, hạn thông thường bằng nhịp mở cộng 16. Riêng đích trạm Q47 dùng hạn bằng nhịp mở cộng 8, kể cả khi màu vật khớp quy tắc thông thường. Nhân viên áp dụng ngoại lệ của đích trước khi xét màu. Quy tắc của khu khác không được dùng cho Phiếu Havik.

Phiếu cấp quyền ghi tên người được phép và nhịp giới hạn. Trong khu Havik, người đúng tên vẫn được thao tác ở chính nhịp giới hạn. Nếu nhịp hiện tại lớn hơn giới hạn hoặc tên không khớp, dừng yêu cầu trước khi lập bản ghi. Quyền đã dùng chỉ đóng sau khi bản ghi được tạo thành công. Trạng thái hiển thị ở màn hình không thay thế việc kiểm tra mã vật và mã quyền.

### Mở hồ sơ Havik

Quy trình **Mở hồ sơ Havik** thuộc khái niệm **Phiếu Havik**. Đầu vào là mã vật, tên người, nhịp hiện tại và đích. Quy trình có đúng ba bước.

1. Đối chiếu mã vật và tên trên phiếu cấp quyền, rồi kiểm tra nhịp hiện tại không vượt giới hạn.
2. Lập Phiếu Havik. Nếu đích là trạm Q47, cộng 8 để tính hạn. Nếu đích khác và vật màu cam, cộng 16.
3. Sau khi lưu bản ghi thành công, đánh dấu đang đối chiếu, đóng quyền đã dùng và thông báo hạn cho người thao tác.

Lưu ý riêng của khu: Mã trên nhãn bị mờ. Ghi hiện tượng vào phần nhận xét để ca sau đối chiếu. Đoạn này không phải bước thứ tư và không thay đổi công thức tính hạn. Ví dụ, vật màu cam tới trạm Q47 ở nhịp 20 có hạn 28, không phải 36.

## Trang 9 · Sổ Ivessa

**Sổ Ivessa** là bản ghi điều phối cho một vật trong khu Ivessa. Bản ghi có mã vật, tên người thao tác, đích, nhịp mở và nhịp đến hạn. Với vật màu đen, hạn thông thường bằng nhịp mở cộng 14. Riêng đích kho T63 dùng hạn bằng nhịp mở cộng 3, kể cả khi màu vật khớp quy tắc thông thường. Nhân viên áp dụng ngoại lệ của đích trước khi xét màu. Quy tắc của khu khác không được dùng cho Sổ Ivessa.

Phiếu cấp quyền ghi tên người được phép và nhịp giới hạn. Trong khu Ivessa, người đúng tên vẫn được thao tác ở chính nhịp giới hạn. Nếu nhịp hiện tại lớn hơn giới hạn hoặc tên không khớp, dừng yêu cầu trước khi lập bản ghi. Quyền đã dùng chỉ đóng sau khi bản ghi được tạo thành công. Trạng thái hiển thị ở màn hình không thay thế việc kiểm tra mã vật và mã quyền.

### Mở hồ sơ Ivessa

Quy trình **Mở hồ sơ Ivessa** thuộc khái niệm **Sổ Ivessa**. Đầu vào là mã vật, tên người, nhịp hiện tại và đích. Quy trình có đúng ba bước.

1. Đối chiếu mã vật và tên trên phiếu cấp quyền, rồi kiểm tra nhịp hiện tại không vượt giới hạn.
2. Lập Sổ Ivessa. Nếu đích là kho T63, cộng 3 để tính hạn. Nếu đích khác và vật màu đen, cộng 14.
3. Sau khi lưu bản ghi thành công, đánh dấu đang đóng gói, đóng quyền đã dùng và thông báo hạn cho người thao tác.

Lưu ý riêng của khu: Hộp có dấu thủng. Ghi hiện tượng vào phần nhận xét để ca sau đối chiếu. Đoạn này không phải bước thứ tư và không thay đổi công thức tính hạn. Ví dụ, vật màu đen tới kho T63 ở nhịp 20 có hạn 23, không phải 34.

## Trang 10 · Biên Jorun

**Biên Jorun** là bản ghi điều phối cho một vật trong khu Jorun. Bản ghi có mã vật, tên người thao tác, đích, nhịp mở và nhịp đến hạn. Với vật màu bạc, hạn thông thường bằng nhịp mở cộng 19. Riêng đích buồng V29 dùng hạn bằng nhịp mở cộng 6, kể cả khi màu vật khớp quy tắc thông thường. Nhân viên áp dụng ngoại lệ của đích trước khi xét màu. Quy tắc của khu khác không được dùng cho Biên Jorun.

Phiếu cấp quyền ghi tên người được phép và nhịp giới hạn. Trong khu Jorun, người đúng tên vẫn được thao tác ở chính nhịp giới hạn. Nếu nhịp hiện tại lớn hơn giới hạn hoặc tên không khớp, dừng yêu cầu trước khi lập bản ghi. Quyền đã dùng chỉ đóng sau khi bản ghi được tạo thành công. Trạng thái hiển thị ở màn hình không thay thế việc kiểm tra mã vật và mã quyền.

### Mở hồ sơ Jorun

Quy trình **Mở hồ sơ Jorun** thuộc khái niệm **Biên Jorun**. Đầu vào là mã vật, tên người, nhịp hiện tại và đích. Quy trình có đúng ba bước.

1. Đối chiếu mã vật và tên trên phiếu cấp quyền, rồi kiểm tra nhịp hiện tại không vượt giới hạn.
2. Lập Biên Jorun. Nếu đích là buồng V29, cộng 6 để tính hạn. Nếu đích khác và vật màu bạc, cộng 19.
3. Sau khi lưu bản ghi thành công, đánh dấu chờ xác nhận, đóng quyền đã dùng và thông báo hạn cho người thao tác.

Lưu ý riêng của khu: Mặt khay bị ướt. Ghi hiện tượng vào phần nhận xét để ca sau đối chiếu. Đoạn này không phải bước thứ tư và không thay đổi công thức tính hạn. Ví dụ, vật màu bạc tới buồng V29 ở nhịp 20 có hạn 26, không phải 39.

## Trang 11 · Bài tập khu Aven

Hai đề sau kiểm tra cách áp dụng **Hồ sơ Aven**. Các dữ kiện ghi trong mỗi đề thuộc riêng vật của đề đó. Không chuyển mã vật, tên người hoặc nhịp giới hạn giữa hai đề. Khi đọc câu hỏi, trước hết xác định phần yêu cầu quyết định quyền, phần yêu cầu tính hạn và phần hỏi trạng thái sau thao tác.

### Bài 1A · Tình huống ngoại lệ Aven

Người V1 đến ở nhịp 41 để đưa vật Aven-1A vào buồng Z11. Vật có màu xanh lam. Phiếu quyền của vật ghi đúng tên V1 và giới hạn nhịp 41. Hãy xác định có được lập Hồ sơ Aven hay không, tính nhịp đến hạn và nêu trạng thái cuối của vật cùng phiếu quyền. Giải thích quy tắc nào được áp dụng trước.

### Bài 1B · Kiểm tra quyền đến muộn Aven

Người W1 đến ở nhịp 43 với vật Aven-1B màu xanh lam, yêu cầu chuyển vào buồng Z11. Phiếu quyền ghi tên W1 nhưng hết hiệu lực sau nhịp 41. Hãy quyết định có tạo Hồ sơ Aven hay không. Nếu không, hãy cho biết thao tác dừng trước bước nào và dữ kiện nào dẫn tới quyết định đó. Đề này không có lời giải trong tài liệu.

Gợi ý cách trình bày: tách kết luận về quyền khỏi phép tính thời hạn. Dữ kiện về đích và màu có thể ảnh hưởng đến hạn, còn điều kiện tên và nhịp ảnh hưởng đến quyền thao tác. Khi viết kết quả, giữ lại mã vật để người đọc biết đang giải đề nào. Gợi ý trình bày này không phải lời giải và không bổ sung dữ kiện cho đề.

## Trang 12 · Bài tập khu Belor

Hai đề sau kiểm tra cách áp dụng **Phiếu Belor**. Các dữ kiện ghi trong mỗi đề thuộc riêng vật của đề đó. Không chuyển mã vật, tên người hoặc nhịp giới hạn giữa hai đề. Khi đọc câu hỏi, trước hết xác định phần yêu cầu quyết định quyền, phần yêu cầu tính hạn và phần hỏi trạng thái sau thao tác.

### Bài 2A · Tình huống ngoại lệ Belor

Người V2 đến ở nhịp 44 để đưa vật Belor-2A vào kho R24. Vật có màu đỏ. Phiếu quyền của vật ghi đúng tên V2 và giới hạn nhịp 44. Hãy xác định có được lập Phiếu Belor hay không, tính nhịp đến hạn và nêu trạng thái cuối của vật cùng phiếu quyền. Giải thích quy tắc nào được áp dụng trước.

### Bài 2B · Kiểm tra quyền đến muộn Belor

Người W2 đến ở nhịp 46 với vật Belor-2B màu đỏ, yêu cầu chuyển vào kho R24. Phiếu quyền ghi tên W2 nhưng hết hiệu lực sau nhịp 44. Hãy quyết định có tạo Phiếu Belor hay không. Nếu không, hãy cho biết thao tác dừng trước bước nào và dữ kiện nào dẫn tới quyết định đó. Đề này không có lời giải trong tài liệu.

Gợi ý cách trình bày: tách kết luận về quyền khỏi phép tính thời hạn. Dữ kiện về đích và màu có thể ảnh hưởng đến hạn, còn điều kiện tên và nhịp ảnh hưởng đến quyền thao tác. Khi viết kết quả, giữ lại mã vật để người đọc biết đang giải đề nào. Gợi ý trình bày này không phải lời giải và không bổ sung dữ kiện cho đề.

## Trang 13 · Bài tập khu Cirva

Hai đề sau kiểm tra cách áp dụng **Sổ Cirva**. Các dữ kiện ghi trong mỗi đề thuộc riêng vật của đề đó. Không chuyển mã vật, tên người hoặc nhịp giới hạn giữa hai đề. Khi đọc câu hỏi, trước hết xác định phần yêu cầu quyết định quyền, phần yêu cầu tính hạn và phần hỏi trạng thái sau thao tác.

### Bài 3A · Tình huống ngoại lệ Cirva

Người V3 đến ở nhịp 47 để đưa vật Cirva-3A vào trạm M08. Vật có màu trắng. Phiếu quyền của vật ghi đúng tên V3 và giới hạn nhịp 47. Hãy xác định có được lập Sổ Cirva hay không, tính nhịp đến hạn và nêu trạng thái cuối của vật cùng phiếu quyền. Giải thích quy tắc nào được áp dụng trước.

### Bài 3B · Kiểm tra quyền đến muộn Cirva

Người W3 đến ở nhịp 49 với vật Cirva-3B màu trắng, yêu cầu chuyển vào trạm M08. Phiếu quyền ghi tên W3 nhưng hết hiệu lực sau nhịp 47. Hãy quyết định có tạo Sổ Cirva hay không. Nếu không, hãy cho biết thao tác dừng trước bước nào và dữ kiện nào dẫn tới quyết định đó. Đề này không có lời giải trong tài liệu.

Gợi ý cách trình bày: tách kết luận về quyền khỏi phép tính thời hạn. Dữ kiện về đích và màu có thể ảnh hưởng đến hạn, còn điều kiện tên và nhịp ảnh hưởng đến quyền thao tác. Khi viết kết quả, giữ lại mã vật để người đọc biết đang giải đề nào. Gợi ý trình bày này không phải lời giải và không bổ sung dữ kiện cho đề.

## Trang 14 · Bài tập khu Doren

Hai đề sau kiểm tra cách áp dụng **Biên Doren**. Các dữ kiện ghi trong mỗi đề thuộc riêng vật của đề đó. Không chuyển mã vật, tên người hoặc nhịp giới hạn giữa hai đề. Khi đọc câu hỏi, trước hết xác định phần yêu cầu quyết định quyền, phần yêu cầu tính hạn và phần hỏi trạng thái sau thao tác.

### Bài 4A · Tình huống ngoại lệ Doren

Người V4 đến ở nhịp 50 để đưa vật Doren-4A vào buồng K19. Vật có màu vàng. Phiếu quyền của vật ghi đúng tên V4 và giới hạn nhịp 50. Hãy xác định có được lập Biên Doren hay không, tính nhịp đến hạn và nêu trạng thái cuối của vật cùng phiếu quyền. Giải thích quy tắc nào được áp dụng trước.

### Bài 4B · Kiểm tra quyền đến muộn Doren

Người W4 đến ở nhịp 52 với vật Doren-4B màu vàng, yêu cầu chuyển vào buồng K19. Phiếu quyền ghi tên W4 nhưng hết hiệu lực sau nhịp 50. Hãy quyết định có tạo Biên Doren hay không. Nếu không, hãy cho biết thao tác dừng trước bước nào và dữ kiện nào dẫn tới quyết định đó. Đề này không có lời giải trong tài liệu.

Gợi ý cách trình bày: tách kết luận về quyền khỏi phép tính thời hạn. Dữ kiện về đích và màu có thể ảnh hưởng đến hạn, còn điều kiện tên và nhịp ảnh hưởng đến quyền thao tác. Khi viết kết quả, giữ lại mã vật để người đọc biết đang giải đề nào. Gợi ý trình bày này không phải lời giải và không bổ sung dữ kiện cho đề.

## Trang 15 · Bài tập khu Elvix

Hai đề sau kiểm tra cách áp dụng **Mã Elvix**. Các dữ kiện ghi trong mỗi đề thuộc riêng vật của đề đó. Không chuyển mã vật, tên người hoặc nhịp giới hạn giữa hai đề. Khi đọc câu hỏi, trước hết xác định phần yêu cầu quyết định quyền, phần yêu cầu tính hạn và phần hỏi trạng thái sau thao tác.

### Bài 5A · Tình huống ngoại lệ Elvix

Người V5 đến ở nhịp 53 để đưa vật Elvix-5A vào trạm P31. Vật có màu tím. Phiếu quyền của vật ghi đúng tên V5 và giới hạn nhịp 53. Hãy xác định có được lập Mã Elvix hay không, tính nhịp đến hạn và nêu trạng thái cuối của vật cùng phiếu quyền. Giải thích quy tắc nào được áp dụng trước.

### Bài 5B · Kiểm tra quyền đến muộn Elvix

Người W5 đến ở nhịp 55 với vật Elvix-5B màu tím, yêu cầu chuyển vào trạm P31. Phiếu quyền ghi tên W5 nhưng hết hiệu lực sau nhịp 53. Hãy quyết định có tạo Mã Elvix hay không. Nếu không, hãy cho biết thao tác dừng trước bước nào và dữ kiện nào dẫn tới quyết định đó. Đề này không có lời giải trong tài liệu.

Gợi ý cách trình bày: tách kết luận về quyền khỏi phép tính thời hạn. Dữ kiện về đích và màu có thể ảnh hưởng đến hạn, còn điều kiện tên và nhịp ảnh hưởng đến quyền thao tác. Khi viết kết quả, giữ lại mã vật để người đọc biết đang giải đề nào. Gợi ý trình bày này không phải lời giải và không bổ sung dữ kiện cho đề.

## Trang 16 · Bài tập khu Faren

Hai đề sau kiểm tra cách áp dụng **Thẻ Faren**. Các dữ kiện ghi trong mỗi đề thuộc riêng vật của đề đó. Không chuyển mã vật, tên người hoặc nhịp giới hạn giữa hai đề. Khi đọc câu hỏi, trước hết xác định phần yêu cầu quyết định quyền, phần yêu cầu tính hạn và phần hỏi trạng thái sau thao tác.

### Bài 6A · Tình huống ngoại lệ Faren

Người V6 đến ở nhịp 56 để đưa vật Faren-6A vào kho H05. Vật có màu xám. Phiếu quyền của vật ghi đúng tên V6 và giới hạn nhịp 56. Hãy xác định có được lập Thẻ Faren hay không, tính nhịp đến hạn và nêu trạng thái cuối của vật cùng phiếu quyền. Giải thích quy tắc nào được áp dụng trước.

### Bài 6B · Kiểm tra quyền đến muộn Faren

Người W6 đến ở nhịp 58 với vật Faren-6B màu xám, yêu cầu chuyển vào kho H05. Phiếu quyền ghi tên W6 nhưng hết hiệu lực sau nhịp 56. Hãy quyết định có tạo Thẻ Faren hay không. Nếu không, hãy cho biết thao tác dừng trước bước nào và dữ kiện nào dẫn tới quyết định đó. Đề này không có lời giải trong tài liệu.

Gợi ý cách trình bày: tách kết luận về quyền khỏi phép tính thời hạn. Dữ kiện về đích và màu có thể ảnh hưởng đến hạn, còn điều kiện tên và nhịp ảnh hưởng đến quyền thao tác. Khi viết kết quả, giữ lại mã vật để người đọc biết đang giải đề nào. Gợi ý trình bày này không phải lời giải và không bổ sung dữ kiện cho đề.

## Trang 17 · Bài tập khu Givon

Hai đề sau kiểm tra cách áp dụng **Hồ sơ Givon**. Các dữ kiện ghi trong mỗi đề thuộc riêng vật của đề đó. Không chuyển mã vật, tên người hoặc nhịp giới hạn giữa hai đề. Khi đọc câu hỏi, trước hết xác định phần yêu cầu quyết định quyền, phần yêu cầu tính hạn và phần hỏi trạng thái sau thao tác.

### Bài 7A · Tình huống ngoại lệ Givon

Người V7 đến ở nhịp 59 để đưa vật Givon-7A vào buồng N12. Vật có màu lục. Phiếu quyền của vật ghi đúng tên V7 và giới hạn nhịp 59. Hãy xác định có được lập Hồ sơ Givon hay không, tính nhịp đến hạn và nêu trạng thái cuối của vật cùng phiếu quyền. Giải thích quy tắc nào được áp dụng trước.

### Bài 7B · Kiểm tra quyền đến muộn Givon

Người W7 đến ở nhịp 61 với vật Givon-7B màu lục, yêu cầu chuyển vào buồng N12. Phiếu quyền ghi tên W7 nhưng hết hiệu lực sau nhịp 59. Hãy quyết định có tạo Hồ sơ Givon hay không. Nếu không, hãy cho biết thao tác dừng trước bước nào và dữ kiện nào dẫn tới quyết định đó. Đề này không có lời giải trong tài liệu.

Gợi ý cách trình bày: tách kết luận về quyền khỏi phép tính thời hạn. Dữ kiện về đích và màu có thể ảnh hưởng đến hạn, còn điều kiện tên và nhịp ảnh hưởng đến quyền thao tác. Khi viết kết quả, giữ lại mã vật để người đọc biết đang giải đề nào. Gợi ý trình bày này không phải lời giải và không bổ sung dữ kiện cho đề.

## Trang 18 · Bài tập khu Havik

Hai đề sau kiểm tra cách áp dụng **Phiếu Havik**. Các dữ kiện ghi trong mỗi đề thuộc riêng vật của đề đó. Không chuyển mã vật, tên người hoặc nhịp giới hạn giữa hai đề. Khi đọc câu hỏi, trước hết xác định phần yêu cầu quyết định quyền, phần yêu cầu tính hạn và phần hỏi trạng thái sau thao tác.

### Bài 8A · Tình huống ngoại lệ Havik

Người V8 đến ở nhịp 62 để đưa vật Havik-8A vào trạm Q47. Vật có màu cam. Phiếu quyền của vật ghi đúng tên V8 và giới hạn nhịp 62. Hãy xác định có được lập Phiếu Havik hay không, tính nhịp đến hạn và nêu trạng thái cuối của vật cùng phiếu quyền. Giải thích quy tắc nào được áp dụng trước.

### Bài 8B · Kiểm tra quyền đến muộn Havik

Người W8 đến ở nhịp 64 với vật Havik-8B màu cam, yêu cầu chuyển vào trạm Q47. Phiếu quyền ghi tên W8 nhưng hết hiệu lực sau nhịp 62. Hãy quyết định có tạo Phiếu Havik hay không. Nếu không, hãy cho biết thao tác dừng trước bước nào và dữ kiện nào dẫn tới quyết định đó. Đề này không có lời giải trong tài liệu.

Gợi ý cách trình bày: tách kết luận về quyền khỏi phép tính thời hạn. Dữ kiện về đích và màu có thể ảnh hưởng đến hạn, còn điều kiện tên và nhịp ảnh hưởng đến quyền thao tác. Khi viết kết quả, giữ lại mã vật để người đọc biết đang giải đề nào. Gợi ý trình bày này không phải lời giải và không bổ sung dữ kiện cho đề.

## Trang 19 · Bài tập khu Ivessa

Hai đề sau kiểm tra cách áp dụng **Sổ Ivessa**. Các dữ kiện ghi trong mỗi đề thuộc riêng vật của đề đó. Không chuyển mã vật, tên người hoặc nhịp giới hạn giữa hai đề. Khi đọc câu hỏi, trước hết xác định phần yêu cầu quyết định quyền, phần yêu cầu tính hạn và phần hỏi trạng thái sau thao tác.

### Bài 9A · Tình huống ngoại lệ Ivessa

Người V9 đến ở nhịp 65 để đưa vật Ivessa-9A vào kho T63. Vật có màu đen. Phiếu quyền của vật ghi đúng tên V9 và giới hạn nhịp 65. Hãy xác định có được lập Sổ Ivessa hay không, tính nhịp đến hạn và nêu trạng thái cuối của vật cùng phiếu quyền. Giải thích quy tắc nào được áp dụng trước.

### Bài 9B · Kiểm tra quyền đến muộn Ivessa

Người W9 đến ở nhịp 67 với vật Ivessa-9B màu đen, yêu cầu chuyển vào kho T63. Phiếu quyền ghi tên W9 nhưng hết hiệu lực sau nhịp 65. Hãy quyết định có tạo Sổ Ivessa hay không. Nếu không, hãy cho biết thao tác dừng trước bước nào và dữ kiện nào dẫn tới quyết định đó. Đề này không có lời giải trong tài liệu.

Gợi ý cách trình bày: tách kết luận về quyền khỏi phép tính thời hạn. Dữ kiện về đích và màu có thể ảnh hưởng đến hạn, còn điều kiện tên và nhịp ảnh hưởng đến quyền thao tác. Khi viết kết quả, giữ lại mã vật để người đọc biết đang giải đề nào. Gợi ý trình bày này không phải lời giải và không bổ sung dữ kiện cho đề.

## Trang 20 · Bài tập khu Jorun

Hai đề sau kiểm tra cách áp dụng **Biên Jorun**. Các dữ kiện ghi trong mỗi đề thuộc riêng vật của đề đó. Không chuyển mã vật, tên người hoặc nhịp giới hạn giữa hai đề. Khi đọc câu hỏi, trước hết xác định phần yêu cầu quyết định quyền, phần yêu cầu tính hạn và phần hỏi trạng thái sau thao tác.

### Bài 10A · Tình huống ngoại lệ Jorun

Người V10 đến ở nhịp 68 để đưa vật Jorun-10A vào buồng V29. Vật có màu bạc. Phiếu quyền của vật ghi đúng tên V10 và giới hạn nhịp 68. Hãy xác định có được lập Biên Jorun hay không, tính nhịp đến hạn và nêu trạng thái cuối của vật cùng phiếu quyền. Giải thích quy tắc nào được áp dụng trước.

### Bài 10B · Kiểm tra quyền đến muộn Jorun

Người W10 đến ở nhịp 70 với vật Jorun-10B màu bạc, yêu cầu chuyển vào buồng V29. Phiếu quyền ghi tên W10 nhưng hết hiệu lực sau nhịp 68. Hãy quyết định có tạo Biên Jorun hay không. Nếu không, hãy cho biết thao tác dừng trước bước nào và dữ kiện nào dẫn tới quyết định đó. Đề này không có lời giải trong tài liệu.

Gợi ý cách trình bày: tách kết luận về quyền khỏi phép tính thời hạn. Dữ kiện về đích và màu có thể ảnh hưởng đến hạn, còn điều kiện tên và nhịp ảnh hưởng đến quyền thao tác. Khi viết kết quả, giữ lại mã vật để người đọc biết đang giải đề nào. Gợi ý trình bày này không phải lời giải và không bổ sung dữ kiện cho đề.

## Trang 21 · Lời giải bài 10A

Đây là lời giải riêng cho **bài 10A**, người V10 và vật Jorun-10A ở phần bài tập. Nó không giải bài 10B. Ba bước dưới đây áp dụng dữ kiện của đề, trong khi quy trình Mở hồ sơ Jorun ở đầu tài liệu mô tả thao tác chung.

1. V10 khớp tên trên phiếu và đến ở nhịp 68, đúng bằng giới hạn. Vì giới hạn được tính bao gồm nhịp cuối nên V10 được thao tác với Jorun-10A.
2. Tạo Biên Jorun ở nhịp 68. Đích buồng V29 kích hoạt ngoại lệ cộng 6, nên hạn là 74. Không cộng 19 theo màu bạc.
3. Sau khi tạo bản ghi, đánh dấu chờ xác nhận cho Jorun-10A, đóng phiếu quyền của V10 và báo hạn 74.

Khi so đáp án, kiểm tra ba điểm riêng: tên người có khớp hay không, nhịp đến có vượt giới hạn hay không và đích có thuộc ngoại lệ hay không. Một lời giải chỉ ghi đáp số 74 vẫn thiếu căn cứ. Nếu đáp án lại dùng mã Jorun-10B, người làm đã chuyển nhầm dữ kiện từ đề khác. Phần tự kiểm tra này không được đánh số và không phải bước giải thứ tư.

Nhận xét cuối mục: quy tắc ngoại lệ chỉ làm thay đổi hạn. Nó không kéo dài quyền và cũng không cho phép bỏ qua bước kiểm tra tên. Nếu khu nhận một hồ sơ có nhịp mở khác, phải tính lại theo nhịp mới thay vì sao chép đáp số của bài này. Không áp dụng công thức của khu Jorun cho vật thuộc khu khác.

## Trang 22 · Lời giải bài 9A

Đây là lời giải riêng cho **bài 9A**, người V9 và vật Ivessa-9A ở phần bài tập. Nó không giải bài 9B. Ba bước dưới đây áp dụng dữ kiện của đề, trong khi quy trình Mở hồ sơ Ivessa ở đầu tài liệu mô tả thao tác chung.

1. V9 khớp tên trên phiếu và đến ở nhịp 65, đúng bằng giới hạn. Vì giới hạn được tính bao gồm nhịp cuối nên V9 được thao tác với Ivessa-9A.
2. Tạo Sổ Ivessa ở nhịp 65. Đích kho T63 kích hoạt ngoại lệ cộng 3, nên hạn là 68. Không cộng 14 theo màu đen.
3. Sau khi tạo bản ghi, đánh dấu đang đóng gói cho Ivessa-9A, đóng phiếu quyền của V9 và báo hạn 68.

Khi so đáp án, kiểm tra ba điểm riêng: tên người có khớp hay không, nhịp đến có vượt giới hạn hay không và đích có thuộc ngoại lệ hay không. Một lời giải chỉ ghi đáp số 68 vẫn thiếu căn cứ. Nếu đáp án lại dùng mã Ivessa-9B, người làm đã chuyển nhầm dữ kiện từ đề khác. Phần tự kiểm tra này không được đánh số và không phải bước giải thứ tư.

Nhận xét cuối mục: quy tắc ngoại lệ chỉ làm thay đổi hạn. Nó không kéo dài quyền và cũng không cho phép bỏ qua bước kiểm tra tên. Nếu khu nhận một hồ sơ có nhịp mở khác, phải tính lại theo nhịp mới thay vì sao chép đáp số của bài này. Không áp dụng công thức của khu Ivessa cho vật thuộc khu khác.

## Trang 23 · Lời giải bài 8A

Đây là lời giải riêng cho **bài 8A**, người V8 và vật Havik-8A ở phần bài tập. Nó không giải bài 8B. Ba bước dưới đây áp dụng dữ kiện của đề, trong khi quy trình Mở hồ sơ Havik ở đầu tài liệu mô tả thao tác chung.

1. V8 khớp tên trên phiếu và đến ở nhịp 62, đúng bằng giới hạn. Vì giới hạn được tính bao gồm nhịp cuối nên V8 được thao tác với Havik-8A.
2. Tạo Phiếu Havik ở nhịp 62. Đích trạm Q47 kích hoạt ngoại lệ cộng 8, nên hạn là 70. Không cộng 16 theo màu cam.
3. Sau khi tạo bản ghi, đánh dấu đang đối chiếu cho Havik-8A, đóng phiếu quyền của V8 và báo hạn 70.

Khi so đáp án, kiểm tra ba điểm riêng: tên người có khớp hay không, nhịp đến có vượt giới hạn hay không và đích có thuộc ngoại lệ hay không. Một lời giải chỉ ghi đáp số 70 vẫn thiếu căn cứ. Nếu đáp án lại dùng mã Havik-8B, người làm đã chuyển nhầm dữ kiện từ đề khác. Phần tự kiểm tra này không được đánh số và không phải bước giải thứ tư.

Nhận xét cuối mục: quy tắc ngoại lệ chỉ làm thay đổi hạn. Nó không kéo dài quyền và cũng không cho phép bỏ qua bước kiểm tra tên. Nếu khu nhận một hồ sơ có nhịp mở khác, phải tính lại theo nhịp mới thay vì sao chép đáp số của bài này. Không áp dụng công thức của khu Havik cho vật thuộc khu khác.

## Trang 24 · Lời giải bài 7A

Đây là lời giải riêng cho **bài 7A**, người V7 và vật Givon-7A ở phần bài tập. Nó không giải bài 7B. Ba bước dưới đây áp dụng dữ kiện của đề, trong khi quy trình Mở hồ sơ Givon ở đầu tài liệu mô tả thao tác chung.

1. V7 khớp tên trên phiếu và đến ở nhịp 59, đúng bằng giới hạn. Vì giới hạn được tính bao gồm nhịp cuối nên V7 được thao tác với Givon-7A.
2. Tạo Hồ sơ Givon ở nhịp 59. Đích buồng N12 kích hoạt ngoại lệ cộng 4, nên hạn là 63. Không cộng 13 theo màu lục.
3. Sau khi tạo bản ghi, đánh dấu chờ làm nguội cho Givon-7A, đóng phiếu quyền của V7 và báo hạn 63.

Khi so đáp án, kiểm tra ba điểm riêng: tên người có khớp hay không, nhịp đến có vượt giới hạn hay không và đích có thuộc ngoại lệ hay không. Một lời giải chỉ ghi đáp số 63 vẫn thiếu căn cứ. Nếu đáp án lại dùng mã Givon-7B, người làm đã chuyển nhầm dữ kiện từ đề khác. Phần tự kiểm tra này không được đánh số và không phải bước giải thứ tư.

Nhận xét cuối mục: quy tắc ngoại lệ chỉ làm thay đổi hạn. Nó không kéo dài quyền và cũng không cho phép bỏ qua bước kiểm tra tên. Nếu khu nhận một hồ sơ có nhịp mở khác, phải tính lại theo nhịp mới thay vì sao chép đáp số của bài này. Không áp dụng công thức của khu Givon cho vật thuộc khu khác.

## Trang 25 · Lời giải bài 6A

Đây là lời giải riêng cho **bài 6A**, người V6 và vật Faren-6A ở phần bài tập. Nó không giải bài 6B. Ba bước dưới đây áp dụng dữ kiện của đề, trong khi quy trình Mở hồ sơ Faren ở đầu tài liệu mô tả thao tác chung.

1. V6 khớp tên trên phiếu và đến ở nhịp 56, đúng bằng giới hạn. Vì giới hạn được tính bao gồm nhịp cuối nên V6 được thao tác với Faren-6A.
2. Tạo Thẻ Faren ở nhịp 56. Đích kho H05 kích hoạt ngoại lệ cộng 5, nên hạn là 61. Không cộng 10 theo màu xám.
3. Sau khi tạo bản ghi, đánh dấu chờ cân cho Faren-6A, đóng phiếu quyền của V6 và báo hạn 61.

Khi so đáp án, kiểm tra ba điểm riêng: tên người có khớp hay không, nhịp đến có vượt giới hạn hay không và đích có thuộc ngoại lệ hay không. Một lời giải chỉ ghi đáp số 61 vẫn thiếu căn cứ. Nếu đáp án lại dùng mã Faren-6B, người làm đã chuyển nhầm dữ kiện từ đề khác. Phần tự kiểm tra này không được đánh số và không phải bước giải thứ tư.

Nhận xét cuối mục: quy tắc ngoại lệ chỉ làm thay đổi hạn. Nó không kéo dài quyền và cũng không cho phép bỏ qua bước kiểm tra tên. Nếu khu nhận một hồ sơ có nhịp mở khác, phải tính lại theo nhịp mới thay vì sao chép đáp số của bài này. Không áp dụng công thức của khu Faren cho vật thuộc khu khác.

## Trang 26 · Lời giải bài 5A

Đây là lời giải riêng cho **bài 5A**, người V5 và vật Elvix-5A ở phần bài tập. Nó không giải bài 5B. Ba bước dưới đây áp dụng dữ kiện của đề, trong khi quy trình Mở hồ sơ Elvix ở đầu tài liệu mô tả thao tác chung.

1. V5 khớp tên trên phiếu và đến ở nhịp 53, đúng bằng giới hạn. Vì giới hạn được tính bao gồm nhịp cuối nên V5 được thao tác với Elvix-5A.
2. Tạo Mã Elvix ở nhịp 53. Đích trạm P31 kích hoạt ngoại lệ cộng 7, nên hạn là 60. Không cộng 17 theo màu tím.
3. Sau khi tạo bản ghi, đánh dấu đang lọc cho Elvix-5A, đóng phiếu quyền của V5 và báo hạn 60.

Khi so đáp án, kiểm tra ba điểm riêng: tên người có khớp hay không, nhịp đến có vượt giới hạn hay không và đích có thuộc ngoại lệ hay không. Một lời giải chỉ ghi đáp số 60 vẫn thiếu căn cứ. Nếu đáp án lại dùng mã Elvix-5B, người làm đã chuyển nhầm dữ kiện từ đề khác. Phần tự kiểm tra này không được đánh số và không phải bước giải thứ tư.

Nhận xét cuối mục: quy tắc ngoại lệ chỉ làm thay đổi hạn. Nó không kéo dài quyền và cũng không cho phép bỏ qua bước kiểm tra tên. Nếu khu nhận một hồ sơ có nhịp mở khác, phải tính lại theo nhịp mới thay vì sao chép đáp số của bài này. Không áp dụng công thức của khu Elvix cho vật thuộc khu khác.

## Trang 27 · Lời giải bài 4A

Đây là lời giải riêng cho **bài 4A**, người V4 và vật Doren-4A ở phần bài tập. Nó không giải bài 4B. Ba bước dưới đây áp dụng dữ kiện của đề, trong khi quy trình Mở hồ sơ Doren ở đầu tài liệu mô tả thao tác chung.

1. V4 khớp tên trên phiếu và đến ở nhịp 50, đúng bằng giới hạn. Vì giới hạn được tính bao gồm nhịp cuối nên V4 được thao tác với Doren-4A.
2. Tạo Biên Doren ở nhịp 50. Đích buồng K19 kích hoạt ngoại lệ cộng 3, nên hạn là 53. Không cộng 12 theo màu vàng.
3. Sau khi tạo bản ghi, đánh dấu đang kiểm định cho Doren-4A, đóng phiếu quyền của V4 và báo hạn 53.

Khi so đáp án, kiểm tra ba điểm riêng: tên người có khớp hay không, nhịp đến có vượt giới hạn hay không và đích có thuộc ngoại lệ hay không. Một lời giải chỉ ghi đáp số 53 vẫn thiếu căn cứ. Nếu đáp án lại dùng mã Doren-4B, người làm đã chuyển nhầm dữ kiện từ đề khác. Phần tự kiểm tra này không được đánh số và không phải bước giải thứ tư.

Nhận xét cuối mục: quy tắc ngoại lệ chỉ làm thay đổi hạn. Nó không kéo dài quyền và cũng không cho phép bỏ qua bước kiểm tra tên. Nếu khu nhận một hồ sơ có nhịp mở khác, phải tính lại theo nhịp mới thay vì sao chép đáp số của bài này. Không áp dụng công thức của khu Doren cho vật thuộc khu khác.

## Trang 28 · Lời giải bài 3A

Đây là lời giải riêng cho **bài 3A**, người V3 và vật Cirva-3A ở phần bài tập. Nó không giải bài 3B. Ba bước dưới đây áp dụng dữ kiện của đề, trong khi quy trình Mở hồ sơ Cirva ở đầu tài liệu mô tả thao tác chung.

1. V3 khớp tên trên phiếu và đến ở nhịp 47, đúng bằng giới hạn. Vì giới hạn được tính bao gồm nhịp cuối nên V3 được thao tác với Cirva-3A.
2. Tạo Sổ Cirva ở nhịp 47. Đích trạm M08 kích hoạt ngoại lệ cộng 6, nên hạn là 53. Không cộng 15 theo màu trắng.
3. Sau khi tạo bản ghi, đánh dấu chờ tiếp nhận cho Cirva-3A, đóng phiếu quyền của V3 và báo hạn 53.

Khi so đáp án, kiểm tra ba điểm riêng: tên người có khớp hay không, nhịp đến có vượt giới hạn hay không và đích có thuộc ngoại lệ hay không. Một lời giải chỉ ghi đáp số 53 vẫn thiếu căn cứ. Nếu đáp án lại dùng mã Cirva-3B, người làm đã chuyển nhầm dữ kiện từ đề khác. Phần tự kiểm tra này không được đánh số và không phải bước giải thứ tư.

Nhận xét cuối mục: quy tắc ngoại lệ chỉ làm thay đổi hạn. Nó không kéo dài quyền và cũng không cho phép bỏ qua bước kiểm tra tên. Nếu khu nhận một hồ sơ có nhịp mở khác, phải tính lại theo nhịp mới thay vì sao chép đáp số của bài này. Không áp dụng công thức của khu Cirva cho vật thuộc khu khác.

## Trang 29 · Lời giải bài 2A

Đây là lời giải riêng cho **bài 2A**, người V2 và vật Belor-2A ở phần bài tập. Nó không giải bài 2B. Ba bước dưới đây áp dụng dữ kiện của đề, trong khi quy trình Mở hồ sơ Belor ở đầu tài liệu mô tả thao tác chung.

1. V2 khớp tên trên phiếu và đến ở nhịp 44, đúng bằng giới hạn. Vì giới hạn được tính bao gồm nhịp cuối nên V2 được thao tác với Belor-2A.
2. Tạo Phiếu Belor ở nhịp 44. Đích kho R24 kích hoạt ngoại lệ cộng 2, nên hạn là 46. Không cộng 9 theo màu đỏ.
3. Sau khi tạo bản ghi, đánh dấu đang chuyển cho Belor-2A, đóng phiếu quyền của V2 và báo hạn 46.

Khi so đáp án, kiểm tra ba điểm riêng: tên người có khớp hay không, nhịp đến có vượt giới hạn hay không và đích có thuộc ngoại lệ hay không. Một lời giải chỉ ghi đáp số 46 vẫn thiếu căn cứ. Nếu đáp án lại dùng mã Belor-2B, người làm đã chuyển nhầm dữ kiện từ đề khác. Phần tự kiểm tra này không được đánh số và không phải bước giải thứ tư.

Nhận xét cuối mục: quy tắc ngoại lệ chỉ làm thay đổi hạn. Nó không kéo dài quyền và cũng không cho phép bỏ qua bước kiểm tra tên. Nếu khu nhận một hồ sơ có nhịp mở khác, phải tính lại theo nhịp mới thay vì sao chép đáp số của bài này. Không áp dụng công thức của khu Belor cho vật thuộc khu khác.

## Trang 30 · Lời giải bài 1A

Đây là lời giải riêng cho **bài 1A**, người V1 và vật Aven-1A ở phần bài tập. Nó không giải bài 1B. Ba bước dưới đây áp dụng dữ kiện của đề, trong khi quy trình Mở hồ sơ Aven ở đầu tài liệu mô tả thao tác chung.

1. V1 khớp tên trên phiếu và đến ở nhịp 41, đúng bằng giới hạn. Vì giới hạn được tính bao gồm nhịp cuối nên V1 được thao tác với Aven-1A.
2. Tạo Hồ sơ Aven ở nhịp 41. Đích buồng Z11 kích hoạt ngoại lệ cộng 4, nên hạn là 45. Không cộng 11 theo màu xanh lam.
3. Sau khi tạo bản ghi, đánh dấu đang hiệu chỉnh cho Aven-1A, đóng phiếu quyền của V1 và báo hạn 45.

Khi so đáp án, kiểm tra ba điểm riêng: tên người có khớp hay không, nhịp đến có vượt giới hạn hay không và đích có thuộc ngoại lệ hay không. Một lời giải chỉ ghi đáp số 45 vẫn thiếu căn cứ. Nếu đáp án lại dùng mã Aven-1B, người làm đã chuyển nhầm dữ kiện từ đề khác. Phần tự kiểm tra này không được đánh số và không phải bước giải thứ tư.

Nhận xét cuối mục: quy tắc ngoại lệ chỉ làm thay đổi hạn. Nó không kéo dài quyền và cũng không cho phép bỏ qua bước kiểm tra tên. Nếu khu nhận một hồ sơ có nhịp mở khác, phải tính lại theo nhịp mới thay vì sao chép đáp số của bài này. Không áp dụng công thức của khu Aven cho vật thuộc khu khác.

