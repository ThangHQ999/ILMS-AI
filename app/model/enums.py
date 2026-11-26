from enum import Enum
from typing import Literal

# 22 nhãn quan hệ ngữ nghĩa nối giữa các (:KnowledgeEntity)-[:RelationLabel]->(:KnowledgeEntity)
RelationLabel = Literal[
    # 1. Phân loại & Kế thừa (Taxonomy / Hierarchy)
    "IS_A",
    "HAS_CATEGORY",
    "HAS_SUBTYPE",
    "CLASSIFIED_INTO",
    "IS_VARIANT_OF",
    # 2. Cấu trúc & Thành phần (Meronymy / Composition)
    "PART_OF",
    "COMPOSED_OF",
    "CONTAINS",
    # 3. Điều kiện tiên quyết & Phạm vi áp dụng (Dependency & Application)
    "REQUIRES",
    "DEPENDS_ON",
    "APPLIES_TO",
    # 4. Liên kết, Sử dụng & Đối chiếu (Association & Comparison)
    "ASSOCIATED_WITH",
    "USES",
    "CONTRASTS_WITH",
    "IMPROVES_UPON",
    # 5. Nhân quả & Giải quyết bài toán (Causality & Output)
    "CAUSES",
    "LEADS_TO",
    "SOLVES",
    "PRODUCES",
    "YIELDS",
    # 6. Nguồn gốc lịch sử / Tác giả (Provenance)
    "CREATED_BY",
    "DISCOVERED_BY",
    "PREREQUISITE",
    "PREREQUISITE_OF",
    "BASED_ON",
    "HAS_PREREQUISITE",
]


class EntityRelationTypeEnum(str, Enum):
    """
    Enum tương ứng 1-1 với RelationLabel (22 loại cạnh nối giữa :KnowledgeEntity với :KnowledgeEntity).
    """

    # Phân loại & Kế thừa
    IS_A = "IS_A"
    HAS_CATEGORY = "HAS_CATEGORY"
    HAS_SUBTYPE = "HAS_SUBTYPE"
    CLASSIFIED_INTO = "CLASSIFIED_INTO"
    IS_VARIANT_OF = "IS_VARIANT_OF"

    # Cấu trúc & Thành phần
    PART_OF = "PART_OF"
    COMPOSED_OF = "COMPOSED_OF"
    CONTAINS = "CONTAINS"

    # Điều kiện tiên quyết & Phạm vi áp dụng
    REQUIRES = "REQUIRES"
    DEPENDS_ON = "DEPENDS_ON"
    APPLIES_TO = "APPLIES_TO"
    PREREQUISITE_OF = "PREREQUISITE_OF"
    PREREQUISITE = "PREREQUISITE"
    BASED_ON = "BASED_ON"
    HAS_PREREQUISITE = "HAS_PREREQUISITE"

    # Liên kết, Sử dụng & Đối chiếu
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    USES = "USES"
    CONTRASTS_WITH = "CONTRASTS_WITH"
    IMPROVES_UPON = "IMPROVES_UPON"

    # Nhân quả & Giải quyết bài toán
    CAUSES = "CAUSES"
    LEADS_TO = "LEADS_TO"
    SOLVES = "SOLVES"
    PRODUCES = "PRODUCES"
    YIELDS = "YIELDS"

    # Nguồn gốc / Tác giả
    CREATED_BY = "CREATED_BY"
    DISCOVERED_BY = "DISCOVERED_BY"


class ScopeEnum(str, Enum):
    """
    Phạm vi quản lý và hiển thị của các Node tri thức và Document Chunks:
    - GLOBAL: Bản chuẩn do Hệ thống / Admin khởi tạo, mọi học sinh và giáo viên đều truy cập được.
    - TEACHER: Bản riêng do Giáo viên tạo hoặc tinh chỉnh cho lớp học của mình.
    """

    GLOBAL = "GLOBAL"
    TEACHER = "TEACHER"


class OwnerRoleEnum(str, Enum):
    """Vai trò người dùng được truyền từ Spring Boot sang FastAPI."""

    SYSTEM = "SYSTEM"
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"


class DifficultyEnum(str, Enum):
    """Mức độ khó của Node :Exercise trong Neo4j."""

    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    ADVANCED = "ADVANCED"


class ExtractionStatusEnum(str, Enum):
    """Trạng thái bóc tách Đồ thị Tri thức (Knowledge Graph) của một Chunk trong MySQL."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class MessageRoleEnum(str, Enum):
    """Vai trò tin nhắn trong phiên hội thoại Socratic Tutor."""

    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "ASSISTANT"


class NodeLabelEnum(str, Enum):
    """7 nhãn Node chuẩn trong cơ sở dữ liệu đồ thị Neo4j."""

    KNOWLEDGE_ENTITY = "KnowledgeEntity"
    DEFINITION = "Definition"
    PROCESS = "Process"
    PROCESS_STEP = "ProcessStep"
    EXAMPLE = "Example"
    EXERCISE = "Exercise"
    ARGUMENT = "Argument"