# Kế hoạch triển khai ingestion text → kho tri thức Socratic

Trạng thái: thiết kế chờ duyệt triển khai. Tài liệu này cập nhật hướng ingestion trong kế hoạch trước. Các runner thử nghiệm vẫn là nơi so sánh chất lượng.

## 1. Phạm vi và điểm xuất phát

- Spring Boot nhận upload, lưu file và điều phối job. FastAPI parse, chunk, gọi LLM và chuẩn hóa graph. MySQL lưu bản nháp, quy trình duyệt và con trỏ xuất bản. Neo4j lưu đồ thị đã duyệt. Chroma phục vụ tìm kiếm chunk, khái niệm và topic.
- Chỉ đọc lớp chữ. Với PDF, trích text theo trang trước khi gọi LLM. Gửi toàn bộ text có nhãn trang/đoạn khi đủ ngân sách. Cách này giữ ngữ cảnh cả tài liệu và tuân thủ phạm vi text-only. Với DOCX hoặc text, dùng đoạn/heading/dòng làm tọa độ nguồn khi parser không có số trang thật.
- Dùng bốn vai trò Extractor → Expert → Validator → Reviewer. Python dựng graph và hậu kiểm. Runner single-pass là nguồn tham khảo cho cách gửi ngữ cảnh và schema trả về. LightRAG giữ ở nhánh đánh giá.
- Tự gom topic, tự nối topic–chunk N–N, tự lưu bản nháp AI và chỉnh sửa của giảng viên. Giáo viên/admin duyệt toàn phiên bản. Chat chỉ đọc publication hiện hành trong phạm vi được phép.
- Upload, worker và API sửa/duyệt đã có ở đường Spring Boot → /api/v1/internal/ingestion/draft. Đường Python hiện chạy theo chunk và graph assembly còn để trống knowledge_relations/arguments. Chat hiện có chỗ lọc marker ingestion_draft. Cần thay bằng publication gate ở tất cả đường đọc học liệu.

## 2. Luồng dữ liệu

~~~mermaid
flowchart TD
  A[FE upload tài liệu] --> B[Spring Boot lưu file bất biến và tạo job]
  B --> C[FastAPI parse text và tạo chunk có nguồn]
  C --> D[Extractor đọc toàn văn hoặc nhóm đoạn]
  D --> E[Expert chuẩn hóa và gắn cha]
  E --> F[Validator kiểm chứng nguồn]
  F --> G[Reviewer xử lý lỗi có căn cứ]
  G --> H[Python dựng graph và kiểm tra contract]
  H --> I[MySQL lưu chunks và revision nháp]
  I --> J[Giảng viên mở lại và tự lưu chỉnh sửa]
  J --> K[Duyệt revision cụ thể]
  K --> L[Neo4j ghi graph theo publication]
  K --> M[Chroma ghi embedding theo publication]
  L --> N[MySQL kích hoạt publication và topic-chunk]
  M --> N
  N --> O[Chat tra cứu theo quyền và publication hiện hành]
~~~

