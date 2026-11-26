from fastapi import HTTPException, status
from app.model.enums import OwnerRoleEnum, ScopeEnum
from app.model.neo4j.nodes import (
    ArgumentNode,
    DefinitionNode,
    ExampleNode,
    ExerciseNode,
    KnowledgeEntityNode,
    ProcessNode,
    ProcessStepNode,
)
from app.model.neo4j.relationships import KnowledgeEntityRelation
from app.repository.neo4j.knowledge_entity_repo import KnowledgeEntityRepository
from app.repository.neo4j.pedagogy_node_repo import PedagogyNodeRepository
from app.repository.neo4j.process_repo import ProcessRepository
from app.schema.common import ApiResponse, SpringBootCallerContext
from app.schema.graph_schema import (
    ArgumentCreate,
    ArgumentResponse,
    DefinitionCreate,
    DefinitionResponse,
    EntityRelationCreate,
    EntityRelationResponse,
    ExampleCreate,
    ExampleResponse,
    ExerciseCreate,
    ExerciseResponse,
    KnowledgeEntityCreate,
    KnowledgeEntityResponse,
    KnowledgeEntitySubgraphResponse,
    ProcessCreate,
    ProcessResponse,
    ProcessStepResponse,
)


class GraphController:
    """
    Controller quản lý trực tiếp 7 loại Node và 22 loại cạnh `RelationLabel` trong Neo4j.
    Đảm bảo quy tắc phân quyền kiến trúc:
    - `:KnowledgeEntity`: Do Hệ thống / Admin chuẩn hóa.
    - `:Definition`, `:Process`, `:ProcessStep`, `:Example`, `:Exercise`, `:Argument`:
      Admin tạo bản chuẩn (`scope = GLOBAL`), Giáo viên tạo bản riêng (`scope = TEACHER`).
    """

    def __init__(
        self,
        kg_repo: KnowledgeEntityRepository,
        pedagogy_repo: PedagogyNodeRepository,
        process_repo: ProcessRepository,
    ) -> None:
        self._kg_repo = kg_repo
        self._pedagogy_repo = pedagogy_repo
        self._process_repo = process_repo

    @staticmethod
    def _resolve_scope(
        requested_scope: ScopeEnum,
        caller: SpringBootCallerContext,
    ) -> ScopeEnum:
        """Giáo viên chỉ được phép tạo các Node vệ tinh với scope=TEACHER; Admin được tạo GLOBAL."""
        if caller.role in (OwnerRoleEnum.ADMIN, OwnerRoleEnum.SYSTEM):
            return requested_scope
        return ScopeEnum.TEACHER

    # ========================================================================
    # 1. :KnowledgeEntity & Subgraph
    # ========================================================================
    async def upsert_knowledge_entity(
        self,
        req: KnowledgeEntityCreate,
    ) -> ApiResponse[KnowledgeEntityResponse]:
        node = KnowledgeEntityNode(
            canonical_code=req.canonical_code,
            name=req.name,
            subject=req.subject,
            source_chunk_id=req.source_chunk_id,
        )
        saved = await self._kg_repo.merge_knowledge_entity(node)
        return ApiResponse(
            success=True,
            message="Đã chuẩn hóa Node :KnowledgeEntity thành công.",
            data=KnowledgeEntityResponse(**saved.to_cypher_props()),
        )

    async def search_knowledge_entities(
        self,
        keyword: str,
        subject: str | None = None,
        limit: int = 10,
    ) -> ApiResponse[list[KnowledgeEntityResponse]]:
        nodes = await self._kg_repo.search_entities(keyword=keyword, subject=subject, limit=limit)
        return ApiResponse(
            success=True,
            data=[KnowledgeEntityResponse(**n.to_cypher_props()) for n in nodes],
        )

    async def get_entity_subgraph(
        self,
        canonical_code: str,
        teacher_id: str | None = None,
    ) -> ApiResponse[KnowledgeEntitySubgraphResponse]:
        subgraph = await self._kg_repo.get_entity_subgraph(
            canonical_code=canonical_code,
            teacher_id=teacher_id,
        )
        if subgraph is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy :KnowledgeEntity với mã '{canonical_code}'.",
            )
        return ApiResponse(success=True, data=subgraph)

    # ========================================================================
    # 2. Cạnh ngữ nghĩa giữa 2 :KnowledgeEntity (22 nhãn RelationLabel)
    # ========================================================================
    async def create_entity_relation(
        self,
        req: EntityRelationCreate,
        caller: SpringBootCallerContext,
    ) -> ApiResponse[EntityRelationResponse]:
        effective_scope = self._resolve_scope(req.scope, caller)
        rel = KnowledgeEntityRelation(
            source_canonical_code=req.source_canonical_code,
            relation_label=req.relation_label,
            target_canonical_code=req.target_canonical_code,
            description=req.description,
            confidence=req.confidence,
            source_chunk_id=req.source_chunk_id,
            owner_id=caller.user_id,
            scope=effective_scope,
        )
        try:
            saved_rel = await self._kg_repo.merge_entity_relation(rel)
            return ApiResponse(
                success=True,
                message=f"Đã nối cạnh [:{req.relation_label}] thành công.",
                data=saved_rel,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

    # ========================================================================
    # 3. Các Node sư phạm vệ tinh (:Definition, :Process, :Example, :Exercise, :Argument)
    # ========================================================================
    async def create_definition(
        self,
        req: DefinitionCreate,
        caller: SpringBootCallerContext,
    ) -> ApiResponse[DefinitionResponse]:
        scope = self._resolve_scope(req.scope, caller)
        node = DefinitionNode(
            content=req.content,
            conditions=req.conditions,
            exceptions=req.exceptions,
            owner_id=caller.user_id,
            scope=scope,
            source_chunk_id=req.source_chunk_id,
        )
        saved = await self._pedagogy_repo.merge_definition(req.canonical_code, node)
        return ApiResponse(
            success=True,
            message="Đã lưu :Definition thành công.",
            data=DefinitionResponse(**saved.to_cypher_props()),
        )

    async def create_process_with_steps(
        self,
        req: ProcessCreate,
        caller: SpringBootCallerContext,
    ) -> ApiResponse[ProcessResponse]:
        scope = self._resolve_scope(req.scope, caller)
        process_node = ProcessNode(
            name=req.name,
            owner_id=caller.user_id,
            scope=scope,
            source_chunk_id=req.source_chunk_id,
        )
        step_nodes = [
            ProcessStepNode(
                step_number=s.step_number,
                action=s.action,
                hint_prompt=s.hint_prompt,
            )
            for s in req.steps
        ]
        saved = await self._process_repo.upsert_process_with_steps(
            canonical_code=req.canonical_code,
            process_node=process_node,
            steps=step_nodes,
        )
        return ApiResponse(
            success=True,
            message=f"Đã lưu :Process '{saved.name}' cùng {len(saved.steps)} bước :ProcessStep.",
            data=ProcessResponse(
                **saved.to_cypher_props(),
                steps=[ProcessStepResponse(**s.to_cypher_props()) for s in saved.steps],
            ),
        )

    async def get_step_hint(
        self,
        process_id: str,
        step_number: int,
    ) -> ApiResponse[dict]:
        step_node, total_steps = await self._process_repo.get_step_hint(
            process_id=process_id,
            step_number=step_number,
        )
        if step_node is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy bước {step_number} của quy trình {process_id}.",
            )
        return ApiResponse(
            success=True,
            data={
                "step": ProcessStepResponse(**step_node.to_cypher_props()),
                "total_steps": total_steps,
            },
        )

    async def create_example(
        self,
        req: ExampleCreate,
        caller: SpringBootCallerContext,
    ) -> ApiResponse[ExampleResponse]:
        scope = self._resolve_scope(req.scope, caller)
        node = ExampleNode(
            title=req.title,
            code_snippet=req.code_snippet,
            explanation=req.explanation,
            owner_id=caller.user_id,
            scope=scope,
            source_chunk_id=req.source_chunk_id,
        )
        saved = await self._pedagogy_repo.merge_example(req.canonical_code, node)
        return ApiResponse(
            success=True,
            message="Đã lưu :Example thành công.",
            data=ExampleResponse(**saved.to_cypher_props()),
        )

    async def create_exercise(
        self,
        req: ExerciseCreate,
        caller: SpringBootCallerContext,
    ) -> ApiResponse[ExerciseResponse]:
        scope = self._resolve_scope(req.scope, caller)
        node = ExerciseNode(
            title=req.title,
            content=req.content,
            difficulty=req.difficulty,
            owner_id=caller.user_id,
            scope=scope,
            source_chunk_id=req.source_chunk_id,
        )
        saved = await self._pedagogy_repo.merge_exercise(
            req.canonical_code,
            node,
            process_id=req.process_id,
        )
        return ApiResponse(
            success=True,
            message="Đã lưu :Exercise thành công.",
            data=ExerciseResponse(**saved.to_cypher_props()),
        )

    async def create_argument(
        self,
        req: ArgumentCreate,
        caller: SpringBootCallerContext,
    ) -> ApiResponse[ArgumentResponse]:
        scope = self._resolve_scope(req.scope, caller)
        node = ArgumentNode(
            hypothesis=req.hypothesis,
            evidence=req.evidence,
            conclusion=req.conclusion,
            owner_id=caller.user_id,
            scope=scope,
            source_chunk_id=req.source_chunk_id,
        )
        saved = await self._pedagogy_repo.merge_argument(req.canonical_code, node)
        return ApiResponse(
            success=True,
            message="Đã lưu :Argument thành công.",
            data=ArgumentResponse(**saved.to_cypher_props()),
        )

    async def delete_pedagogy_node(
        self,
        node_id: str,
        caller: SpringBootCallerContext,
    ) -> ApiResponse[dict[str, bool]]:
        is_admin = caller.role in (OwnerRoleEnum.ADMIN, OwnerRoleEnum.SYSTEM)
        deleted = await self._pedagogy_repo.delete_node_by_id(
            node_id=node_id,
            owner_id=caller.user_id,
            is_admin=is_admin,
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy Node hoặc bạn không có quyền xóa Node của người khác.",
            )
        return ApiResponse(
            success=True,
            message="Đã xóa Node khỏi Neo4j.",
            data={"deleted": True},
        )