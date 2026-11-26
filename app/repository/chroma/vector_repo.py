import inspect
import asyncio
from typing import Any
from chromadb.api.models.AsyncCollection import AsyncCollection
from chromadb.api.models.Collection import Collection
from app.model.chroma.vector_record import ChromaChunkMetadata, ChromaVectorRecord
from app.model.enums import ScopeEnum
from app.model.mysql.material_chunk import MaterialChunk

class ChromaVectorRepository:
    """
    Repository thao tác với ChromaDB Collection để lưu và tìm kiếm tương đồng vector cho `material_chunks`.
    Hỗ trợ trong suốt cả `AsyncCollection` (chế độ http) lẫn `Collection` (chế độ persistent).
    """

    def __init__(self, collection: AsyncCollection | Collection) -> None:
        self._collection = collection

    async def _invoke(self, method_name: str, **kwargs: Any) -> Any:
        """Gọi hàm trên Chroma Collection bất kể đang dùng AsyncHttpClient hay PersistentClient."""
        method = getattr(self._collection, method_name)
        result = await method(**kwargs) if inspect.iscoroutinefunction(method) else await asyncio.to_thread(method, **kwargs)
        if inspect.isawaitable(result):
            return await result
        return result

    @staticmethod
    def _build_metadata_from_chunk(chunk: MaterialChunk) -> dict[str, str | int | float | bool]:
        """Chuyển đổi bản ghi `MaterialChunk` sang từ điển metadata phẳng của ChromaDB."""
        material_id = str(getattr(chunk, "material_id", None) or getattr(chunk, "document_id", ""))
        scope_val = chunk.scope.value if isinstance(chunk.scope, ScopeEnum) else str(chunk.scope)
        codes_csv = ",".join(chunk.canonical_codes or [])
        return {
            "material_id": material_id,
            "document_id": material_id,
            "owner_id": str(chunk.owner_id),
            "scope": scope_val,
            "subject": str(chunk.subject).strip().upper(),
            "chunk_index": int(chunk.chunk_index),
            "canonical_codes_csv": codes_csv,
        }

    async def upsert_chunks(
        self,
        chunks: list[MaterialChunk],
        embeddings: list[list[float]] | None = None,
    ) -> None:
        """
        Thêm mới hoặc cập nhật hàng loạt chunks vào ChromaDB.
        `id` trong ChromaDB trùng khớp 1-1 với `MaterialChunk.id` trong MySQL.
        """
        if not chunks:
            return

        ids = [str(c.id) for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = [self._build_metadata_from_chunk(c) for c in chunks]

        payload: dict[str, Any] = {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas,
        }
        if embeddings is not None:
            payload["embeddings"] = embeddings

        await self._invoke("upsert", **payload)

    async def update_chunk_canonical_codes(
        self,
        chunk: MaterialChunk,
        canonical_codes: list[str],
    ) -> None:
        """
        Cập nhật lại `canonical_codes_csv` trong metadata của ChromaDB sau khi AI bóc tách KG xong.
        """
        meta = self._build_metadata_from_chunk(chunk)
        meta["canonical_codes_csv"] = ",".join(canonical_codes)
        await self._invoke(
            "update",
            ids=[str(chunk.id)],
            metadatas=[meta],
        )

    @staticmethod
    def build_where_filter(
        *,
        subject: str | None = None,
        teacher_id: str | None = None,
        material_ids: list[str] | None = None,
    ) -> dict[str, Any] | None:
        """
        Tạo bộ lọc `where` chuẩn cho ChromaDB:
        - Luôn lấy kiến thức `scope = GLOBAL` của Admin.
        - Nếu có `teacher_id`, lấy thêm kiến thức `scope = TEACHER` của đúng `owner_id = teacher_id`.
        - Hỗ trợ lọc theo `subject` và danh sách `material_ids`.
        """
        base_filter = ChromaVectorRecord.build_access_where_filter(
            subject=subject,
            teacher_id=teacher_id,
        )
        conditions: list[dict[str, Any]] = []
        if base_filter:
            conditions.append(base_filter)

        if material_ids:
            if len(material_ids) == 1:
                conditions.append({"material_id": {"$eq": material_ids[0]}})
            else:
                conditions.append({"material_id": {"$in": material_ids}})

        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}

    async def similarity_search(
        self,
        *,
        query_text: str | None = None,
        query_embedding: list[float] | None = None,
        top_k: int = 5,
        subject: str | None = None,
        teacher_id: str | None = None,
        material_ids: list[str] | None = None,
    ) -> list[ChromaVectorRecord]:
        """
        Truy vấn top_k đoạn văn bản gần nghĩa nhất từ ChromaDB để phục vụ Socratic RAG.
        """
        if query_text is None and query_embedding is None:
            raise ValueError("Phải cung cấp `query_text` hoặc `query_embedding` khi tìm kiếm vector.")

        where_clause = self.build_where_filter(
            subject=subject,
            teacher_id=teacher_id,
            material_ids=material_ids,
        )

        query_kwargs: dict[str, Any] = {
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"],
        }
        if where_clause is not None:
            query_kwargs["where"] = where_clause

        if query_embedding is not None:
            query_kwargs["query_embeddings"] = [query_embedding]
        else:
            query_kwargs["query_texts"] = [query_text]

        raw_res: dict[str, Any] = await self._invoke("query", **query_kwargs)

        ids_list: list[str] = (raw_res.get("ids") or [[]])[0]
        docs_list: list[str] = (raw_res.get("documents") or [[]])[0]
        metas_list: list[dict[str, Any]] = (raw_res.get("metadatas") or [[]])[0]
        dists_list: list[float] = (raw_res.get("distances") or [[]])[0]

        records: list[ChromaVectorRecord] = []
        for idx, chunk_id in enumerate(ids_list):
            meta_dict = metas_list[idx] if idx < len(metas_list) and metas_list[idx] else {}
            doc_text = docs_list[idx] if idx < len(docs_list) and docs_list[idx] else ""
            dist_val = float(dists_list[idx]) if idx < len(dists_list) and dists_list[idx] is not None else 0.0

            records.append(
                ChromaVectorRecord(
                    chunk_id=str(chunk_id),
                    document=doc_text,
                    metadata=ChromaChunkMetadata.from_chroma_dict(meta_dict),
                    distance=dist_val,
                )
            )
        return records

    async def delete_by_material_id(self, material_id: str) -> None:
        """Xóa toàn bộ vector của một học liệu khỏi ChromaDB."""
        await self._invoke("delete", where={"material_id": {"$eq": material_id}})

    async def delete_by_chunk_ids(self, chunk_ids: list[str]) -> None:
        """Xóa danh sách vector theo chunk_ids."""
        if not chunk_ids:
            return
        await self._invoke("delete", ids=chunk_ids)