1. Upload có file, title, subject, courseId, sourcePolicy mặc định DOCUMENT_ONLY và Idempotency-Key. Actor, owner, quyền đọc và scope lấy từ Spring Security và dữ liệu lớp học. Lưu file dưới đường dẫn bất biến theo version trên storage dùng chung, hash SHA-256 trong lúc ghi. Tạo materials, material_versions và ingestion_jobs trong transaction sau khi file đã ghi bền vững. Nếu transaction thất bại, dọn file mồ côi bằng cơ chế thu hồi có kiểm tra tham chiếu. Cùng khóa và cùng request trả lại job đã có. Cùng khóa với nội dung khác trả 409.
2. Worker nhận QUEUED bằng transaction ngắn, cấp lease_token và hạn thuê. Chuyển sang PROCESSING, gửi bytes cùng material_id, version_id, filename, source_hash và options được BE xác thực. Worker renew lease trong khi chờ. Mọi ghi kết quả phải còn đúng token. Worker quá hạn có thể được thay, kết quả về muộn bị loại.
3. Parser trả danh sách block theo thứ tự. Giữ nguyên bản text chuẩn hóa dùng để kiểm chứng quote. Ghi warning theo trang, ví dụ NO_TEXT_PAGE. Tài liệu hoàn toàn thiếu text trả NO_EXTRACTABLE_TEXT. Nếu có trang thiếu text, reviewer thấy rõ coverage và phải xác nhận thiếu sót trước khi duyệt phiên bản.
4. Chunk theo đoạn/section, rồi dùng khoảng cách ngữ nghĩa để chọn điểm cắt nếu cấu hình semantic. Giữ đoạn code, bảng text và danh sách bước cùng nhau khi còn đủ ngân sách. Chunk có overlap và source spans. Kiểm tra coverage, offsets, thứ tự, giới hạn token. Nếu semantic embedding tạm lỗi, chỉ dùng structural fallback khi config cho phép và lưu chunker thực tế. Embedding phục vụ chọn biên là dữ liệu tạm. Embedding tra cứu được tạo lúc xuất bản.
5. LLM dùng cửa sổ trích xuất riêng với chunk tra cứu. Nếu đủ ngân sách, Extractor nhận toàn văn đã đánh dấu block. Với file lớn, ưu tiên nhóm section, giữ tiêu đề cha và overlap. Giới hạn theo token đầu vào, dự trữ token output và ngân sách số lượt gọi. Chuẩn hóa và ghép kết quả bằng source IDs. Nếu section dài bị chia ngang, đưa danh sách cha lân cận cho Expert giải quyết liên kết. Nếu đầu ra bị cắt, chia cửa sổ nhỏ hơn trong giới hạn retry.
6. Python xác minh và ráp DTO. Spring Boot xác thực response version, source hash và provenance. Lưu chunks, revision 1, source manifest và issues rồi chuyển AWAITING_REVIEW trong một transaction. Nếu một cửa sổ thất bại, ghi coverage gap có tọa độ và giữ phần hợp lệ để sửa. Nếu không còn dữ liệu hợp lệ, job FAILED với mã cụ thể.

## 3. Vai trò của bốn agent

| Agent | Dữ liệu nhận | Dữ liệu trả | Kiểm soát |
|---|---|---|---|
| Extractor | Toàn văn hoặc một cửa sổ text có block IDs, ngữ cảnh tiêu đề | Claims có loại, quote, nguồn, ứng viên cha, số bước nguồn nếu có | Chỉ lấy điều có trong text. Nhận diện bước theo ngữ nghĩa, kể cả tiêu đề đa ngôn ngữ, viết sai hoặc bước ngầm |
| Expert | Claims, đoạn nguồn, cha lân cận và danh sách ứng viên khái niệm | Entities, nội dung sư phạm, cạnh, topic candidates, ánh xạ claims → node/edge | Bài tập thuộc khái niệm, bước giải thuộc bài tập, bước quy trình thuộc quy trình. Giữ nguồn khi gom |
| Validator | Candidate IDs và các trích đoạn liên quan | Verdict theo ID, mã lỗi, trích đoạn đối chiếu, mức độ | Phát hiện sai nguồn, gán cha sai, nhầm quy trình với bài giải, quan hệ suy diễn, thiếu đề bài, số bước mâu thuẫn |
| Reviewer | Issues và phần graph bị ảnh hưởng, cha hợp lệ, nguồn | Patch theo ID hoặc yêu cầu giảng viên xem | Chỉ sửa có căn cứ. Giới hạn một vòng sửa có LLM cho phần lỗi. Lưu issue chưa giải quyết |

