# Giới hạn tiết lộ khi hỗ trợ bài đang làm

Người dùng duyệt sửa ca học sinh chỉ tính được một phần bao đóng, AI lập tức suy ra hết và đưa kết quả cuối. Phạm vi sửa dự án AI, không chạy app/test/provider/DB.

## Thay đổi

- IntentAnalysis thêm is_practice_attempt và asks_for_solution. Intent prompt phân biệt lập luận của người học với câu hỏi định nghĩa hoặc xin trợ giúp; có learning_mode và tình trạng bài tập trong context. Attempt không có pending không tự thành evaluation hoặc bị ghi sai.
- TeachingAction thêm support_scope. Policy áp SINGLE_STEP cho PARTIAL/INCORRECT, SCAFFOLD, attempt chưa chấm được hoặc xin lời giải bài hiện tại; đóng hội thoại/đổi chủ đề/phản biện/tạo artifact không bị biến thành câu hỏi luyện tập. Đúng hoàn toàn vẫn đi nhánh ADVANCE hiện có.
- RubricService nhận learner_message/evaluation để lập đúng câu hỏi phụ. SINGLE_STEP chỉ chấp nhận một criterion. Nếu action yêu cầu câu hỏi mà không lập được câu có căn cứ, không fallback sang giải bài.
- Prompt phản hồi giới hạn một điểm vướng và một bước để người học tự làm, không nối các bước còn lại. PromptBuilder chỉ gửi một missing_element vào phần feedback cho response writer. Không hardcode đáp án bài bao đóng hoặc danh sách từ khóa học thuật.
- ResponseGenerator kiểm tra toàn bộ body + câu hỏi bằng GuidanceCheck trước khi phát các gợi ý SINGLE_STEP: có nhiều bước không, lộ kết quả cuối không, trả lời hộ câu hỏi mới không. Từ chối thì sinh lại tối đa một lần, không đạt nữa hoặc kiểm tra lỗi thì lượt thất bại. Kiểm tra citation hiện có vẫn áp dụng.
- Gợi ý có thể không stream từng token trực tiếp từ provider vì phải kiểm tra trước khi lộ đáp án; status/heartbeat vẫn hoạt động. Giải thích khái niệm thông thường giữ live stream. Thêm một LLM check trên nhánh hạn chế; nếu cần viết lại thì thêm một generation và một check nữa.
- Log theo turn_id: intent/verdict/action/support_scope và kết quả kiểm tra. Không log câu trả lời thực, đáp án nội bộ hoặc lý do suy luận dài.

## Trạng thái học

Không sửa công thức tiến độ hoặc thêm bảng. Câu hỏi phụ do rubric tạo không được đánh dấu completes_exercise_step; lượt kế tiếp không được coi trả lời đúng câu phụ là hoàn thành bước bài tập gốc. Finalize chỉ chạy sau generation/check thành công, nên lỗi kiểm tra không commit evaluation/progress/ngộ nhận của lượt đó. Lease/turn vẫn được đánh dấu failed để retry theo cơ chế có sẵn.

## Kiểm chứng

Đọc lại đường policy, rubric, generation, live callback và finalize. Kiểm tra tĩnh cú pháp Python, trường contract và prompt paths. Không chạy tests, import ứng dụng, gọi DB/LLM hoặc benchmark. Chưa có bằng chứng kiểm tra chất lượng hội thoại runtime.

GuidanceCheck là kiểm tra bằng LLM, không phải bộ chứng minh: vẫn có thể chấp nhận nhầm hoặc từ chối nhầm. Intent cũng có thể phân loại sai. Không tuyên bố triệt tiêu hoàn toàn việc giải hộ. Không mở rộng đợt sửa thành hệ thống solver/agent mới.

## Ca nghiệm thu người dùng tự chạy

1. Tạo bài khóa ứng viên đủ dữ kiện, xin gợi ý, rồi nêu chỉ tính được A/B/C vì không có phụ thuộc trực tiếp đến các thuộc tính còn lại. Mong đợi: công nhận phần đúng và gợi một quy tắc, để người học tự áp dụng; không ghi bao đóng hoàn chỉnh hay tất cả khóa.
2. Sau khi AI đưa câu hỏi phụ, trả lời một bước. Kiểm tra pending/snapshot không nhầm câu phụ thành hoàn thành bài gốc.
3. Nhập một lập luận bài tập chưa có pending. Không được tự chấm sai nhưng cũng không đưa luôn lời giải đầy đủ.
4. Xin đáp án bài đang làm: giữ hỗ trợ từng bước. Xin giải thích khái niệm độc lập: vẫn giải thích tự nhiên, không ép mọi lượt thành bài kiểm tra.
5. Kiểm tra nhánh SINGLE_STEP: không có token chứa bản nháp trước khi check chấp nhận; kiểm tra lỗi không có done/progress mới. Với protocol 2, status vẫn xuất hiện trong lúc chờ.
