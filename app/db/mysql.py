import logging
import os
from pathlib import Path
import ssl
from dotenv import dotenv_values
from collections.abc import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import settings

logger = logging.getLogger(__name__)

class MySQLDatabaseManager:
    """
    Quản lý AsyncEngine và AsyncSessionMaker cho MySQL (lưu trữ chunks và trạng thái phiên chat).
    """

    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    def init_mysql(self) -> None:
        """Khởi tạo connection pool tới MySQL khi FastAPI khởi động."""
        if self._engine is not None:
            return

        connect_args = {}
        if settings.MYSQL_PORT == 4000 or "tidbcloud.com" in settings.MYSQL_HOST:
            connect_args["ssl"] = ssl.create_default_context()
            
        self._engine = create_async_engine(
            settings.MYSQL_ASYNC_URI,
            echo=settings.MYSQL_ECHO,
            pool_size=settings.MYSQL_POOL_SIZE,
            max_overflow=settings.MYSQL_MAX_OVERFLOW,
            pool_recycle=settings.MYSQL_POOL_RECYCLE,
            pool_pre_ping=True, 
            connect_args=connect_args,
        )

        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
        logger.info("Đã khởi tạo MySQL AsyncEngine tại %s:%s/%s", settings.MYSQL_HOST, settings.MYSQL_PORT, settings.MYSQL_DATABASE)

    async def verify_connectivity(self) -> bool:
        """Kiểm tra kết nối thực tế tới MySQL (dùng khi startup hoặc healthcheck từ Spring Boot)."""
        if self._engine is None:
            raise RuntimeError("MySQLDatabaseManager chưa được khởi tạo. Hãy gọi init_mysql() trước.")
        async with self._engine.connect() as conn:
            database = await conn.scalar(text("SELECT DATABASE()"))
            # Uvicorn configures its own logger; application INFO may otherwise be hidden.
            startup_logger = logging.getLogger('uvicorn.error')
            env_path = Path(__file__).resolve().parents[2] / '.env'
            file_database = dotenv_values(env_path).get('MYSQL_DATABASE')
            startup_logger.info(
                'MySQL database thực tế=%s; cấu hình=%s; .env=%s; pid=%s',
                database, settings.MYSQL_DATABASE, file_database, os.getpid())
            if file_database and file_database != settings.MYSQL_DATABASE:
                startup_logger.warning(
                    'MYSQL_DATABASE runtime khác .env. Kiểm tra biến môi trường của terminal/IDE/container; '
                    'biến môi trường ưu tiên hơn .env. env_file=%s', env_path)
            if database != settings.MYSQL_DATABASE:
                raise RuntimeError('Database MySQL thực tế không khớp MYSQL_DATABASE; kiểm tra cấu hình kết nối.')
        return True

    async def close_mysql(self) -> None:
        """Giải phóng toàn bộ kết nối trong pool khi FastAPI dừng."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Đã đóng kết nối MySQL AsyncEngine.")

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            raise RuntimeError("MySQL session factory chưa sẵn sàng. Hãy kiểm tra lifespan của ứng dụng.")
        return self._session_factory


mysql_manager = MySQLDatabaseManager()


async def get_mysql_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI Dependency cung cấp AsyncSession cho từng request từ Spring Boot.
    Tự động rollback nếu xảy ra lỗi và đóng session khi kết thúc request/stream.
    """
    session_factory = mysql_manager.session_factory
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
