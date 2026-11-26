from neo4j import AsyncSession as Neo4jAsyncSession
from app.model.enums import ScopeEnum
from app.model.neo4j.nodes import (
    ArgumentNode,
    DefinitionNode,
    ExampleNode,
    ExerciseNode,
    KnowledgeEntityNode,
    ProcessNode,
    ProcessStepNode,
    normalize_canonical_code,
)
from app.model.neo4j.relationships import KnowledgeEntityRelation
from app.repository.neo4j.cypher_queries import (
    GET_ENTITY_INCOMING_RELATIONS_CYPHER,
    GET_ENTITY_OUTGOING_RELATIONS_CYPHER,
    GET_KNOWLEDGE_ENTITY_BY_CODE_CYPHER,
    MERGE_KNOWLEDGE_ENTITY_CYPHER,
    SEARCH_KNOWLEDGE_ENTITIES_CYPHER,
    build_merge_entity_relation_cypher,
)
from app.repository.neo4j.pedagogy_node_repo import PedagogyNodeRepository
from app.repository.neo4j.process_repo import ProcessRepository
# from app.schema.extraction_schema import ChunkKnowledgeGraphLLMOutput
from app.schema.graph_schema import (
    ArgumentResponse,
    DefinitionResponse,
    EntityRelationResponse,
    ExampleResponse,
    ExerciseResponse,
    KnowledgeEntityResponse,
    KnowledgeEntitySubgraphResponse,
    ProcessResponse,
    ProcessStepResponse,
)


