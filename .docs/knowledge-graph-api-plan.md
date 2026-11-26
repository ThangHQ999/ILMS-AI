# Kế hoạch API quản trị đồ thị tri thức

Trạng thái: được duyệt triển khai ngày 2026-11-08. Code và giới hạn kiểm chứng xem knowledge-graph-api-guide.md. API công khai đi qua Spring Boot. FastAPI phục vụ đồ thị và xuất bản qua kênh nội bộ. Phạm vi là đồ thị tạo từ ingestion và quản lý theo tài liệu. Đồ thị theo môn/lớp là góc nhìn tổng hợp từ các bản xuất bản hợp lệ của nhiều tài liệu.

## 1. Mô hình và nguồn dữ liệu

| Thành phần | Trách nhiệm |
|---|---|
| material_versions | Phiên bản file nguồn. Giữ nguyên khi chỉ sửa graph |
| ingestion_jobs | Phiên chỉnh sửa hoặc xử lý ingestion. Job chỉnh graph khởi tạo AWAITING_REVIEW, bỏ qua Extractor |
| knowledge_graph_drafts | Snapshot JSON bất biến theo revision, nguồn, lỗi kiểm tra, hash và quyết định duyệt |
| material_publications | Chọn revision chat được đọc. Tối đa một current mỗi tài liệu |
| Neo4j | Projection bản nháp theo graph_revision_id và đồ thị xuất bản theo publication_id |
| Chroma | Embedding chunk, entity và topic theo publication_id |
| topics/topic_chunks | Projection chủ đề và liên kết của dữ liệu hiện hành |

Định danh dùng trong editor là ID nghiệp vụ của node/edge bên trong revision. graph_revision_id nhận diện snapshot. canonical_code nhóm đóng góp cùng khái niệm ở nhiều tài liệu. FE sửa thông qua materialId và jobId, kể cả khi bắt đầu từ đồ thị tổng hợp. Nếu một khái niệm có ba nguồn, màn hình cho chọn nguồn đóng góp trước khi sửa hoặc xóa. Gộp hai canonical code là nghiệp vụ riêng vì ảnh hưởng tiến độ học và dữ liệu nhiều tài liệu.

Code hiện tại đã có đọc graph nháp, lưu toàn bộ JSON, duyệt và worker publish. Quyền hiện tại là người upload còn quyền lớp hoặc admin. Code publisher đang từ chối publication cùng số phiên bản file. Đây là chỗ cần sửa để xuất bản lại graph của cùng file.

## 2. Phân quyền đề xuất

| Quyền | Admin | Chủ lớp ACTIVE | Giảng viên ACTIVE | Học viên ACTIVE |
|---|---|---|---|---|
| Xem bản xuất bản | Mọi tài liệu | Trong phạm vi lớp | Trong phạm vi lớp | Học liệu công khai hoặc được cấp trong lớp |
| Xem draft, lịch sử và nguồn | Mọi tài liệu | Học liệu quản lý trong lớp | Học liệu mình upload hoặc được cấp quyền sửa | — |
| Tạo draft, thêm/sửa/xóa node/cạnh | Mọi tài liệu | Học liệu quản lý trong lớp | Học liệu mình upload hoặc được cấp quyền sửa | — |
| Duyệt, từ chối, yêu cầu sửa | Mọi tài liệu | Học liệu quản lý trong lớp | Học liệu mình quản lý nếu chính sách lớp cho phép | — |
| Thu hồi bản xuất bản | Mọi tài liệu | Học liệu quản lý trong lớp | — | — |
| Xem audit, restore hoặc purge | Toàn hệ thống | Audit/restore trong phạm vi quản lý | Lịch sử học liệu mình quản lý | — |

Purge là tác vụ quản trị riêng dành cho admin, ngoài API CRUD thông thường. Tài khoản chưa có lớp chỉ thấy đồ thị được cấp quyền công khai. Cột giảng viên dùng quyền uploader hiện hành ở đợt đầu. Chia sẻ quyền chỉnh sửa cho đồng nghiệp để sau khi có cơ chế phân quyền rõ ràng.

