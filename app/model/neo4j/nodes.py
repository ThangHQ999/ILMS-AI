from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
from typing import Any
import uuid
from app.model.enums import DifficultyEnum, NodeLabelEnum, ScopeEnum


def generate_node_uuid() -> str:
    return str(uuid.uuid4())


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_canonical_code(raw_code: str) -> str:
    """
    Chuẩn hóa canonical_code của :KnowledgeEntity về dạng UPPER_SNAKE_CASE bất biến.
    Ví dụ: 'Pythagoras Theorem' -> 'PYTHAGORAS_THEOREM'.
    """
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", raw_code.strip())
    return re.sub(r"_+", "_", cleaned).strip("_").upper()


@dataclass(slots=True)
class KnowledgeEntityNode:
    """
    1. Label :KnowledgeEntity
    - Vai trò: Tâm chung bất biến đại diện cho 1 khái niệm khoa học.
    - Quản lý bởi: Hệ thống / Admin chuẩn hóa.
    """

    canonical_code: str
    name: str
    subject: str
    source_chunk_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    label: NodeLabelEnum = field(default=NodeLabelEnum.KNOWLEDGE_ENTITY, init=False)

    def __post_init__(self) -> None:
        self.canonical_code = normalize_canonical_code(self.canonical_code)
        self.subject = self.subject.strip().upper()

    def to_cypher_props(self) -> dict[str, Any]:
        return {
            "canonical_code": self.canonical_code,
            "name": self.name,
            "subject": self.subject,
            "source_chunk_id": self.source_chunk_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_neo4j(cls, data: dict[str, Any]) -> "KnowledgeEntityNode":
        return cls(
            canonical_code=data["canonical_code"],
            name=data["name"],
            subject=data["subject"],
            source_chunk_id=data.get("source_chunk_id"),
            created_at=data.get("created_at", utc_now_iso()),
            updated_at=data.get("updated_at", utc_now_iso()),
        )


@dataclass(slots=True)
class DefinitionNode:
    """
    2. Label :Definition
    - Vai trò: Định nghĩa / Diễn giải lý thuyết.
    - Quản lý bởi: Admin tạo bản chuẩn (GLOBAL), Giáo viên tạo bản riêng (TEACHER).
    """

    content: str
    owner_id: str
    scope: ScopeEnum = ScopeEnum.GLOBAL
    conditions: list[str] = field(default_factory=list)
    exceptions: list[str] = field(default_factory=list)
    id: str = field(default_factory=generate_node_uuid)
    source_chunk_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    label: NodeLabelEnum = field(default=NodeLabelEnum.DEFINITION, init=False)

    def to_cypher_props(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "conditions": self.conditions,
            "exceptions": self.exceptions,
            "owner_id": self.owner_id,
            "scope": self.scope.value if isinstance(self.scope, ScopeEnum) else self.scope,
            "source_chunk_id": self.source_chunk_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_neo4j(cls, data: dict[str, Any]) -> "DefinitionNode":
        return cls(
            id=data["id"],
            content=data["content"],
            conditions=list(data.get("conditions") or []),
            exceptions=list(data.get("exceptions") or []),
            owner_id=data["owner_id"],
            scope=ScopeEnum(data["scope"]),
            source_chunk_id=data.get("source_chunk_id"),
            created_at=data.get("created_at", utc_now_iso()),
            updated_at=data.get("updated_at", utc_now_iso()),
        )


@dataclass(slots=True)
class ProcessStepNode:
    """
    4. Label :ProcessStep
    - Vai trò: Từng bước giải chi tiết (để gợi ý từng bước trong Socratic Chat).
    - Quản lý bởi: Nối trực tiếp với :Process tương ứng.
    """

    step_number: int
    action: str
    hint_prompt: str
    id: str = field(default_factory=generate_node_uuid)
    process_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    label: NodeLabelEnum = field(default=NodeLabelEnum.PROCESS_STEP, init=False)

    def to_cypher_props(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "step_number": int(self.step_number),
            "action": self.action,
            "hint_prompt": self.hint_prompt,
            "process_id": self.process_id,
            "created_at": self.created_at,
        }

    @classmethod
    def from_neo4j(cls, data: dict[str, Any]) -> "ProcessStepNode":
        return cls(
            id=data["id"],
            step_number=int(data["step_number"]),
            action=data["action"],
            hint_prompt=data["hint_prompt"],
            process_id=data.get("process_id"),
            created_at=data.get("created_at", utc_now_iso()),
        )


@dataclass(slots=True)
class ProcessNode:
    """
    3. Label :Process
    - Vai trò: Phương pháp / Quy trình giải dạng bài.
    - Quản lý bởi: Admin (GLOBAL) hoặc Giáo viên (TEACHER).
    """

    name: str
    owner_id: str
    scope: ScopeEnum = ScopeEnum.GLOBAL
    id: str = field(default_factory=generate_node_uuid)
    steps: list[ProcessStepNode] = field(default_factory=list)
    source_chunk_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    label: NodeLabelEnum = field(default=NodeLabelEnum.PROCESS, init=False)

    def to_cypher_props(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "owner_id": self.owner_id,
            "scope": self.scope.value if isinstance(self.scope, ScopeEnum) else self.scope,
            "source_chunk_id": self.source_chunk_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_neo4j(
        cls,
        data: dict[str, Any],
        steps: list[ProcessStepNode] | None = None,
    ) -> "ProcessNode":
        sorted_steps = sorted(steps or [], key=lambda s: s.step_number)
        return cls(
            id=data["id"],
            name=data["name"],
            owner_id=data["owner_id"],
            scope=ScopeEnum(data["scope"]),
            steps=sorted_steps,
            source_chunk_id=data.get("source_chunk_id"),
            created_at=data.get("created_at", utc_now_iso()),
            updated_at=data.get("updated_at", utc_now_iso()),
        )


@dataclass(slots=True)
class ExampleNode:
    """
    5. Label :Example
    - Vai trò: Ví dụ minh họa / Đoạn code mẫu.
    - Quản lý bởi: Admin (GLOBAL) hoặc Giáo viên (TEACHER).
    """

    title: str
    explanation: str
    owner_id: str
    code_snippet: str | None = None
    scope: ScopeEnum = ScopeEnum.GLOBAL
    id: str = field(default_factory=generate_node_uuid)
    source_chunk_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    label: NodeLabelEnum = field(default=NodeLabelEnum.EXAMPLE, init=False)

    def to_cypher_props(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "code_snippet": self.code_snippet,
            "explanation": self.explanation,
            "owner_id": self.owner_id,
            "scope": self.scope.value if isinstance(self.scope, ScopeEnum) else self.scope,
            "source_chunk_id": self.source_chunk_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_neo4j(cls, data: dict[str, Any]) -> "ExampleNode":
        return cls(
            id=data["id"],
            title=data["title"],
            code_snippet=data.get("code_snippet"),
            explanation=data["explanation"],
            owner_id=data["owner_id"],
            scope=ScopeEnum(data["scope"]),
            source_chunk_id=data.get("source_chunk_id"),
            created_at=data.get("created_at", utc_now_iso()),
            updated_at=data.get("updated_at", utc_now_iso()),
        )


@dataclass(slots=True)
class ExerciseNode:
    """
    6. Label :Exercise
    - Vai trò: Bài tập rèn luyện.
    - Quản lý bởi: Admin (GLOBAL) hoặc Giáo viên (TEACHER).
    """

    title: str
    content: str
    owner_id: str
    difficulty: DifficultyEnum = DifficultyEnum.MEDIUM
    scope: ScopeEnum = ScopeEnum.GLOBAL
    id: str = field(default_factory=generate_node_uuid)
    source_chunk_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    label: NodeLabelEnum = field(default=NodeLabelEnum.EXERCISE, init=False)

    def to_cypher_props(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "difficulty": (
                self.difficulty.value
                if isinstance(self.difficulty, DifficultyEnum)
                else self.difficulty
            ),
            "owner_id": self.owner_id,
            "scope": self.scope.value if isinstance(self.scope, ScopeEnum) else self.scope,
            "source_chunk_id": self.source_chunk_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_neo4j(cls, data: dict[str, Any]) -> "ExerciseNode":
        return cls(
            id=data["id"],
            title=data["title"],
            content=data["content"],
            difficulty=DifficultyEnum(data.get("difficulty", DifficultyEnum.MEDIUM.value)),
            owner_id=data["owner_id"],
            scope=ScopeEnum(data["scope"]),
            source_chunk_id=data.get("source_chunk_id"),
            created_at=data.get("created_at", utc_now_iso()),
            updated_at=data.get("updated_at", utc_now_iso()),
        )


@dataclass(slots=True)
class ArgumentNode:
    """
    7. Label :Argument
    - Vai trò: Lập luận logic / Chứng minh.
    - Quản lý bởi: Admin (GLOBAL) hoặc Giáo viên (TEACHER).
    """

    hypothesis: str
    evidence: str
    conclusion: str
    owner_id: str
    scope: ScopeEnum = ScopeEnum.GLOBAL
    id: str = field(default_factory=generate_node_uuid)
    source_chunk_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    label: NodeLabelEnum = field(default=NodeLabelEnum.ARGUMENT, init=False)

    def to_cypher_props(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "hypothesis": self.hypothesis,
            "evidence": self.evidence,
            "conclusion": self.conclusion,
            "owner_id": self.owner_id,
            "scope": self.scope.value if isinstance(self.scope, ScopeEnum) else self.scope,
            "source_chunk_id": self.source_chunk_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_neo4j(cls, data: dict[str, Any]) -> "ArgumentNode":
        return cls(
            id=data["id"],
            hypothesis=data["hypothesis"],
            evidence=data["evidence"],
            conclusion=data["conclusion"],
            owner_id=data["owner_id"],
            scope=ScopeEnum(data["scope"]),
            source_chunk_id=data.get("source_chunk_id"),
            created_at=data.get("created_at", utc_now_iso()),
            updated_at=data.get("updated_at", utc_now_iso()),
        )