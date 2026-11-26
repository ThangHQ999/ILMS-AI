from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, get_args
from app.model.enums import (
    EntityRelationTypeEnum,
    NodeLabelEnum,
    RelationLabel,
    ScopeEnum,
)
from app.model.neo4j.nodes import normalize_canonical_code

VALID_ENTITY_RELATION_LABELS: frozenset[str] = frozenset(get_args(RelationLabel))


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class PedagogyRelationTypeEnum(str, Enum):
    """
    Các loại cạnh cấu trúc sư phạm (Structural / Pedagogical Edges)
    nối từ :KnowledgeEntity ra 6 loại Node vệ tinh và giữa :Process với :ProcessStep.
    """

    # Nối từ tâm :KnowledgeEntity ra các Node vệ tinh
    HAS_DEFINITION = "HAS_DEFINITION"      # (:KnowledgeEntity)-[:HAS_DEFINITION]->(:Definition)
    HAS_PROCESS = "HAS_PROCESS"            # (:KnowledgeEntity)-[:HAS_PROCESS]->(:Process)
    HAS_EXAMPLE = "HAS_EXAMPLE"            # (:KnowledgeEntity)-[:HAS_EXAMPLE]->(:Example)
    HAS_EXERCISE = "HAS_EXERCISE"          # (:KnowledgeEntity)-[:HAS_EXERCISE]->(:Exercise)
    HAS_ARGUMENT = "HAS_ARGUMENT"          # (:KnowledgeEntity)-[:HAS_ARGUMENT]->(:Argument)

    # Nối từ :Process sang chuỗi các bước :ProcessStep
    HAS_STEP = "HAS_STEP"                  # (:Process)-[:HAS_STEP {step_number}]->(:ProcessStep)
    NEXT_STEP = "NEXT_STEP"                # (:ProcessStep)-[:NEXT_STEP]->(:ProcessStep)

    # Nối bổ trợ giữa bài tập / ví dụ với quy trình giải
    USES_PROCESS = "USES_PROCESS"          # (:Exercise | :Example)-[:USES_PROCESS]->(:Process)


class RelationshipTypeEnum(str, Enum):
    """
    Tập hợp toàn bộ các loại cạnh trong Neo4j:
    - 8 cạnh cấu trúc sư phạm (nối :KnowledgeEntity với 6 Node vệ tinh).
    - 22 cạnh ngữ nghĩa thuộc RelationLabel (nối :KnowledgeEntity với :KnowledgeEntity).
    """

    # --- Nhóm 1: Cạnh cấu trúc sư phạm ---
    HAS_DEFINITION = "HAS_DEFINITION"
    HAS_PROCESS = "HAS_PROCESS"
    HAS_EXAMPLE = "HAS_EXAMPLE"
    HAS_EXERCISE = "HAS_EXERCISE"
    HAS_ARGUMENT = "HAS_ARGUMENT"
    HAS_STEP = "HAS_STEP"
    NEXT_STEP = "NEXT_STEP"
    USES_PROCESS = "USES_PROCESS"

    # --- Nhóm 2: 22 cạnh ngữ nghĩa nối giữa các :KnowledgeEntity (RelationLabel) ---
    IS_A = "IS_A"
    HAS_CATEGORY = "HAS_CATEGORY"
    HAS_SUBTYPE = "HAS_SUBTYPE"
    CLASSIFIED_INTO = "CLASSIFIED_INTO"
    IS_VARIANT_OF = "IS_VARIANT_OF"

    PART_OF = "PART_OF"
    COMPOSED_OF = "COMPOSED_OF"
    CONTAINS = "CONTAINS"

    REQUIRES = "REQUIRES"
    DEPENDS_ON = "DEPENDS_ON"
    APPLIES_TO = "APPLIES_TO"

    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    USES = "USES"
    CONTRASTS_WITH = "CONTRASTS_WITH"
    IMPROVES_UPON = "IMPROVES_UPON"

    CAUSES = "CAUSES"
    LEADS_TO = "LEADS_TO"
    SOLVES = "SOLVES"
    PRODUCES = "PRODUCES"
    YIELDS = "YIELDS"

    CREATED_BY = "CREATED_BY"
    DISCOVERED_BY = "DISCOVERED_BY"


