CREATE CONSTRAINT ke_canonical_code_unique IF NOT EXISTS
FOR (ke:KnowledgeEntity) REQUIRE ke.canonical_code IS UNIQUE;

CREATE INDEX ke_subject_idx IF NOT EXISTS
FOR (ke:KnowledgeEntity) ON (ke.subject);

CREATE INDEX ke_revision_idx IF NOT EXISTS
FOR (ke:KnowledgeEntity) ON (ke.graph_revision_id);

CREATE CONSTRAINT definition_id_unique IF NOT EXISTS
FOR (d:Definition) REQUIRE d.id IS UNIQUE;

CREATE INDEX definition_scope_owner_idx IF NOT EXISTS
FOR (d:Definition) ON (d.scope, d.owner_id);

CREATE INDEX definition_revision_idx IF NOT EXISTS
FOR (d:Definition) ON (d.graph_revision_id);

CREATE CONSTRAINT process_id_unique IF NOT EXISTS
FOR (p:Process) REQUIRE p.id IS UNIQUE;

CREATE INDEX process_scope_owner_idx IF NOT EXISTS
FOR (p:Process) ON (p.scope, p.owner_id);

CREATE INDEX process_revision_idx IF NOT EXISTS
FOR (p:Process) ON (p.graph_revision_id);

CREATE CONSTRAINT process_step_id_unique IF NOT EXISTS
FOR (ps:ProcessStep) REQUIRE ps.id IS UNIQUE;

CREATE INDEX process_step_number_idx IF NOT EXISTS
FOR (ps:ProcessStep) ON (ps.step_number);

CREATE INDEX process_step_revision_idx IF NOT EXISTS
FOR (ps:ProcessStep) ON (ps.graph_revision_id);

CREATE CONSTRAINT example_id_unique IF NOT EXISTS
FOR (ex:Example) REQUIRE ex.id IS UNIQUE;

CREATE INDEX example_scope_owner_idx IF NOT EXISTS
FOR (ex:Example) ON (ex.scope, ex.owner_id);

CREATE INDEX example_revision_idx IF NOT EXISTS
FOR (ex:Example) ON (ex.graph_revision_id);

CREATE CONSTRAINT exercise_id_unique IF NOT EXISTS
FOR (exer:Exercise) REQUIRE exer.id IS UNIQUE;

CREATE INDEX exercise_scope_owner_idx IF NOT EXISTS
FOR (exer:Exercise) ON (exer.scope, exer.owner_id, exer.difficulty);

CREATE INDEX exercise_revision_idx IF NOT EXISTS
FOR (exer:Exercise) ON (exer.graph_revision_id);

CREATE CONSTRAINT exercise_step_id_unique IF NOT EXISTS
FOR (es:ExerciseStep) REQUIRE es.id IS UNIQUE;

CREATE INDEX exercise_step_lookup_idx IF NOT EXISTS
FOR (es:ExerciseStep) ON (es.exercise_id, es.step_number);

CREATE INDEX exercise_step_revision_idx IF NOT EXISTS
FOR (es:ExerciseStep) ON (es.graph_revision_id);

CREATE CONSTRAINT argument_id_unique IF NOT EXISTS
FOR (arg:Argument) REQUIRE arg.id IS UNIQUE;

CREATE INDEX argument_scope_owner_idx IF NOT EXISTS
FOR (arg:Argument) ON (arg.scope, arg.owner_id);

CREATE INDEX argument_revision_idx IF NOT EXISTS
FOR (arg:Argument) ON (arg.graph_revision_id);


// ------------------------------------------------------------------------------
// PHẦN 1: KHỞI TẠO 17 NODE TÂM `:KnowledgeEntity` (CÓ ĐẦY ĐỦ graph_revision_id)
// Khớp 100% với `question_concepts`, `student_knowledge_heatmaps`, `material_chunks` và `material_publications`
// ------------------------------------------------------------------------------
UNWIND [
    // === Môn INT1306: Cơ sở dữ liệu (Revision 01 - Slide Chương 1 CSDL) ===
    {
        canonical_code: 'KHOA_CHINH',
        name: 'Khóa chính và Ràng buộc toàn vẹn thực thể (Primary Key)',
        subject: 'INT1306',
        description: 'Tập hợp một hoặc nhiều thuộc tính xác định duy nhất mỗi bộ trong quan hệ, không được phép chứa giá trị NULL.',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c01',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c01'
    },
    {
        canonical_code: 'KHOA_UNG_VIEN',
        name: 'Khóa dự tuyển / Khóa ứng viên (Candidate Key)',
        subject: 'INT1306',
        description: 'Siêu khóa tối thiểu, nghĩa là không thể bỏ bất kỳ thuộc tính nào mà vẫn giữ được tính chất định danh duy nhất.',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c01',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c01'
    },
    {
        canonical_code: 'RANG_BUOC_THUC_THE',
        name: 'Ràng buộc toàn vẹn thực thể (Entity Integrity)',
        subject: 'INT1306',
        description: 'Ràng buộc quy định rằng không có giá trị nào của khóa chính được phép nhận giá trị NULL trong quan hệ cơ sở.',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c01',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c01'
    },

    // === Môn INT1306: Cơ sở dữ liệu (Revision 02 - Hướng dẫn ERD & SQL Queries) ===
    {
        canonical_code: 'SQL_JOIN',
        name: 'Các phép kết nối bảng trong SQL (INNER JOIN & OUTER JOIN)',
        subject: 'INT1306',
        description: 'Phép toán kết hợp các hàng từ hai hay nhiều bảng dựa trên điều kiện so khớp cột liên quan.',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c02',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c02'
    },
    {
        canonical_code: 'WINDOW_FUNCTION_DENSE_RANK',
        name: 'Hàm cửa sổ xếp hạng DENSE_RANK() trên MySQL 8.0',
        subject: 'INT1306',
        description: 'Hàm gán thứ hạng liên tục cho các hàng trong mỗi phân vùng mà không bỏ cách số thứ tự khi có giá trị bằng nhau.',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c02',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c02'
    },

    // === Môn INT1306: Cơ sở dữ liệu (Revision 03 - Chuẩn hóa 2NF, 3NF, BCNF) ===
    {
        canonical_code: 'CHUAN_HOA_2NF',
        name: 'Dạng chuẩn 2 (Second Normal Form - 2NF)',
        subject: 'INT1306',
        description: 'Dạng chuẩn yêu cầu đạt 1NF và mọi thuộc tính không khóa đều phụ thuộc hàm đầy đủ vào khóa chính ghép.',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c03',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
    },
    {
        canonical_code: 'CHUAN_HOA_3NF',
        name: 'Dạng chuẩn 3 (Third Normal Form - 3NF)',
        subject: 'INT1306',
        description: 'Dạng chuẩn yêu cầu đạt 2NF và không có thuộc tính không khóa nào phụ thuộc hàm bắc cầu vào khóa dự tuyển.',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c04',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
    },
    {
        canonical_code: 'PHU_THUOC_BAC_CAU',
        name: 'Phụ thuộc hàm bắc cầu (Transitive Functional Dependency)',
        subject: 'INT1306',
        description: 'Phụ thuộc hàm dạng X -> Y và Y -> Z dẫn đến X -> Z, trong đó Y không phải là siêu khóa và Z không thuộc Y.',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c04',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
    },
    {
        canonical_code: 'CHUAN_HOA_BCNF',
        name: 'Dạng chuẩn Boyce-Codd (BCNF)',
        subject: 'INT1306',
        description: 'Dạng chuẩn nghiêm ngặt yêu cầu mọi vế trái của các phụ thuộc hàm không tầm thường đều phải là siêu khóa.',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c05',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
    },

    // === Môn INT1306: Cơ sở dữ liệu (Revision 05 - Giao dịch & Chỉ mục B-Tree) ===
    {
        canonical_code: 'TRANSACTION_ACID',
        name: 'Giao dịch ACID và Mức cô lập (Isolation Levels)',
        subject: 'INT1306',
        description: 'Tập hợp 4 thuộc tính đảm bảo tính tin cậy của giao dịch CSDL: Nguyên tử, Nhất quán, Cô lập và Bền vững.',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c06',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c05'
    },
    {
        canonical_code: 'INDEX_BTREE',
        name: 'Cấu trúc chỉ mục B+Tree trong InnoDB',
        subject: 'INT1306',
        description: 'Cấu trúc cây tự cân bằng đa nhánh dùng để tối ưu hóa truy vấn tìm kiếm điểm và quét phạm vi dữ liệu.',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c07',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c05'
    },

    // === Môn INT1434: Lập trình Web với Spring Boot & Next.js (Revision 06) ===
    {
        canonical_code: 'DTO_PATTERN',
        name: 'Mẫu thiết kế DTO (Data Transfer Object) & Kiến trúc Phân tầng',
        subject: 'INT1434',
        description: 'Mẫu đối tượng truyền tải dữ liệu giữa các phân tầng kiến trúc, ngăn chặn rò rỉ JPA Entity ra API.',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c08',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c06'
    },
    {
        canonical_code: 'JPA_N_PLUS_1',
        name: 'Bài toán N+1 Query và @EntityGraph trong Spring Data JPA',
        subject: 'INT1434',
        description: 'Hiện tượng hiệu năng kém khi 1 truy vấn cha kích hoạt thêm N truy vấn con để nạp liên kết LAZY.',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c08',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c06'
    },
    {
        canonical_code: 'SPRING_SECURITY_JWT',
        name: 'Xác thực JWT HttpOnly Cookie & Phân quyền RBAC 2 tầng',
        subject: 'INT1434',
        description: 'Cơ chế bảo mật không trạng thái với JSON Web Token đặt trong HttpOnly cookie và phân quyền RBAC đa cấp.',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c09',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c06'
    },

    // === Môn INT1303: Cấu trúc dữ liệu và Giải thuật (Revision 07) ===
    {
        canonical_code: 'QUICKSORT',
        name: 'Thuật toán Sắp xếp nhanh (QuickSort)',
        subject: 'INT1303',
        description: 'Thuật toán sắp xếp chia để trị chọn phần tử chốt (pivot) và phân hoạch mảng con có độ phức tạp trung bình O(N log N).',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c10',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c07'
    },
    {
        canonical_code: 'DIJKSTRA',
        name: 'Thuật toán Tìm đường đi ngắn nhất Dijkstra',
        subject: 'INT1303',
        description: 'Thuật toán tham lam tìm đường đi ngắn nhất từ một đỉnh nguồn trên đồ thị có trọng số cạnh không âm.',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c11',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c07'
    },

    // === Môn INT1405: Trí tuệ nhân tạo và Ứng dụng LLM (Revision 04) ===
    {
        canonical_code: 'RAG_EMBEDDING',
        name: 'Kiến trúc Hybrid RAG, Chunking và Vector Embedding',
        subject: 'INT1405',
        description: 'Kiến trúc kết hợp mô hình ngôn ngữ lớn với việc phân đoạn văn bản, nhúng vector và truy xuất tri thức kết hợp.',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c12',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c04'
    }
] AS row
MERGE (ke:KnowledgeEntity {canonical_code: row.canonical_code})
SET ke.name = row.name,
    ke.subject = row.subject,
    ke.description = row.description,
    ke.source_chunk_id = row.source_chunk_id,
    ke.graph_revision_id = row.graph_revision_id,
    ke.created_at = '2026-10-20T08:00:00Z',
    ke.updated_at = '2026-10-20T08:00:00Z';


