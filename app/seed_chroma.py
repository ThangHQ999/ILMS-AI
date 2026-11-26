"""
Script nạp (seed) dữ liệu mẫu 12 bản ghi `material_chunks` của hệ thống ILMS (PTIT Context) vào ChromaDB.
Đảm bảo đồng bộ 100% UUID (`8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c01` -> `...12`), `material_id`, `owner_id`,
`scope` (`GLOBAL` / `TEACHER`), `subject` và `canonical_codes_csv` với file `seed_socratic_and_chunks.sql`.

Cách chạy:
  1. Nạp trực tiếp từ danh sách 12 chunks chuẩn trong script (tính vector qua LLMService Gemini/OpenAI):
     python seed_chroma.py

  2. Đọc trực tiếp các dòng từ bảng `material_chunks` trong MySQL và đồng bộ sang ChromaDB:
     python seed_chroma.py --from-mysql

  3. Chế độ test nhanh offline (nếu chưa cấu hình API key của OpenAI/Gemini, sinh vector giả lập đúng số chiều):
     python seed_chroma.py --mock-embedding
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import logging
import math
from typing import Any

from app.core.config import settings
from app.db.chroma import chroma_manager
from app.db.mysql import mysql_manager
from app.model.enums import ScopeEnum
from app.repository.chroma.vector_repo import ChromaVectorRepository
from app.repository.mysql.chunk_repo import MaterialChunkRepository
from app.service.llm_service import llm_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)
logger = logging.getLogger("seed_chroma")


# ==============================================================================
# DỮ LIỆU 12 CHUNKS KHỚP 100% VỚI BẢNG `material_chunks` TRONG `seed_socratic_and_chunks.sql`
# (UUID dạng 36 ký tự có gạch ngang tương ứng với UNHEX(...) trong MySQL)
# ==============================================================================
SEED_CHUNKS_DATA: list[dict[str, Any]] = [
    {
        "id": "8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c01",
        "material_id": "ffff1111-ffff-1111-ffff-1111ffff1102",
        "owner_id": "aaaaaaaa-aaaa-aaaa-0000-000000000001",
        "scope": ScopeEnum.GLOBAL.value,
        "subject": "INT1306",
        "chunk_index": 0,
        "canonical_codes": ["KHOA_CHINH", "KHOA_UNG_VIEN", "RANG_BUOC_THUC_THE"],
        "content": (
            "Ràng buộc toàn vẹn thực thể (Entity Integrity) và Khóa chính (Primary Key): "
            "Trong mô hình cơ sở dữ liệu quan hệ, một lược đồ quan hệ R có thể có nhiều khóa dự tuyển "
            "(Candidate Keys) là các siêu khóa tối tiểu. Quản trị viên CSDL chọn một khóa dự tuyển làm "
            "khóa chính (Primary Key). Ràng buộc toàn vẹn thực thể quy định mọi thuộc tính tham gia vào "
            "khóa chính tuyệt đối không được nhận giá trị rỗng (NOT NULL) và giá trị khóa chính phải "
            "duy nhất giữa các bộ."
        ),
    },
    {
        "id": "8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c02",
        "material_id": "ffff1111-ffff-1111-ffff-1111ffff1103",
        "owner_id": "cccccccc-cccc-cccc-dddd-dddddddddddd",
        "scope": ScopeEnum.TEACHER.value,
        "subject": "INT1306",
        "chunk_index": 0,
        "canonical_codes": ["SQL_JOIN", "WINDOW_FUNCTION_DENSE_RANK"],
        "content": (
            "Phân biệt INNER JOIN, LEFT OUTER JOIN và hàm cửa sổ DENSE_RANK() trên MySQL 8.0: "
            "Khi thống kê số lượng thực thể con (ví dụ đếm số sinh viên đăng ký mỗi học phần bao gồm cả "
            "học phần có 0 sinh viên), bắt buộc dùng LEFT JOIN từ bảng cha sang bảng con kết hợp "
            "COUNT(bảng_con.id). Khi xếp hạng lấy Top K điểm cao nhất mỗi lớp mà không muốn nhảy bậc "
            "thứ hạng khi có điểm trùng nhau, sử dụng DENSE_RANK() OVER (PARTITION BY class_id ORDER BY "
            "score DESC) bên trong biểu thức bảng chung (CTE WITH)."
        ),
    },
    {
        "id": "8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c03",
        "material_id": "ffff1111-ffff-1111-ffff-1111ffff1104",
        "owner_id": "cccccccc-cccc-cccc-dddd-dddddddddddd",
        "scope": ScopeEnum.TEACHER.value,
        "subject": "INT1306",
        "chunk_index": 0,
        "canonical_codes": ["CHUAN_HOA_2NF", "CHUAN_HOA_3NF", "KHOA_CHINH"],
        "content": (
            "Định nghĩa Dạng chuẩn 2 (2NF): Một lược đồ quan hệ R ở dạng chuẩn 2 (2NF) nếu nó đã ở "
            "dạng chuẩn 1 (1NF) và mọi thuộc tính không khóa (Non-prime Attribute) của R đều phụ thuộc "
            "hàm đầy đủ vào mọi khóa dự tuyển của R. Nói cách khác, không tồn tại thuộc tính không khóa A "
            "nào chỉ phụ thuộc vào một tập con thực sự của một khóa dự tuyển K (vi phạm phụ thuộc hàm "
            "bộ phận - Partial Dependency). Lưu ý: Nếu mọi khóa dự tuyển của R đều chỉ gồm 1 thuộc tính "
            "đơn thì R ở 1NF chắc chắn đạt 2NF."
        ),
    },
    {
        "id": "8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c04",
        "material_id": "ffff1111-ffff-1111-ffff-1111ffff1104",
        "owner_id": "cccccccc-cccc-cccc-dddd-dddddddddddd",
        "scope": ScopeEnum.TEACHER.value,
        "subject": "INT1306",
        "chunk_index": 1,
        "canonical_codes": ["CHUAN_HOA_3NF", "PHU_THUOC_BAC_CAU"],
        "content": (
            "Định nghĩa Dạng chuẩn 3 (3NF): Một lược đồ quan hệ R ở dạng chuẩn 3 (3NF) nếu nó ở "
            "dạng chuẩn 2 (2NF) và không có bất kỳ thuộc tính không khóa nào của R phụ thuộc hàm bắc cầu "
            "(Transitive Dependency) vào một khóa dự tuyển bất kỳ của R. Phát biểu tương đương dùng để "
            "kiểm tra nhanh trong đề thi: Với mọi phụ thuộc hàm không tầm thường X -> A thỏa mãn trên R, "
            "HOẶC vế trái X là một siêu khóa của R, HOẶC vế phải A là một thuộc tính khóa (Prime Attribute - "
            "tức A tham gia vào ít nhất một khóa dự tuyển)."
        ),
    },
    {
        "id": "8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c05",
        "material_id": "ffff1111-ffff-1111-ffff-1111ffff1104",
        "owner_id": "cccccccc-cccc-cccc-dddd-dddddddddddd",
        "scope": ScopeEnum.TEACHER.value,
        "subject": "INT1306",
        "chunk_index": 2,
        "canonical_codes": ["CHUAN_HOA_BCNF", "CHUAN_HOA_3NF"],
        "content": (
            "Định nghĩa Dạng chuẩn Boyce-Codd (BCNF): Một lược đồ quan hệ R ở dạng chuẩn BCNF nếu với "
            "mọi phụ thuộc hàm không tầm thường X -> A thỏa mãn trên R, vế trái X bắt buộc phải là một "
            "siêu khóa (Superkey) của R. BCNF loại bỏ hoàn toàn điều kiện ân xá 'A là thuộc tính khóa' "
            "của 3NF. Ví dụ điển hình: Cho R(A,B,C,D) với F = {AB -> C, C -> D, D -> A}, các khóa dự tuyển "
            "là AB, BC, BD nên mọi thuộc tính đều là thuộc tính khóa (R đạt 3NF), nhưng vì C và D không phải "
            "siêu khóa nên C -> D và D -> A vi phạm BCNF."
        ),
    },
    {
        "id": "8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c06",
        "material_id": "ffff1111-ffff-1111-ffff-1111ffff1105",
        "owner_id": "aaaaaaaa-aaaa-aaaa-0000-000000000001",
        "scope": ScopeEnum.GLOBAL.value,
        "subject": "INT1306",
        "chunk_index": 0,
        "canonical_codes": ["TRANSACTION_ACID", "ISOLATION_LEVELS"],
        "content": (
            "Giao dịch ACID và 4 mức cô lập (Isolation Levels) trong MySQL InnoDB: Đọc bẩn (Dirty Read) "
            "xảy ra khi đọc dữ liệu chưa COMMIT; Đọc không lặp lại (Non-repeatable Read) xảy ra khi giao dịch "
            "khác UPDATE và COMMIT một dòng đang đọc; Đọc bóng ma (Phantom Read) xảy ra khi giao dịch khác "
            "INSERT hoặc DELETE làm thay đổi tập kết quả thỏa điều kiện WHERE. InnoDB đặt mức mặc định là "
            "REPEATABLE READ kết hợp cơ chế MVCC (Read View) và khóa Next-Key Lock để ngăn chặn cả "
            "Non-repeatable Read lẫn Phantom Read."
        ),
    },
    {
        "id": "8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c07",
        "material_id": "ffff1111-ffff-1111-ffff-1111ffff1105",
        "owner_id": "cccccccc-cccc-cccc-dddd-dddddddddddd",
        "scope": ScopeEnum.TEACHER.value,
        "subject": "INT1306",
        "chunk_index": 1,
        "canonical_codes": ["INDEX_BTREE"],
        "content": (
            "Cấu trúc chỉ mục B+Tree trong InnoDB (MySQL 8.0): Khác với cây BST hay B-Tree truyền thống, "
            "cây B+Tree có hệ số phân nhánh (fan-out) rất lớn giúp chiều cao cây chỉ từ 3-4 tầng cho hàng "
            "chục triệu dòng, giảm tối đa số thao tác đọc đĩa (Disk I/O). Các nút trong (Internal Nodes) "
            "chỉ chứa khóa định hướng, còn toàn bộ dữ liệu hoặc khóa chính nằm ở nút lá (Leaf Nodes) nối "
            "với nhau bằng danh sách liên kết kép giúp truy vấn khoảng (BETWEEN, >, <, ORDER BY) cực nhanh."
        ),
    },
    {
        "id": "8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c08",
        "material_id": "ffff1111-ffff-1111-ffff-1111ffff1106",
        "owner_id": "cccccccc-cccc-cccc-dddd-ddddddddddde",
        "scope": ScopeEnum.TEACHER.value,
        "subject": "INT1434",
        "chunk_index": 0,
        "canonical_codes": ["DTO_PATTERN", "JPA_N_PLUS_1"],
        "content": (
            "Chuẩn kiến trúc Spring Boot 3.3 (DTO Pattern & Xử lý lỗi N+1 Query): Controller tuyệt đối "
            "không trả trực tiếp JPA Entity về Client nhằm tránh lộ trường nhạy cảm (password hash) và "
            "lỗi đệ quy JSON hai chiều, mà phải ánh xạ sang DTO bọc trong ApiResponse<T>. Khi cấu hình "
            "spring.jpa.open-in-view=false, để tránh LazyInitializationException và bài toán N+1 Query "
            "trên các quan hệ FetchType.LAZY, phải đặt @Transactional(readOnly = true) tại tầng Service "
            "kết hợp @EntityGraph(attributePaths = {...}) hoặc JOIN FETCH tại Repository."
        ),
    },
    {
        "id": "8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c09",
        "material_id": "ffff1111-ffff-1111-ffff-1111ffff1107",
        "owner_id": "cccccccc-cccc-cccc-dddd-ddddddddddde",
        "scope": ScopeEnum.TEACHER.value,
        "subject": "INT1434",
        "chunk_index": 0,
        "canonical_codes": ["SPRING_SECURITY_JWT"],
        "content": (
            "Xác thực JWT qua HttpOnly Cookie và Phân quyền 2 tầng trong ILMS: Lưu trữ Access Token và "
            "Refresh Token trong Cookie có cờ HttpOnly=true, Secure=true, SameSite=Lax giúp ngăn chặn "
            "hoàn toàn mã độc JavaScript đọc trộm token qua document.cookie khi xảy ra tấn công XSS. "
            "Hệ thống áp dụng RBAC 2 tầng: cấp hệ thống kiểm tra ROLE_ADMIN / ROLE_USER qua @PreAuthorize, "
            "còn cấp lớp học kiểm tra vai trò OWNER / TEACHER / STUDENT theo ngữ cảnh classId trong bảng "
            "class_members."
        ),
    },
    {
        "id": "8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c10",
        "material_id": "ffff1111-ffff-1111-ffff-1111ffff1108",
        "owner_id": "aaaaaaaa-aaaa-aaaa-0000-000000000001",
        "scope": ScopeEnum.GLOBAL.value,
        "subject": "INT1303",
        "chunk_index": 0,
        "canonical_codes": ["QUICKSORT"],
        "content": (
            "Độ phức tạp thuật toán QuickSort và kỹ thuật chọn phần tử chốt (Pivot): QuickSort hoạt động "
            "theo chiến lược Chia để trị với độ phức tạp trung bình đạt O(N log N). Tuy nhiên nếu chọn "
            "Pivot cố định ở đầu hoặc cuối mảng trên dữ liệu đầu vào đã sắp xếp tăng/giảm dần, cây đệ quy "
            "bị lệch hoàn toàn làm độ phức tạp suy biến thành O(N^2) gây quá thời gian (TLE). Giải pháp "
            "chuẩn là chọn chốt ngẫu nhiên (Randomized Pivot) hoặc trung vị của 3 phần tử đầu - giữa - cuối "
            "(Median-of-Three)."
        ),
    },
    {
        "id": "8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c11",
        "material_id": "ffff1111-ffff-1111-ffff-1111ffff1109",
        "owner_id": "cccccccc-cccc-cccc-dddd-dddddddddddf",
        "scope": ScopeEnum.TEACHER.value,
        "subject": "INT1303",
        "chunk_index": 0,
        "canonical_codes": ["DIJKSTRA"],
        "content": (
            "Thuật toán Dijkstra tìm đường đi ngắn nhất từ một đỉnh nguồn u0: Sử dụng hàng đợi ưu tiên "
            "Min-Heap (PriorityQueue) lưu cặp (khoảng cách d[u], đỉnh u) với độ phức tạp O((V + E) log V). "
            "Khi lấy cặp (d, u) ra khỏi hàng đợi, bắt buộc kiểm tra điều kiện if (d > dist[u]) continue "
            "để bỏ qua trạng thái cũ. Vì chiến lược tham lam của Dijkstra giả định đỉnh đã đóng có khoảng "
            "cách tối ưu vĩnh viễn, thuật toán sẽ chạy sai nếu đồ thị có cạnh mang trọng số âm (khi đó "
            "phải dùng Bellman-Ford)."
        ),
    },
    {
        "id": "8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c12",
        "material_id": "ffff1111-ffff-1111-ffff-1111ffff1110",
        "owner_id": "cccccccc-cccc-cccc-dddd-ddddddddddd1",
        "scope": ScopeEnum.TEACHER.value,
        "subject": "INT1405",
        "chunk_index": 0,
        "canonical_codes": ["RAG_EMBEDDING"],
        "content": (
            "Chiến lược Chunking và chống ảo giác (Hallucination) trong hệ thống Hybrid RAG Giáo dục: "
            "Với giáo trình đại học tiếng Việt chứa nhiều định nghĩa và công thức, nên chia nhỏ văn bản "
            "theo cấu trúc đoạn văn với kích thước chunk_size từ 250 đến 512 tokens và độ gối đầu "
            "(chunk_overlap) từ 40 đến 64 tokens để bảo toàn ngữ cảnh giữa định nghĩa và ví dụ. Kết hợp "
            "truy xuất Vector trên ChromaDB với Đồ thị Tri thức Neo4j giúp Gia sư Socratic dẫn dắt từng "
            "bước chính xác mà không bịa đặt kiến thức."
        ),
    },
]


def generate_deterministic_mock_embedding(text: str, dimension: int) -> list[float]:
    """
    Sinh vector chuẩn hóa (unit vector) tất định từ nội dung văn bản khi chạy với cờ `--mock-embedding`
    (phục vụ môi trường dev/test chưa nạp API Key của Gemini/OpenAI).
    """
    vec: list[float] = []
    seed_bytes = text.encode("utf-8")
    for idx in range(dimension):
        digest = hashlib.sha256(seed_bytes + f":{idx}".encode("utf-8")).digest()
        raw_val = (int.from_bytes(digest[:4], "big") / 0xFFFFFFFF) * 2.0 - 1.0
        vec.append(raw_val)
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [round(x / norm, 6) for x in vec]


async def load_chunks_from_mysql() -> list[dict[str, Any]]:
    """Đọc toàn bộ các bản ghi hiện có trong bảng `material_chunks` của MySQL."""
    mysql_manager.init_mysql()
    try:
        async with mysql_manager.session_factory() as session:
            repo = MaterialChunkRepository(session)
            # Đọc theo danh sách 12 ID chuẩn hoặc toàn bộ bảng
            seed_ids = [item["id"] for item in SEED_CHUNKS_DATA]
            rows = await repo.get_by_ids_preserve_order(seed_ids)
            if not rows:
                logger.warning(
                    "Không tìm thấy 12 ID chuẩn trong bảng material_chunks, chuyển sang dùng dữ liệu tích hợp sẵn."
                )
                return SEED_CHUNKS_DATA

            loaded: list[dict[str, Any]] = []
            for r in rows:
                material_id = str(getattr(r, "material_id", None) or getattr(r, "document_id", ""))
                scope_val = r.scope.value if isinstance(r.scope, ScopeEnum) else str(r.scope)
                loaded.append(
                    {
                        "id": str(r.id),
                        "material_id": material_id,
                        "owner_id": str(r.owner_id),
                        "scope": scope_val,
                        "subject": str(r.subject).strip().upper(),
                        "chunk_index": int(r.chunk_index),
                        "canonical_codes": list(r.canonical_codes or []),
                        "content": r.content,
                    }
                )
            logger.info("Đã đọc thành công %d bản ghi từ bảng MySQL `material_chunks`.", len(loaded))
            return loaded
    finally:
        await mysql_manager.close_mysql()


async def seed_chroma(from_mysql: bool = False, mock_embedding: bool = False) -> None:
    """
    Khởi tạo kết nối tới ChromaDB, tính toán Vector Embeddings và upsert toàn bộ 12 chunks.
    """
    await chroma_manager.init_chroma()
    try:
        collection = chroma_manager.collection
        vector_repo = ChromaVectorRepository(collection)

        chunks_data = await load_chunks_from_mysql() if from_mysql else SEED_CHUNKS_DATA

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict[str, str | int | float | bool]] = []

        for item in chunks_data:
            ids.append(item["id"])
            documents.append(item["content"])
            codes_csv = ",".join(item["canonical_codes"])
            metadatas.append(
                {
                    "material_id": item["material_id"],
                    "document_id": item["material_id"],
                    "owner_id": item["owner_id"],
                    "scope": item["scope"],
                    "subject": item["subject"].strip().upper(),
                    "chunk_index": int(item["chunk_index"]),
                    "canonical_codes_csv": codes_csv,
                }
            )

        if mock_embedding:
            dim = settings.active_embedding_dimension
            logger.info(
                "Đang sinh vector giả lập (mock_embedding=True, dimension=%d) cho %d chunks...",
                dim,
                len(documents),
            )
            embeddings = [generate_deterministic_mock_embedding(doc, dim) for doc in documents]
        else:
            logger.info(
                "Đang gọi AI Provider ('%s') để tính toán vector embeddings thực tế cho %d chunks...",
                settings.EMBEDDING_PROVIDER,
                len(documents),
            )
            embeddings = await llm_service.embed_texts(documents)

        await vector_repo._invoke(
            "upsert",
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        logger.info(
            "Đã upsert thành công %d chunks vào ChromaDB Collection '%s'!",
            len(ids),
            settings.CHROMA_COLLECTION_NAME,
        )

        # Kiểm tra truy vấn thử 1 câu hỏi Socratic về BCNF của giảng viên Trần Thị Hương
        test_query = "Tại sao lược đồ có nhiều khóa dự tuyển chồng lấn đạt 3NF nhưng vi phạm BCNF?"
        test_vec = (
            generate_deterministic_mock_embedding(test_query, settings.active_embedding_dimension)
            if mock_embedding
            else (await llm_service.embed_texts([test_query]))[0]
        )
        hits = await vector_repo.similarity_search(
            query_text=test_query,
            query_embedding=test_vec,
            top_k=2,
            subject="INT1306",
            teacher_id="cccccccc-cccc-cccc-dddd-dddddddddddd",
        )
        logger.info("Kiểm tra tìm kiếm vector mẫu (Top %d kết quả):", len(hits))
        for idx, h in enumerate(hits, start=1):
            logger.info(
                "  [%d] chunk_id=%s | distance=%.4f | canonical_codes=%s",
                idx,
                h.chunk_id,
                h.distance or 0.0,
                h.metadata.canonical_codes,
            )

    finally:
        await chroma_manager.close_chroma()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed 12 bản ghi material_chunks của hệ thống ILMS PTIT vào ChromaDB."
    )
    parser.add_argument(
        "--from-mysql",
        action="store_true",
        help="Đọc dữ liệu trực tiếp từ bảng material_chunks trong MySQL thay vì dùng mảng cố định.",
    )
    parser.add_argument(
        "--mock-embedding",
        action="store_true",
        help="Sinh vector tất định đúng số chiều khi chưa cấu hình API Key của OpenAI/Gemini.",
    )
    args = parser.parse_args()
    asyncio.run(seed_chroma(from_mysql=args.from_mysql, mock_embedding=args.mock_embedding))


if __name__ == "__main__":
    main()