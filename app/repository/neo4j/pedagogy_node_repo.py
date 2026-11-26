from typing import Any
from neo4j import AsyncSession as Neo4jAsyncSession
from app.model.enums import NodeLabelEnum
from app.model.neo4j.nodes import (
    ArgumentNode,
    DefinitionNode,
    ExampleNode,
    ExerciseNode,
)
from app.model.neo4j.relationships import PedagogyRelationTypeEnum
from app.repository.neo4j.cypher_queries import (
    DELETE_PEDAGOGY_NODE_BY_ID_CYPHER,
    MERGE_ARGUMENT_NODE_CYPHER,
    MERGE_DEFINITION_NODE_CYPHER,
    MERGE_EXAMPLE_NODE_CYPHER,
    MERGE_EXERCISE_NODE_CYPHER,
    build_get_satellite_nodes_cypher,
)


class PedagogyNodeRepository:
    """
    Repository quản lý 4 loại Node sư phạm vệ tinh nối với `:KnowledgeEntity`:
    - `:Definition` (Định nghĩa / Lý thuyết)
    - `:Example` (Ví dụ minh họa / Code mẫu)
    - `:Exercise` (Bài tập rèn luyện)
    - `:Argument` (Lập luận logic / Chứng minh)
    Hỗ trợ phân tách dữ liệu theo `scope` (GLOBAL của Admin và TEACHER của Giáo viên).
    """

    def __init__(self, session: Neo4jAsyncSession) -> None:
        self._session = session

    # ========================================================================
    # 1. :Definition (Định nghĩa / Diễn giải lý thuyết)
    # ========================================================================
    async def merge_definition(
        self,
        canonical_code: str,
        node: DefinitionNode,
    ) -> DefinitionNode:
        params = {"canonical_code": canonical_code, **node.to_cypher_props()}
        result = await self._session.run(MERGE_DEFINITION_NODE_CYPHER, params)
        record = await result.single()
        if record is None:
            raise RuntimeError(f"Không tìm thấy :KnowledgeEntity({canonical_code}) để gắn :Definition.")
        return DefinitionNode.from_neo4j(dict(record["node"]))

    async def get_definitions_for_entity(
        self,
        canonical_code: str,
        teacher_id: str | None = None,
    ) -> list[DefinitionNode]:
        cypher = build_get_satellite_nodes_cypher(
            NodeLabelEnum.DEFINITION,
            PedagogyRelationTypeEnum.HAS_DEFINITION,
        )
        result = await self._session.run(
            cypher,
            {"canonical_code": canonical_code, "teacher_id": teacher_id},
        )
        records = await result.data()
        return [DefinitionNode.from_neo4j(r["node"]) for r in records]

    # ========================================================================
    # 2. :Example (Ví dụ minh họa / Đoạn code mẫu)
    # ========================================================================
    async def merge_example(
        self,
        canonical_code: str,
        node: ExampleNode,
    ) -> ExampleNode:
        params = {"canonical_code": canonical_code, **node.to_cypher_props()}
        result = await self._session.run(MERGE_EXAMPLE_NODE_CYPHER, params)
        record = await result.single()
        if record is None:
            raise RuntimeError(f"Không tìm thấy :KnowledgeEntity({canonical_code}) để gắn :Example.")
        return ExampleNode.from_neo4j(dict(record["node"]))

    async def get_examples_for_entity(
        self,
        canonical_code: str,
        teacher_id: str | None = None,
    ) -> list[ExampleNode]:
        cypher = build_get_satellite_nodes_cypher(
            NodeLabelEnum.EXAMPLE,
            PedagogyRelationTypeEnum.HAS_EXAMPLE,
        )
        result = await self._session.run(
            cypher,
            {"canonical_code": canonical_code, "teacher_id": teacher_id},
        )
        records = await result.data()
        return [ExampleNode.from_neo4j(r["node"]) for r in records]

    # ========================================================================
    # 3. :Exercise (Bài tập rèn luyện)
    # ========================================================================
    async def merge_exercise(
        self,
        canonical_code: str,
        node: ExerciseNode,
        process_id: str | None = None,
    ) -> ExerciseNode:
        params = {
            "canonical_code": canonical_code,
            "process_id": process_id,
            **node.to_cypher_props(),
        }
        result = await self._session.run(MERGE_EXERCISE_NODE_CYPHER, params)
        record = await result.single()
        if record is None:
            raise RuntimeError(f"Không tìm thấy :KnowledgeEntity({canonical_code}) để gắn :Exercise.")
        return ExerciseNode.from_neo4j(dict(record["node"]))

    async def get_exercises_for_entity(
        self,
        canonical_code: str,
        teacher_id: str | None = None,
    ) -> list[ExerciseNode]:
        cypher = build_get_satellite_nodes_cypher(
            NodeLabelEnum.EXERCISE,
            PedagogyRelationTypeEnum.HAS_EXERCISE,
        )
        result = await self._session.run(
            cypher,
            {"canonical_code": canonical_code, "teacher_id": teacher_id},
        )
        records = await result.data()
        return [ExerciseNode.from_neo4j(r["node"]) for r in records]

    async def get_exercise_by_id(self, exercise_id: str) -> ExerciseNode | None:
        cypher = "MATCH (exer:Exercise {id: $exercise_id}) RETURN properties(exer) AS node"
        result = await self._session.run(cypher, {"exercise_id": exercise_id})
        record = await result.single()
        if record is None:
            return None
        return ExerciseNode.from_neo4j(dict(record["node"]))

    # ========================================================================
    # 4. :Argument (Lập luận logic / Chứng minh)
    # ========================================================================
    async def merge_argument(
        self,
        canonical_code: str,
        node: ArgumentNode,
    ) -> ArgumentNode:
        params = {"canonical_code": canonical_code, **node.to_cypher_props()}
        result = await self._session.run(MERGE_ARGUMENT_NODE_CYPHER, params)
        record = await result.single()
        if record is None:
            raise RuntimeError(f"Không tìm thấy :KnowledgeEntity({canonical_code}) để gắn :Argument.")
        return ArgumentNode.from_neo4j(dict(record["node"]))

    async def get_arguments_for_entity(
        self,
        canonical_code: str,
        teacher_id: str | None = None,
    ) -> list[ArgumentNode]:
        cypher = build_get_satellite_nodes_cypher(
            NodeLabelEnum.ARGUMENT,
            PedagogyRelationTypeEnum.HAS_ARGUMENT,
        )
        result = await self._session.run(
            cypher,
            {"canonical_code": canonical_code, "teacher_id": teacher_id},
        )
        records = await result.data()
        return [ArgumentNode.from_neo4j(r["node"]) for r in records]

    # ========================================================================
    # 5. XÓA NODE VỆ TINH (Kiểm tra quyền sở hữu owner_id hoặc Admin)
    # ========================================================================
    async def delete_node_by_id(
        self,
        node_id: str,
        owner_id: str,
        is_admin: bool = False,
    ) -> bool:
        result = await self._session.run(
            DELETE_PEDAGOGY_NODE_BY_ID_CYPHER,
            {"node_id": node_id, "owner_id": owner_id, "is_admin": is_admin},
        )
        record: dict[str, Any] | None = await result.single()
        return bool(record and int(record["deleted_count"]) > 0)