// ------------------------------------------------------------------------------
// PHẦN 2: NỐI CẠNH NGỮ NGHĨA GIỮA CÁC `:KnowledgeEntity` (GẮN graph_revision_id)
// ------------------------------------------------------------------------------
MATCH (k1:KnowledgeEntity {canonical_code: 'KHOA_CHINH'}),
      (k2:KnowledgeEntity {canonical_code: 'KHOA_UNG_VIEN'})
MERGE (k1)-[r:IS_A]->(k2)
SET r.description = 'Khóa chính là một khóa dự tuyển được người thiết kế chọn làm định danh chính cho các bộ trong quan hệ',
    r.confidence = 0.99,
    r.source_chunk_id = '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c01',
    r.owner_id = 'aaaaaaaa-aaaa-aaaa-0000-000000000001',
    r.scope = 'GLOBAL',
    r.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c01',
    r.created_at = '2026-10-20T08:00:00Z';

MATCH (k1:KnowledgeEntity {canonical_code: 'KHOA_CHINH'}),
      (k2:KnowledgeEntity {canonical_code: 'RANG_BUOC_THUC_THE'})
MERGE (k1)-[r:REQUIRES]->(k2)
SET r.description = 'Mọi thuộc tính của khóa chính bắt buộc thỏa mãn ràng buộc toàn vẹn thực thể (NOT NULL và UNIQUE)',
    r.confidence = 0.99,
    r.source_chunk_id = '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c01',
    r.owner_id = 'aaaaaaaa-aaaa-aaaa-0000-000000000001',
    r.scope = 'GLOBAL',
    r.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c01',
    r.created_at = '2026-10-20T08:00:00Z';

MATCH (k1:KnowledgeEntity {canonical_code: 'CHUAN_HOA_2NF'}),
      (k2:KnowledgeEntity {canonical_code: 'KHOA_UNG_VIEN'})
MERGE (k1)-[r:DEPENDS_ON]->(k2)
SET r.description = 'Kiểm tra dạng chuẩn 2NF phụ thuộc vào việc xác định tất cả các khóa dự tuyển và tập thuộc tính không khóa',
    r.confidence = 0.96,
    r.source_chunk_id = '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c03',
    r.owner_id = 'cccccccc-cccc-cccc-dddd-dddddddddddd',
    r.scope = 'TEACHER',
    r.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03',
    r.created_at = '2026-10-20T08:00:00Z';

MATCH (k1:KnowledgeEntity {canonical_code: 'CHUAN_HOA_3NF'}),
      (k2:KnowledgeEntity {canonical_code: 'CHUAN_HOA_2NF'})
MERGE (k1)-[r:REQUIRES]->(k2)
SET r.description = 'Một lược đồ quan hệ muốn đạt chuẩn 3NF thì điều kiện tiên quyết là phải đạt chuẩn 2NF',
    r.confidence = 0.99,
    r.source_chunk_id = '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c04',
    r.owner_id = 'cccccccc-cccc-cccc-dddd-dddddddddddd',
    r.scope = 'TEACHER',
    r.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03',
    r.created_at = '2026-10-20T08:00:00Z';

MATCH (k1:KnowledgeEntity {canonical_code: 'CHUAN_HOA_3NF'}),
      (k2:KnowledgeEntity {canonical_code: 'PHU_THUOC_BAC_CAU'})
MERGE (k1)-[r:SOLVES]->(k2)
SET r.description = 'Phân rã lược đồ về chuẩn 3NF giúp loại bỏ phụ thuộc hàm bắc cầu của thuộc tính không khóa vào khóa dự tuyển',
    r.confidence = 0.98,
    r.source_chunk_id = '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c04',
    r.owner_id = 'cccccccc-cccc-cccc-dddd-dddddddddddd',
    r.scope = 'TEACHER',
    r.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03',
    r.created_at = '2026-10-20T08:00:00Z';

MATCH (k1:KnowledgeEntity {canonical_code: 'CHUAN_HOA_BCNF'}),
      (k2:KnowledgeEntity {canonical_code: 'CHUAN_HOA_3NF'})
MERGE (k1)-[r:IMPROVES_UPON]->(k2)
SET r.description = 'Chuẩn BCNF chặt hơn 3NF vì yêu cầu mọi vế trái của phụ thuộc hàm không tầm thường đều bắt buộc là siêu khóa',
    r.confidence = 0.99,
    r.source_chunk_id = '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c05',
    r.owner_id = 'cccccccc-cccc-cccc-dddd-dddddddddddd',
    r.scope = 'TEACHER',
    r.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03',
    r.created_at = '2026-10-20T08:00:00Z';

MATCH (k1:KnowledgeEntity {canonical_code: 'INDEX_BTREE'}),
      (k2:KnowledgeEntity {canonical_code: 'SQL_JOIN'})
MERGE (k1)-[r:APPLIES_TO]->(k2)
SET r.description = 'Chỉ mục B+Tree trên cột khóa ngoại tăng tốc độ thực thi phép kết nối SQL JOIN và truy vấn khoảng',
    r.confidence = 0.95,
    r.source_chunk_id = '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c07',
    r.owner_id = 'cccccccc-cccc-cccc-dddd-dddddddddddd',
    r.scope = 'TEACHER',
    r.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c05',
    r.created_at = '2026-10-20T08:00:00Z';

MATCH (k1:KnowledgeEntity {canonical_code: 'JPA_N_PLUS_1'}),
      (k2:KnowledgeEntity {canonical_code: 'SQL_JOIN'})
MERGE (k1)-[r:USES]->(k2)
SET r.description = 'Sử dụng @EntityGraph hoặc JOIN FETCH sinh câu lệnh LEFT JOIN trong SQL để triệt tiêu lỗi N+1 Query',
    r.confidence = 0.97,
    r.source_chunk_id = '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c08',
    r.owner_id = 'cccccccc-cccc-cccc-dddd-ddddddddddde',
    r.scope = 'TEACHER',
    r.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c06',
    r.created_at = '2026-10-20T08:00:00Z';