class KnowledgeEntityRepository:
    """
    Repository quản lý Node tâm `:KnowledgeEntity`, 22 loại cạnh ngữ nghĩa (`RelationLabel`)
    nối giữa các `:KnowledgeEntity`, đồng thời cung cấp hàm lưu trọn gói kết quả AI bóc tách KG
    và truy xuất cụm Subgraph cho Socratic Tutor SSE.
    """

    def __init__(self, session: Neo4jAsyncSession) -> None:
        self._session = session
        self._pedagogy_repo = PedagogyNodeRepository(session)
        self._process_repo = ProcessRepository(session)

    async def merge_knowledge_entity(
        self,
        node: KnowledgeEntityNode,
    ) -> KnowledgeEntityNode:
        """Tạo mới hoặc cập nhật `:KnowledgeEntity` theo khóa duy nhất `canonical_code`."""
        result = await self._session.run(
            MERGE_KNOWLEDGE_ENTITY_CYPHER,
            node.to_cypher_props(),
        )
        record = await result.single()
        if record is None:
            raise RuntimeError(f"Không thể MERGE :KnowledgeEntity({node.canonical_code}).")
        return KnowledgeEntityNode.from_neo4j(dict(record["entity"]))

    async def get_by_canonical_code(
        self,
        canonical_code: str,
    ) -> KnowledgeEntityNode | None:
        """Tra cứu `:KnowledgeEntity` theo `canonical_code`."""
        norm_code = normalize_canonical_code(canonical_code)
        result = await self._session.run(
            GET_KNOWLEDGE_ENTITY_BY_CODE_CYPHER,
            {"canonical_code": norm_code},
        )
        record = await result.single()
        if record is None or record["entity"] is None:
            return None
        return KnowledgeEntityNode.from_neo4j(dict(record["entity"]))

    async def search_entities(
        self,
        keyword: str,
        subject: str | None = None,
        limit: int = 10,
    ) -> list[KnowledgeEntityNode]:
        """Tìm kiếm `:KnowledgeEntity` theo từ khóa tên hoặc `canonical_code`."""
        norm_subject = subject.strip().upper() if subject else None
        result = await self._session.run(
            SEARCH_KNOWLEDGE_ENTITIES_CYPHER,
            {"keyword": keyword.strip(), "subject": norm_subject, "limit": limit},
        )
        records = await result.data()
        return [KnowledgeEntityNode.from_neo4j(r["entity"]) for r in records]

    async def merge_entity_relation(
        self,
        relation: KnowledgeEntityRelation,
    ) -> EntityRelationResponse:
        """
        Tạo hoặc cập nhật cạnh nối giữa 2 `:KnowledgeEntity` theo đúng 22 nhãn `RelationLabel`.
        """
        cypher = build_merge_entity_relation_cypher(relation.relation_label)
        params = {
            "source_canonical_code": relation.source_canonical_code,
            "target_canonical_code": relation.target_canonical_code,
            **relation.to_cypher_props(),
        }
        result = await self._session.run(cypher, params)
        record = await result.single()
        if record is None:
            raise RuntimeError(
                f"Không thể nối cạnh {relation.source_canonical_code} -[{relation.relation_label}]-> "
                f"{relation.target_canonical_code}. Đảm bảo cả 2 :KnowledgeEntity đã tồn tại."
            )
        rel_props = dict(record["rel_props"] or {})
        return EntityRelationResponse(
            source_canonical_code=record["source_canonical_code"],
            relation_label=record["relation_label"],
            target_canonical_code=record["target_canonical_code"],
            target_name=record.get("target_name"),
            description=rel_props.get("description"),
            confidence=float(rel_props.get("confidence", 1.0)),
            source_chunk_id=rel_props.get("source_chunk_id"),
            owner_id=rel_props.get("owner_id", "SYSTEM"),
            scope=ScopeEnum(rel_props.get("scope", ScopeEnum.GLOBAL.value)),
            created_at=rel_props.get("created_at"),
        )

    async def get_entity_relations(
        self,
        canonical_code: str,
        teacher_id: str | None = None,
    ) -> tuple[list[EntityRelationResponse], list[EntityRelationResponse]]:
        """Lấy toàn bộ các cạnh đi ra (outgoing) và đi vào (incoming) của 1 `:KnowledgeEntity`."""
        norm_code = normalize_canonical_code(canonical_code)
        params = {"canonical_code": norm_code, "teacher_id": teacher_id}

        out_res = await self._session.run(GET_ENTITY_OUTGOING_RELATIONS_CYPHER, params)
        out_records = await out_res.data()

        in_res = await self._session.run(GET_ENTITY_INCOMING_RELATIONS_CYPHER, params)
        in_records = await in_res.data()

        def _parse_rows(rows: list[dict]) -> list[EntityRelationResponse]:
            parsed: list[EntityRelationResponse] = []
            for r in rows:
                props = dict(r.get("rel_props") or {})
                rel_label = r["relation_label"]
                try:
                    parsed.append(
                        EntityRelationResponse(
                            source_canonical_code=r["source_canonical_code"],
                            relation_label=rel_label,
                            target_canonical_code=r["target_canonical_code"],
                            target_name=r.get("target_name"),
                            description=props.get("description"),
                            confidence=float(props.get("confidence", 1.0)),
                            source_chunk_id=props.get("source_chunk_id"),
                            owner_id=props.get("owner_id", "SYSTEM"),
                            scope=ScopeEnum(props.get("scope", ScopeEnum.GLOBAL.value)),
                            created_at=props.get("created_at"),
                        )
                    )
                except ValueError:
                    continue
            return parsed

        return _parse_rows(out_records), _parse_rows(in_records)

    async def get_entity_subgraph(
        self,
        canonical_code: str,
        teacher_id: str | None = None,
    ) -> KnowledgeEntitySubgraphResponse | None:
        """
        Truy xuất trọn bộ Subgraph xoay quanh 1 `:KnowledgeEntity` (gồm 7 loại Node + 22 loại cạnh `RelationLabel`),
        ưu tiên các Node `scope = 'TEACHER'` của `teacher_id` trước rồi mới tới `scope = 'GLOBAL'`.
        """
        entity_node = await self.get_by_canonical_code(canonical_code)
        if entity_node is None:
            return None

        norm_code = entity_node.canonical_code
        definitions = await self._pedagogy_repo.get_definitions_for_entity(norm_code, teacher_id)
        processes = await self._process_repo.get_processes_for_entity(norm_code, teacher_id)
        examples = await self._pedagogy_repo.get_examples_for_entity(norm_code, teacher_id)
        exercises = await self._pedagogy_repo.get_exercises_for_entity(norm_code, teacher_id)
        arguments = await self._pedagogy_repo.get_arguments_for_entity(norm_code, teacher_id)
        outgoing_rels, incoming_rels = await self.get_entity_relations(norm_code, teacher_id)

        return KnowledgeEntitySubgraphResponse(
            entity=KnowledgeEntityResponse(**entity_node.to_cypher_props()),
            definitions=[DefinitionResponse(**d.to_cypher_props()) for d in definitions],
            processes=[
                ProcessResponse(
                    **p.to_cypher_props(),
                    steps=[ProcessStepResponse(**s.to_cypher_props()) for s in p.steps],
                )
                for p in processes
            ],
            examples=[ExampleResponse(**ex.to_cypher_props()) for ex in examples],
            exercises=[ExerciseResponse(**exer.to_cypher_props()) for exer in exercises],
            arguments=[ArgumentResponse(**arg.to_cypher_props()) for arg in arguments],
            outgoing_relations=outgoing_rels,
            incoming_relations=incoming_rels,
        )

    # async def save_extracted_chunk_graph(
    #     self,
    #     *,
    #     chunk_id: str,
    #     owner_id: str,
    #     scope: ScopeEnum,
    #     subject_fallback: str,
    #     llm_output: ChunkKnowledgeGraphLLMOutput,
    # ) -> tuple[list[str], int, int]:
    #     """
    #     Lưu toàn bộ kết quả bóc tách Đồ thị Tri thức (`ChunkKnowledgeGraphLLMOutput`) của 1 `MaterialChunk` vào Neo4j:
    #     1. MERGE tất cả `:KnowledgeEntity`.
    #     2. MERGE các Node vệ tinh (`:Definition`, `:Process` + `:ProcessStep`, `:Example`, `:Exercise`, `:Argument`).
    #     3. MERGE các cạnh ngữ nghĩa (`RelationLabel`) giữa các `:KnowledgeEntity`.
    #     Trả về: `(danh_sách_canonical_codes, số_node_vệ_tinh_đã_lưu, số_cạnh_RelationLabel_đã_nối)`.
    #     """
    #     canonical_codes: list[str] = []
    #     pedagogy_nodes_count = 0
    #     relations_count = 0

    #     for bundle in llm_output.entities:
    #         ke_node = KnowledgeEntityNode(
    #             canonical_code=bundle.canonical_code,
    #             name=bundle.name,
    #             subject=bundle.subject or subject_fallback,
    #             source_chunk_id=chunk_id,
    #         )
    #         saved_ke = await self.merge_knowledge_entity(ke_node)
    #         code = saved_ke.canonical_code
    #         canonical_codes.append(code)

    #         for d_item in bundle.definitions:
    #             await self._pedagogy_repo.merge_definition(
    #                 code,
    #                 DefinitionNode(
    #                     content=d_item.content,
    #                     conditions=d_item.conditions,
    #                     exceptions=d_item.exceptions,
    #                     owner_id=owner_id,
    #                     scope=scope,
    #                     source_chunk_id=chunk_id,
    #                 ),
    #             )
    #             pedagogy_nodes_count += 1

    #         for p_item in bundle.processes:
    #             step_nodes = [
    #                 ProcessStepNode(
    #                     step_number=s.step_number,
    #                     action=s.action,
    #                     hint_prompt=s.hint_prompt,
    #                 )
    #                 for s in p_item.steps
    #             ]
    #             await self._process_repo.upsert_process_with_steps(
    #                 code,
    #                 ProcessNode(
    #                     name=p_item.name,
    #                     owner_id=owner_id,
    #                     scope=scope,
    #                     source_chunk_id=chunk_id,
    #                 ),
    #                 steps=step_nodes,
    #             )
    #             pedagogy_nodes_count += 1 + len(step_nodes)

    #         for ex_item in bundle.examples:
    #             await self._pedagogy_repo.merge_example(
    #                 code,
    #                 ExampleNode(
    #                     title=ex_item.title,
    #                     code_snippet=ex_item.code_snippet,
    #                     explanation=ex_item.explanation,
    #                     owner_id=owner_id,
    #                     scope=scope,
    #                     source_chunk_id=chunk_id,
    #                 ),
    #             )
    #             pedagogy_nodes_count += 1

    #         for exer_item in bundle.exercises:
    #             await self._pedagogy_repo.merge_exercise(
    #                 code,
    #                 ExerciseNode(
    #                     title=exer_item.title,
    #                     content=exer_item.content,
    #                     difficulty=exer_item.difficulty,
    #                     owner_id=owner_id,
    #                     scope=scope,
    #                     source_chunk_id=chunk_id,
    #                 ),
    #             )
    #             pedagogy_nodes_count += 1

    #         for arg_item in bundle.arguments:
    #             await self._pedagogy_repo.merge_argument(
    #                 code,
    #                 ArgumentNode(
    #                     hypothesis=arg_item.hypothesis,
    #                     evidence=arg_item.evidence,
    #                     conclusion=arg_item.conclusion,
    #                     owner_id=owner_id,
    #                     scope=scope,
    #                     source_chunk_id=chunk_id,
    #                 ),
    #             )
    #             pedagogy_nodes_count += 1

    #     # Nối các cạnh ngữ nghĩa RelationLabel giữa các :KnowledgeEntity
    #     for rel_item in llm_output.entity_relations:
    #         # Đảm bảo cả 2 đầu mút :KnowledgeEntity đều đã tồn tại trước khi MERGE cạnh
    #         for endpoint_code in (rel_item.source_canonical_code, rel_item.target_canonical_code):
    #             existing_ke = await self.get_by_canonical_code(endpoint_code)
    #             if existing_ke is None:
    #                 await self.merge_knowledge_entity(
    #                     KnowledgeEntityNode(
    #                         canonical_code=endpoint_code,
    #                         name=endpoint_code.replace("_", " ").title(),
    #                         subject=subject_fallback,
    #                         source_chunk_id=chunk_id,
    #                     )
    #                 )
    #             if endpoint_code not in canonical_codes:
    #                 canonical_codes.append(endpoint_code)

    #         await self.merge_entity_relation(
    #             KnowledgeEntityRelation(
    #                 source_canonical_code=rel_item.source_canonical_code,
    #                 relation_label=rel_item.relation_label,
    #                 target_canonical_code=rel_item.target_canonical_code,
    #                 description=rel_item.description,
    #                 confidence=rel_item.confidence,
    #                 source_chunk_id=chunk_id,
    #                 owner_id=owner_id,
    #                 scope=scope,
    #             )
    #         )
    #         relations_count += 1

    #     return sorted(set(canonical_codes)), pedagogy_nodes_count, relations_count
    
    