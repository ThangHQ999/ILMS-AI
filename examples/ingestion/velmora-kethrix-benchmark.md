# Kho phiến Velmora Kethrix

## Trang 1 · Khái niệm và quy tắc

Velmora Kethrix là một kho giả lập để luyện đọc quy tắc nghiệp vụ. Tên gọi, mã và các phép tính bên dưới được đặt riêng cho bài này. Mỗi vật trong kho được gọi là phiến, có một mã, một dấu nhịp và một trạng thái. Hai phiến trùng màu vẫn được theo dõi riêng bằng mã. Kho sử dụng đồng hồ tính theo nhịp nguyên. Nếu hai thao tác cùng diễn ra trong một nhịp, người vận hành hoàn tất thao tác đã nhận trước rồi mới xử lý thao tác sau.

**Neo Vez** là quyền nhận một phiến dành riêng cho một người đến trước nhịp hết hạn. Nếu Neo Vez hết hạn ở nhịp 40, người được chỉ định còn quyền ở nhịp 39 và hết quyền ngay tại nhịp 40. Màu phiến và danh tính người đến trước không làm thay đổi điều kiện này. Nếu phiến chưa có Neo Vez thì kho có thể nhận yêu cầu mới theo quy định tại quầy.

**Phiếu Keth** là bản ghi mở khi phiến được giao đi. Nó chứa mã phiến, tên người nhận, nhịp giao và nhịp hoàn trả. Trong kho này, nhịp hoàn trả bằng nhịp giao cộng 13 khi dấu nhịp là chẵn, hoặc cộng 9 khi dấu nhịp là lẻ. Tính chẵn lẻ dùng dấu nhịp của phiến, không dùng nhịp giao. Mỗi phiến có tối đa một Phiếu Keth đang mở.

**Dấu Orv** là bản xác nhận hoàn trả. Nó ghi mã phiến, mã Phiếu Keth vừa đóng và nhịp hoàn trả thực tế. Nếu chưa tìm thấy phiếu đang mở thì chưa tạo Dấu Orv. Việc trả muộn không làm mất các thông tin cần ghi trên xác nhận.

Ví dụ, một phiến mang dấu 8 được giao ở nhịp 31 có hạn trả ở nhịp 44. Dấu 8 quyết định cộng 13 dù nhịp giao 31 là số lẻ. Đây là ví dụ minh họa phép tính và không phải đề bài.

## Trang 2 · Hai quy trình nghiệp vụ

Quy trình **Mở lượt mang phiến** thuộc khái niệm Phiếu Keth. Nhân viên thực hiện khi người nhận đến lấy một phiến cụ thể. Cần có mã phiến, tên người nhận và nhịp hiện tại trước khi bắt đầu.

Bước 1: Đối chiếu mã phiến và tên người nhận. Nếu có Neo Vez, kiểm tra tên khớp và nhịp hiện tại nhỏ hơn nhịp hết hạn.

Bước 2: Tạo Phiếu Keth với nhịp giao hiện tại. Tính hạn trả bằng cách cộng 13 nếu dấu phiến chẵn hoặc cộng 9 nếu dấu phiến lẻ.

Bước 3: Chuyển phiến sang trạng thái đang mang, đóng Neo Vez đã dùng nếu có và thông báo hạn trả cho người nhận.

Nếu kiểm tra không đạt, dừng trước khi lập phiếu. Nếu không tạo được phiếu, giữ nguyên trạng thái của phiến. Ví dụ, một người có tên đúng nhưng đến đúng nhịp hết hạn vẫn không nhận theo Neo Vez cũ. Người đó có thể gửi một yêu cầu mới nếu kho cho phép, nhưng yêu cầu mới không tự động kéo dài quyền cũ.

Quy trình **Khép lượt mang phiến** thuộc khái niệm Dấu Orv. Nhân viên thực hiện khi nhận lại một phiến đã giao đi.

Bước 1: Quét mã phiến và tìm Phiếu Keth đang mở tương ứng.

Bước 2: Ghi nhịp trả thực tế, đóng Phiếu Keth và tạo Dấu Orv chứa mã phiến, mã phiếu vừa đóng và nhịp trả.

Bước 3: Kiểm tra mặt phiến. Nếu mặt phiến nứt thì chuyển sang trạng thái cách ly, nếu nguyên vẹn thì chuyển sang trạng thái sẵn sàng.

Một phiến nứt vẫn có thể được trả đúng thủ tục. Trạng thái cách ly chỉ xác định phiến có thể giao tiếp cho người khác hay chưa. Mã Dấu Orv giúp nhân viên ca sau kiểm tra lại lần trả, kể cả khi đã có thêm thao tác kiểm định sau đó.

## Trang 3 · Bài tập và lời giải

### Bài tập A · Nhận phiến XQ17

Người Sira đến nhận phiến XQ17 ở nhịp 52. Phiến mang dấu 7 và có Neo Vez cho Sira đến trước nhịp 53. Hãy xác định Sira có thể nhận phiến không, tính nhịp hoàn trả và mô tả trạng thái cuối của phiến cùng Neo Vez.

### Bài tập B · Trả phiến TM28

Phiến TM28 được mang về ở nhịp 71. Phiếu Keth đang mở có mã PK66. Khi kiểm tra, nhân viên thấy mặt phiến nứt. Hãy liệt kê thông tin trên Dấu Orv, nêu trạng thái cuối của Phiếu Keth và quyết định phiến có sẵn sàng để giao tiếp không.

### Lời giải bài tập A

Phần này chỉ giải bài A về phiến XQ17. Bài B được để cho người học tự giải.

Bước 1: Sira đúng tên và đến ở nhịp 52, nhỏ hơn nhịp hết hạn 53. Vì vậy Sira có thể nhận XQ17.

Bước 2: Dấu 7 là số lẻ nên cộng 9 vào nhịp giao 52. Nhịp hoàn trả là 61.

Bước 3: Chuyển XQ17 sang trạng thái đang mang và đóng Neo Vez đã dùng cho Sira. Thông báo nhịp trả 61.

Khi giải thích kết quả, cần chỉ ra đại lượng quyết định cộng 9. Đáp số 61 chỉ có ý nghĩa khi người học xác định đúng dấu của phiến và nhịp giao. Phần lời giải này không thay đổi quy tắc tổng quát của kho.