// ------------------------------------------------------------------------------
// PHẦN 3: KHỞI TẠO NODE `:Definition` (GẮN graph_revision_id, owner_role, scope)
// ------------------------------------------------------------------------------
UNWIND [
    {
        id: 'd0000000-1122-3344-5566-778899aabb01',
        canonical_code: 'CHUAN_HOA_BCNF',
        content: 'Một lược đồ quan hệ R ở dạng chuẩn Boyce-Codd (BCNF) nếu với mọi phụ thuộc hàm không tầm thường X -> A thỏa mãn trên R, vế trái X bắt buộc phải là một siêu khóa (Superkey) của R.',
        conditions: [
            'Lược đồ R đã ở dạng chuẩn 1NF',
            'Mọi phụ thuộc hàm không tầm thường X -> A đều có X là siêu khóa của R'
        ],
        exceptions: [
            'Không chấp nhận ngoại lệ vế phải A là thuộc tính khóa (Prime Attribute) như ở chuẩn 3NF',
            'Phép phân rã về BCNF luôn bảo toàn thông tin nhưng đôi khi không bảo toàn được toàn bộ phụ thuộc hàm'
        ],
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        owner_id: 'cccccccc-cccc-cccc-dddd-dddddddddddd',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c05',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
    },
    {
        id: 'd0000000-1122-3344-5566-778899aabb02',
        canonical_code: 'CHUAN_HOA_3NF',
        content: 'Một lược đồ quan hệ R ở dạng chuẩn 3 (3NF) nếu với mọi phụ thuộc hàm không tầm thường X -> A trên R, hoặc X là siêu khóa của R, hoặc A là thuộc tính khóa (tham gia vào ít nhất một khóa dự tuyển của R).',
        conditions: [
            'Lược đồ R đã đạt chuẩn 2NF (không có phụ thuộc hàm bộ phận của thuộc tính không khóa vào khóa dự tuyển)',
            'Không có thuộc tính không khóa nào phụ thuộc hàm bắc cầu vào khóa dự tuyển'
        ],
        exceptions: [
            'Nếu A là thuộc tính khóa thì X không cần là siêu khóa (điều này có thể gây dư thừa dữ liệu khi có nhiều khóa chồng lấn, cần nâng lên BCNF)'
        ],
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        owner_id: 'cccccccc-cccc-cccc-dddd-dddddddddddd',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c04',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
    },
    {
        id: 'd0000000-1122-3344-5566-778899aabb03',
        canonical_code: 'SQL_JOIN',
        content: 'LEFT OUTER JOIN trả về toàn bộ bản ghi từ bảng bên trái kèm các bản ghi khớp điều kiện từ bảng bên phải; nếu bảng bên phải không có dòng khớp thì các cột của bảng bên phải nhận giá trị NULL.',
        conditions: [
            'Đặt bảng cần giữ lại toàn bộ thực thể (kể cả thực thể có số lượng giao dịch bằng 0) ở vế trái của LEFT JOIN',
            'Sử dụng COUNT(bảng_phải.khóa_chính) thay vì COUNT(*) để đếm chính xác giá trị 0'
        ],
        exceptions: [
            'Nếu đặt điều kiện lọc cột của bảng bên phải khác NULL ở mệnh đề WHERE thì LEFT JOIN sẽ bị biến thành INNER JOIN (phải đặt điều kiện đó ở mệnh đề ON)'
        ],
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        owner_id: 'cccccccc-cccc-cccc-dddd-dddddddddddd',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c02',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c02'
    },
    {
        id: 'd0000000-1122-3344-5566-778899aabb04',
        canonical_code: 'JPA_N_PLUS_1',
        content: 'Lỗi N+1 Query xảy ra khi ứng dụng thực hiện 1 câu truy vấn SELECT để lấy danh sách N thực thể cha, sau đó phát sinh thêm N câu truy vấn SELECT riêng lẻ để nạp quan hệ FetchType.LAZY của từng thực thể cha.',
        conditions: [
            'Quan hệ @ManyToOne hoặc @OneToMany được cấu hình FetchType.LAZY',
            'Truy cập thuộc tính quan hệ bên trong vòng lặp hoặc khi ánh xạ sang DTO'
        ],
        exceptions: [
            'Không nên đổi toàn bộ Entity sang FetchType.EAGER vì sẽ luôn tải dư thừa dữ liệu ở mọi API không cần dùng quan hệ đó'
        ],
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        owner_id: 'cccccccc-cccc-cccc-dddd-ddddddddddde',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c08',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c06'
    },
    {
        id: 'd0000000-1122-3344-5566-778899aabb05',
        canonical_code: 'DIJKSTRA',
        content: 'Thuật toán Dijkstra tìm đường đi ngắn nhất từ một đỉnh nguồn u0 đến tất cả các đỉnh còn lại trên đồ thị có trọng số không âm theo chiến lược tham lam kết hợp hàng đợi ưu tiên (PriorityQueue).',
        conditions: [
            'Mọi cạnh (u, v) trên đồ thị bắt buộc có trọng số không âm: w(u, v) >= 0'
        ],
        exceptions: [
            'Không đảm bảo kết quả đúng nếu đồ thị có cạnh mang trọng số âm (cần chuyển sang thuật toán Bellman-Ford)'
        ],
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        owner_id: 'cccccccc-cccc-cccc-dddd-dddddddddddf',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c11',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c07'
    },
    {
        id: 'd0000000-1122-3344-5566-778899aabb06',
        canonical_code: 'RAG_EMBEDDING',
        content: 'Hybrid RAG kết hợp tìm kiếm tương đồng ngữ nghĩa trên Vector Database (ChromaDB) với truy xuất cấu trúc sư phạm trên Đồ thị Tri thức (Neo4j) để cung cấp ngữ cảnh chuẩn xác cho LLM.',
        conditions: [
            'Văn bản học liệu cần được chia nhỏ (chunking) với kích thước 250-512 tokens và có độ gối đầu (chunk_overlap) khoảng 10-15%'
        ],
        exceptions: [
            'Nếu đặt chunk_overlap = 0 sẽ dễ làm đứt gãy ngữ cảnh giữa phần định nghĩa ở cuối đoạn trước và ví dụ minh họa ở đầu đoạn sau'
        ],
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        owner_id: 'cccccccc-cccc-cccc-dddd-ddddddddddd1',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c12',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c04'
    }
] AS d_row
MATCH (ke:KnowledgeEntity {canonical_code: d_row.canonical_code})
MERGE (d:Definition {id: d_row.id})
SET d.content = d_row.content,
    d.conditions = d_row.conditions,
    d.exceptions = d_row.exceptions,
    d.owner_role = d_row.owner_role,
    d.scope = d_row.scope,
    d.owner_id = d_row.owner_id,
    d.source_chunk_id = d_row.source_chunk_id,
    d.graph_revision_id = d_row.graph_revision_id,
    d.created_at = '2026-10-20T08:05:00Z',
    d.updated_at = '2026-10-20T08:05:00Z'
MERGE (ke)-[r:HAS_DEFINITION]->(d)
SET r.graph_revision_id = d_row.graph_revision_id;


// ------------------------------------------------------------------------------
// PHẦN 4: KHỞI TẠO 6 NODE `:Process` VÀ 15 NODE `:ProcessStep` (ĐẦY ĐỦ graph_revision_id)
// Khớp 1-1 với UNHEX('77889900112233445566778899AABB01'..'06') trong MySQL
// ------------------------------------------------------------------------------

// --- Quy trình 1: Kiểm tra 3NF vs BCNF khi có nhiều khóa ứng viên chồng lấn ---
MATCH (ke:KnowledgeEntity {canonical_code: 'CHUAN_HOA_BCNF'})
MERGE (p:Process {id: '77889900-1122-3344-5566-778899aabb01'})
SET p.name = 'Quy trình kiểm tra dạng chuẩn 3NF và BCNF khi có nhiều khóa ứng viên chồng lấn',
    p.description = 'Phương pháp 3 bước tính bao đóng, kiểm tra thuộc tính khóa ở 3NF và kiểm tra siêu khóa vế trái ở BCNF.',
    p.owner_role = 'TEACHER',
    p.scope = 'TEACHER',
    p.owner_id = 'cccccccc-cccc-cccc-dddd-dddddddddddd',
    p.source_chunk_id = '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c05',
    p.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03',
    p.created_at = '2026-10-20T08:05:00Z',
    p.updated_at = '2026-10-20T08:05:00Z'
MERGE (ke)-[r_kp:HAS_PROCESS]->(p)
SET r_kp.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
MERGE (s1:ProcessStep {id: 'b0000000-1122-3344-5566-778899aabb01'})
SET s1.process_id = '77889900-1122-3344-5566-778899aabb01',
    s1.step_number = 1,
    s1.action = 'Tìm bao đóng tập thuộc tính để xác định toàn bộ các khóa dự tuyển (Candidate Keys) và liệt kê tập thuộc tính khóa (Prime Attributes).',
    s1.hint_prompt = 'Dựa vào tập phụ thuộc hàm F, thuộc tính nào không hề xuất hiện ở vế phải? Hãy tính bao đóng để liệt kê tất cả các khóa dự tuyển và cho biết những thuộc tính nào là thuộc tính khóa?',
    s1.owner_role = 'TEACHER',
    s1.scope = 'TEACHER',
    s1.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03',
    s1.created_at = '2026-10-20T08:05:00Z'
MERGE (s2:ProcessStep {id: 'b0000000-1122-3344-5566-778899aabb02'})
SET s2.process_id = '77889900-1122-3344-5566-778899aabb01',
    s2.step_number = 2,
    s2.action = 'Kiểm tra điều kiện chuẩn 3NF: Với mỗi phụ thuộc hàm X -> Y, xét xem X có phải siêu khóa hoặc Y có phải thuộc tính khóa hay không.',
    s2.hint_prompt = 'Khi tất cả các thuộc tính ở vế phải đều là thuộc tính khóa, theo định nghĩa 3NF thì có phụ thuộc hàm nào vi phạm 3NF không?',
    s2.owner_role = 'TEACHER',
    s2.scope = 'TEACHER',
    s2.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03',
    s2.created_at = '2026-10-20T08:05:00Z'
MERGE (s3:ProcessStep {id: 'b0000000-1122-3344-5566-778899aabb03'})
SET s3.process_id = '77889900-1122-3344-5566-778899aabb01',
    s3.step_number = 3,
    s3.action = 'Kiểm tra điều kiện chuẩn BCNF: Xét từng phụ thuộc hàm không tầm thường X -> Y xem vế trái X có bắt buộc là siêu khóa hay không.',
    s3.hint_prompt = 'Chuẩn BCNF không còn quan tâm vế phải là thuộc tính khóa nữa mà bắt buộc vế trái X phải là siêu khóa. Vậy phụ thuộc hàm nào trong F đang có vế trái không phải là siêu khóa?',
    s3.owner_role = 'TEACHER',
    s3.scope = 'TEACHER',
    s3.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03',
    s3.created_at = '2026-10-20T08:05:00Z'
MERGE (p)-[r_ps1:HAS_STEP {step_number: 1}]->(s1)
SET r_ps1.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
MERGE (p)-[r_ps2:HAS_STEP {step_number: 2}]->(s2)
SET r_ps2.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
MERGE (p)-[r_ps3:HAS_STEP {step_number: 3}]->(s3)
SET r_ps3.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
MERGE (s1)-[r_n1:NEXT_STEP]->(s2)
SET r_n1.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
MERGE (s2)-[r_n2:NEXT_STEP]->(s3)
SET r_n2.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03';

// --- Quy trình 2: Truy vấn Top K mỗi nhóm bằng Window Function DENSE_RANK ---
MATCH (ke:KnowledgeEntity {canonical_code: 'SQL_JOIN'})
MERGE (p:Process {id: '77889900-1122-3344-5566-778899aabb02'})
SET p.name = 'Quy trình viết câu lệnh SQL tìm Top K sinh viên điểm cao nhất mỗi lớp trên MySQL 8.0',
    p.description = 'Quy trình lựa chọn hàm cửa sổ xếp hạng không nhảy cóc DENSE_RANK và đóng gói trong biểu thức bảng chung CTE.',
    p.owner_role = 'TEACHER',
    p.scope = 'TEACHER',
    p.owner_id = 'cccccccc-cccc-cccc-dddd-dddddddddddd',
    p.source_chunk_id = '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c02',
    p.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c02',
    p.created_at = '2026-10-20T08:05:00Z',
    p.updated_at = '2026-10-20T08:05:00Z'