- Validator trả đúng một verdict mỗi candidate. Kiểm tra thiếu, dư hoặc trùng ID. Nếu output thiếu một ID, retry riêng tập thiếu trong ngân sách chung rồi đánh dấu phần đó chưa kiểm chứng. Các verdict hợp lệ vẫn được giữ.
- LLM chỉ dùng local ID trong response. Python cấp UUID và canonical mapping, kiểm tra quote với block/offset, loại endpoint lạ và chặn chu trình sở hữu. Thứ tự bước dùng số trong nguồn nếu có. Với chuỗi bước không đánh số, ghi thứ tự theo vị trí đã xác minh và đánh dấu thứ tự suy ra từ bố cục. Nếu số bước trùng cùng cha với nội dung khác, giữ issue để sửa. Không dò từ khóa cố định như “Bước”.
- Ràng buộc JSON bằng DTO Pydantic strict và Structured Outputs khi phù hợp. Sau mỗi stage, validate kiểu, enum, kích thước, references và nguồn. LLM có thể đề xuất sửa nội dung. Quyền duyệt, namespace, trạng thái và phạm vi truy cập do ứng dụng quyết định.
- Model cấu hình theo agent. Với stage cần temperature tùy chỉnh, mặc định theo lựa chọn GPT‑4o mini. Với stage dùng chế độ mặc định tương ứng temp = 1, chọn GPT‑6 Luna. Khi Luna chạy reasoning, bỏ field temperature. Ghi snapshot model, reasoning effort, prompt version và usage vào job, tránh gửi toàn văn lần hai cho agent chỉ cần kiểm vài claim. [Tương thích tham số OpenAI](https://developers.openai.com/api/docs/guides/latest-model) · [Lịch ngừng GPT‑4o mini](https://developers.openai.com/api/docs/deprecations).

## 4. DTO và quy tắc dữ liệu

| DTO | Trường tối thiểu |
|---|---|
| ParsedDocument | materialVersionId, sourceHash, parserVersion, blocks[], warnings[] |
| DocumentBlock | blockId, ordinal, page hoặc sectionPath, text, charStart, charEnd |
| ChunkProposal | chunkId, ordinal, text, tokenCount, textHash, spans[{blockId,start,end}], pageFrom, pageTo |
| EvidenceRef | evidenceId, origin, chunkId, blockId, start, end, quote, sourceUrl nếu ngoài tài liệu |
| GraphDraft | schemaVersion, sourceHash, entities[], nodes[], edges[], topics[], topicChunkLinks[] |
| EntityDraft | id, canonicalCode đề xuất, name, subject, description, evidenceIds[] |
| NodeDraft | id, kind, parentId nếu có, attributes theo kind, evidenceIds[] |
| EdgeDraft | id, kind thuộc allowlist, fromId, toId, evidenceIds[] |
| TopicDraft | id cục bộ, name, summary, entityIds[], evidenceIds[], resolvedTopicId nếu đã khớp |
| TopicChunkLink | topicId cục bộ, chunkId, evidenceIds[] |
| ValidationIssue | code, severity, targetId, evidenceIds, windowId nếu có, message |
| DraftResult | graph, chunks, sourceManifest, validationReport, coverage, parserVersion, chunkerVersion, usage |

Quy ước offsets dùng code point trong text chuẩn hóa và khoảng nửa mở [start, end). Java/FE phải chuyển offset sang UTF-16 khi highlight. UUID JSON là chuỗi 36 ký tự. MySQL dùng BINARY(16) với cùng thứ tự byte trong Java và Python. Graph và vector dùng UUID nghiệp vụ, canonical_code dùng liên kho và tiến độ học. Cấp ID chunk ổn định theo version và chỉ số. Cấp ID cho node/edge theo định danh nguồn hoặc ID do server cấp khi chỉnh sửa, tránh đổi ID vì giảng viên sửa tiêu đề.

Ví dụ phần graph sau khi ráp. Các ID được rút ngắn để dễ đọc.

~~~json
{
  "schemaVersion": "ingestion-graph-1",
  "entities": [{"id":"e1","canonicalCode":"CS201.ATTRIBUTE_CLOSURE","name":"Bao đóng thuộc tính","evidenceIds":["s1"]}],
  "nodes": [
    {"id":"p1","kind":"PROCESS","parentId":"e1","attributes":{"name":"Tính bao đóng"},"evidenceIds":["s1"]},
    {"id":"ps1","kind":"PROCESS_STEP","parentId":"p1","attributes":{"stepNumber":1,"action":"Khởi tạo tập kết quả"},"evidenceIds":["s1"]},
    {"id":"x1","kind":"EXERCISE","parentId":"e1","attributes":{"title":"Bài tập 1","content":"Tính A⁺ với tập phụ thuộc hàm đã cho."},"evidenceIds":["s2"]},
    {"id":"xs1","kind":"EXERCISE_STEP","parentId":"x1","attributes":{"stepNumber":1,"instruction":"Khởi tạo A⁺ bằng A","processStepId":"ps1"},"evidenceIds":["s2"]}
  ],
  "edges": [],
  "topics": [{"id":"t1","name":"Phụ thuộc hàm","summary":"Tính bao đóng thuộc tính","entityIds":["e1"],"evidenceIds":["s1"]}],
  "topicChunkLinks": [{"topicId":"t1","chunkId":"c1","evidenceIds":["s1"]},{"topicId":"t1","chunkId":"c2","evidenceIds":["s2"]}]
}
~~~

Python suy ra các cạnh sở hữu từ parentId, còn edges chứa các quan hệ nghiệp vụ có bằng chứng. processStepId và processId chỉ được gắn khi có mapping xác minh. Mỗi bước có đúng một cha, số bước duy nhất trong cha. Definition.conditions/exceptions là mảng string nếu có. ExerciseStep giữ instruction, expected_outcome, socratic_question và common_mistake theo schema hiện hành. Trường thiếu nguồn để null nếu schema cho phép. Tương tự với Example và Argument. Đề bài và lời giải được tách rõ để chat áp dụng chính sách gợi ý.

DOCUMENT_ONLY chỉ chấp nhận origin DOCUMENT. Nếu nguồn ngoài được bật, nguồn có URL và trích dẫn dùng origin EXTERNAL. Nội dung AI bổ sung dùng AI_GENERATED và được gắn nhãn cho reviewer. Phần này được duyệt cùng revision nhưng giữ provenance riêng. Chỉ tài liệu nguồn mới sinh material_chunks của file upload.

## 5. Schema và nguồn dữ liệu chuẩn

### MySQL

| Bảng | Khóa và dữ liệu sử dụng |
|---|---|
| materials | id, owner/course/scope theo schema BE. Metadata học liệu và quyền |
| material_versions | id, material_id, version_number, source_hash, source_snapshot_url, parser_version, chunker_version, created_by. Unique material + version_number |
| ingestion_jobs | id, material_version_id, requested_by, idempotency_key, source_policy, status, current_stage, pipeline_version, configuration JSON, checkpoint JSON, publication_state JSON, lease, attempts, error. Unique requester + key |
| material_chunks | id, material_id, material_version_id, owner_id, scope, subject, chunk_index, content, token_count, offsets, canonical_codes, extra_metadata JSON. Unique version + chunk_index. Metadata lưu spans/page/hash |
| knowledge_graph_drafts | id, job_id, revision_number, payload_schema_version, graph_payload, source_manifest, validation_report, payload_hash, review_status, reviewed_by/at/hash/comment. Unique job + revision_number |
| material_publications | id, material_id, material_version_id, job_id, draft_id, status, is_current, thông tin người duyệt/xuất bản. Một row mỗi job, tối đa một current mỗi material |
| topics | id, name, summary, concepts_included. Hàng topic là định danh dùng lại. Nội dung chi tiết có nguồn theo publication nằm trong approved draft |
| topic_chunks | PK topic_id + chunk_id, FK về topics/material_chunks. Projection của các publication hiện hành. Lịch sử mapping nằm trong approved draft |

Đề xuất dùng bộ CREATE TABLE hiện hành của BE, chưa cần bảng mới. Topic đang nháp nằm trong graph_payload, được tự lưu cùng link. Khi activate, thêm/upsert topic và thay link cho đúng material trong transaction MySQL. Nếu hai job cùng material_version_id, vẫn gỡ link hiện hành của tài liệu rồi chèn đúng bộ link từ draft đang activate. Chủ đề dùng chung giữ links đến tài liệu khác. Summary và concepts_included của topic dùng chung chỉ là projection. Reader lấy nội dung theo approved draft và tài liệu mà người đọc được phép truy cập. canonical_codes cấp chunk lấy từ publication hiện hành, cập nhật cùng transaction nếu cần projection cho reader cũ.

### Neo4j

- Giữ KnowledgeEntity(canonical_code, name, subject, description) làm định danh chuẩn. Chỉ chia sẻ thuộc tính nhận dạng ổn định và an toàn giữa các tài liệu. Đề xuất thêm KnowledgeEntitySnapshot theo publication cho name/description trích xuất có provenance, tránh ghi đè mô tả dùng chung trong lúc PREPARING.
- Giữ các label Definition, Process, ProcessStep, Exercise, ExerciseStep, Example, Argument. Tạo node ID vật lý ổn định theo publicationId + draftNodeId. Lưu publication_id, material_version_id, owner_role, scope và source refs theo contract kho. Các quan hệ mang publication_id. Cạnh giữa hai KnowledgeEntity được MERGE với khóa riêng của publication và edgeId để bảo toàn nguồn từng tài liệu.
- Tách mapping nhãn và quan hệ thành allowlist trong publisher. Dùng parameterized Cypher và batch UNWIND. Kiểm tra count, parent endpoints và uniqueness trước khi đánh dấu graph ready. Canonical code đã dùng trong chat/tiến độ cần tái sử dụng khi có mapping chắc chắn. Tên giống nhau khác môn hoặc nghĩa giữ định danh riêng.
- Reader lọc publication_id cả truy vấn theo canonical_code, theo node ID trực tiếp, và khi đi qua bước giải, định nghĩa hoặc quan hệ. Truy vấn graph tổng quát cũng phải áp dụng quyền nếu FE có dùng đường đó.

### Chroma

| Collection logic | Nội dung embedding | Metadata |
|---|---|---|
| chunk | Text chunk | chunk_id, publication_id, material_version_id, subject, scope, text_hash |
| entity | Tên + mô tả + định nghĩa nguồn trong publication | canonical_code, publication_id, material_version_id, subject, scope |
| topic | Tên + tóm tắt có nguồn + tên các khái niệm | topic_id, publication_id, material_version_id, subject, scope |

ID vector theo publicationId + kind + itemId. Mỗi collection vật lý khai báo provider, model và dimension trong embedding identity. Nếu identity khác, tạo collection mới và lập kế hoạch chuyển reader/index. Dùng batch embedding theo giới hạn token/provider và cache theo embedding identity + input hash khi có cache phù hợp. Vector search lấy ứng viên theo allowlist publication. Kiểm tra lại publication và quyền bằng MySQL trước khi đưa nội dung vào LLM. Giá trị canonical code hoặc topic ID có sẵn trong session vẫn phải qua kiểm tra.

## 6. Tự gom topic

1. Chuẩn hóa Unicode, khoảng trắng và case để tìm ứng viên. Giữ dấu và tên hiển thị gốc. Gom trong tài liệu khi topic cùng nghĩa và evidence/concepts tương thích.
2. Map entityIds thành canonical codes sau khi giải quyết định danh. Tìm topic cùng namespace được phép chia sẻ và cùng subject. Ưu tiên khóa từ canonical codes đã xác minh. Similarity của embedding dùng để tìm ứng viên, rồi so evidence và concepts. Topic chỉ có tên giống hoặc vector gần mà thiếu bằng chứng thì giữ riêng.
3. Tạo ID ổn định cho topic mới theo namespace + khóa nội dung đã xác minh khi có khóa chắc chắn. Khi activate, khóa tài liệu và khóa các topic IDs theo thứ tự ổn định, chạy lại kiểm tra trùng dựa trên dữ liệu hiện hành. Nếu mapping đổi vì publication đồng thời, chuẩn bị lại các topic vectors theo mapping mới trước khi activate. Nếu nghĩa thực sự thay đổi, trả về giảng viên rà soát. Không đổi nội dung của revision đã duyệt.
4. Xây topicChunkLinks từ evidence: một chunk có thể gắn nhiều topic. Dedupe theo cặp. Chunk phải thuộc version hiện tại và chứa bằng chứng. Không lấy chunk có liên quan chỉ vì nó liền kề.
5. Nếu tái sử dụng topic, metadata khác nhau theo publication. Giảng viên có thể sửa topic/link trong phạm vi tài liệu của mình, tránh sửa nội dung đã xuất bản của tài liệu khác.

## 7. API, tự lưu và duyệt

| Route Spring Boot | Hợp đồng đề xuất |
|---|---|
| POST /api/v1/materials | 202, materialId/versionId/jobId/status. Giữ multipart hiện tại |
| GET /api/v1/materials/ingestion/{jobId} | JobView, coverage, lỗi, latestDraft id/revision/hash/graph/validation, publication status |
| GET danh sách job theo material hoặc phạm vi giảng viên | Cho FE tìm lại draft sau đăng nhập, phân trang theo updatedAt/id |
| POST /api/v1/materials/ingestion/{jobId}/drafts | baseRevisionId + baseHash + graph đã sửa. Server validate và trả revision/hash mới |
| POST /api/v1/materials/ingestion/{jobId}/review | baseRevisionId + baseHash + decision + comment và xác nhận coverage warning nếu có |
| POST /api/v1/materials/ingestion/{jobId}/retry | Retry theo stage lỗi. Retry xuất bản dùng cùng publication ID và approved hash |
| GET /api/v1/materials/{materialId}/ingestion/{jobId}/file | Xem nguồn gốc có phân quyền |

- Mở rộng endpoint save hiện tại. FE debounce khi sửa, tuần tự hóa request và chỉ hiện Đã lưu sau ACK. Nếu offline hiện Chưa lưu. Khi 409 DRAFT_CONFLICT, giữ thay đổi cục bộ và hiện bản mới để giảng viên đối chiếu. Chặn nút duyệt khi còn thay đổi đang gửi.
- BE khóa job trong transaction, kiểm tra quyền, so baseRevisionId và baseHash với bản mới nhất rồi mới insert revision. Revision ID cần thiết vì hai revision có thể có payload hash giống nhau. Gọi trùng với payload y hệt có thể trả revision hiện tại. Reviewer chỉ duyệt revision đã lưu và không còn BLOCKER. Hành động duyệt ghi reviewed_payload_hash = payload_hash và tạo publication PREPARING trong cùng transaction.
- Quyền đợt đầu giữ uploader có quyền giảng viên hiện hành và admin như API đang có. Quyền phải được kiểm tra lại khi tải file, mở draft, save, review hoặc retry. Chat học sinh đọc theo access scope của tài liệu hiện hành.

## 8. Xuất bản có thể retry

1. Worker claim job PUBLISHING, đọc đúng draft_id từ material_publications và đối chiếu hash đã duyệt. Chuẩn hóa mapping, tính publication manifest gồm các ID dự kiến và embedding identity. Ghi checkpoint/manifest theo lease vào publication_state.
2. Publisher Python nhận lệnh nội bộ từ BE theo publication ID và đọc payload đã được duyệt hoặc nhận immutable payload kèm hash xác thực. Chuẩn bị graph và vectors độc lập có giới hạn concurrency. Ghi theo publication ID. Dùng upsert xác định và kiểm tra ready bằng manifest để retry không tạo node trùng hoặc bỏ thiếu item.
3. Chỉ khi cả hai kho ready, BE mở transaction MySQL, khóa material rồi kiểm tra lease, approval hash, version và current pointer kỳ vọng. Job cũ đến muộn không được thay bản mới đã xuất bản. Cập nhật projection topic–chunk, chuyển bản cũ sang SUPERSEDED và bản mới sang PUBLISHED/is_current=1. Đặt job COMPLETED trong cùng commit.
4. Lỗi trước commit giữ nguyên bản hiện hành. Retry tiếp tục những stage chưa ready, sử dụng lại kết quả đã xác minh. Nếu sửa draft sau lỗi publish, tạo job/revision xuất bản mới theo ràng buộc một publication mỗi job. Thu hồi bản PREPARING/FAILED bằng tác vụ riêng sau khi hết lease và xác minh chưa current.
5. Graph/vector đang chuẩn bị chỉ truy cập được qua đường publisher nội bộ. Cache chat gắn access scope và bộ publication IDs. Khi publication hoặc quyền đổi, invalidate hoặc xác minh lại trước khi trả context. Legacy seed chưa có publication phải được rà soát và xuất bản qua bước riêng trước khi bật gate toàn hệ thống.

## 9. Triển khai code theo gói

| Gói | Nơi sửa dự kiến | Kết quả |
|---|---|---|
| 1. Contract và dữ liệu | app/schema/ingestion_contracts.py, DTO Spring, .docs/ingestion.env.example | DTO có version, model theo stage, giới hạn kích thước và mã lỗi. Đối chiếu Flyway đang chạy với DDL BE và mapping UUID |
| 2. Text và extraction | document_parser.py, preprocessing.py, multi_agent.py, app/prompts/ingestion/, graph_assembly.py | Parse text, semantic chunks, cửa sổ toàn văn hoặc nhóm section, bốn agent, evidence và ráp graph; tái dùng contract runner thử nghiệm phù hợp |
| 3. Draft API và autosave | app/api/v1/ingestion_api.py, MaterialIngestionService/Controller của BE, màn hình review FE | API trả DTO có version; worker transaction/lease; revision, conflict, coverage và mở lại từ thiết bị khác |
| 4. Publisher | Module publisher mới thuộc app/service/ingestion/, BE worker hiện hành, Neo4j/Chroma adapters | Review → PREPARING → graph + vectors → atomic pointer. Topic resolve/link và retry từng kho |
| 5. Chat reader | app/repository/mysql/topic_repo.py, app/repository/neo4j/tutoring_repo.py, app/repository/chroma/, app/service/tutoring/retrieval_service.py | Một publication gate áp dụng cả chunk, entity, topic, đường theo ID và cache. Chat tự nhận diện topic |
| 6. Nghiệm thu | Runner đường dẫn file dùng chung core pipeline, mẫu tài liệu và checklist | Người dùng có thể kiểm riêng từng gói; production lưu dữ liệu nghiệp vụ và metrics, bỏ file truy vết từng stage |

Cấu hình cần thêm vào mẫu env: model/temperature/reasoning cho từng stage, max window input/output, số cửa sổ song song, ngân sách LLM calls/tokens, timeout/retry, lease duration/heartbeat, embedding model/dimension/batch size, collection names và giới hạn publish concurrency. Giữ các giới hạn file/pages/parser/chunk đã có. Timeout không giữ transaction. Metrics chỉ lưu thời gian từng stage, usage, số chunks/candidates, số lỗi và coverage, tránh lưu toàn bộ prompt/response thành log.

## 10. Điều kiện nghiệm thu

- File text nhỏ chạy đúng một cửa sổ trích xuất. File lớn chia theo giới hạn và giữ liên kết cha qua ranh giới cửa sổ. PDF scan báo thiếu text có vị trí. Nghiệm thu bằng tài liệu có bước đa ngôn ngữ và lỗi chính tả.
- Đối chiếu đúng node/edge/nguồn cho khái niệm, quy trình, bài tập và bước giải. Kiểm riêng số bước trùng giữa hai bài và bước bị gán nhầm loại cha. Tính tỷ lệ thực thể/quan hệ đúng so với bộ chuẩn, tỷ lệ có nguồn đúng và số chỉnh sửa thực tế của giảng viên. Tách chỉ số schema hợp lệ khỏi chất lượng trích xuất.
- Một chunk nối nhiều topic, một topic nối nhiều chunk. Tên topic giống nhau ở lớp khác không làm lộ summary, codes, evidence hoặc vectors. Thử hai publication cùng tài liệu và thử retry giữa các kho.
- Hai thiết bị mở cùng draft, chỉnh đồng thời tạo 409 đúng. Đăng xuất, đăng nhập máy khác lấy đúng revision server đã xác nhận. Approve revision cũ sau một lần save mới bị từ chối.
- Chat chưa đọc gì từ draft hoặc PREPARING, kể cả gọi theo UUID trực tiếp. Lỗi Neo4j/Chroma giữ nguyên publication cũ. Sau activate, chat đọc được dữ liệu mới và liên kết nguồn đúng. Thử tài liệu legacy trước khi bật gate.
- Báo cáo thời gian, token và chi phí theo số trang có text, số cửa sổ và số lần sửa. Đo riêng chi phí parse/chunk, LLM và publish. Chốt ngưỡng chất lượng/chi phí sau khi có benchmark cùng tài liệu và cùng bộ chấm.

Các đề xuất cần xác nhận khi duyệt plan: dùng approved draft làm snapshot topic để giữ schema MySQL hiện có, dùng thêm label Neo4j KnowledgeEntitySnapshot cho nội dung theo publication, và giữ quyền review theo uploader có quyền giảng viên hoặc admin trong gói đầu.
