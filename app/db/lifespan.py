import logging
from collections.abc import AsyncIterator
from typing import Any
from fastapi import FastAPI
from app.db.chroma import chroma_manager
from app.db.mysql import mysql_manager
from app.db.neo4j import neo4j_manager

logger = logging.getLogger(__name__)

async def db_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Quản lý vòng đời kết nối của cả 3 cơ sở dữ liệu (MySQL, Neo4j, ChromaDB).
    """
    logger.info("Đang thiết lập kết nối tới MySQL, Neo4j và ChromaDB...")
    try:
        # 1. Khởi tạo và kiểm tra MySQL
        mysql_manager.init_mysql()
        await mysql_manager.verify_connectivity()

        # 2. Khởi tạo, kiểm tra Neo4j và tạo Unique Constraints cho 7 loại Node
        neo4j_manager.init_neo4j()
        await neo4j_manager.verify_connectivity()
        await neo4j_manager.init_constraints_and_indexes()

        # 3. Khởi tạo và kiểm tra ChromaDB
        await chroma_manager.init_chroma()
        await chroma_manager.verify_connectivity()

        logger.info("Tất cả 3 cơ sở dữ liệu (MySQL, Neo4j, ChromaDB) đã sẵn sàng nhận request từ Spring Boot.")
        yield
    finally:
        logger.info("Đang đóng kết nối tới MySQL, Neo4j và ChromaDB...")
        await chroma_manager.close_chroma()
        await neo4j_manager.close_neo4j()
        await mysql_manager.close_mysql()
        logger.info("Đã đóng toàn bộ kết nối cơ sở dữ liệu an toàn.")


async def check_all_databases_health() -> dict[str, Any]:
    """
    Kiểm tra trạng thái sống của cả 3 DB (phục vụ route /health để Spring Boot kiểm tra trước khi stream SSE).
    """
    status_report: dict[str, Any] = {
        "mysql": "down",
        "neo4j": "down",
        "chroma": "down",
        "healthy": False,
    }
    try:
        if await mysql_manager.verify_connectivity():
            status_report["mysql"] = "up"
    except Exception as exc:
        status_report["mysql_error"] = str(exc)

    try:
        if await neo4j_manager.verify_connectivity():
            status_report["neo4j"] = "up"
    except Exception as exc:
        status_report["neo4j_error"] = str(exc)

    try:
        if await chroma_manager.verify_connectivity():
            status_report["chroma"] = "up"
    except Exception as exc:
        status_report["chroma_error"] = str(exc)

    status_report["healthy"] = (
        status_report["mysql"] == "up"
        and status_report["neo4j"] == "up"
        and status_report["chroma"] == "up"
    )
    return status_report