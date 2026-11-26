# Quản lý mượn trả trong thư viện mô phỏng

## Trang 1 · Các khái niệm của hệ thống

Tài liệu này mô tả một thư viện giả lập dùng để học cách phân biệt quy tắc nghiệp vụ, quy trình, ví dụ và bài tập. Các mã độc giả, mã bản sách và thời hạn đều được đặt riêng cho mô hình này. Mỗi bản sách vật lý có một mã riêng. Hai bản cùng nhan đề vẫn có thể ở hai trạng thái khác nhau. Độc giả tìm tài liệu theo nhan đề, nhưng nhân viên thao tác mượn trả trên mã bản sách.

**Giữ chỗ** là việc dành một bản sách đang sẵn sàng cho một độc giả đến một thời điểm hết hạn. Trong thời gian giữ chỗ còn hiệu lực, chỉ người được ghi tên mới có thể nhận bản đó. Khi thời hạn kết thúc mà chưa nhận, hệ thống giải phóng giữ chỗ. Giữ chỗ không thay đổi thời hạn của một lượt mượn vì lượt mượn chỉ bắt đầu khi bàn giao bản sách.

**Lượt mượn** là bản ghi nối một độc giả với một bản sách đã bàn giao, gồm thời điểm mượn và hạn trả. Mỗi bản sách chỉ có tối đa một lượt mượn đang mở. Trong mô hình này, hạn trả là ngày bàn giao cộng bảy ngày. Ngày bàn giao được tính là ngày bắt đầu, không phải ngày thứ nhất trong bảy ngày cộng thêm.

**Biên nhận trả** là xác nhận rằng nhân viên đã tiếp nhận bản sách và đóng lượt mượn tương ứng. Biên nhận ghi mã bản sách, thời điểm trả và mã lượt mượn. Việc hệ thống in biên nhận không làm thay đổi thứ tự hàng chờ của nhan đề.

**Hàng chờ** là danh sách độc giả đăng ký một nhan đề khi chưa có bản phù hợp để nhận ngay. Thứ tự được xác định theo thời điểm đăng ký. Một vị trí trong hàng chờ chưa phải giữ chỗ trên một bản cụ thể. Chỉ khi một bản được dành cho người đầu hàng thì người đó mới có giữ chỗ.

Ví dụ, hai bản K11 và K12 cùng nhan đề. Nếu K11 đang được mượn và K12 đang được giữ cho người khác, việc tìm thấy hai bản trong danh mục không có nghĩa độc giả mới có thể mượn một trong hai.

## Trang 2 · Quy trình bàn giao bản sách

Quy trình **Bàn giao bản sách** thuộc khái niệm lượt mượn. Nhân viên dùng quy trình này khi độc giả đến quầy nhận bản cụ thể. Trước khi bắt đầu, nhân viên cần mã độc giả và mã bản sách. Quy trình có bốn bước. Thứ tự quan trọng vì hệ thống chỉ đánh dấu bản sách đang mượn sau khi đã tạo được bản ghi.

Bước 1: Đối chiếu mã độc giả và mã bản sách, rồi đọc trạng thái hiện tại của bản sách.

Bước 2: Kiểm tra điều kiện nhận. Bản sách phải sẵn sàng, hoặc có giữ chỗ còn hiệu lực dành cho chính độc giả này. Dừng bàn giao nếu điều kiện không đạt.

Bước 3: Tạo lượt mượn với mã độc giả, mã bản sách, ngày bàn giao và hạn trả bằng ngày bàn giao cộng bảy ngày.

Bước 4: Đổi trạng thái bản sách thành đang mượn và đóng giữ chỗ của người nhận nếu có. Trả thông tin hạn trả cho độc giả.

Việc nhìn thấy bản sách nằm trên quầy chỉ là một dấu hiệu vật lý. Nhân viên vẫn cần kiểm tra trạng thái trong hệ thống. Chẳng hạn, bản A22 nằm trên quầy có thể đã được dành cho độc giả B07. Nếu độc giả B08 đưa đúng mã bản A22 nhưng không có quyền nhận, kết quả kiểm tra ở bước 2 là dừng. Nhân viên có thể giới thiệu một bản khác cùng nhan đề nếu có, nhưng đó là một lần kiểm tra mới.

Trong mô hình bài học, hệ thống coi việc tạo lượt mượn và cập nhật trạng thái là một thao tác nhất quán. Nếu không tạo được bản ghi thì trạng thái bản sách vẫn giữ nguyên. Cách diễn giải này giúp người học nhận ra vì sao trạng thái trên danh mục và lượt mượn cần khớp nhau.

Ví dụ minh họa về thời hạn. Một bản sách được bàn giao ngày 10 tháng 4 thì hạn trả là ngày 17 tháng 4. Ví dụ này chỉ minh họa cách cộng ngày, không phải một bài yêu cầu tính toán.

## Trang 3 · Quy trình tiếp nhận trả sách

Quy trình **Tiếp nhận trả sách** thuộc khái niệm biên nhận trả. Đầu vào là mã bản sách đã được đưa tới quầy. Mục đích là đóng lượt mượn đang mở và xác định bản trả có thể được dành cho ai. Nếu không tìm thấy lượt mượn đang mở, nhân viên cần đối chiếu dữ liệu trước khi tiếp tục.

