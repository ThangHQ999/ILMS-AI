# Đánh giá luồng ingestion bốn agent

Phạm vi: đọc code, prompt, schema, merge/resolution/storage và đối chiếu contract chat; không chạy hoặc sửa ingestion/app/DB/LLM.

Người dùng xác nhận đang dùng run_pipeline tại app/service/ingestion/multi_agent.py. Chính sách vừa xác nhận: mặc định chỉ lấy tài liệu gốc; chỉ lấy/sinh thêm nội dung ngoài khi giảng viên chọn đồng ý; giảng viên duyệt đồ thị cuối. Việc nguồn ngoài là truy hồi nguồn có trích dẫn hay nội dung AI bổ sung cần phân biệt trong thiết kế, không tự coi hai loại là bằng chứng tương đương.

## Luồng quan sát

File -> load_file_content -> chunker -> Extractor từng chunk chạy gather -> nhóm năm bản thô -> Expert -> Validator ép schema -> Python merge toàn file -> entity embeddings -> cosine pairwise -> Reviewer cho cặp nghi ngờ -> apply_resolutions -> file JSON -> CustomNeo4jStorage.

Extractor/Expert/Validator gọi model riêng bằng client trực tiếp; Reviewer và embedding dùng client đồng bộ. Đây là pipeline nhiều bước, không có vòng kiểm chứng nội dung đối chiếu nguồn độc lập hoàn chỉnh. API ingestion chưa được include ở router đang chạy. app/ingest.py là luồng LightRAG riêng, không phải orchestration bốn agent này.

## Phát hiện ưu tiên cao

1. Reviewer đọc extractor_prompt.md thay vì reviewer_prompt.md (app/agents/reviewer_agent.py:13). Đầu ra merge/delete bị yêu cầu bằng schema nhưng system prompt sai nhiệm vụ.
2. Import src.* không khớp cây app hiện tại. Schema thật đang có tại app/schema/extraction_schema.py; run_pipeline/agents/utils vẫn gọi src.schemas.schemas. Không chạy để kết luận môi trường ngoài có alias src hay không.
3. Storage ghi Entity{id:name}, chat đọc KnowledgeEntity{canonical_code} và subject; ingestion không cung cấp đồng bộ scope/owner_id, ExerciseStep và rubric theo contract chat. Storage mở Neo4j session mặc định trong khi chat chọn NEO4J_DATABASE. Hai đường cần cùng contract và database.
4. Bốn-agent run_pipeline không lưu material_chunks/topic_chunks/topics vào MySQL hoặc index chunks/entity đúng contract chat. Topic được gộp thành global_topic rồi không được dùng trong bước ghi hiện tại. Luồng LightRAG riêng có storage, nhưng chưa được orchestration bốn agent liên kết bằng ID nguồn.
5. Chỉ cosine >=0.95 đã auto merge; độ gần ngữ nghĩa không chứng minh đồng nhất. Gộp theo lowercase name trước đó bỏ qua môn/nghĩa/scope. processed_names làm lựa chọn cặp phụ thuộc thứ tự và có thể bỏ sót cặp khác.
6. apply_resolutions chỉ chuyển exercises/processes khi merge, không bảo toàn đầy đủ definition/examples/nguồn/topic. Khi delete node không lọc cạnh còn trỏ tới tên đã xóa; upsert_edges dùng MERGE endpoint, có thể tạo lại node ma. Không xử lý rõ alias chain/cycle hoặc self-loop sau merge. merge_graphs_python cũng giữ definition/description của bản đầu, một số lỗi schema bị except/pass.
7. Expert chỉ thấy bản trích của Extractor; Validator chỉ thấy bản Expert. Nếu bước đầu mất điều kiện hoặc bịa quan hệ, bước sau thiếu văn bản gốc để bác bỏ. Prompt Expert yêu cầu JSON nhưng pipeline xem là markdown rồi cho agent khác chuyển JSON. Structured output kiểm tra hình dạng, chưa chứng minh nội dung đúng.
8. Prompt ép tên tài liệu thành entity và cấm cả MAC/SMTP/cáp quang thành concept độc lập có thể làm mất cấu trúc tri thức đúng. Chunker chỉ thêm ngữ cảnh heading, không tạo đủ thẻ TÀI LIỆU/NGỮ CẢNH mà prompt yêu cầu. Quy tắc bắt buộc có quan hệ/Topic có thể ép dữ liệu không có căn cứ.
9. Chunker bỏ đoạn dưới 100 ký tự, dùng PythonCodeTextSplitter cho nhiều ngôn ngữ; sanitize_text xóa indentation trước khi cắt code. Semantic split không có bước đảm bảo hard cap sau split; kích thước đang tính theo ký tự, không token.
10. gather không giới hạn concurrency, batch cố định năm bản thô thay vì token budget; một lỗi có thể làm pipeline không có checkpoint để tiếp tục. Embedding/Reviewer đồng bộ chặn event loop. Client được tạo lặp; config/retry/timeout/model của LLMService không áp dụng cho các helper này.
11. Output dùng đường dẫn chung, extractor append trộn job; mkdir output không phải data/output nơi ghi. Không có identity/version/content hash hoặc checkpoint theo run để tránh ghi chồng khi chạy đồng thời.
12. Ghi nodes/edges/document là các lần ghi riêng; catch lỗi rồi vẫn in HOÀN TẤT. Không có trạng thái từng kho hay publish gate sau duyệt; teacher approval chưa nằm trong run_pipeline hiện tại.

