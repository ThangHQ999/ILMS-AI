import logging
import chromadb
from chromadb.api import AsyncClientAPI, ClientAPI
from chromadb.api.models.AsyncCollection import AsyncCollection
from chromadb.api.models.Collection import Collection
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings

logger = logging.getLogger(__name__)


class ChromaDatabaseManager:
    """
    Quản lý kết nối tới ChromaDB để lưu trữ và truy vấn vector embeddings của các document chunks.
    Hỗ trợ cả 2 chế độ:
    - 'http': Kết nối bất đồng bộ (AsyncHttpClient) tới Chroma Server chạy độc lập (Docker/K8s).
    - 'persistent': Lưu trữ trực tiếp trên ổ đĩa local (PersistentClient) phục vụ phát triển nhanh.
    """

    def __init__(self) -> None:
        self._async_client: AsyncClientAPI | None = None
        self._sync_client: ClientAPI | None = None
        self._async_collection: AsyncCollection | None = None
        self._sync_collection: Collection | None = None

    async def init_chroma(self) -> None:
        """Khởi tạo Chroma Client và tạo/lấy Collection lưu vector chunks."""
        collection_metadata = {
            "hnsw:space": settings.CHROMA_DISTANCE_METRIC,
            "description": "Vector embeddings của các chunks phục vụ Socratic Tutor & KG Extraction",
        }

        if settings.CHROMA_MODE == "http":
            headers = {}
            if settings.CHROMA_AUTH_TOKEN:
                headers["Authorization"] = f"Bearer {settings.CHROMA_AUTH_TOKEN}"

            self._async_client = await chromadb.AsyncHttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
                ssl=settings.CHROMA_SSL,
                headers=headers or None,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self._async_collection = await self._async_client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata=collection_metadata,
            )
            logger.info(
                "Đã kết nối Chroma AsyncHttpClient tại %s:%s (collection=%s, metric=%s)",
                settings.CHROMA_HOST,
                settings.CHROMA_PORT,
                settings.CHROMA_COLLECTION_NAME,
                settings.CHROMA_DISTANCE_METRIC,
            )
        else:
            self._sync_client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self._sync_collection = self._sync_client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata=collection_metadata,
            )
            logger.info(
                "Đã khởi tạo Chroma PersistentClient tại '%s' (collection=%s)",
                settings.CHROMA_PERSIST_DIR,
                settings.CHROMA_COLLECTION_NAME,
            )

    async def verify_connectivity(self) -> bool:
        """Kiểm tra heartbeat của ChromaDB."""
        if settings.CHROMA_MODE == "http":
            if self._async_client is None:
                raise RuntimeError("Chroma AsyncHttpClient chưa được khởi tạo.")
            await self._async_client.heartbeat()
            return True

        if self._sync_client is None:
            raise RuntimeError("Chroma PersistentClient chưa được khởi tạo.")
        self._sync_client.heartbeat()
        return True

    async def close_chroma(self) -> None:
        """Đặt lại tham chiếu client khi ứng dụng dừng."""
        self._async_collection = None
        self._sync_collection = None
        self._async_client = None
        self._sync_client = None
        logger.info("Đã giải phóng tài nguyên ChromaDatabaseManager.")

    @property
    def collection(self) -> AsyncCollection | Collection:
        """Trả về đối tượng Collection hiện hành (AsyncCollection ở chế độ http, Collection ở chế độ persistent)."""
        if settings.CHROMA_MODE == "http" and self._async_collection is not None:
            return self._async_collection
        if settings.CHROMA_MODE == "persistent" and self._sync_collection is not None:
            return self._sync_collection
        raise RuntimeError("Chroma collection chưa sẵn sàng. Hãy kiểm tra lifespan của ứng dụng.")


chroma_manager = ChromaDatabaseManager()


def get_chroma_collection() -> AsyncCollection | Collection:
    """
    FastAPI Dependency cung cấp Chroma Collection cho VectorRepository.
    """
    return chroma_manager.collection