MERGE (ke)-[r_kp:HAS_PROCESS]->(p)
SET r_kp.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c02'
MERGE (s1:ProcessStep {id: 'b0000000-1122-3344-5566-778899aabb04'})
SET s1.process_id = '77889900-1122-3344-5566-778899aabb02',
    s1.step_number = 1,
    s1.action = 'So sánh cách đánh số thứ hạng của ROW_NUMBER(), RANK() và DENSE_RANK() trên tập điểm có giá trị trùng nhau.',
    s1.hint_prompt = 'Giả sử 4 sinh viên trong lớp có điểm [9.5, 9.5, 9.0, 8.5], ba hàm ROW_NUMBER(), RANK() và DENSE_RANK() sẽ đánh số thứ hạng cho 4 bạn này khác nhau như thế nào?',
    s1.owner_role = 'TEACHER',
    s1.scope = 'TEACHER',
    s1.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c02',
    s1.created_at = '2026-10-20T08:05:00Z'
MERGE (s2:ProcessStep {id: 'b0000000-1122-3344-5566-778899aabb05'})
SET s2.process_id = '77889900-1122-3344-5566-778899aabb02',
    s2.step_number = 2,
    s2.action = 'Đặt hàm DENSE_RANK() OVER (PARTITION BY class_id ORDER BY final_score DESC) bên trong CTE (WITH) và lọc rnk <= 3 ở truy vấn ngoài.',
    s2.hint_prompt = 'Vì MySQL không cho phép đặt hàm cửa sổ trực tiếp trong mệnh đề WHERE, bạn sẽ kết hợp CTE (WITH) với điều kiện lọc thứ hạng rnk <= 3 như thế nào?',
    s2.owner_role = 'TEACHER',
    s2.scope = 'TEACHER',
    s2.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c02',
    s2.created_at = '2026-10-20T08:05:00Z'
MERGE (p)-[r_ps1:HAS_STEP {step_number: 1}]->(s1)
SET r_ps1.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c02'
MERGE (p)-[r_ps2:HAS_STEP {step_number: 2}]->(s2)
SET r_ps2.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c02'
MERGE (s1)-[r_n:NEXT_STEP]->(s2)
SET r_n.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c02';

// --- Quy trình 3: Phân biệt nhanh vi phạm 2NF và vi phạm 3NF ---
MATCH (ke:KnowledgeEntity {canonical_code: 'CHUAN_HOA_3NF'})
MERGE (p:Process {id: '77889900-1122-3344-5566-778899aabb03'})
SET p.name = 'Quy trình nhận diện phụ thuộc hàm bộ phận (vi phạm 2NF) và phụ thuộc bắc cầu (vi phạm 3NF)',
    p.description = 'Quy trình phát hiện vi phạm phụ thuộc hàm bộ phận và bắc cầu để tiến hành phân rã lược đồ đạt chuẩn 3NF.',
    p.owner_role = 'TEACHER',
    p.scope = 'TEACHER',
    p.owner_id = 'cccccccc-cccc-cccc-dddd-dddddddddddd',
    p.source_chunk_id = '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c04',
    p.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03',
    p.created_at = '2026-10-20T08:05:00Z',
    p.updated_at = '2026-10-20T08:05:00Z'
MERGE (ke)-[r_kp:HAS_PROCESS]->(p)
SET r_kp.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
MERGE (s1:ProcessStep {id: 'b0000000-1122-3344-5566-778899aabb06'})
SET s1.process_id = '77889900-1122-3344-5566-778899aabb03',
    s1.step_number = 1,
    s1.action = 'Kiểm tra xem vế trái của phụ thuộc hàm có phải là một tập con thực sự của khóa dự tuyển ghép hay không (dấu hiệu vi phạm 2NF).',
    s1.hint_prompt = 'Khi khóa chính là cặp (MaSV, MaMon), ở phụ thuộc hàm MaSV -> HoTenSV thì vế trái MaSV có quan hệ gì với khóa chính?',
    s1.owner_role = 'TEACHER',
    s1.scope = 'TEACHER',
    s1.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03',
    s1.created_at = '2026-10-20T08:05:00Z'
MERGE (s2:ProcessStep {id: 'b0000000-1122-3344-5566-778899aabb07'})
SET s2.process_id = '77889900-1122-3344-5566-778899aabb03',
    s2.step_number = 2,
    s2.action = 'Kiểm tra xem cả vế trái và vế phải đều là các thuộc tính không khóa suy ra nhau hay không (dấu hiệu vi phạm 3NF).',
    s2.hint_prompt = 'Ở phụ thuộc hàm MaKhoa -> TenKhoa, cả MaKhoa lẫn TenKhoa có nằm trong khóa chính không? Khi thuộc tính không khóa suy ra thuộc tính không khóa khác thì vi phạm dạng chuẩn mấy?',
    s2.owner_role = 'TEACHER',
    s2.scope = 'TEACHER',
    s2.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03',
    s2.created_at = '2026-10-20T08:05:00Z'
MERGE (s3:ProcessStep {id: 'b0000000-1122-3344-5566-778899aabb08'})
SET s3.process_id = '77889900-1122-3344-5566-778899aabb03',
    s3.step_number = 3,
    s3.action = 'Tách các thuộc tính phụ thuộc bộ phận và phụ thuộc bắc cầu ra bảng riêng sao cho bảo toàn thông tin và phụ thuộc hàm.',
    s3.hint_prompt = 'Để lược đồ đạt chuẩn 3NF, bạn sẽ tách bảng KetQuaHocTap thành mấy bảng con với khóa chính của từng bảng là gì?',
    s3.owner_role = 'TEACHER',
    s3.scope = 'TEACHER',
    s3.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03',
    s3.created_at = '2026-10-20T08:05:00Z'
MERGE (p)-[r_ps1:HAS_STEP {step_number: 1}]->(s1)
SET r_ps1.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
MERGE (p)-[r_ps2:HAS_STEP {step_number: 2}]->(s2)
SET r_ps2.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
MERGE (p)-[r_ps3:HAS_STEP {step_number: 3}]->(s3)
SET r_ps3.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
MERGE (s1)-[r_n1:NEXT_STEP]->(s2)
SET r_n1.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
MERGE (s2)-[r_n2:NEXT_STEP]->(s3)
SET r_n2.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03';

// --- Quy trình 4: Xử lý LazyInitializationException và N+1 Query trong Spring Data JPA ---
MATCH (ke:KnowledgeEntity {canonical_code: 'JPA_N_PLUS_1'})
MERGE (p:Process {id: '77889900-1122-3344-5566-778899aabb04'})
SET p.name = 'Quy trình khắc phục lỗi LazyInitializationException và N+1 Query khi tắt open-in-view',
    p.description = 'Quy trình thiết lập ranh giới giao dịch ở Service và sử dụng @EntityGraph tại Repository để nạp dữ liệu bằng một câu lệnh LEFT JOIN.',
    p.owner_role = 'TEACHER',
    p.scope = 'TEACHER',
    p.owner_id = 'cccccccc-cccc-cccc-dddd-ddddddddddde',
    p.source_chunk_id = '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c08',
    p.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c06',
    p.created_at = '2026-10-20T08:05:00Z',
    p.updated_at = '2026-10-20T08:05:00Z'
MERGE (ke)-[r_kp:HAS_PROCESS]->(p)
SET r_kp.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c06'
MERGE (s1:ProcessStep {id: 'b0000000-1122-3344-5566-778899aabb09'})
SET s1.process_id = '77889900-1122-3344-5566-778899aabb04',
    s1.step_number = 1,
    s1.action = 'Kiểm tra phạm vi phiên Hibernate (@Transactional) ở tầng Service và đếm số câu lệnh SELECT phát sinh khi lặp qua danh sách Entity.',
    s1.hint_prompt = 'Nếu hàm ở Service chưa có @Transactional(readOnly = true) hoặc lặp qua 10 ClassEntity để gọi getOwner(), Hibernate sẽ bắn ra bao nhiêu câu lệnh SELECT?',
    s1.owner_role = 'TEACHER',
    s1.scope = 'TEACHER',
    s1.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c06',
    s1.created_at = '2026-10-20T08:05:00Z'
MERGE (s2:ProcessStep {id: 'b0000000-1122-3344-5566-778899aabb10'})
SET s2.process_id = '77889900-1122-3344-5566-778899aabb04',
    s2.step_number = 2,
    s2.action = 'Kết hợp @Transactional(readOnly = true) tại Service với @EntityGraph(attributePaths = {"owner"}) tại Repository để gom thành 1 câu lệnh LEFT JOIN.',
    s2.hint_prompt = 'Làm thế nào để ép Hibernate tải sẵn luôn đối tượng owner bằng 1 câu lệnh LEFT JOIN duy nhất ngay tại ClassRepository mà không cần đổi sang FetchType.EAGER?',
    s2.owner_role = 'TEACHER',
    s2.scope = 'TEACHER',
    s2.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c06',
    s2.created_at = '2026-10-20T08:05:00Z'
MERGE (p)-[r_ps1:HAS_STEP {step_number: 1}]->(s1)
SET r_ps1.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c06'
MERGE (p)-[r_ps2:HAS_STEP {step_number: 2}]->(s2)
SET r_ps2.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c06'
MERGE (s1)-[r_n:NEXT_STEP]->(s2)
SET r_n.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c06';

// --- Quy trình 5: Phân tích thuật toán Dijkstra & xây dựng phản ví dụ cạnh âm ---
MATCH (ke:KnowledgeEntity {canonical_code: 'DIJKSTRA'})
MERGE (p:Process {id: '77889900-1122-3344-5566-778899aabb05'})
SET p.name = 'Quy trình phân tích nguyên lý tham lam của Dijkstra và xây dựng phản ví dụ đồ thị có cạnh âm',
    p.description = 'Quy trình phân tích tính đúng đắn của chiến lược tham lam và cách thiết kế đồ thị phản ví dụ với cạnh trọng số âm.',
    p.owner_role = 'TEACHER',
    p.scope = 'TEACHER',
    p.owner_id = 'cccccccc-cccc-cccc-dddd-dddddddddddf',
    p.source_chunk_id = '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c11',
    p.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c07',
    p.created_at = '2026-10-20T08:05:00Z',
    p.updated_at = '2026-10-20T08:05:00Z'
