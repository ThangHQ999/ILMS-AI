# Tương thích temperature và lỗi index V2

Log người dùng cho thấy đã chạy V2: OpenAI từ chối temperature=0 và 0.3; Chroma thiếu/khác embedding_identity.

Thêm OPENAI_SEND_TEMPERATURE=false mặc định: bỏ tham số temperature trên cả structured parse và chat stream, dùng mặc định model. Gemini vẫn giữ temperature. Có thể bật true nếu model/endpoint thực sự hỗ trợ, không đoán theo tên model, không retry lỗi 400 lặp lại. Thay đổi áp dụng adapter chung cho V1/V2.

Retrieval kiểm tra metric/identity trước gọi embedding và vector search; khi identity sai thông báo collection, expected/actual và lệnh seed. Không gắn nhãn model cho vector cũ hoặc tự chạy seed. Người dùng cần collection mới được nạp từ dữ liệu thật, cùng provider/model/dimension và restart backend. Lỗi này độc lập với temperature.

Kiểm tra cú pháp tĩnh và đọc call sites; không chạy test/app/LLM/DB/Chroma/seed. Không xác nhận chất lượng hoặc hoạt động runtime.