@dataclass(slots=True)
class KnowledgeEntityRelation:
    """
    Đại diện chuyên biệt cho cạnh nối giữa 2 thực thể tri thức:
    (:KnowledgeEntity {canonical_code: source})-[r:<RelationLabel>]->(:KnowledgeEntity {canonical_code: target})
    Phục vụ trực tiếp cho luồng AI trích xuất đồ thị tri thức (KG Extraction) và suy luận Socratic.
    """

    source_canonical_code: str
    relation_label: RelationLabel
    target_canonical_code: str
    description: str | None = None
    confidence: float = 1.0
    source_chunk_id: str | None = None
    owner_id: str = "SYSTEM"
    scope: ScopeEnum = ScopeEnum.GLOBAL
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        self.source_canonical_code = normalize_canonical_code(self.source_canonical_code)
        self.target_canonical_code = normalize_canonical_code(self.target_canonical_code)
        if self.relation_label not in VALID_ENTITY_RELATION_LABELS:
            raise ValueError(
                f"Relation '{self.relation_label}' không nằm trong 22 nhãn RelationLabel hợp lệ: "
                f"{sorted(VALID_ENTITY_RELATION_LABELS)}"
            )

    def to_cypher_props(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "confidence": float(self.confidence),
            "source_chunk_id": self.source_chunk_id,
            "owner_id": self.owner_id,
            "scope": self.scope.value if isinstance(self.scope, ScopeEnum) else self.scope,
            "created_at": self.created_at,
        }


@dataclass(slots=True)
class GraphRelationship:
    """
    Đại diện tổng quát cho một cạnh có hướng giữa 2 Node bất kỳ trong Neo4j.
    """

    source_label: NodeLabelEnum
    source_id_field: str
    source_id_value: str
    rel_type: RelationshipTypeEnum | EntityRelationTypeEnum | PedagogyRelationTypeEnum
    target_label: NodeLabelEnum
    target_id_field: str
    target_id_value: str
    properties: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def link_entities(
        cls,
        source_canonical_code: str,
        relation_label: RelationLabel,
        target_canonical_code: str,
        **props: Any,
    ) -> "GraphRelationship":
        """
        Tạo cạnh nối giữa 2 :KnowledgeEntity bằng 1 trong 22 nhãn thuộc RelationLabel.
        """
        if relation_label not in VALID_ENTITY_RELATION_LABELS:
            raise ValueError(f"RelationLabel không hợp lệ: {relation_label}")

        return cls(
            source_label=NodeLabelEnum.KNOWLEDGE_ENTITY,
            source_id_field="canonical_code",
            source_id_value=normalize_canonical_code(source_canonical_code),
            rel_type=EntityRelationTypeEnum(relation_label),
            target_label=NodeLabelEnum.KNOWLEDGE_ENTITY,
            target_id_field="canonical_code",
            target_id_value=normalize_canonical_code(target_canonical_code),
            properties=props,
        )

    @classmethod
    def link_entity_to_satellite(
        cls,
        canonical_code: str,
        rel_type: PedagogyRelationTypeEnum | RelationshipTypeEnum,
        satellite_label: NodeLabelEnum,
        satellite_id: str,
        **props: Any,
    ) -> "GraphRelationship":
        """Tạo cạnh nối từ :KnowledgeEntity(canonical_code) sang một Node vệ tinh(id)."""
        return cls(
            source_label=NodeLabelEnum.KNOWLEDGE_ENTITY,
            source_id_field="canonical_code",
            source_id_value=normalize_canonical_code(canonical_code),
            rel_type=rel_type,
            target_label=satellite_label,
            target_id_field="id",
            target_id_value=satellite_id,
            properties=props,
        )

    @classmethod
    def link_process_to_step(
        cls,
        process_id: str,
        step_id: str,
        step_number: int,
    ) -> "GraphRelationship":
        """Tạo cạnh (:Process)-[:HAS_STEP {step_number}]->(:ProcessStep)."""
        return cls(
            source_label=NodeLabelEnum.PROCESS,
            source_id_field="id",
            source_id_value=process_id,
            rel_type=PedagogyRelationTypeEnum.HAS_STEP,
            target_label=NodeLabelEnum.PROCESS_STEP,
            target_id_field="id",
            target_id_value=step_id,
            properties={"step_number": step_number},
        )