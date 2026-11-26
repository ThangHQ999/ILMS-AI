import logging
from collections.abc import AsyncGenerator
from neo4j import AsyncDriver, AsyncGraphDatabase, AsyncSession as Neo4jAsyncSession
from app.core.config import settings

logger = logging.getLogger(__name__)

# Danh sách các Unique Constraints và Indexes cho 7 loại Node trong đồ thị tri thức Socratic
NEO4J_SCHEMA_CONSTRAINTS: list[str] = [
    """
    CREATE CONSTRAINT ingestion_graph_revision_id_unique IF NOT EXISTS
    FOR (r:IngestionGraphRevision) REQUIRE r.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT ingestion_draft_node_id_unique IF NOT EXISTS
    FOR (n:IngestionDraftNode) REQUIRE n.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT ingestion_node_id_unique IF NOT EXISTS
    FOR (n:IngestedKnowledge) REQUIRE n.id IS UNIQUE
    """,
    """
    CREATE INDEX ingestion_publication_idx IF NOT EXISTS
    FOR (n:IngestedKnowledge) ON (n.publication_id, n.node_kind)
    """,
    # 1. :KnowledgeEntity — Khóa duy nhất là canonical_code (VD: "PYTHAGORAS_THEOREM")
    """
    CREATE CONSTRAINT ke_canonical_code_unique IF NOT EXISTS
    FOR (ke:KnowledgeEntity) REQUIRE ke.canonical_code IS UNIQUE
    """,
    """
    CREATE INDEX ke_subject_idx IF NOT EXISTS
    FOR (ke:KnowledgeEntity) ON (ke.subject)
    """,
    # 2. :Definition — Khóa duy nhất id, đánh index theo (owner_id, scope) để lọc GLOBAL/TEACHER
    """
    CREATE CONSTRAINT definition_id_unique IF NOT EXISTS
    FOR (d:Definition) REQUIRE d.id IS UNIQUE
    """,
    """
    CREATE INDEX definition_scope_owner_idx IF NOT EXISTS
    FOR (d:Definition) ON (d.scope, d.owner_id)
    """,
    # 3. :Process — Phương pháp / Quy trình giải dạng bài
    """
    CREATE CONSTRAINT process_id_unique IF NOT EXISTS
    FOR (p:Process) REQUIRE p.id IS UNIQUE
    """,
    """
    CREATE INDEX process_scope_owner_idx IF NOT EXISTS
    FOR (p:Process) ON (p.scope, p.owner_id)
    """,
    # 4. :ProcessStep — Từng bước giải chi tiết để gợi ý Socratic
    """
    CREATE CONSTRAINT process_step_id_unique IF NOT EXISTS
    FOR (ps:ProcessStep) REQUIRE ps.id IS UNIQUE
    """,
    """
    CREATE INDEX process_step_number_idx IF NOT EXISTS
    FOR (ps:ProcessStep) ON (ps.step_number)
    """,
    # 5. :Example — Ví dụ minh họa / Đoạn code mẫu
    """
    CREATE CONSTRAINT example_id_unique IF NOT EXISTS
    FOR (ex:Example) REQUIRE ex.id IS UNIQUE
    """,
    """
    CREATE INDEX example_scope_owner_idx IF NOT EXISTS
    FOR (ex:Example) ON (ex.scope, ex.owner_id)
    """,
    # 6. :Exercise — Bài tập rèn luyện
    """
    CREATE CONSTRAINT exercise_id_unique IF NOT EXISTS
    FOR (exer:Exercise) REQUIRE exer.id IS UNIQUE
    """,
    """
    CREATE INDEX exercise_scope_owner_idx IF NOT EXISTS
    FOR (exer:Exercise) ON (exer.scope, exer.owner_id, exer.difficulty)
    """,
    # 7. :Argument — Lập luận logic / Chứng minh
    """
    CREATE CONSTRAINT argument_id_unique IF NOT EXISTS
    FOR (arg:Argument) REQUIRE arg.id IS UNIQUE
    """,
    """
    CREATE INDEX argument_scope_owner_idx IF NOT EXISTS
    FOR (arg:Argument) ON (arg.scope, arg.owner_id)
    """,
]


class Neo4jDatabaseManager:
    """
    Quản lý AsyncDriver cho Neo4j và thiết lập Unique Constraints cho 7 loại Node.
    """

    def __init__(self) -> None:
        self._driver: AsyncDriver | None = None

    def init_neo4j(self) -> None:
        """Khởi tạo Neo4j AsyncDriver với cấu hình connection pool từ .env."""
        if self._driver is not None:
            return

        self._driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
            max_connection_lifetime=settings.NEO4J_MAX_CONNECTION_LIFETIME,
            max_connection_pool_size=settings.NEO4J_MAX_CONNECTION_POOL_SIZE,
            connection_timeout=settings.NEO4J_CONNECTION_TIMEOUT,
        )
        logger.info("Đã khởi tạo Neo4j AsyncDriver tại %s (database=%s)", settings.NEO4J_URI, settings.NEO4J_DATABASE)

    async def verify_connectivity(self) -> bool:
        """Xác thực kết nối tới Neo4j server."""
        if self._driver is None:
            raise RuntimeError("Neo4jDatabaseManager chưa được khởi tạo. Hãy gọi init_neo4j() trước.")
        await self._driver.verify_connectivity()
        return True

    async def init_constraints_and_indexes(self) -> None:
        """
        Tự động khởi tạo Unique Constraints và Indexes cho 7 Label Node
        (:KnowledgeEntity, :Definition, :Process, :ProcessStep, :Example, :Exercise, :Argument).
        """
        if self._driver is None:
            raise RuntimeError("Neo4jDatabaseManager chưa được khởi tạo.")

        async with self._driver.session(database=settings.NEO4J_DATABASE) as session:
            for cypher_stmt in NEO4J_SCHEMA_CONSTRAINTS:
                await session.run(cypher_stmt.strip())
        logger.info("Đã đồng bộ toàn bộ Unique Constraints và Indexes cho 7 loại Node trên Neo4j.")

    async def close_neo4j(self) -> None:
        """Đóng Neo4j AsyncDriver khi ứng dụng dừng."""
        if self._driver is not None:
            await self._driver.close()
            self._driver = None
            logger.info("Đã đóng kết nối Neo4j AsyncDriver.")

    @property
    def driver(self) -> AsyncDriver:
        if self._driver is None:
            raise RuntimeError("Neo4j driver chưa sẵn sàng. Hãy kiểm tra lifespan của ứng dụng.")
        return self._driver


neo4j_manager = Neo4jDatabaseManager()


async def get_neo4j_session() -> AsyncGenerator[Neo4jAsyncSession, None]:
    """
    FastAPI Dependency cung cấp Neo4j AsyncSession cho từng request.
    """
    driver = neo4j_manager.driver
    async with driver.session(database=settings.NEO4J_DATABASE) as session:
        yield session