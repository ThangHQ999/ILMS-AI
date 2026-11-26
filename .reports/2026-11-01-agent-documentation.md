# Đợt tạo tài liệu điều khiển agent

## Phạm vi

Theo yêu cầu người dùng: lập kế hoạch chi tiết và tạo AGENTS.md, ARCHITECTURE.md, TASK.md, .agents/, .docs/, .reports/. Không sửa ứng dụng hay triển khai DB.

## Nguồn và hiện trạng

Đọc lại danh sách file, git status, app/main.py, router chính, cấu trúc SocraticChatService/ChromaVectorRepository và model session. Kết hợp quyết định và schema người dùng đã cung cấp trong cuộc chat.

Working tree có sửa đổi/xóa file src và app/ chưa được Git theo dõi từ trước. Không thay đổi các phần đó. Không mở .env.

## Kết quả

- Tạo quy tắc, bản đồ kiến trúc hiện tại/đích và task backlog.
- Ghi quyết định đã thay thế để agent sau không quay về phương án heatmap/state cũ.
- Tạo kế hoạch P0–P7, contract dữ liệu/SSE và chính sách dạy học.
- Ghi rõ Topic do backend tự suy ra; workflow duyệt rubric ngoài phạm vi chat.
- Tạo workflow đọc/triển khai/review và mẫu bàn giao.

## Kiểm tra

Đã kiểm tra 14 file tài liệu, không có liên kết Markdown nội bộ hỏng. Đối chiếu trạng thái Git trước/sau: các đường dẫn mới là bộ tài liệu yêu cầu; các thay đổi ứng dụng có sẵn được giữ nguyên. Đã rà tính nhất quán về Topic, ranh giới ingestion/chat, ba bảng mới và phạm vi chưa được phép triển khai. Không chạy ứng dụng, test, migration, seed, DB hoặc LLM.

## Giới hạn

Chưa xác nhận schema DB thật, migration đã áp dụng hay runtime. Ba bảng SQL đã trao đổi vẫn là bản thiết kế cần đối chiếu. Backlog service chưa bắt đầu; chỉ cho phép triển khai sau khi người dùng duyệt phạm vi.