Admin có toàn quyền nghiệp vụ ở mọi phạm vi. Quy tắc revision, kiểm tra tham chiếu và kiểm tra index áp dụng cả với admin. Backend lấy actor từ phiên đăng nhập và kiểm tra lại quyền cho từng thao tác. FE nhận capabilities để bật nút tương ứng. Nếu học liệu được dùng chung nhiều lớp, quyền từ một lớp chỉ đủ chỉnh nếu actor có quyền quản lý phạm vi học liệu gốc. Dùng courseId làm ngữ cảnh lọc, đối chiếu quan hệ học liệu và lớp trong DB. Dữ liệu học viên chỉ gồm nội dung được phép học, ví dụ đề bài và quy trình công khai. Đáp án, bước giải nội bộ, ghi chú duyệt và file nguồn cần quyền riêng.

## 3. API đề xuất

Base path là /api/v1/knowledge-graphs. Các route ingestion hiện hành tiếp tục phục vụ FE cũ qua cùng service nghiệp vụ.

| Method và path | Người dùng và dữ liệu |
|---|---|
| GET /published | Danh sách tài liệu đã xuất bản theo quyền. Lọc courseId, subject, q. Phân trang cursor |
| GET /published/materials/{materialId} | Snapshot current của tài liệu, trả node/edge có giới hạn |
| GET /published/concepts/{canonicalCode} | Góc nhìn tổng hợp nhiều nguồn hợp lệ. Mỗi đóng góp có materialId và publicationId |
| GET /materials/{materialId}/revisions | Lịch sử cho người quản lý. Filter trạng thái, cursor. Trả revision metadata |
| GET /drafts/{jobId}/revisions/{revisionId} | Mở đúng snapshot hoặc subgraph theo nodeId và depth. Kiểm tra revision thuộc job |
| POST /materials/{materialId}/drafts | Tạo phiên chỉnh sửa từ current hoặc revision lịch sử. Trả jobId và revision đầu |
| POST /drafts/{jobId}/changes | Gửi một batch thao tác thêm, sửa, xóa. Tạo revision mới trong một transaction |
| POST /drafts/{jobId}/review | Duyệt, yêu cầu sửa hoặc từ chối revision chính xác. Duyệt hợp lệ trả 202 và publicationId |
| DELETE /drafts/{jobId} | Hủy phiên nháp còn mở, lưu audit, giữ các revision |
| POST /materials/{materialId}/publications/{publicationId}/withdraw | Thu hồi đúng bản current, yêu cầu lý do |
| GET /publications/{publicationId} | Trạng thái xuất bản và lỗi an toàn để poll |
| POST /publications/{publicationId}/retry | Thử lại cùng revision và cùng publicationId nếu lỗi kho tạm thời |
| GET /materials/{materialId}/audit | Lịch sử thao tác cho người có quyền, phân trang |

FE có thể dùng endpoint batch cho cả nút thêm, sửa và xóa. Ví dụ xóa nút gửi DELETE_NODE. Nếu cần route REST riêng sau này, các route đó gọi chung GraphEditService. Đồ thị lớn đọc theo neighborhood, giới hạn depth và số node, trả truncated và nextCursor khi phù hợp.

## 4. DTO

| DTO | Trường chính |
|---|---|
| GraphViewResponse | materialId, jobId nếu là draft, revisionId, publicationId nếu đã xuất bản, revisionNumber, hash nếu được sửa, status, nodes, edges, capabilities, nextCursor |
| GraphNodeDto | nodeId, kind, label, canonicalCode nếu có, attributes theo kind, sourceRefs theo quyền |
| GraphEdgeDto | edgeId, kind, fromNodeId, toNodeId, attributes, sourceRefs |
| GraphSourceRefDto | materialId, chunkId, locator, spanStart, spanEnd, origin. Excerpt chỉ hiện khi có quyền |
| StartDraftRequest | baseRevisionId hoặc current mặc định, expectedCurrentPublicationId, reason. Hỗ trợ Idempotency-Key |
| GraphChangeRequest | baseRevisionId, baseHash, operations[], clientRequestId |
| GraphChangeResponse | jobId, revisionId, revisionNumber, hash, validationIssues[], idMappings nếu có |
| GraphReviewRequest | revisionId, baseHash, decision, comment, acknowledgedIssueIds[] |
| WithdrawPublicationRequest | reason. Publication ID lấy từ URL |
| PublicationStatusResponse | publicationId, revisionId, status, stage, retryable, errorCode |
| GraphValidationIssue | code, severity, nodeId/edgeId, field, message, sourceRefs |