MERGE (ke)-[r_kp:HAS_PROCESS]->(p)
SET r_kp.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c07'
MERGE (s1:ProcessStep {id: 'b0000000-1122-3344-5566-778899aabb11'})
SET s1.process_id = '77889900-1122-3344-5566-778899aabb05',
    s1.step_number = 1,
    s1.action = 'Xác định giả định cốt lõi khi thuật toán Dijkstra lấy đỉnh có khoảng cách nhỏ nhất ra khỏi PriorityQueue và đóng đỉnh đó lại.',
    s1.hint_prompt = 'Khi Dijkstra lấy đỉnh C có d[C] nhỏ nhất ra khỏi PriorityQueue trước đỉnh B (d[C] < d[B]), thuật toán đang giả định điều gì về mọi đường đi đi vòng qua B tới C?',
    s1.owner_role = 'TEACHER',
    s1.scope = 'TEACHER',
    s1.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c07',
    s1.created_at = '2026-10-20T08:05:00Z'
MERGE (s2:ProcessStep {id: 'b0000000-1122-3344-5566-778899aabb12'})
SET s2.process_id = '77889900-1122-3344-5566-778899aabb05',
    s2.step_number = 2,
    s2.action = 'Thiết kế đồ thị có hướng 3 đỉnh A, B, C với 1 cạnh âm B -> C sao cho tổng đường đi A -> B -> C nhỏ hơn cạnh trực tiếp A -> C.',
    s2.hint_prompt = 'Hãy thử chọn trọng số cho 3 cạnh A -> B, A -> C (dương) và B -> C (âm) sao cho Dijkstra chốt nhầm đỉnh C trước khi kịp xét cạnh âm từ B?',
    s2.owner_role = 'TEACHER',
    s2.scope = 'TEACHER',
    s2.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c07',
    s2.created_at = '2026-10-20T08:05:00Z'
MERGE (p)-[r_ps1:HAS_STEP {step_number: 1}]->(s1)
SET r_ps1.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c07'
MERGE (p)-[r_ps2:HAS_STEP {step_number: 2}]->(s2)
SET r_ps2.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c07'
MERGE (s1)-[r_n:NEXT_STEP]->(s2)
SET r_n.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c07';

// --- Quy trình 6: Thiết kế Text Chunker & Overlap cho Hybrid RAG tiếng Việt ---
MATCH (ke:KnowledgeEntity {canonical_code: 'RAG_EMBEDDING'})
MERGE (p:Process {id: '77889900-1122-3344-5566-778899aabb06'})
SET p.name = 'Quy trình lựa chọn kích thước chunk_size và chunk_overlap cho hệ thống RAG giáo trình đại học',
    p.description = 'Quy trình đánh giá sự đánh đổi giữa độ dài phân đoạn và độ trôi ngữ nghĩa, xác định tham số gối đầu tối ưu cho tài liệu tiếng Việt.',
    p.owner_role = 'TEACHER',
    p.scope = 'TEACHER',
    p.owner_id = 'cccccccc-cccc-cccc-dddd-ddddddddddd1',
    p.source_chunk_id = '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c12',
    p.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c04',
    p.created_at = '2026-10-20T08:05:00Z',
    p.updated_at = '2026-10-20T08:05:00Z'
MERGE (ke)-[r_kp:HAS_PROCESS]->(p)
SET r_kp.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c04'
MERGE (s1:ProcessStep {id: 'b0000000-1122-3344-5566-778899aabb13'})
SET s1.process_id = '77889900-1122-3344-5566-778899aabb06',
    s1.step_number = 1,
    s1.action = 'Phân tích sự đánh đổi khi chọn chunk_size quá nhỏ (<100 tokens) hoặc quá lớn (>2000 tokens).',
    s1.hint_prompt = 'Nếu cắt mỗi chunk quá ngắn (chỉ 1-2 câu) hoặc quá dài (cả chương học), độ chính xác của vector embedding khi tìm kiếm tương đồng sẽ bị ảnh hưởng thế nào?',
    s1.owner_role = 'TEACHER',
    s1.scope = 'TEACHER',
    s1.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c04',
    s1.created_at = '2026-10-20T08:05:00Z'
MERGE (s2:ProcessStep {id: 'b0000000-1122-3344-5566-778899aabb14'})
SET s2.process_id = '77889900-1122-3344-5566-778899aabb06',
    s2.step_number = 2,
    s2.action = 'Đánh giá vai trò của phần gối đầu (chunk_overlap) tại vị trí ranh giới giữa Định nghĩa lý thuyết và Ví dụ minh họa.',
    s2.hint_prompt = 'Nếu nhát cắt rơi đúng vào giữa câu tiêu đề Định nghĩa BCNF (cuối Chunk 1) và công thức Ví dụ R(A,B,C,D) (đầu Chunk 2) mà chunk_overlap = 0, chuyện gì xảy ra khi sinh viên tìm ví dụ về BCNF?',
    s2.owner_role = 'TEACHER',
    s2.scope = 'TEACHER',
    s2.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c04',
    s2.created_at = '2026-10-20T08:05:00Z'
MERGE (s3:ProcessStep {id: 'b0000000-1122-3344-5566-778899aabb15'})
SET s3.process_id = '77889900-1122-3344-5566-778899aabb06',
    s3.step_number = 3,
    s3.action = 'Chốt cấu hình chunk_size (250-512 tokens) và chunk_overlap (10-15%) kết hợp ưu tiên ngắt theo đoạn văn.',
    s3.hint_prompt = 'Với chunk_size = 300 đến 512 tokens, bạn nên đặt chunk_overlap bao nhiêu tokens và ưu tiên tách theo ký tự ngắt dòng nào?',
    s3.owner_role = 'TEACHER',
    s3.scope = 'TEACHER',
    s3.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c04',
    s3.created_at = '2026-10-20T08:05:00Z'
MERGE (p)-[r_ps1:HAS_STEP {step_number: 1}]->(s1)
SET r_ps1.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c04'
MERGE (p)-[r_ps2:HAS_STEP {step_number: 2}]->(s2)
SET r_ps2.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c04'
MERGE (p)-[r_ps3:HAS_STEP {step_number: 3}]->(s3)
SET r_ps3.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c04'
MERGE (s1)-[r_n1:NEXT_STEP]->(s2)
SET r_n1.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c04'
MERGE (s2)-[r_n2:NEXT_STEP]->(s3)
SET r_n2.graph_revision_id = '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c04';


// ------------------------------------------------------------------------------
// PHẦN 5: KHỞI TẠO NODE `:Example` (GẮN graph_revision_id, owner_role, scope)
// ------------------------------------------------------------------------------
UNWIND [
    {
        id: 'e0000000-1122-3344-5566-778899aabb01',
        canonical_code: 'SQL_JOIN',
        title: 'Truy vấn lấy Top 3 sinh viên có điểm cuối kỳ cao nhất mỗi lớp bằng CTE và DENSE_RANK()',
        code_snippet: 'WITH RankedStudents AS (\n    SELECT cm.class_id, cm.user_id, gr.final_score,\n           DENSE_RANK() OVER (PARTITION BY cm.class_id ORDER BY gr.final_score DESC) AS rnk\n    FROM class_members cm\n    INNER JOIN grade_reports gr ON gr.class_member_id = cm.id\n    WHERE cm.role = \'STUDENT\' AND gr.final_score IS NOT NULL\n)\nSELECT * FROM RankedStudents WHERE rnk <= 3;',
        explanation: 'DENSE_RANK() đảm bảo khi có nhiều sinh viên đồng điểm hạng Nhất hoặc Nhì thì thứ hạng kế tiếp không bị nhảy cóc như RANK(), giữ đủ 3 mốc điểm cao nhất của từng lớp.',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        owner_id: 'cccccccc-cccc-cccc-dddd-dddddddddddd',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c02',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c02'
    },
    {
        id: 'e0000000-1122-3344-5566-778899aabb02',
        canonical_code: 'JPA_N_PLUS_1',
        title: 'Sử dụng @EntityGraph trong ClassRepository để nạp sẵn owner trong 1 câu lệnh LEFT JOIN',
        code_snippet: '@Repository\npublic interface ClassRepository extends JpaRepository<ClassEntity, UUID>, JpaSpecificationExecutor<ClassEntity> {\n    @Override\n    @EntityGraph(attributePaths = {"owner"})\n    Page<ClassEntity> findAll(Specification<ClassEntity> spec, Pageable pageable);\n}',
        explanation: 'Khi kết hợp với @Transactional(readOnly = true) ở ClassService, Hibernate tự động sinh 1 câu lệnh SELECT ... LEFT JOIN users duy nhất thay vì N+1 câu truy vấn.',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        owner_id: 'cccccccc-cccc-cccc-dddd-ddddddddddde',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c08',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c06'
    }
] AS ex_row
MATCH (ke:KnowledgeEntity {canonical_code: ex_row.canonical_code})
MERGE (ex:Example {id: ex_row.id})
SET ex.title = ex_row.title,
    ex.code_snippet = ex_row.code_snippet,
    ex.explanation = ex_row.explanation,
    ex.owner_role = ex_row.owner_role,
    ex.scope = ex_row.scope,
    ex.owner_id = ex_row.owner_id,
    ex.source_chunk_id = ex_row.source_chunk_id,
    ex.graph_revision_id = ex_row.graph_revision_id,
    ex.created_at = '2026-10-20T08:10:00Z',
    ex.updated_at = '2026-10-20T08:10:00Z'
MERGE (ke)-[r:HAS_EXAMPLE]->(ex)
SET r.graph_revision_id = ex_row.graph_revision_id;


