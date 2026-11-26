from dataclasses import dataclass, field
from typing import Any
from app.model.enums import ScopeEnum


@dataclass(slots=True)
class ChromaChunkMetadata:
    """
    Cấu trúc Metadata phẳng gắn kèm mỗi Vector trong ChromaDB.
    Lưu ý: ChromaDB chỉ cho phép giá trị nguyên thủy (str, int, float, bool) trong metadata,
    do đó danh sách `canonical_codes` được nối thành chuỗi phân cách bởi dấu phẩy.
    """

    document_id: str
    owner_id: str
    scope: ScopeEnum
    subject: str
    chunk_index: int
    canonical_codes_csv: str = ""

    def to_chroma_dict(self) -> dict[str, str | int | float | bool]:
        return {
            "document_id": self.document_id,
            "owner_id": self.owner_id,
            "scope": self.scope.value if isinstance(self.scope, ScopeEnum) else str(self.scope),
            "subject": self.subject.upper(),
            "chunk_index": int(self.chunk_index),
            "canonical_codes_csv": self.canonical_codes_csv,
        }

    @property
    def canonical_codes(self) -> list[str]:
        if not self.canonical_codes_csv:
            return []
        return [code.strip() for code in self.canonical_codes_csv.split(",") if code.strip()]

    @classmethod
    def from_chroma_dict(cls, data: dict[str, Any]) -> "ChromaChunkMetadata":
        return cls(
            document_id=str(data.get("document_id", "")),
            owner_id=str(data.get("owner_id", "")),
            scope=ScopeEnum(data.get("scope", ScopeEnum.GLOBAL.value)),
            subject=str(data.get("subject", "")),
            chunk_index=int(data.get("chunk_index", 0)),
            canonical_codes_csv=str(data.get("canonical_codes_csv", "")),
        )


@dataclass(slots=True)
class ChromaVectorRecord:
    """
    Đại diện cho 1 bản ghi Vector trong ChromaDB.
    `chunk_id` trùng khớp 1-1 với `DocumentChunk.id` trong MySQL.
    """

    chunk_id: str
    document: str
    metadata: ChromaChunkMetadata
    embedding: list[float] | None = None
    distance: float | None = None

    @staticmethod
    def build_access_where_filter(
        subject: str | None = None,
        teacher_id: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Tạo bộ lọc `where` cho ChromaDB đảm bảo quyền truy cập kiến thức:
        - Nếu có `teacher_id`: Lấy cả kiến thức chuẩn của hệ thống (scope='GLOBAL')
          VÀ kiến thức riêng của giáo viên đó (scope='TEACHER' & owner_id=teacher_id).
        - Nếu không có `teacher_id`: Chỉ lấy kiến thức chuẩn (scope='GLOBAL').
        """
        conditions: list[dict[str, Any]] = []

        if subject:
            conditions.append({"subject": {"$eq": subject.strip().upper()}})

        if teacher_id:
            scope_filter: dict[str, Any] = {
                "$or": [
                    {"scope": {"$eq": ScopeEnum.GLOBAL.value}},
                    {
                        "$and": [
                            {"scope": {"$eq": ScopeEnum.TEACHER.value}},
                            {"owner_id": {"$eq": teacher_id}},
                        ]
                    },
                ]
            }
        else:
            scope_filter = {"scope": {"$eq": ScopeEnum.GLOBAL.value}}

        conditions.append(scope_filter)

        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}