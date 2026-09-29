import os
import json
import hashlib
from typing import Any, Dict, Iterable, List, Optional, Set
import pymysql
from lightrag.base import BaseKVStorage


class MySQLKVStorage(BaseKVStorage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Bảng KV chuẩn của LightRAG (lightrag_text_chunks, lightrag_full_docs, lightrag_llm_response_cache)
        self.table_name = f"lightrag_{self.namespace}"
        
        # Bảng nghiệp vụ song hành (chỉ kích hoạt khi namespace là text_chunks)
        self.is_chunk_namespace = (self.namespace == "text_chunks")
        self.custom_table_name = "material_chunks"

        self.host = os.getenv("MYSQL_HOST", "localhost")
        self.port = int(os.getenv("MYSQL_PORT", 3306))
        self.user = os.getenv("MYSQL_USER", "root")
        self.password = os.getenv("MYSQL_PASSWORD", "")
        self.db = os.getenv("MYSQL_DATABASE", "lightrag_db")
        
        self._init_db()

    def _get_connection(self):
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.db,
            charset="utf8mb4",
            autocommit=True
        )

    def _init_db(self):
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. Luôn tạo bảng mặc định cho LightRAG
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS `{self.table_name}` (
                        `id` VARCHAR(255) NOT NULL,
                        `data` LONGTEXT NOT NULL,
                        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        PRIMARY KEY (`id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """)

                # 2. Nếu là text_chunks, tạo thêm bảng material_chunks
                if self.is_chunk_namespace:
                    cursor.execute(f"""
                        CREATE TABLE IF NOT EXISTS `{self.custom_table_name}` (
                                `id` binary(16) NOT NULL,
#                               `material_id` binary(16) NOT NULL,
                                `chunk_index` int(11) NOT NULL DEFAULT 0,
                                `token_count` int(11) DEFAULT NULL,
                                `content_text` longtext NOT NULL,
#                               `embedding_vector` text DEFAULT NULL, -- Hoặc kiểu VECTOR (nếu dùng MySQL hỗ trợ native vector như MySQL 9.0+)
                                `created_at` datetime(6) DEFAULT current_timestamp(6),
                                PRIMARY KEY (`id`)
#                               KEY `idx_material_chunks_material` (`material_id`)
#                               CONSTRAINT `fk_material_chunks_material` FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                    """)
        finally:
            conn.close()

    @staticmethod
    def to_binary_16(key: str) -> bytes:
        """
        Quy đổi ID dạng chuỗi (từ Chroma/LightRAG) thành đúng 16 bytes nhị phân.
        - Nếu key là UUID hex (32 ký tự), chuyển trực tiếp sang bytes.
        - Nếu key là chuỗi tùy ý, dùng MD5 băm thành 16 bytes chuẩn.
        """
        clean = key.replace("-", "")
        if len(clean) == 32:
            try:
                return bytes.fromhex(clean)
            except ValueError:
                pass
        return hashlib.md5(key.encode("utf-8")).digest()

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        # LightRAG đọc từ bảng mặc định để giữ trọn vẹn dữ liệu
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT `data` FROM `{self.table_name}` WHERE `id` = %s", (id,))
                result = cursor.fetchone()
                return json.loads(result[0]) if result else None
        finally:
            conn.close()

    async def get_by_ids(self, ids: List[str], fields: Optional[List[str]] = None) -> List[Optional[Dict[str, Any]]]:
        if not ids:
            return []

        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                format_strings = ",".join(["%s"] * len(ids))
                query = f"SELECT `id`, `data` FROM `{self.table_name}` WHERE `id` IN ({format_strings})"
                cursor.execute(query, ids)
                rows = cursor.fetchall()
                data_map = {row[0]: json.loads(row[1]) for row in rows}
                return [data_map.get(chunk_id) for chunk_id in ids]
        finally:
            conn.close()

    async def filter_keys(self, data: List[str]) -> Set[str]:
        if not data:
            return set()

        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                format_strings = ",".join(["%s"] * len(data))
                query = f"SELECT `id` FROM `{self.table_name}` WHERE `id` IN ({format_strings})"
                cursor.execute(query, data)
                existing_keys = {row[0] for row in cursor.fetchall()}
                return set(data) - existing_keys
        finally:
            conn.close()

    async def upsert(self, data: Dict[str, Dict[str, Any]]):
        if not data:
            return

        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                # BƯỚC 1: Ghi vào bảng lightrag_{namespace} (đảm bảo LightRAG hoạt động trơn tru)
                default_records = [
                    (key, json.dumps(val, ensure_ascii=False))
                    for key, val in data.items()
                ]
                query_default = f"""
                    INSERT INTO `{self.table_name}` (`id`, `data`) 
                    VALUES (%s, %s) 
                    ON DUPLICATE KEY UPDATE 
                        `data` = VALUES(`data`),
                        `updated_at` = CURRENT_TIMESTAMP
                """
                cursor.executemany(query_default, default_records)

                # BƯỚC 2: Ghi SONG HÀNH vào bảng material_chunks nếu là text_chunks
                if self.is_chunk_namespace:
                    custom_records = []
                    for key, val in data.items():
                        bin_id = self.to_binary_16(key)
                        chunk_index = val.get("chunk_order_index", 0)
                        token_count = val.get("tokens", 0)
                        content_text = val.get("content", "")
                        custom_records.append((bin_id, chunk_index, token_count, content_text))

                    query_custom = f"""
                        INSERT INTO `{self.custom_table_name}` 
                            (`id`, `chunk_index`, `token_count`, `content_text`)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            `chunk_index` = VALUES(`chunk_index`),
                            `token_count` = VALUES(`token_count`),
                            `content_text` = VALUES(`content_text`)
                    """
                    cursor.executemany(query_custom, custom_records)
        finally:
            conn.close()

    async def delete(self, ids: Iterable[str]):
        """Xóa các bản ghi dựa trên danh sách ID"""
        ids_list = list(ids)
        if not ids_list:
            return

        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. Xóa trong bảng mặc định của LightRAG
                format_strings = ",".join(["%s"] * len(ids_list))
                query_default = f"DELETE FROM `{self.table_name}` WHERE `id` IN ({format_strings})"
                cursor.execute(query_default, ids_list)

                # 2. Xóa trong bảng custom (material_chunks) nếu có
                if self.is_chunk_namespace:
                    bin_ids = [self.to_binary_16(i) for i in ids_list]
                    query_custom = f"DELETE FROM `{self.custom_table_name}` WHERE `id` IN ({format_strings})"
                    cursor.execute(query_custom, bin_ids)
        finally:
            conn.close()

    async def drop(self):
        """Xóa toàn bộ dữ liệu trong bảng (Reset namespace)"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                # Dùng TRUNCATE để xóa sạch dữ liệu nhưng giữ lại cấu trúc bảng
                cursor.execute(f"TRUNCATE TABLE `{self.table_name}`")
                if self.is_chunk_namespace:
                    cursor.execute(f"TRUNCATE TABLE `{self.custom_table_name}`")
        finally:
            conn.close()

    async def is_empty(self) -> bool:
        """Kiểm tra xem bảng có đang trống hay không"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT 1 FROM `{self.table_name}` LIMIT 1")
                result = cursor.fetchone()
                return result is None
        finally:
            conn.close()

    async def index_done_callback(self):
        pass