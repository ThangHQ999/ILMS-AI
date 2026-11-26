from functools import lru_cache
from pathlib import Path
import json
from typing import Any, Literal
from urllib.parse import quote_plus
from pydantic import Field, computed_field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Cấu hình toàn diện cho FastAPI Socratic Tutor & Knowledge Graph Extraction Service.
    Tự động đọc biến môi trường từ file `.env`, kiểm tra tính hợp lệ và cung cấp các thuộc tính
    tính toán sẵn (Computed Fields) cho MySQL, Neo4j, ChromaDB, Gemini, OpenAI và Spring Boot Gateway.
    """

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / '.env'),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # =========================================================================
    # 1. CẤU HÌNH ỨNG DỤNG, SERVER & LOGGING
    # =========================================================================
    PROJECT_NAME: str = Field(default="ILMS-AI")
    APP_NAME: str = Field(default="ILMS-AI-Service")
    APP_VERSION: str = Field(default="1.0.0")
    APP_DESCRIPTION: str = Field(
        default=(
            "FastAPI Microservice cho Socratic Tutor Chat SSE & "
            "Automatic Knowledge Graph Extraction (Neo4j + ChromaDB + MySQL)"
        )
    )
    APP_ENV: Literal["development", "staging", "production", "test"] = Field(
        default="development"
    )
    DEBUG: bool = Field(default=False)
    TIMEZONE: str = Field(default="Asia/Ho_Chi_Minh")

    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8001, ge=1, le=65535)
    WORKERS: int = Field(default=1, ge=1, le=32)
    RELOAD: bool = Field(default=True)

    API_V1_PREFIX: str = Field(default="/api/v1")
    ENABLE_DOCS_IN_PROD: bool = Field(
        default=False,
        description="Cho phép bật Swagger UI (/docs) ngay cả khi APP_ENV=production",
    )

    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )
    LOG_JSON_FORMAT: bool = Field(
        default=False,
        description="True: Xuất log dạng JSON phục vụ ELK / Loki / Grafana",
    )

    @computed_field
    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @computed_field
    @property
    def docs_url(self) -> str | None:
        if self.is_production and not self.ENABLE_DOCS_IN_PROD:
            return None
        return "/docs"

    @computed_field
    @property
    def redoc_url(self) -> str | None:
        if self.is_production and not self.ENABLE_DOCS_IN_PROD:
            return None
        return "/redoc"

    # =========================================================================
    # 2. CẤU HÌNH BẢO MẬT NỘI BỘ & GIAO TIẾP VỚI SPRING BOOT
    # =========================================================================
    INTERNAL_API_KEY: str = Field(
        ...,
        min_length=16,
        description="Secret key bắt buộc để xác thực request từ Spring Boot gọi sang FastAPI",
    )
    INTERNAL_API_KEY_HEADER: str = Field(default="X-Internal-Api-Key")
    USER_ID_HEADER: str = Field(default="X-User-Id")
    USER_ROLE_HEADER: str = Field(default="X-User-Role")
    TEACHER_ID_HEADER: str = Field(default="X-Teacher-Id")

    SPRING_BOOT_BASE_URL: str = Field(
        default="http://localhost:8080",
        description="URL gốc của Spring Boot Backend",
    )
    SPRING_BOOT_KG_WEBHOOK_PATH: str = Field(
        default="/api/internal/ai/kg-extraction-callback",
        description="Đường dẫn webhook bên Spring Boot nhận thông báo khi bóc tách KG nền hoàn tất",
    )
    SPRING_BOOT_TIMEOUT_SECONDS: float = Field(default=30.0, gt=0.0)

    CORS_ALLOWED_ORIGINS: list[str] | str = Field(
        default=["http://localhost:8080", "http://localhost:3000", "http://localhost:5173"]
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    CORS_ALLOW_METHODS: list[str] = Field(default=["*"])
    CORS_ALLOW_HEADERS: list[str] = Field(default=["*"])

    @field_validator("CORS_ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        """Hỗ trợ đọc CORS_ALLOWED_ORIGINS từ chuỗi phân cách dấu phẩy hoặc mảng JSON."""
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            val = value.strip()
            if val.startswith("[") and val.endswith("]"):
                try:
                    parsed = json.loads(val)
                    if isinstance(parsed, list):
                        return [str(x).strip() for x in parsed if str(x).strip()]
                except json.JSONDecodeError:
                    pass
            return [origin.strip() for origin in val.split(",") if origin.strip()]
        return ["*"]

    # =========================================================================
    # 3. CẤU HÌNH MYSQL (LƯU MATERIAL_CHUNKS & SOCRATIC_CHAT_SESSIONS/MESSAGES)
    # =========================================================================
    MYSQL_HOST: str = Field(default="localhost")
    MYSQL_PORT: int = Field(default=3306, ge=1, le=65535)
    MYSQL_USER: str = Field(default="root")
    MYSQL_PASSWORD: str = Field(...)
    MYSQL_DATABASE: str = Field(default="ilms_db")
    MYSQL_CHARSET: str = Field(default="utf8mb4")
    MYSQL_ASYNC_DRIVER: Literal["asyncmy", "aiomysql"] = Field(default="asyncmy")
    MYSQL_SYNC_DRIVER: Literal["pymysql", "mysqldb"] = Field(
        default="pymysql",
        description="Driver đồng bộ dùng khi chạy Alembic migrations",
    )

    MYSQL_POOL_SIZE: int = Field(default=10, ge=1, le=200)
    MYSQL_MAX_OVERFLOW: int = Field(default=20, ge=0, le=200)
    MYSQL_POOL_RECYCLE: int = Field(default=3600, ge=60)
    MYSQL_POOL_TIMEOUT: float = Field(default=30.0, gt=0.0)
    MYSQL_POOL_PRE_PING: bool = Field(default=True)
    MYSQL_CONNECT_TIMEOUT: int = Field(default=10, ge=1)
    MYSQL_ECHO: bool = Field(default=False)

    @computed_field
    @property
    def MYSQL_ASYNC_URI(self) -> str:
        """
        Chuỗi kết nối bất đồng bộ cho SQLAlchemy AsyncEngine.
        Tự động mã hóa URL (`quote_plus`) cho user/password chứa ký tự đặc biệt (`@`, `:`, `/`).
        """
        safe_user = quote_plus(self.MYSQL_USER)
        safe_pass = quote_plus(self.MYSQL_PASSWORD)
        return (
            f"mysql+{self.MYSQL_ASYNC_DRIVER}://{safe_user}:{safe_pass}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset={self.MYSQL_CHARSET}"
        )

    @computed_field
    @property
    def MYSQL_SYNC_URI(self) -> str:
        """Chuỗi kết nối đồng bộ phục vụ công cụ Alembic chạy migration bảng MySQL."""
        safe_user = quote_plus(self.MYSQL_USER)
        safe_pass = quote_plus(self.MYSQL_PASSWORD)
        return (
            f"mysql+{self.MYSQL_SYNC_DRIVER}://{safe_user}:{safe_pass}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset={self.MYSQL_CHARSET}"
        )

    # =========================================================================
    # 4. CẤU HÌNH NEO4J (7 LOẠI NODE & 22 CẠNH RELATIONLABEL)
    # =========================================================================
    NEO4J_URI: str = Field(
        default="bolt://localhost:7687",
        description="Hỗ trợ bolt://, neo4j:// hoặc neo4j+s:// (AuraDB)",
    )
    NEO4J_USERNAME: str = Field(default="neo4j")
    NEO4J_PASSWORD: str = Field(...)
    NEO4J_DATABASE: str = Field(default="neo4j")

    NEO4J_MAX_CONNECTION_LIFETIME: int = Field(default=3600, ge=60)
    NEO4J_MAX_CONNECTION_POOL_SIZE: int = Field(default=50, ge=1, le=500)
    NEO4J_CONNECTION_TIMEOUT: float = Field(default=30.0, gt=0.0)
    NEO4J_MAX_TRANSACTION_RETRY_TIME: float = Field(default=30.0, gt=0.0)
    NEO4J_FETCH_SIZE: int = Field(default=1000, ge=100)
    NEO4J_AUTO_INIT_CONSTRAINTS: bool = Field(
        default=True,
        description="True: Tự động tạo Unique Constraints và Indexes cho 7 loại Node khi khởi động",
    )

    # =========================================================================
    # 5. CẤU HÌNH CHROMADB (VECTOR DATABASE LƯU EMBEDDINGS CỦA CHUNKS)
    # =========================================================================
    CHROMA_MODE: Literal["http", "persistent"] = Field(
        default="http",
        description="'http' khi kết nối tới Chroma Server (Docker), 'persistent' khi lưu trên ổ cứng",
    )
    CHROMA_HOST: str = Field(default="localhost")
    CHROMA_PORT: int = Field(default=8001, ge=1, le=65535)
    CHROMA_SSL: bool = Field(default=False)
    CHROMA_AUTH_TOKEN: str | None = Field(default=None)
    CHROMA_TENANT: str = Field(default="default_tenant")
    CHROMA_DATABASE: str = Field(default="default_database")

    CHROMA_PERSIST_DIR: str = Field(default="./chroma_data")
    CHROMA_COLLECTION_NAME: str = Field(default="socratic_knowledge_chunks")
    CHROMA_DISTANCE_METRIC: Literal["cosine", "l2", "ip"] = Field(default="cosine")
    CHROMA_ANONYMIZED_TELEMETRY: bool = Field(default=False)

    # Tham số tinh chỉnh chỉ mục HNSW của ChromaDB
    CHROMA_HNSW_M: int = Field(default=16, ge=4, le=128)
    CHROMA_HNSW_CONSTRUCTION_EF: int = Field(default=100, ge=10, le=1000)
    CHROMA_HNSW_SEARCH_EF: int = Field(default=50, ge=10, le=1000)

    # =========================================================================
    # 6. CẤU HÌNH DUAL-PROVIDER AI / LLM (GOOGLE GEMINI & OPENAI)
    # =========================================================================
    LLM_DEFAULT_PROVIDER: Literal["gemini", "openai"] = Field(
        default="openai",
        description="Provider ưu tiên mặc định cho Socratic Chat SSE và KG Extraction",
    )
    EMBEDDING_PROVIDER: Literal["gemini", "openai"] = Field(
        default="openai",
        description="Provider cố định để tính toán vector embedding (giữ đồng nhất số chiều trong ChromaDB)",
    )
    LLM_ENABLE_FALLBACK: bool = Field(
        default=True,
        description="True: Tự động chuyển đổi sang provider còn lại nếu provider chính lỗi hoặc quá tải",
    )
    LLM_REQUEST_TIMEOUT: float = Field(default=60.0, gt=0.0)
    LLM_MAX_RETRIES: int = Field(default=2, ge=0, le=10)

    # --- 6.1. Cấu hình Google Gemini (google-genai SDK) ---
    GEMINI_API_KEY: str | None = Field(default=None)
    GEMINI_CHAT_MODEL: str = Field(
        default="gemini-2.5-flash",
        description="Model Gemini tốc độ cao dùng để stream câu trả lời gợi mở Socratic SSE",
    )
    GEMINI_EXTRACTION_MODEL: str = Field(
        default="gemini-2.5-pro",
        description="Model Gemini suy luận sâu dùng để bóc tách 7 loại Node & 22 cạnh RelationLabel",
    )
    GEMINI_EMBEDDING_MODEL: str = Field(default="text-embedding-004")
    GEMINI_EMBEDDING_DIMENSION: int = Field(default=768, ge=128, le=3072)
    GEMINI_CHAT_TEMPERATURE: float = Field(default=0.4, ge=0.0, le=2.0)
    GEMINI_EXTRACTION_TEMPERATURE: float = Field(default=0.1, ge=0.0, le=2.0)
    GEMINI_MAX_OUTPUT_TOKENS: int = Field(default=4096, ge=256, le=65536)

    # --- 6.2. Cấu hình OpenAI (AsyncOpenAI SDK) ---
    OPENAI_API_KEY: str | None = Field(default=None)
    OPENAI_BASE_URL: str | None = Field(default=None)
    OPENAI_ORG_ID: str | None = Field(default=None)
    OPENAI_PROJECT_ID: str | None = Field(default=None)
    OPENAI_CHAT_MODEL: str = Field(
        default="gpt-4o-mini",
        description="Model OpenAI phản hồi nhanh cho Socratic Chat SSE",
    )
    OPENAI_EXTRACTION_MODEL: str = Field(
        default="gpt-4o-mini",
        description="Model OpenAI chuẩn xác cho Structured Outputs bóc tách Đồ thị Tri thức",
    )
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-3-small")
    OPENAI_EMBEDDING_DIMENSION: int = Field(default=1536, ge=256, le=3072)
    OPENAI_CHAT_TEMPERATURE: float = Field(default=0.4, ge=0.0, le=2.0)
    OPENAI_SEND_TEMPERATURE: bool = False
    OPENAI_EXTRACTION_TEMPERATURE: float = Field(default=0.1, ge=0.0, le=2.0)
    OPENAI_MAX_OUTPUT_TOKENS: int = Field(default=4096, ge=256, le=32768)

    @computed_field
    @property
    def active_embedding_dimension(self) -> int:
        """Trả về số chiều vector ứng với EMBEDDING_PROVIDER đang chọn."""
        if self.EMBEDDING_PROVIDER == "gemini":
            return self.GEMINI_EMBEDDING_DIMENSION
        return self.OPENAI_EMBEDDING_DIMENSION

    # =========================================================================
    # 7. CẤU HÌNH NGHIỆP VỤ: CHUNKING, KG EXTRACTION & SOCRATIC RAG SSE
    # =========================================================================
    # --- 7.1. Cắt nhỏ học liệu (Chunking & Embedding) ---
    CHUNK_DEFAULT_SIZE_TOKENS: int = Field(default=512, ge=100, le=4000)
    CHUNK_DEFAULT_OVERLAP_TOKENS: int = Field(default=64, ge=0, le=1000)
    EMBEDDING_BATCH_SIZE: int = Field(
        default=64,
        ge=1,
        le=512,
        description="Số lượng chunks tối đa gửi đi tính embedding trong 1 lần gọi API",
    )

    # --- 7.2. Trích xuất Đồ thị Tri thức (Knowledge Graph Extraction) ---
    KG_EXTRACTION_CONCURRENCY: int = Field(
        default=3,
        ge=1,
        le=20,
        description="Số lượng chunks tối đa được gọi AI bóc tách KG song song cùng lúc",
    )
    KG_MIN_RELATION_CONFIDENCE: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Ngưỡng độ tự tin tối thiểu để lưu cạnh RelationLabel vào Neo4j",
    )
    KG_AUTO_EXTRACT_ON_INGEST: bool = Field(default=True)

    # --- 7.3. Socratic Tutor Hybrid RAG & SSE Stream ---
    SOCRATIC_RAG_TOP_K_CHUNKS: int = Field(
        default=4,
        ge=1,
        le=20,
        description="Số lượng chunks lấy từ ChromaDB/MySQL đưa vào ngữ cảnh mỗi lượt hỏi",
    )
    SOCRATIC_MAX_HISTORY_MESSAGES: int = Field(
        default=8,
        ge=2,
        le=30,
        description="Số tin nhắn gần nhất trong bảng socratic_chat_messages nạp vào prompt",
    )

    SSE_PING_INTERVAL_SECONDS: int = Field(
        default=15,
        ge=5,
        le=120,
        description="Chu kỳ gửi gói ping giữ kết nối SSE với Spring Boot không bị timeout",
    )
    SSE_RETRY_TIMEOUT_MS: int = Field(default=3000, ge=500)

    # Socratic tutoring: single service, task budgets and retrieval configuration.
    SOCRATIC_LEASE_SECONDS: int = Field(default=120, ge=30)
    SOCRATIC_CACHE_SECONDS: int = Field(default=120, ge=0)
    SOCRATIC_CACHE_SIZE: int = Field(default=128, ge=1)
    SOCRATIC_CONTEXT_CHARS: int = Field(default=18000, ge=2000)
    SOCRATIC_MAX_OUTPUT_CHARS: int = Field(default=18000, ge=1000)
    SOCRATIC_MAX_STACK: int = Field(default=3, ge=1, le=8)
    SOCRATIC_INDEPENDENT_SUCCESSES: int = Field(default=3, ge=2)
    SOCRATIC_RETRIEVAL_K: int = Field(default=12, ge=2, le=50)
    SOCRATIC_MIN_SIMILARITY: float = Field(default=0.5, ge=-1, le=1)
    SOCRATIC_ENTITY_COLLECTION: str = 'socratic_knowledge_entities'
    SOCRATIC_GRAPH_NODES: int = Field(default=8, ge=1, le=30)
    SOCRATIC_RUBRIC_STATUSES: list[str] = ['ACTIVE', 'APPROVED']
    SOCRATIC_REQUEST_TIMEOUT: float = Field(default=180, gt=0)
    SOCRATIC_TOPIC_MARGIN: float = Field(default=0.02, ge=0)
    SOCRATIC_SATELLITE_EDGES: list[str] = ['HAS_DEFINITION', 'HAS_EXAMPLE', 'HAS_ARGUMENT']
    SOCRATIC_SEMANTIC_EDGES: list[str] = ['REQUIRES', 'DEPENDS_ON', 'IS_A', 'PART_OF', 'CONTRASTS_WITH', 'USES', 'APPLIES_TO']
    SOCRATIC_RUBRIC_EDGE: str = 'HAS_RUBRIC'
    SOCRATIC_CRITERION_EDGE: str = 'HAS_CRITERION'
    SOCRATIC_EXERCISE_EDGE: str = 'HAS_EXERCISE'
    OPENAI_INTENT_MODEL: str | None = None
    OPENAI_EVALUATION_MODEL: str | None = None
    OPENAI_QUESTION_MODEL: str | None = None
    OPENAI_ARTIFACT_MODEL: str | None = None
    GEMINI_INTENT_MODEL: str | None = None
    GEMINI_EVALUATION_MODEL: str | None = None
    GEMINI_QUESTION_MODEL: str | None = None
    GEMINI_ARTIFACT_MODEL: str | None = None

    # =========================================================================
    # 8. KIỂM TRA TÍNH NHẤT QUÁN TOÀN CỤC (CROSS-FIELD VALIDATION)
    # =========================================================================
    @model_validator(mode="after")
    def validate_ai_and_chunk_settings(self) -> "Settings":
        """Đảm bảo cấu hình overlap hợp lệ và ít nhất 1 AI Provider có API Key khi chạy thực tế."""
        if self.CHUNK_DEFAULT_OVERLAP_TOKENS >= self.CHUNK_DEFAULT_SIZE_TOKENS:
            raise ValueError(
                "CHUNK_DEFAULT_OVERLAP_TOKENS phải nhỏ hơn CHUNK_DEFAULT_SIZE_TOKENS."
            )

        if self.APP_ENV != "test":
            has_gemini = bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY.strip())
            has_openai = bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY.strip())
            if not has_gemini and not has_openai:
                raise ValueError(
                    "Phải cấu hình ít nhất GEMINI_API_KEY hoặc OPENAI_API_KEY trong file .env."
                )
        return self


@lru_cache
def get_settings() -> Settings:
    """Khởi tạo Singleton Settings duy nhất trong suốt vòng đời ứng dụng."""
    return Settings()


settings = get_settings()