Node kind gồm KNOWLEDGE_ENTITY, DEFINITION, PROCESS, PROCESS_STEP, EXERCISE, EXERCISE_STEP, EXAMPLE, ARGUMENT, TOPIC và CHUNK. CHUNK là nguồn tham chiếu, chỉnh nội dung file qua quy trình phiên bản tài liệu. attributes có DTO riêng theo kind. Server cấp UUID cho node mới, giữ ID khi đổi tên hoặc đổi cha. Dữ liệu sinh từ AI và sửa thủ công giữ origin và audit riêng. FE không đặt owner, scope, status, canonical_code, publication_id hoặc graph_revision_id.

Ví dụ lưu ba thay đổi trong một revision.

~~~json
{
  "baseRevisionId": "<revision-uuid>",
  "baseHash": "<payload-hash>",
  "clientRequestId": "<request-uuid>",
  "operations": [
    {"op": "UPDATE_NODE", "nodeId": "<definition-id>", "fields": {"content": "Nội dung mới"}},
    {"op": "MOVE_NODE", "nodeId": "<exercise-id>", "newParentId": "<concept-id>"},
    {"op": "DELETE_EDGE", "edgeId": "<relation-id>"}
  ]
}
~~~

Allowlist thao tác gồm CREATE_NODE, UPDATE_NODE, DELETE_NODE, MOVE_NODE, CREATE_EDGE, UPDATE_EDGE, DELETE_EDGE, LINK_TOPIC_CHUNK và UNLINK_TOPIC_CHUNK. DTO theo discriminator op. Trả 409 khi revision hoặc publication đã thay đổi, kèm revision hiện hành nếu actor có quyền. Trả 422 khi trường hoặc quan hệ sai, trả mã lỗi và target để FE tô đúng vị trí. Tài nguyên ngoài phạm vi trả 404 để hạn chế dò ID.

## 5. Nghiệp vụ sửa, xóa và xuất bản

### Sửa

1. Khi bắt đầu sửa bản xuất bản, Spring Boot tạo job chỉnh sửa gắn cùng material_version_id, clone snapshot và provenance vào revision đầu. Lưu base publication ID và generation trong cấu hình job. Restore cũng tạo draft từ revision lịch sử rồi đi qua duyệt.
2. Khi FE gửi operations, khóa job, kiểm tra quyền và đối chiếu revision/hash. Áp batch lên bản sao trong bộ nhớ, validate toàn graph sau khi áp xong, rồi lưu revision mới. Một batch thất bại không ghi phần còn lại. Lưu idempotency receipt để retry request bị mất ACK trả đúng kết quả.
3. Đồng bộ Neo4j theo revision như hiện tại. FE được ACK sau MySQL commit. Hiển thị đang đồng bộ khi projection chưa sẵn sàng. Khi nhận 409, giữ edits cục bộ và cho người dùng xem khác biệt trước khi áp lại.

### Xóa

- Xóa node lá sẽ xóa các cạnh liên quan trong revision mới. Node có con mặc định trả dependency report. Người quản lý chọn chuyển con hoặc gửi yêu cầu xóa cây con rõ ràng. Cấm xóa tài liệu, chunk nguồn hoặc node của tài liệu khác thông qua thao tác graph.
- Xóa một đóng góp khỏi bản xuất bản đi qua draft và duyệt. Nếu khái niệm còn nguồn khác, nó vẫn xuất hiện từ nguồn đó.
- Hủy draft chuyển job CANCELLED. Thu hồi publication khóa material, kiểm tra đúng current, chuyển hàng sang SUPERSEDED và is_current=NULL, lưu sự kiện WITHDRAWN kèm lý do. Giữ lịch sử. Xóa projection topic_chunks của tài liệu đó trong cùng transaction nếu cần. Chat ngừng lấy publication ở lượt truy xuất mới. Các hội thoại đã lưu vẫn theo chính sách lưu lịch sử hiện hành.
- Giai đoạn đầu giữ dữ liệu lịch sử. Công cụ purge dành riêng admin thiết kế sau với kiểm tra FK, retention và audit.

### Validate và publish