## Hướng cải tiến đề xuất, chưa triển khai

Giữ bốn vai trò nhưng thay contract:

- Extractor: tạo facts có chunk_id, source span/quote, loại tri thức; dùng JSON từ đầu. Không tự bổ sung. Giữ các fact riêng, không nhét mọi nguyên lý vào definition duy nhất.
- Expert: chuẩn hóa/ghép mảnh bằng chứng cùng nghĩa, đề xuất entity/relations/topic, giữ ID fact và nguồn; không tự xuất bản. Khi option ngoài bật, gọi nhánh bổ sung riêng, ghi nguồn gốc external hoặc AI_GENERATED khác với DOCUMENT_EXTRACTED.
- Validator: đối chiếu claim/điều kiện/hướng cạnh với original chunks, đưa vấn đề cụ thể và patch; Python kiểm tra schema, tham chiếu, phạm vi, danh sách bước và hash trích đoạn. Không lặp LLM chỉ để đổi Markdown sang JSON.
- Reviewer: chỉ phân xử duplicate/collision/mâu thuẫn chưa rõ. Nhìn source evidence, subject/type/context/aliases; giữ riêng khi không chắc. Merge chỉ là đề xuất; không dùng model tự ý xóa thông tin nguồn.

Pipeline đích: register document/version -> parse có vị trí -> lưu chunk ổn định -> Extractor -> Expert -> Validator -> candidate resolution + Reviewer -> deterministic integrity check -> DRAFT graph -> giảng viên APPROVE/REJECT/REQUEST_CHANGES -> publish đồng bộ graph/topic/chunk/vector -> đánh dấu published revision.

Mặc định DOCUMENT_ONLY. Quyền bật nguồn ngoài nằm ở request ingestion của giảng viên, được lưu cùng run và truyền xuống mọi stage; nội dung tài liệu không được tự đổi quyền này. Nguồn ngoài có URL/tựa đề/đoạn dẫn và snapshot/hash; nội dung AI sinh ghi AI_GENERATED, không giả là trích từ tài liệu. Duyệt theo graph revision; sửa sau duyệt tạo revision mới, không tái sử dụng phê duyệt cũ.

Không ghi đè graph đang phục vụ chat bằng draft chưa duyệt. Draft có thể lưu riêng trước (JSON/staging với ID run); publisher là nơi duy nhất chuyển dữ liệu được duyệt sang contract active. Chat chỉ truy hồi revision đã xuất bản. Không coi trạng thái AI_CHECKED là teacher-approved.

Chuẩn hóa KnowledgeEntity canonical_code/subject, Definition conditions/exceptions, Process/ProcessStep, Exercise/ExerciseStep và owner/scope trước khi publish. Topic ở mức hợp lý theo tài liệu/chunk, không ép tất cả thành một topic; topic_chunks giữ quan hệ nhiều-nhiều. Canonical resolution phải tra cả kho đã có, không chỉ dedup trong file mới.

Không có transaction thật bao cả MySQL/Neo4j/Chroma. Dùng idempotent upsert, checkpoint và trạng thái thành công từng kho; chỉ quảng bá published revision khi tất cả kho bắt buộc đã sẵn sàng. Bản ghi graph/source là dữ liệu gốc; vector là chỉ mục có thể rebuild. Embedding provider/model/dimension/metric/identity đồng bộ với chat.

## Ưu tiên

P0: đúng entrypoint/import, prompt Reviewer, contract graph với chat, báo lỗi trạng thái đúng, chặn auto-merge semantic và direct publish chưa duyệt.

P1: source provenance xuyên suốt, JSON facts, Validator đối chiếu nguồn, Topic/chunk canonical mapping và integrity checks sau resolution.

P2: job/run/checkpoint/idempotency, concurrency và token budget, shared async provider adapter, index publication/retry, nội dung ngoài theo opt-in và review revision.

P3: bộ tài liệu nghiệm thu có nhãn (đa môn, công thức, bảng, code, điều kiện/ngoại lệ, đồng nghĩa/khác nghĩa); đo grounded facts, missing facts, relation direction, false merge, orphan edges, cost/page và elapsed-time.

## Số lần gọi và chi phí

Hiện tại với n chunks, b=ceil(n/5) batches: n Extractor + b Expert + b Validator + r Reviewer (r=0 hoặc 1 trong code hiện tại), chưa tính embedding semantic chunking/entity, retry hoặc luồng LightRAG chạy riêng. Ví dụ 100 chunks -> 140 hoặc 141 generation calls. Không có usage đo thực tế, không đưa giá tiền.

Khử trùng lặp all-pairs O(m²) theo số entity m; thay bằng candidate retrieval theo môn/loại + top-k rồi phân xử. Gom batch theo token budget; skip cache cho file/chunk không đổi bằng hash; AI review có chọn lọc trên claim chưa chắc. Giảm call đổi format sẽ hữu ích hơn tăng model cho mọi stage.

## Giới hạn đánh giá

Đây là đọc mã tĩnh. Không xác nhận code hiện chạy được, graph thật có label gì hoặc độ chính xác extraction. Những phát hiện liên quan entrypoint/import cần đối chiếu môi trường chạy mà người dùng xác nhận. Không tự sửa code theo đề xuất này.