// ------------------------------------------------------------------------------
// PHẦN 6: KHỞI TẠO NODE `:Argument` (GẮN graph_revision_id, owner_role, scope)
// ------------------------------------------------------------------------------
UNWIND [
    {
        id: 'a0000000-1122-3344-5566-778899aabb01',
        canonical_code: 'CHUAN_HOA_BCNF',
        hypothesis: 'Cho lược đồ R(A, B, C, D) với tập phụ thuộc hàm F = {AB -> C, C -> D, D -> A}.',
        evidence: 'Bao đóng cho thấy R có 3 khóa dự tuyển là AB, BC, BD nên cả 4 thuộc tính A, B, C, D đều là thuộc tính khóa (thỏa mãn 3NF). Tuy nhiên trong hai phụ thuộc hàm C -> D và D -> A, vế trái C và D không chứa B nên không phải là siêu khóa.',
        conclusion: 'Lược đồ R đạt dạng chuẩn 3 (3NF) nhưng vi phạm dạng chuẩn Boyce-Codd (BCNF).',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        owner_id: 'cccccccc-cccc-cccc-dddd-dddddddddddd',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c05',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
    },
    {
        id: 'a0000000-1122-3344-5566-778899aabb02',
        canonical_code: 'DIJKSTRA',
        hypothesis: 'Xét đồ thị có hướng 3 đỉnh A, B, C với đỉnh nguồn A và trọng số các cạnh: w(A, B) = 5, w(A, C) = 2, w(B, C) = -10.',
        evidence: 'Tại bước đầu, d[C] = 2 < d[B] = 5 nên Dijkstra lấy C ra khỏi PriorityQueue trước và chốt cố định khoảng cách ngắn nhất tới C là 2. Trong khi đó đường đi A -> B -> C có tổng trọng số là 5 + (-10) = -5 < 2.',
        conclusion: 'Thuật toán tham lam Dijkstra không đảm bảo kết quả đúng khi đồ thị xuất hiện cạnh có trọng số âm.',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        owner_id: 'cccccccc-cccc-cccc-dddd-dddddddddddf',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c11',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c07'
    }
] AS arg_row
MATCH (ke:KnowledgeEntity {canonical_code: arg_row.canonical_code})
MERGE (arg:Argument {id: arg_row.id})
SET arg.hypothesis = arg_row.hypothesis,
    arg.evidence = arg_row.evidence,
    arg.conclusion = arg_row.conclusion,
    arg.owner_role = arg_row.owner_role,
    arg.scope = arg_row.scope,
    arg.owner_id = arg_row.owner_id,
    arg.source_chunk_id = arg_row.source_chunk_id,
    arg.graph_revision_id = arg_row.graph_revision_id,
    arg.created_at = '2026-10-20T08:10:00Z',
    arg.updated_at = '2026-10-20T08:10:00Z'
MERGE (ke)-[r:HAS_ARGUMENT]->(arg)
SET r.graph_revision_id = arg_row.graph_revision_id;


// ------------------------------------------------------------------------------
// PHẦN 7: KHỞI TẠO 6 NODE `:Exercise` (GẮN graph_revision_id, owner_role, scope)
// Khớp 1-1 với UNHEX('8899AABB112233445566778899AABB01'..'06') trong MySQL
// ------------------------------------------------------------------------------
UNWIND [
    {
        id: '8899aabb-1122-3344-5566-778899aabb01',
        canonical_code: 'CHUAN_HOA_BCNF',
        process_id: '77889900-1122-3344-5566-778899aabb01',
        title: 'Xác định dạng chuẩn cao nhất của lược đồ có các khóa ứng viên chồng lấn',
        content: 'Cho lược đồ quan hệ R(A, B, C, D) và tập phụ thuộc hàm F = {AB -> C, C -> D, D -> A}. Hãy tìm tất cả các khóa dự tuyển của R và giải thích tại sao R đạt 3NF nhưng chưa đạt BCNF.',
        difficulty: 'HARD',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        owner_id: 'cccccccc-cccc-cccc-dddd-dddddddddddd',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c05',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
    },
    {
        id: '8899aabb-1122-3344-5566-778899aabb02',
        canonical_code: 'SQL_JOIN',
        process_id: '77889900-1122-3344-5566-778899aabb02',
        title: 'Tìm Top 3 sinh viên có điểm tổng kết cao nhất mỗi lớp học phần',
        content: 'Sử dụng CTE và hàm cửa sổ trên MySQL 8.0, hãy viết truy vấn lấy danh sách sinh viên thuộc 3 mức điểm cao nhất của từng lớp sao cho không bỏ sót các sinh viên đồng hạng.',
        difficulty: 'MEDIUM',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        owner_id: 'cccccccc-cccc-cccc-dddd-dddddddddddd',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c02',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c02'
    },
    {
        id: '8899aabb-1122-3344-5566-778899aabb03',
        canonical_code: 'CHUAN_HOA_3NF',
        process_id: '77889900-1122-3344-5566-778899aabb03',
        title: 'Phân rã lược đồ KetQuaHocTap vi phạm 2NF và 3NF',
        content: 'Cho lược đồ KetQuaHocTap(MaSV, MaMon, HoTenSV, MaKhoa, TenKhoa, DiemThi) với khóa chính (MaSV, MaMon) và F = {MaSV -> HoTenSV, MaSV -> MaKhoa, MaKhoa -> TenKhoa, (MaSV, MaMon) -> DiemThi}. Hãy chỉ ra các phụ thuộc hàm vi phạm 2NF, 3NF và phân rã về chuẩn 3NF.',
        difficulty: 'MEDIUM',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        owner_id: 'cccccccc-cccc-cccc-dddd-dddddddddddd',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c04',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
    },
    {
        id: '8899aabb-1122-3344-5566-778899aabb04',
        canonical_code: 'JPA_N_PLUS_1',
        process_id: '77889900-1122-3344-5566-778899aabb04',
        title: 'Tối ưu hóa truy vấn danh sách Lớp học kèm thông tin Giảng viên sở hữu',
        content: 'Khi đặt spring.jpa.open-in-view=false, hãy tái cấu trúc phương thức lấy danh sách lớp học có phân trang tại ClassRepository và ClassService để không xảy ra LazyInitializationException và chỉ tốn 1 câu lệnh SELECT có JOIN.',
        difficulty: 'MEDIUM',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        owner_id: 'cccccccc-cccc-cccc-dddd-ddddddddddde',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c08',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c06'
    },
    {
        id: '8899aabb-1122-3344-5566-778899aabb05',
        canonical_code: 'DIJKSTRA',
        process_id: '77889900-1122-3344-5566-778899aabb05',
        title: 'Xây dựng phản ví dụ chứng minh Dijkstra sai trên đồ thị có cạnh âm',
        content: 'Cho đồ thị có hướng 3 đỉnh A, B, C với đỉnh xuất phát là A. Hãy gán trọng số cụ thể cho các cạnh A -> B, A -> C và B -> C (trong đó B -> C có trọng số âm) để chứng minh thuật toán Dijkstra kết luận sai đường đi ngắn nhất từ A tới C.',
        difficulty: 'HARD',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        owner_id: 'cccccccc-cccc-cccc-dddd-dddddddddddf',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c11',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c07'
    },
    {
        id: '8899aabb-1122-3344-5566-778899aabb06',
        canonical_code: 'RAG_EMBEDDING',
        process_id: '77889900-1122-3344-5566-778899aabb06',
        title: 'Thiết kế bộ chia nhỏ văn bản (Text Chunker) cho giáo trình tiếng Việt',
        content: 'Hãy phân tích ảnh hưởng của tham số chunk_size và chunk_overlap tới độ chính xác truy hồi ngữ nghĩa của hệ thống Gia sư Socratic và đề xuất bộ tham số tối ưu cho giáo trình đại học.',
        difficulty: 'MEDIUM',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        owner_id: 'cccccccc-cccc-cccc-dddd-ddddddddddd1',
        source_chunk_id: '8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c12',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c04'
    }
] AS exer_row
MATCH (ke:KnowledgeEntity {canonical_code: exer_row.canonical_code})
OPTIONAL MATCH (p:Process {id: exer_row.process_id})
MERGE (exer:Exercise {id: exer_row.id})
SET exer.title = exer_row.title,
    exer.content = exer_row.content,
    exer.difficulty = exer_row.difficulty,
    exer.owner_role = exer_row.owner_role,
    exer.scope = exer_row.scope,
    exer.owner_id = exer_row.owner_id,
    exer.source_chunk_id = exer_row.source_chunk_id,
    exer.graph_revision_id = exer_row.graph_revision_id,
    exer.created_at = '2026-10-20T08:10:00Z',
    exer.updated_at = '2026-10-20T08:10:00Z'
MERGE (ke)-[r_ke:HAS_EXERCISE]->(exer)
SET r_ke.graph_revision_id = exer_row.graph_revision_id
FOREACH (_ IN CASE WHEN p IS NOT NULL THEN [1] ELSE [] END |
    MERGE (exer)-[r_ep:USES_PROCESS]->(p)
    SET r_ep.graph_revision_id = exer_row.graph_revision_id
);