- Kiểm tra ID trùng, cạnh treo, kiểu cha–con, chu trình trong cây sở hữu, số bước trùng trong cùng cha, field bắt buộc và topic–chunk cùng phiên bản nguồn. Phân biệt lỗi chặn lưu với vấn đề có thể lưu draft nhưng chặn duyệt. Server tính lại issues và nguồn hợp lệ.
- Duyệt đúng revision/hash rồi queue. Publisher tạo graph và vector theo publicationId như hiện tại. Dùng cache embedding theo provider/model/dimension và hash nội dung nếu input giữ nguyên. Khi cả kho sẵn sàng, khóa material, so expected current và generation. Cho phép xuất bản graph mới trên cùng material_version_id nếu các điều kiện này khớp. Job ingestion file mới vẫn phải kiểm tra thứ tự phiên bản nguồn. Nếu có người đã publish hoặc withdraw trong lúc chờ, trả xung đột và yêu cầu lấy lại base.
- Trường hợp hai publication dùng chung material_version_id phải kiểm tra publication ID tại cả graph, vector và đường hydrate chunk. Topic links và canonical codes projection được chuyển cùng transaction với current pointer. Cache chat gắn publication IDs và phạm vi quyền. Nếu worker lỗi, bản current trước đó vẫn được phục vụ.

## 6. Schema bổ sung đề xuất

Giữ các bảng hiện hành. Đề xuất một bảng knowledge_graph_events cho audit, mutation receipt và generation xuất bản. Tạo bằng migration CREATE TABLE riêng của BE sau khi duyệt thiết kế.

- id BIGINT UNSIGNED AUTO_INCREMENT làm PK và thứ tự sự kiện.
- material_id BINARY(16) NOT NULL, job_id/revision_id/publication_id BINARY(16) tùy thao tác, actor_id BINARY(16) NOT NULL.
- event_type VARCHAR(40), reason VARCHAR(500) nullable, request_id VARCHAR(128) nullable, request_hash CHAR(64) nullable, metadata JSON, created_at DATETIME(6).
- Index (material_id, id), (job_id, id) và unique theo actor/material/event_type/request_id. FK và quy tắc retention theo schema hiện hành.
- Generation là ID sự kiện publish/withdraw gần nhất của material, hoặc 0. Tạo sự kiện trong transaction chuyển current. Không lưu toàn bộ payload hay trích đoạn trong audit. Cần backfill generation nếu chọn dùng dữ liệu lịch sử trước khi bật giao diện mới. Có thể dùng 0 cho publication đã tồn tại, rồi bắt đầu ghi event từ lần đổi current kế tiếp.

## 7. Cách triển khai code

1. **BE đọc và quyền.** Tạo KnowledgeGraphController, DTO module knowledgegraph, GraphAccessService và repository truy vấn theo actor. Tái dùng kiểm tra quyền học liệu hiện tại. Viết published read và revision history trước, rồi nối trang knowledge-graph hiện có.
2. **BE chỉnh sửa.** GraphEditService xử lý batch và transaction, GraphValidator áp quy tắc DTO và graph. Tái dùng luồng save/review của ingestion qua service chung để giữ hợp đồng cũ. Neo4j projection bổ sung business ID và shape cho FE chọn node.
3. **Publish/thu hồi.** Mở rộng publisher FastAPI và worker Spring Boot để nhận job chỉnh graph, CAS theo current/generation, retry, cập nhật projection và audit. Chốt contract lỗi xung đột để BE và FE xử lý đúng.
4. **FE.** Tách chế độ xem Published và Edit Draft. Dùng canvas hiện có, panel sửa theo loại node, tạo/xóa cạnh, dialog xem tác động xóa và diff revision. Nút điều khiển lấy từ capabilities. Trong graph tổng hợp, hiển thị nguồn trước khi vào editor.
5. **Nghiệm thu.** Kiểm quyền admin/giảng viên/học viên ở hai lớp, thử UUID ngoài quyền, concurrent edits, xóa node có con, sửa lại graph cùng file, thu hồi đúng publication, retry khi một kho lỗi, và xóa đóng góp trong khi tài liệu khác vẫn có cùng canonical code.

Các quyết định cần duyệt gồm quyền tự duyệt của giảng viên, quyền chủ lớp với học liệu dùng chung và bảng audit. Plan mặc định dùng quyền theo bảng ở trên.
