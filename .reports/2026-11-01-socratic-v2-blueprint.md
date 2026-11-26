# Kế hoạch triển khai chi tiết Socratic V2

## Phạm vi

Người dùng yêu cầu viết file thật chi tiết về nghiệp vụ, code và các phần triển khai của phiên bản đã thống nhất. Chỉ tạo/cập nhật tài liệu, không sửa ứng dụng/migration.

## Nguồn đã đọc

AGENTS.md, TASK.md, decisions/open-questions/kế hoạch/contract hiện có; LLMService, endpoint chat, dependency MySQL, ProcessRepository, schema/message model, luồng service và đoạn repository chat/subgraph liên quan. Không đọc DB hay secret.

## Kết quả

Tạo `.docs/socratic-chat-implementation-blueprint.md` gồm 27 phần: mục tiêu quan sát được, module/chữ ký dự kiến, API/state, nhận diện Topic theo chunk, retrieval, rubric/evaluation, policy, backtracking, bài tập, prompt, artifact, SSE, hiệu năng, transaction/retry, tiến độ, failure paths, ví dụ, gói code và nghiệm thu.

Làm rõ các bổ sung chưa được duyệt vào SQL nháp: turn metadata và khóa/lease; nơi lưu artifact nội bộ/public; công thức mastery. Không tự thêm bảng thứ tư hay tuyên bố ba bảng đã đủ xử lý retry.

## Kiểm tra và giới hạn

Đã kiểm tra 27 phần đánh số, 641 dòng, 16 dấu mở/đóng code fence cân bằng và không có liên kết file hỏng trong .docs/.reports. Đã rà nội dung về trạng thái phê duyệt và bổ sung schema. Không chạy app/test/benchmark/DB/LLM. Đây là kế hoạch thiết kế, không phải bằng chứng hệ thống đáp ứng chất lượng hoặc thời gian phản hồi.
