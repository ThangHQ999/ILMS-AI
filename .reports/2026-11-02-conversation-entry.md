# Lời chào cho người dùng chưa tham gia lớp

**Đã hoàn tác theo yêu cầu người dùng.** Đã xóa conversation_entry.py và toàn bộ import/nhánh đặc biệt trong V2. Nội dung dưới đây chỉ là lịch sử thay đổi đã bị gỡ, không mô tả code hiện hành.

V2 trước đây đưa hi/hello qua intent và semantic retrieval nên người dùng mới gặp lỗi metadata vector dù không yêu cầu kiến thức.

Thêm conversation_entry với nhận diện chính xác lời chào và câu hướng dẫn bắt đầu; chuẩn hóa Unicode/hoa thường/khoảng trắng/dấu câu cuối. Chạy trước intent/retrieval trong V2. Không gọi LLM/embedding/graph/vector; không đòi teacher/material/topic/class. Nếu có pending thì chào và hỏi có tiếp tục không, giữ nguyên câu hỏi và tiến độ. Không chấm, không sinh evaluation hay cập nhật ngộ nhận.

Vẫn dùng accept, replay, lease, finalize và SSE token/done cho protocol 1/2; lưu hội thoại như bình thường. Không bypass FK users. Không dùng prefix matching nên câu 'hi, giải thích ...' đi luồng kiến thức; action/exercise/concept explicit cũng không bị nuốt.

Đây là xử lý hội thoại, không tự sửa index thiếu embedding_identity. Câu hỏi học thuật cần nguồn vẫn theo kiểm tra index. Nhánh không phụ thuộc truy hồi nhưng DI/lifespan ứng dụng hiện vẫn khởi tạo Chroma/Neo4j; không tuyên bố chạy khi các hạ tầng đó tắt.

Kiểm tra syntax tĩnh và đường finalize không có evaluation; không chạy test/app/DB/LLM theo yêu cầu người dùng.
