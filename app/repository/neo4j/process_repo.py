from neo4j import AsyncSession as Neo4jAsyncSession
from app.model.neo4j.nodes import ProcessNode, ProcessStepNode
from app.repository.neo4j.cypher_queries import (
    GET_PROCESS_BY_ID_CYPHER,
    GET_PROCESS_STEP_HINT_CYPHER,
    GET_PROCESSES_FOR_ENTITY_CYPHER,
    UPSERT_PROCESS_WITH_STEPS_CYPHER,
)


class ProcessRepository:
    """
    Repository chuyên biệt quản lý `:Process` (Phương pháp giải) và chuỗi `:ProcessStep` (Bước gợi ý Socratic).
    Đảm bảo các `:ProcessStep` luôn được sắp xếp theo `step_number` (1, 2, 3...)
    và nối với nhau qua cả cạnh `(:Process)-[:HAS_STEP]->(:ProcessStep)` lẫn `(:ProcessStep)-[:NEXT_STEP]->(:ProcessStep)`.
    """

    def __init__(self, session: Neo4jAsyncSession) -> None:
        self._session = session

    async def upsert_process_with_steps(
        self,
        canonical_code: str,
        process_node: ProcessNode,
        steps: list[ProcessStepNode] | None = None,
    ) -> ProcessNode:
        """
        Tạo mới hoặc cập nhật `:Process` kèm chuỗi `:ProcessStep` của một `:KnowledgeEntity`.
        """
        target_steps = sorted(
            steps if steps is not None else process_node.steps,
            key=lambda s: s.step_number,
        )
        steps_payload = []
        for idx, step in enumerate(target_steps, start=1):
            step.step_number = idx
            step.process_id = process_node.id
            steps_payload.append(step.to_cypher_props())

        props = process_node.to_cypher_props()
        params = {
            "canonical_code": canonical_code,
            "process_id": props["id"],
            "name": props["name"],
            "owner_id": props["owner_id"],
            "scope": props["scope"],
            "source_chunk_id": props["source_chunk_id"],
            "created_at": props["created_at"],
            "updated_at": props["updated_at"],
            "steps": steps_payload,
        }
        result = await self._session.run(UPSERT_PROCESS_WITH_STEPS_CYPHER, params)
        record = await result.single()
        if record is None:
            raise RuntimeError(f"Không tìm thấy :KnowledgeEntity({canonical_code}) để gắn :Process.")

        saved_steps = [ProcessStepNode.from_neo4j(s) for s in (record["steps"] or []) if s]
        return ProcessNode.from_neo4j(dict(record["process"]), steps=saved_steps)

    async def get_processes_for_entity(
        self,
        canonical_code: str,
        teacher_id: str | None = None,
    ) -> list[ProcessNode]:
        """
        Lấy danh sách các quy trình giải (`:Process` kèm `:ProcessStep`) của 1 `:KnowledgeEntity`.
        Ưu tiên trả về quy trình `scope = 'TEACHER'` của `teacher_id` ở đầu danh sách, sau đó mới tới `GLOBAL`.
        """
        result = await self._session.run(
            GET_PROCESSES_FOR_ENTITY_CYPHER,
            {"canonical_code": canonical_code, "teacher_id": teacher_id},
        )
        records = await result.data()
        processes: list[ProcessNode] = []
        for row in records:
            step_objs = [ProcessStepNode.from_neo4j(s) for s in (row.get("steps") or []) if s]
            processes.append(ProcessNode.from_neo4j(row["process"], steps=step_objs))
        return processes

    async def get_process_by_id(self, process_id: str) -> ProcessNode | None:
        """Lấy chi tiết 1 `:Process` và toàn bộ các bước `:ProcessStep` theo `process_id`."""
        result = await self._session.run(GET_PROCESS_BY_ID_CYPHER, {"process_id": process_id})
        record = await result.single()
        if record is None or record["process"] is None:
            return None
        step_objs = [ProcessStepNode.from_neo4j(s) for s in (record["steps"] or []) if s]
        return ProcessNode.from_neo4j(dict(record["process"]), steps=step_objs)

    async def get_step_hint(
        self,
        process_id: str,
        step_number: int,
    ) -> tuple[ProcessStepNode | None, int]:
        """
        Lấy `:ProcessStep` ứng với `step_number` hiện tại của học sinh cùng tổng số bước của `:Process`.
        Phục vụ trực tiếp cho Socratic Tutor SSE để lấy `hint_prompt` và `action`.
        """
        result = await self._session.run(
            GET_PROCESS_STEP_HINT_CYPHER,
            {"process_id": process_id, "step_number": int(step_number)},
        )
        record = await result.single()
        if record is None or record["step"] is None:
            return None, 0
        step_node = ProcessStepNode.from_neo4j(dict(record["step"]))
        total_steps = int(record["total_steps"] or 0)
        return step_node, total_steps