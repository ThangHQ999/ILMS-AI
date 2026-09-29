import os
from pinecone import Pinecone, ServerlessSpec
from lightrag.base import BaseVectorStorage

class PineconeVectorStorage(BaseVectorStorage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = "lightrag-index"
        
        # Tự động tạo index nếu chưa có
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=1536, # Dimension của text-embedding-3-small
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        self.index = self.pc.Index(self.index_name)

    async def upsert(self, data: dict[str, dict]):
        vectors = []
        for key, val in data.items():
            vector = val.get("vector", [])
            # Lọc các trường metadata cần thiết
            metadata = {k: v for k, v in val.items() if k in self.meta_fields}
            vectors.append({"id": key, "values": vector, "metadata": metadata})
        
        # Pinecone khuyến nghị upsert theo batch (từng cụm 100 vector)
        for i in range(0, len(vectors), 100):
            self.index.upsert(vectors=vectors[i:i+100], namespace=self.namespace)

    async def query(self, query: str, top_k: int):
        # Dùng cho API Query sau này
        vector = await self.embedding_func([query])
        res = self.index.query(vector=vector[0], top_k=top_k, include_metadata=True, namespace=self.namespace)
        return [item["metadata"] for item in res["matches"]]