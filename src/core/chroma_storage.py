import inspect
import os
from typing import Any, Dict, Iterable, List, Optional
import chromadb
from lightrag.base import BaseVectorStorage

class ChromaVectorStorage(BaseVectorStorage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Khởi tạo ChromaDB lưu trữ cục bộ (Persistent)
        chroma_path = os.getenv("CHROMA_PATH", "./data/chroma")
        if not os.path.exists(chroma_path):
            os.makedirs(chroma_path)
            
        self.client = chromadb.PersistentClient(path=chroma_path)
        
        # Tạo hoặc lấy collection (bảng) tương ứng với namespace (VD: chunks, entities)
        # Sử dụng cosine similarity để khớp với thuật toán embedding của OpenAI
        self.collection = self.client.get_or_create_collection(
            name=self.namespace,
            metadata={"hnsw:space": "cosine"} 
        )
    
    async def _compute_embedding(self, texts: List[str]) -> List[List[float]]:
        """Hỗ trợ gọi embedding_func linh hoạt (kể cả sync hay async)"""
        if inspect.iscoroutinefunction(self.embedding_func):
            return await self.embedding_func(texts)
        return self.embedding_func(texts)

    async def upsert(self, data: Dict[str, dict]):
            """Thêm mới hoặc cập nhật vector vào ChromaDB theo batch an toàn"""
            if not data:
                return

            ids: List[str] = []
            embeddings: List[List[float]] = []
            metadatas: List[Dict[str, Any]] = []

            for key, val in data.items():
                # Lấy vector nhúng có sẵn
                vector = val.get("vector")
                if vector is None:
                    continue

                ids.append(str(key))
                embeddings.append(vector)

                # Lọc metadata theo meta_fields mà LightRAG quy định
                meta: Dict[str, Any] = {}
                for field in self.meta_fields:
                    if field in val and val[field] is not None:
                        field_val = val[field]
                        if isinstance(field_val, (str, int, float, bool)):
                            meta[field] = field_val
                        else:
                            meta[field] = str(field_val)

                if not meta:
                    meta["_id"] = str(key)
                else:
                    meta.setdefault("id", str(key))

                metadatas.append(meta)

            if not ids:
                return

            # Chia nhỏ batch để tránh vượt ngưỡng max_batch_size của ChromaDB
            max_batch_size = self.client.get_max_batch_size()
            batch_size = min(max_batch_size, 500)

            for i in range(0, len(ids), batch_size):
                end_idx = i + batch_size
                self.collection.upsert(
                    ids=ids[i:end_idx],
                    embeddings=embeddings[i:end_idx],
                    metadatas=metadatas[i:end_idx]
                )

    async def query(self, query: str, top_k: int) -> List[dict]:
        """Tìm kiếm vector tương đồng và trả về format LightRAG mong đợi"""
        total_records = self.collection.count()
        if total_records == 0:
            return []

        # Giới hạn n_results không vượt quá số lượng bản ghi thực tế trong collection
        actual_k = min(top_k, total_records)
        if actual_k <= 0:
            return []

        # 1. Tính toán embedding cho câu truy vấn
        query_embeddings = await self._compute_embedding([query])

        # 2. Thực hiện truy vấn trong ChromaDB
        results = self.collection.query(
            query_embeddings=query_embeddings,
            n_results=actual_k,
            include=["metadatas", "distances"]
        )

        output: List[dict] = []
        if not results.get("metadatas") or not results["metadatas"][0]:
            return output

        matched_ids = results["ids"][0] if results.get("ids") else []
        matched_metas = results["metadatas"][0]
        matched_distances = results["distances"][0] if results.get("distances") else []

        for idx, meta in enumerate(matched_metas):
            res_item = dict(meta)
            
            # Gắn lại ID gốc nếu metadata chưa có
            if "id" not in res_item and idx < len(matched_ids):
                res_item["id"] = matched_ids[idx]

            # Gắn khoảng cách/điểm tương đồng (nếu LightRAG cần dùng để xếp hạng)
            if idx < len(matched_distances):
                res_item["distance"] = matched_distances[idx]

            output.append(res_item)

        return output
    
    async def delete(self, ids: Iterable[str]):
        """Xóa vector theo danh sách ID"""
        ids_list = list(ids)
        if ids_list:
            try:
                self.collection.delete(ids=ids_list)
            except Exception:
                pass

    async def drop(self):
        """Xóa toàn bộ collection vector và tạo lại"""
        try:
            self.client.delete_collection(name=self.namespace)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=self.namespace,
            metadata={"hnsw:space": "cosine"}
        )

    async def get_by_id(self, id: str) -> Optional[dict]:
        """Lấy metadata của 1 vector bằng ID"""
        try:
            res = self.collection.get(ids=[id], include=["metadatas"])
            if res.get("metadatas") and len(res["metadatas"]) > 0 and res["metadatas"][0] is not None:
                return res["metadatas"][0]
        except Exception:
            pass
        return None

    async def get_by_ids(self, ids: Iterable[str]) -> List[dict]:
        """Lấy metadata của nhiều vector bằng list ID"""
        ids_list = list(ids)
        if not ids_list:
            return []
        try:
            res = self.collection.get(ids=ids_list, include=["metadatas"])
            if res.get("metadatas"):
                return [m for m in res["metadatas"] if m is not None]
        except Exception:
            pass
        return []

    async def get_vectors_by_ids(self, ids: Iterable[str]) -> List[List[float]]:
        """Lấy trực tiếp mảng vector (embedding) của list ID"""
        ids_list = list(ids)
        if not ids_list:
            return []
        try:
            res = self.collection.get(ids=ids_list, include=["embeddings"])
            if res.get("embeddings"):
                return res["embeddings"]
        except Exception:
            pass
        return []

    async def delete_entity(self, entity_name: str):
        """Xóa vector của một thực thể (Dùng cho Knowledge Graph)"""
        try:
            self.collection.delete(ids=[entity_name])
        except Exception:
            pass

    async def delete_entity_relation(self, entity_name: str):
        """Xóa các quan hệ liên quan đến thực thể (Dựa theo metadata)"""
        try:
            # ChromaDB cho phép xóa dựa trên điều kiện (where clause)
            self.collection.delete(where={"source_id": entity_name})
        except Exception:
            pass

    async def index_done_callback(self):
        """Hàm callback khi quá trình nạp dữ liệu hoàn tất"""
        pass