Bước 1: Quét mã bản sách và tìm đúng lượt mượn đang mở cho bản đó.

Bước 2: Ghi nhận thời điểm trả, đóng lượt mượn và tạo biên nhận trả theo mã lượt vừa đóng.

Bước 3: Kiểm tra hàng chờ của nhan đề. Nếu có người chờ, giữ bản sách cho người đứng đầu. Nếu hàng chờ rỗng, chuyển bản sách thành sẵn sàng.

Bước 4: Gửi biên nhận cho người trả và ghi lại trạng thái mới của bản sách để nhân viên ca sau có thể tra cứu.

Một nhan đề có thể có nhiều bản đang được mượn. Khi trả một bản, việc kiểm tra hàng chờ dựa vào nhan đề của bản đó. Nếu một người chờ đã được cấp một bản khác, hệ thống sẽ dùng hàng chờ đã cập nhật. Quy trình chỉ mô tả kết quả khi dữ liệu hàng chờ tại thời điểm xử lý đã được xác định.

Ví dụ minh họa. Bản D09 được trả lúc 14 giờ. Nhân viên tìm thấy lượt M31 đang mở và đóng lượt đó. Nhan đề không có ai chờ, nên bản D09 trở lại trạng thái sẵn sàng. Biên nhận vẫn ghi mã D09 và M31, kể cả khi một lượt mượn mới được tạo sau đó.

Nếu độc giả đưa nhầm một bản cùng nhan đề, mã bản sách trên biên nhận giúp phát hiện sự khác nhau. Hãy so mã bản trên vật phẩm với mã trên lượt mượn. Đây là một lưu ý thao tác cho nhân viên, không phải bước thứ năm của quy trình.

## Trang 4 · Bài tập áp dụng

### Bài tập A · Nhận bản sách đã giữ

Độc giả L04 đến quầy ngày 12 tháng 5 lúc 09 giờ 30. Bản sách S17 đang có giữ chỗ cho L04 tới 11 giờ cùng ngày. Nhân viên đã xác nhận mã trên bản sách đúng là S17. Hãy quyết định có bàn giao bản sách hay không, xác định ngày đến hạn và nêu trạng thái cuối của bản sách cùng giữ chỗ. Trình bày kết quả theo ba bước có lý do.

### Bài tập B · Trả bản có người chờ

Bản sách P23 thuộc nhan đề Cơ sở dữ liệu được trả lúc 15 giờ. Lượt mượn đang mở là M08. Hàng chờ của nhan đề theo thứ tự là độc giả H02 rồi H05. Hãy nêu thông tin cần có trên biên nhận, xác định người được giữ bản P23 và giải thích H05 còn ở trạng thái gì.

### Bài tập C · Kiểm tra quyền nhận bản sách

Hai bản Q31 và Q32 cùng nhan đề. Q31 có giữ chỗ còn hiệu lực cho độc giả T03, còn Q32 đang sẵn sàng. Độc giả T09 đến xin mượn Q31 và đồng ý nhận bản khác nếu được. Hãy cho biết nhân viên nên xử lý yêu cầu với Q31 thế nào, bản nào có thể được xem xét tiếp và vì sao trạng thái của mỗi bản phải được kiểm tra riêng.

Ba bài trên kiểm tra các khái niệm khác nhau. Bài A vận dụng lượt mượn và giữ chỗ. Bài B vận dụng biên nhận trả và hàng chờ. Bài C tập trung vào giữ chỗ và cách phân biệt hai bản của cùng nhan đề. Những đoạn giới thiệu mục đích này giúp người học chọn quy tắc thích hợp khi đọc đề.

## Trang 5 · Lời giải bài tập A

Phần lời giải sau đây dành riêng cho **Bài tập A về bản S17 và độc giả L04**. Bài B và bài C được để cho người học tự giải.

Bước 1: Kiểm tra người nhận và thời điểm. Giữ chỗ thuộc L04 và còn hiệu lực lúc 09 giờ 30 vì chỉ hết hạn lúc 11 giờ ngày 12 tháng 5. Do đó nhân viên có thể bàn giao S17 cho L04.

Bước 2: Tạo lượt mượn cho L04 với bản S17 vào ngày 12 tháng 5. Cộng bảy ngày theo quy tắc của mô hình, nên hạn trả là ngày 19 tháng 5.

Bước 3: Chuyển S17 thành đang mượn và đóng giữ chỗ đã được sử dụng. Nhân viên thông báo hạn trả ngày 19 tháng 5 cho L04.

Khi tự kiểm tra bài A, học sinh cần giải thích cả điều kiện về người nhận và điều kiện về thời điểm. Nếu chỉ ghi rằng bản sách được giữ chỗ, kết luận chưa đầy đủ vì giữ chỗ có thể thuộc về một người khác hoặc đã hết hạn. Ngày đến hạn phải được tính từ ngày bàn giao ghi trong đề. Trạng thái cuối phải nêu cả bản sách và giữ chỗ.

Trong thực hành, việc để lời giải xuất hiện sau những bài khác là bình thường. Nhãn bài và dữ kiện riêng giúp người đọc xác định lời giải tương ứng. Trước khi kết thúc bài học, học sinh có thể đọc lại bốn định nghĩa ở trang đầu và giải thích vì sao mỗi bước trong hai quy trình lại tác động lên một bản ghi khác nhau.
