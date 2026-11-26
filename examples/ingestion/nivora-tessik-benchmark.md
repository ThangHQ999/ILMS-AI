# Trạm điều phối lăng kính Nivora Tessik

## Trang 1 · Quy tắc của trạm

Nivora Tessik là một trạm giả lập chuyên chuyển lăng kính giữa hai buồng. Mỗi lăng kính có mã riêng, chỉ số pha và một trạng thái. Hai lăng kính có cùng chỉ số pha vẫn phải được kiểm tra bằng mã riêng. Mọi sự kiện được ghi theo nhịp nguyên của đồng hồ trạm. Khi đọc nhật ký, người vận hành cần phân biệt nhịp bắt đầu chuyển với nhịp hoàn tất.

**Khóa Ulen** là quyền chuyển một lăng kính dành cho một người vận hành đến hết nhịp ghi trên khóa. Khác với nhiều quy tắc hết hạn, ở trạm này nhịp giới hạn vẫn hợp lệ. Ví dụ, khóa hết hạn ở nhịp 40 thì người có tên trên khóa vẫn dùng được ở nhịp 40, nhưng không dùng được ở nhịp 41. Người đến đúng nhịp mà sai tên cũng không được dùng khóa.

**Phiếu Sern** là bản ghi mở khi một lần chuyển bắt đầu. Phiếu ghi mã lăng kính, mã buồng đích, nhịp bắt đầu và nhịp đến hạn. Nếu chỉ số pha chia hết cho 3 thì cộng 8 nhịp, nếu không thì cộng 5 nhịp. Riêng buồng đích V09 có thời hạn cố định là nhịp bắt đầu cộng 2, bất kể chỉ số pha. Quy tắc riêng của V09 được áp dụng trước quy tắc chia hết.

**Dấu Pavo** xác nhận một lần chuyển đã kết thúc. Nó ghi mã phiếu, mã lăng kính và nhịp tiếp nhận thực tế. Chỉ cấp dấu nếu tìm thấy Phiếu Sern còn mở. Dấu xác nhận lần chuyển đã kết thúc, kể cả khi lăng kính được chuyển sang cách ly sau khi kiểm tra.

Ví dụ minh họa: lăng kính pha 12 đi tới V09 ở nhịp 20 có hạn ở nhịp 22, không phải 28. Đây là ví dụ về thứ tự áp dụng quy tắc, không phải lời giải cho bài tập bên dưới.

## Trang 2 · Quy trình vận hành

### Mở lượt chuyển

Quy trình này thuộc khái niệm **Phiếu Sern**. Nó áp dụng khi người vận hành chuẩn bị chuyển một lăng kính sang buồng đích. Phần mô tả này giới thiệu quy trình, chưa phải một thao tác.

1. Đối chiếu mã lăng kính, tên trên Khóa Ulen và nhịp hiện tại. Dừng nếu tên sai hoặc nhịp hiện tại lớn hơn nhịp giới hạn.
2. Tạo Phiếu Sern với mã buồng đích và nhịp bắt đầu. Tính hạn theo quy tắc V09 trước, rồi mới xét chỉ số pha nếu buồng đích khác V09.
3. Đánh dấu lăng kính đang chuyển và đóng Khóa Ulen đã dùng. Chỉ thay đổi trạng thái sau khi đã tạo phiếu.

Nếu mã buồng được ghi nhầm, nhân viên sửa dữ kiện đầu vào trước khi lập phiếu. Việc cập nhật mã buồng có thể làm thay đổi hạn. Nhân viên ghi hạn đã tính vào phiếu để ca sau không phải suy ra từ trí nhớ.

### Khép lượt chuyển

Quy trình này thuộc khái niệm **Dấu Pavo**. Số bước bắt đầu lại từ 1 vì đây là một quy trình riêng, áp dụng tại buồng nhận.

1. Quét mã lăng kính và tìm Phiếu Sern đang mở của đúng lăng kính đó.
2. Ghi nhịp tiếp nhận thực tế, đóng phiếu và cấp Dấu Pavo với mã phiếu và mã lăng kính.
3. Kiểm tra cạnh lăng kính. Nếu cạnh mẻ, đặt trạng thái cách ly. Nếu nguyên vẹn, đặt trạng thái sẵn sàng.

Trạng thái cách ly không làm mất Dấu Pavo đã cấp. Không được diễn giải bước kiểm tra cạnh như điều kiện để bỏ qua thao tác ghi nhận tiếp nhận.

## Trang 3 · Bài tập

### Bài A · Mở phiếu cho lăng kính R17

Người vận hành Elun đến ở nhịp 66. Khóa Ulen của lăng kính R17 ghi tên Elun và giới hạn nhịp 66. Chỉ số pha là 15, buồng đích là V09. Hãy xác định Elun có quyền chuyển không, tính nhịp đến hạn và nêu trạng thái cuối của lăng kính cùng khóa. Bài này vận dụng Phiếu Sern và điều kiện của Khóa Ulen.

### Bài B · Tiếp nhận lăng kính Q24

Lăng kính Q24 đến ở nhịp 75, có Phiếu Sern PS29 đang mở và một cạnh bị mẻ. Hãy nêu ba thông tin ghi trên Dấu Pavo, trạng thái của phiếu sau khi tiếp nhận và trạng thái của lăng kính. Bài này vận dụng Dấu Pavo. Tài liệu không cung cấp lời giải cho bài B.

### Lời giải bài A

Các bước dưới đây chỉ giải bài A về Elun và R17.

1. Elun đúng tên trên khóa và đến ở nhịp 66. Vì trạm cho phép dùng khóa tại đúng nhịp giới hạn, Elun có quyền chuyển R17.
2. Buồng đích V09 kích hoạt quy tắc riêng, cộng 2 vào nhịp 66. Hạn là nhịp 68, dù pha 15 chia hết cho 3.
3. Sau khi lập Phiếu Sern, đặt R17 ở trạng thái đang chuyển và đóng Khóa Ulen đã dùng.

Khi tự kiểm tra, người học cần giải thích cả điều kiện tại nhịp giới hạn và lý do ngoại lệ V09 được ưu tiên. Việc chỉ ghi đáp số 68 chưa cho thấy người học đã áp dụng đúng cả hai quy tắc.