// ------------------------------------------------------------------------------
// PHẦN 8: KHỞI TẠO 15 NODE `:ExerciseStep` (GẮN graph_revision_id, owner_role, scope)
// - Khớp 1-1 với UNHEX('C0000000112233445566778899AABB01'..'15')
// - Nối từ (:Exercise)-[:HAS_EXERCISE_STEP {step_number, graph_revision_id}]->(:ExerciseStep)
// - Nối chuỗi thứ tự (:ExerciseStep)-[:NEXT_EXERCISE_STEP {graph_revision_id}]->(:ExerciseStep)
// - Ánh xạ sang bước phương pháp (:ExerciseStep)-[:MAPS_TO_PROCESS_STEP {graph_revision_id}]->(:ProcessStep)
// ------------------------------------------------------------------------------
UNWIND [
    // === Bài tập 1 (8899aabb-...-01): Kiểm tra 3NF vs BCNF trên R(A,B,C,D), F={AB->C, C->D, D->A} ===
    {
        id: 'c0000000-1122-3344-5566-778899aabb01',
        exercise_id: '8899aabb-1122-3344-5566-778899aabb01',
        process_step_id: 'b0000000-1122-3344-5566-778899aabb01',
        step_number: 1,
        instruction: 'Xác định thuộc tính nguồn (không xuất hiện ở vế phải của F) và tính bao đóng để tìm tất cả các khóa dự tuyển của lược đồ R(A,B,C,D).',
        expected_outcome: 'Thuộc tính B không xuất hiện ở vế phải nên mọi khóa phải chứa B. Tính bao đóng (AB)+ = ABCD, (BC)+ = BCDA, (BD)+ = BDAC => 3 khóa dự tuyển là AB, BC, BD và tập thuộc tính khóa Prime = {A, B, C, D}.',
        socratic_question: 'Quan sát tập F = {AB -> C, C -> D, D -> A}, thuộc tính nào không hề xuất hiện ở vế phải? Từ đó khi ghép thuộc tính đó với A, C, D để tính bao đóng thì bạn tìm được những khóa dự tuyển nào?',
        common_mistake: 'Sinh viên thường chỉ tìm được khóa AB mà bỏ sót hai khóa dự tuyển chồng lấn là BC và BD (do D -> A và C -> D -> A).',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
    },
    {
        id: 'c0000000-1122-3344-5566-778899aabb02',
        exercise_id: '8899aabb-1122-3344-5566-778899aabb01',
        process_step_id: 'b0000000-1122-3344-5566-778899aabb02',
        step_number: 2,
        instruction: 'Đối chiếu 3 phụ thuộc hàm AB -> C, C -> D, D -> A với điều kiện của dạng chuẩn 3 (3NF).',
        expected_outcome: 'Vì cả 4 thuộc tính A, B, C, D đều nằm trong các khóa dự tuyển {AB, BC, BD} nên mọi thuộc tính vế phải (C, D, A) đều là thuộc tính khóa (Prime Attribute) => Lược đồ R thỏa mãn hoàn toàn chuẩn 3NF.',
        socratic_question: 'Từ 3 khóa dự tuyển AB, BC, BD vừa tìm được ở Bước 1, có thuộc tính nào của R là thuộc tính không khóa (Non-prime) không? Vậy theo định nghĩa 3NF, hai phụ thuộc hàm C -> D và D -> A có được chấp nhận ở 3NF không?',
        common_mistake: 'Nhầm lẫn rằng C -> D vi phạm 3NF vì quên mất D đã tham gia vào khóa dự tuyển BD (D là thuộc tính khóa).',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
    },
    {
        id: 'c0000000-1122-3344-5566-778899aabb03',
        exercise_id: '8899aabb-1122-3344-5566-778899aabb01',
        process_step_id: 'b0000000-1122-3344-5566-778899aabb03',
        step_number: 3,
        instruction: 'Kiểm tra điều kiện siêu khóa ở vế trái đối với chuẩn BCNF cho hai phụ thuộc hàm C -> D và D -> A.',
        expected_outcome: 'Ở C -> D và D -> A, vế trái là C (bao đóng C+ = CDA) và D (bao đóng D+ = DA) đều thiếu B nên không phải là siêu khóa của R => Vi phạm chuẩn BCNF.',
        socratic_question: 'Ở chuẩn BCNF, mọi vế trái bắt buộc phải là siêu khóa (không còn ngoại lệ cho thuộc tính khóa ở vế phải). Bạn hãy kiểm tra bao đóng C+ và D+ xem C và D có phải là siêu khóa của R không?',
        common_mistake: 'Kết luận R đạt BCNF vì tưởng rằng không có thuộc tính không khóa thì tự động đạt BCNF.',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
    },

    // === Bài tập 2 (8899aabb-...-02): Tìm Top 3 sinh viên điểm cao nhất mỗi lớp bằng CTE & DENSE_RANK ===
    {
        id: 'c0000000-1122-3344-5566-778899aabb04',
        exercise_id: '8899aabb-1122-3344-5566-778899aabb02',
        process_step_id: 'b0000000-1122-3344-5566-778899aabb04',
        step_number: 1,
        instruction: 'Lựa chọn hàm cửa sổ xếp hạng phù hợp (DENSE_RANK vs RANK vs ROW_NUMBER) và viết mệnh đề OVER (PARTITION BY ... ORDER BY ...).',
        expected_outcome: 'Chọn DENSE_RANK() OVER (PARTITION BY cm.class_id ORDER BY gr.final_score DESC) AS rnk để không bị nhảy cóc thứ hạng khi có sinh viên đồng điểm.',
        socratic_question: 'Để lấy đủ 3 mức điểm cao nhất của mỗi lớp mà không làm mất các bạn đồng điểm cũng không bị nhảy số hạng (ví dụ 1, 1, 2 thay vì 1, 1, 3), bạn cần chọn hàm cửa sổ nào và phân vùng (PARTITION BY) theo cột nào?',
        common_mistake: 'Dùng ROW_NUMBER() làm cắt mất sinh viên đồng điểm, hoặc dùng RANK() làm nhảy mất mốc điểm thứ 2 khi có 3 bạn đồng hạng 1.',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c02'
    },
    {
        id: 'c0000000-1122-3344-5566-778899aabb05',
        exercise_id: '8899aabb-1122-3344-5566-778899aabb02',
        process_step_id: 'b0000000-1122-3344-5566-778899aabb05',
        step_number: 2,
        instruction: 'Bọc truy vấn xếp hạng vào trong biểu thức bảng chung CTE (WITH RankedStudents AS (...)) và lọc rnk <= 3 ở truy vấn bên ngoài.',
        expected_outcome: 'Viết hoàn chỉnh khối WITH RankedStudents AS (...) SELECT * FROM RankedStudents WHERE rnk <= 3.',
        socratic_question: 'Sau khi đã có biểu thức DENSE_RANK() AS rnk, nếu viết WHERE rnk <= 3 ngay trong cùng câu SELECT thì MySQL sẽ báo lỗi. Bạn hãy viết cấu trúc CTE (WITH ...) để lọc rnk <= 3 ở truy vấn ngoài nhé?',
        common_mistake: 'Đặt trực tiếp điều kiện DENSE_RANK() OVER (...) <= 3 ở mệnh đề WHERE hoặc HAVING.',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c02'
    },

    // === Bài tập 3 (8899aabb-...-03): Phân rã lược đồ KetQuaHocTap vi phạm 2NF và 3NF ===
    {
        id: 'c0000000-1122-3344-5566-778899aabb06',
        exercise_id: '8899aabb-1122-3344-5566-778899aabb03',
        process_step_id: 'b0000000-1122-3344-5566-778899aabb06',
        step_number: 1,
        instruction: 'Xác định các phụ thuộc hàm bộ phận vào khóa chính ghép (MaSV, MaMon) gây vi phạm chuẩn 2NF.',
        expected_outcome: 'Hai phụ thuộc hàm MaSV -> HoTenSV và MaSV -> MaKhoa có vế trái MaSV là tập con thực sự của khóa chính (MaSV, MaMon) nên vi phạm 2NF.',
        socratic_question: 'Khóa chính của bảng là cặp (MaSV, MaMon). Trong tập F đã cho, những thuộc tính không khóa nào chỉ phụ thuộc vào riêng MaSV mà không cần tới MaMon?',
        common_mistake: 'Chỉ nêu MaSV -> HoTenSV mà quên mất MaSV -> MaKhoa cũng là phụ thuộc hàm bộ phận.',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
    },
    {
        id: 'c0000000-1122-3344-5566-778899aabb07',
        exercise_id: '8899aabb-1122-3344-5566-778899aabb03',
        process_step_id: 'b0000000-1122-3344-5566-778899aabb07',
        step_number: 2,
        instruction: 'Xác định phụ thuộc hàm bắc cầu giữa các thuộc tính không khóa gây vi phạm chuẩn 3NF.',
        expected_outcome: 'Phụ thuộc hàm MaKhoa -> TenKhoa là phụ thuộc giữa hai thuộc tính không khóa (bắc cầu qua MaSV -> MaKhoa -> TenKhoa) nên vi phạm 3NF.',
        socratic_question: 'Sau khi xét MaSV, bạn hãy nhìn vào phụ thuộc hàm MaKhoa -> TenKhoa: cả MaKhoa và TenKhoa đều là thuộc tính không khóa, vậy dây chuyền (MaSV, MaMon) -> MaSV -> MaKhoa -> TenKhoa gọi là phụ thuộc hàm gì?',
        common_mistake: 'Tách SinhVien(MaSV, HoTenSV, MaKhoa, TenKhoa) chung một bảng mà quên tách tiếp MaKhoa -> TenKhoa để đạt 3NF.',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
    },
    {
        id: 'c0000000-1122-3344-5566-778899aabb08',
        exercise_id: '8899aabb-1122-3344-5566-778899aabb03',
        process_step_id: 'b0000000-1122-3344-5566-778899aabb08',
        step_number: 3,
        instruction: 'Phân rã lược đồ KetQuaHocTap thành 3 lược đồ con đạt chuẩn 3NF và chỉ rõ khóa chính, khóa ngoại của từng bảng.',
        expected_outcome: 'Tách thành 3 bảng: 1) Khoa(MaKhoa PK, TenKhoa), 2) SinhVien(MaSV PK, HoTenSV, MaKhoa FK), 3) DiemHocTap(MaSV FK, MaMon, DiemThi, PK(MaSV, MaMon)).',
        socratic_question: 'Từ các vi phạm 2NF và 3NF vừa tìm được, bạn hãy viết ra các lược đồ quan hệ sau khi phân rã kèm khóa chính (PK) và khóa ngoại (FK) của mỗi bảng nhé?',
        common_mistake: 'Làm mất cột khóa ngoại MaKhoa trong bảng SinhVien khiến phép phân rã không bảo toàn thông tin (Lossy Join).',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c03'
    },

    // === Bài tập 4 (8899aabb-...-04): Khắc phục N+1 Query & LazyInitializationException trong Spring Data JPA ===
    {
        id: 'c0000000-1122-3344-5566-778899aabb09',
        exercise_id: '8899aabb-1122-3344-5566-778899aabb04',
        process_step_id: 'b0000000-1122-3344-5566-778899aabb09',
        step_number: 1,
        instruction: 'Giải thích nguyên nhân ném LazyInitializationException khi open-in-view=false và bổ sung @Transactional(readOnly = true) ở tầng ClassService.',
        expected_outcome: 'Khi open-in-view=false, Hibernate Session đóng ngay sau khi hàm Repository kết thúc nếu Service không có @Transactional. Đặt @Transactional(readOnly = true) giữ Session mở suốt quá trình map sang DTO nhưng vẫn còn N câu lệnh SELECT con.',
        socratic_question: 'Khi spring.jpa.open-in-view=false, vòng đời của Hibernate Persistence Context sẽ đóng lại ở thời điểm nào nếu hàm tại ClassService không đánh dấu @Transactional?',
        common_mistake: 'Đổi quan hệ @ManyToOne(fetch = FetchType.LAZY) sang EAGER trên ClassEntity thay vì quản lý Transaction và Fetch Plan.',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c06'
    },
    {
        id: 'c0000000-1122-3344-5566-778899aabb10',
        exercise_id: '8899aabb-1122-3344-5566-778899aabb04',
        process_step_id: 'b0000000-1122-3344-5566-778899aabb10',
        step_number: 2,
        instruction: 'Khai báo @EntityGraph(attributePaths = {"owner"}) trên phương thức findAll(Specification, Pageable) tại ClassRepository.',
        expected_outcome: 'Viết đúng @EntityGraph(attributePaths = {"owner"}) kết hợp Page<ClassEntity> findAll(...) để Hibernate gộp thành 1 câu lệnh SELECT ... LEFT JOIN users duy nhất.',
        socratic_question: 'Để gộp 1 câu SELECT lấy danh sách lớp và N câu SELECT lấy thông tin giảng viên (owner) thành đúng 1 câu lệnh LEFT JOIN duy nhất mà vẫn giữ nguyên phân trang Pageable, bạn sẽ khai báo annotation nào trên hàm findAll ở ClassRepository?',
        common_mistake: 'Dùng JOIN FETCH với quan hệ @OneToMany trực tiếp trong câu query có Pageable gây cảnh báo HHH90003004 (phân trang trên bộ nhớ RAM).',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c06'
    },

    // === Bài tập 5 (8899aabb-...-05): Xây dựng phản ví dụ Dijkstra trên đồ thị 3 đỉnh có cạnh âm ===
    {
        id: 'c0000000-1122-3344-5566-778899aabb11',
        exercise_id: '8899aabb-1122-3344-5566-778899aabb05',
        process_step_id: 'b0000000-1122-3344-5566-778899aabb11',
        step_number: 1,
        instruction: 'Chọn trọng số dương cho hai cạnh xuất phát từ nguồn A (A -> B và A -> C) sao cho d[C] < d[B] để Dijkstra lấy C ra khỏi PriorityQueue trước.',
        expected_outcome: 'Chọn w(A, C) < w(A, B), ví dụ w(A, C) = 2 và w(A, B) = 5. Khi đó ở bước đầu tiên Dijkstra sẽ chốt đỉnh C với d[C] = 2.',
        socratic_question: 'Từ đỉnh nguồn A có hai cạnh đi trực tiếp tới B và C. Để ép thuật toán tham lam Dijkstra lấy đỉnh C ra khỏi PriorityQueue và chốt cứng khoảng cách của C trước khi xét đỉnh B, bạn nên chọn w(A, C) và w(A, B) bằng bao nhiêu?',
        common_mistake: 'Chọn w(A, B) < w(A, C) khiến Dijkstra xét đỉnh B trước và cập nhật được cạnh âm B -> C nên không tạo ra được phản ví dụ.',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c07'
    },
    {
        id: 'c0000000-1122-3344-5566-778899aabb12',
        exercise_id: '8899aabb-1122-3344-5566-778899aabb05',
        process_step_id: 'b0000000-1122-3344-5566-778899aabb12',
        step_number: 2,
        instruction: 'Gán trọng số âm đủ lớn cho cạnh B -> C sao cho w(A, B) + w(B, C) < w(A, C) và chỉ ra sự sai lệch của Dijkstra.',
        expected_outcome: 'Với w(A, B) = 5 và w(A, C) = 2, chọn w(B, C) = -10 (hoặc bất kỳ giá trị nào < -3). Đường đi thực tế A -> B -> C có chi phí 5 + (-10) = -5 < 2, nhưng Dijkstra đã đóng đỉnh C ở giá trị 2.',
        socratic_question: 'Với w(A, C) = 2 và w(A, B) = 5, bạn hãy chọn một trọng số âm cho cạnh B -> C sao cho tổng đường đi A -> B -> C nhỏ hơn 2, từ đó giải thích vì sao Dijkstra lại bỏ lỡ đường đi này?',
        common_mistake: 'Tạo chu trình âm (Negative Cycle) thay vì một đồ thị có hướng không chu trình (DAG) chỉ có 1 cạnh âm.',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c07'
    },

    // === Bài tập 6 (8899aabb-...-06): Thiết kế Text Chunker & Overlap cho giáo trình tiếng Việt ===
    {
        id: 'c0000000-1122-3344-5566-778899aabb13',
        exercise_id: '8899aabb-1122-3344-5566-778899aabb06',
        process_step_id: 'b0000000-1122-3344-5566-778899aabb13',
        step_number: 1,
        instruction: 'Phân tích hậu quả trên Vector Search khi đặt chunk_size quá nhỏ (<100 tokens) hoặc quá lớn (>2000 tokens).',
        expected_outcome: 'Chunk quá nhỏ làm mất ngữ cảnh chủ ngữ/tham chiếu (ví dụ chỉ còn công thức mà mất tên định lý); chunk quá lớn làm vector trung bình bị loãng ngữ nghĩa (Semantic Dilution) và tốn token context.',
        socratic_question: 'Nếu một đoạn giáo trình Cơ sở dữ liệu bị cắt với chunk_size chỉ 50 tokens hoặc gộp tới 3000 tokens một chunk, vector nhúng thu được sẽ gặp vấn đề gì khi tìm kiếm tương đồng Cosine?',
        common_mistake: 'Cho rằng chunk càng lớn thì LLM càng có nhiều thông tin nên truy hồi vector càng chính xác.',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c04'
    },
    {
        id: 'c0000000-1122-3344-5566-778899aabb14',
        exercise_id: '8899aabb-1122-3344-5566-778899aabb06',
        process_step_id: 'b0000000-1122-3344-5566-778899aabb14',
        step_number: 2,
        instruction: 'Giải thích cơ chế bảo toàn mạch ngữ nghĩa qua biên cắt của tham số chunk_overlap.',
        expected_outcome: 'Khi câu kết luận định nghĩa nằm cuối Chunk N và ví dụ code nằm đầu Chunk N+1, khoảng gối đầu 10-15% giúp cả 2 chunk đều giữ được phần giao thoa kết nối định nghĩa với ví dụ.',
        socratic_question: 'Tại sao khi chia các bài giảng có kèm đoạn code SQL/Java minh họa, việc đặt chunk_overlap = 0 lại khiến AI Tutor thường xuyên lấy được định nghĩa nhưng bị cụt mất đoạn code ví dụ đi kèm?',
        common_mistake: 'Đặt chunk_overlap quá cao (>50%) gây trùng lặp dữ liệu hàng loạt trong ChromaDB.',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c04'
    },
    {
        id: 'c0000000-1122-3344-5566-778899aabb15',
        exercise_id: '8899aabb-1122-3344-5566-778899aabb06',
        process_step_id: 'b0000000-1122-3344-5566-778899aabb15',
        step_number: 3,
        instruction: 'Đề xuất bộ thông số cụ thể (chunk_size, chunk_overlap, separators) cho giáo trình đại học tiếng Việt.',
        expected_outcome: 'Chọn chunk_size = 350 - 512 tokens, chunk_overlap = 40 - 64 tokens (10-15%), ưu tiên tách theo RecursiveCharacterTextSplitter với thứ tự ["\\n\\n", "\\n", ". ", " "].',
        socratic_question: 'Từ hai phân tích trên, bạn hãy chốt bộ 3 tham số: chunk_size, chunk_overlap và danh sách ký tự ngắt câu (separators) tối ưu cho giáo trình tiếng Việt?',
        common_mistake: 'Cắt cứng theo số lượng ký tự (Fixed-size character split) làm chém đôi từ ghép tiếng Việt hoặc chém ngang khối code.',
        owner_role: 'TEACHER',
        scope: 'TEACHER',
        graph_revision_id: '9c9c9c9c-9c9c-9c9c-9c9c-9c9c9c9c9c04'
    }
] AS es_row
MATCH (exer:Exercise {id: es_row.exercise_id})
OPTIONAL MATCH (ps:ProcessStep {id: es_row.process_step_id})
MERGE (es:ExerciseStep {id: es_row.id})
SET es.exercise_id = es_row.exercise_id,
    es.process_step_id = es_row.process_step_id,
    es.step_number = es_row.step_number,
    es.instruction = es_row.instruction,
    es.expected_outcome = es_row.expected_outcome,
    es.socratic_question = es_row.socratic_question,
    es.common_mistake = es_row.common_mistake,
    es.owner_role = es_row.owner_role,
    es.scope = es_row.scope,
    es.graph_revision_id = es_row.graph_revision_id,
    es.created_at = '2026-10-20T08:15:00Z'
MERGE (exer)-[r_es:HAS_EXERCISE_STEP {step_number: es_row.step_number}]->(es)
SET r_es.graph_revision_id = es_row.graph_revision_id
FOREACH (_ IN CASE WHEN ps IS NOT NULL THEN [1] ELSE [] END |
    MERGE (es)-[r_map:MAPS_TO_PROCESS_STEP]->(ps)
    SET r_map.graph_revision_id = es_row.graph_revision_id
);

// Nối chuỗi thứ tự liên tiếp (:ExerciseStep)-[:NEXT_EXERCISE_STEP]->(:ExerciseStep) trong cùng một bài tập
MATCH (exer:Exercise)-[:HAS_EXERCISE_STEP]->(es1:ExerciseStep),
      (exer)-[:HAS_EXERCISE_STEP]->(es2:ExerciseStep)
WHERE es2.step_number = es1.step_number + 1
MERGE (es1)-[r_next:NEXT_EXERCISE_STEP]->(es2)
SET r_next.graph_revision_id = es1.graph_revision_id;