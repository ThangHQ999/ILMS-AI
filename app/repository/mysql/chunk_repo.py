import uuid
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.model.enums import ExtractionStatusEnum
from app.model.mysql.material_chunk import MaterialChunk
from app.model.neo4j.nodes import normalize_canonical_code
from app.schema.chunk_schema import MaterialChunkCreate, MaterialChunkUpdate


class MaterialChunkRepository:
    """
    Repository thao tác trực tiếp với bảng `material_chunks` trong MySQL.
    Hỗ trợ đồng bộ khóa `id` (BinaryUUID / 36-char UUID) với ChromaDB và Neo4j.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_chunk(self, chunk_in: MaterialChunkCreate) -> MaterialChunk:
        """Tạo mới 1 bản ghi chunk trong MySQL."""
        chunk_id = chunk_in.id or str(uuid.uuid4())
        db_chunk = MaterialChunk(
            id=chunk_id,
            material_id=chunk_in.material_id,
            owner_id=chunk_in.owner_id,
            scope=chunk_in.scope,
            subject=chunk_in.subject,
            chunk_index=chunk_in.chunk_index,
            content=chunk_in.content,
            token_count=chunk_in.token_count,
            char_start=chunk_in.char_start,
            char_end=chunk_in.char_end,
            canonical_codes=chunk_in.canonical_codes or [],
            extraction_status=ExtractionStatusEnum.PENDING,
            extra_metadata=chunk_in.extra_metadata or {},
        )
        self._session.add(db_chunk)
        await self._session.commit()
        await self._session.refresh(db_chunk)
        return db_chunk

    async def bulk_create_chunks(
        self,
        chunks_in: list[MaterialChunkCreate],
    ) -> list[MaterialChunk]:
        """Lưu hàng loạt chunks của một học liệu (`material_id`) trong 1 transaction."""
        if not chunks_in:
            return []

        db_chunks: list[MaterialChunk] = []
        for item in chunks_in:
            chunk_id = item.id or str(uuid.uuid4())
            db_chunks.append(
                MaterialChunk(
                    id=chunk_id,
                    material_id=item.material_id,
                    owner_id=item.owner_id,
                    scope=item.scope,
                    subject=item.subject,
                    chunk_index=item.chunk_index,
                    content=item.content,
                    token_count=item.token_count,
                    char_start=item.char_start,
                    char_end=item.char_end,
                    canonical_codes=item.canonical_codes or [],
                    extraction_status=ExtractionStatusEnum.PENDING,
                    extra_metadata=item.extra_metadata or {},
                )
            )
        self._session.add_all(db_chunks)
        await self._session.commit()
        for chunk in db_chunks:
            await self._session.refresh(chunk)
        return db_chunks

    async def get_by_id(self, chunk_id: str) -> MaterialChunk | None:
        """Lấy chi tiết 1 chunk theo UUID."""
        stmt = select(MaterialChunk).where(MaterialChunk.id == chunk_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids_preserve_order(
        self,
        chunk_ids: list[str],
    ) -> list[MaterialChunk]:
        """
        Truy xuất danh sách chunks theo `chunk_ids` (do ChromaDB trả về sau khi tìm kiếm tương đồng)
        và giữ nguyên thứ tự xếp hạng độ tương đồng của ChromaDB.
        """
        if not chunk_ids:
            return []

        stmt = select(MaterialChunk).where(MaterialChunk.id.in_(chunk_ids))
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        chunk_map = {str(row.id): row for row in rows}
        return [chunk_map[cid] for cid in chunk_ids if cid in chunk_map]

    async def list_by_material_id(
        self,
        material_id: str,
        only_unextracted: bool = False,
    ) -> list[MaterialChunk]:
        """
        Lấy toàn bộ các chunks thuộc một tài liệu gốc (`material_id`), sắp xếp theo `chunk_index` tăng dần.
        """
        stmt = select(MaterialChunk).where(MaterialChunk.material_id == material_id)
        if only_unextracted:
            stmt = stmt.where(
                MaterialChunk.extraction_status.in_(
                    [ExtractionStatusEnum.PENDING, ExtractionStatusEnum.FAILED]
                )
            )
        stmt = stmt.order_by(MaterialChunk.chunk_index.asc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_chunk(
        self,
        chunk_id: str,
        update_in: MaterialChunkUpdate,
    ) -> MaterialChunk | None:
        """Cập nhật thông tin hoặc trạng thái trích xuất KG của 1 chunk."""
        db_chunk = await self.get_by_id(chunk_id)
        if db_chunk is None:
            return None

        update_data = update_in.model_dump(exclude_unset=True)
        for field_name, value in update_data.items():
            setattr(db_chunk, field_name, value)

        await self._session.commit()
        await self._session.refresh(db_chunk)
        return db_chunk

    async def mark_extraction_processing(self, chunk_ids: list[str]) -> None:
        """Đánh dấu hàng loạt chunks sang trạng thái PROCESSING trước khi gọi AI bóc tách KG."""
        if not chunk_ids:
            return
        stmt = (
            update(MaterialChunk)
            .where(MaterialChunk.id.in_(chunk_ids))
            .values(
                extraction_status=ExtractionStatusEnum.PROCESSING,
                extraction_error=None,
            )
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def mark_extraction_completed(
        self,
        chunk_id: str,
        canonical_codes: list[str],
    ) -> MaterialChunk | None:
        """Cập nhật chunk sau khi AI đã trích xuất thành công các Node vào Neo4j."""
        normalized_codes = sorted(
            {normalize_canonical_code(c) for c in canonical_codes if c and c.strip()}
        )
        db_chunk = await self.get_by_id(chunk_id)
        if db_chunk is None:
            return None

        db_chunk.canonical_codes = normalized_codes
        db_chunk.extraction_status = ExtractionStatusEnum.COMPLETED
        db_chunk.extraction_error = None
        await self._session.commit()
        await self._session.refresh(db_chunk)
        return db_chunk

    async def mark_extraction_failed(
        self,
        chunk_id: str,
        error_message: str,
    ) -> MaterialChunk | None:
        """Ghi nhận lỗi nếu quá trình AI bóc tách đồ thị tri thức cho chunk gặp sự cố."""
        db_chunk = await self.get_by_id(chunk_id)
        if db_chunk is None:
            return None

        db_chunk.extraction_status = ExtractionStatusEnum.FAILED
        db_chunk.extraction_error = error_message[:2000]
        await self._session.commit()
        await self._session.refresh(db_chunk)
        return db_chunk

    async def delete_by_material_id(self, material_id: str) -> int:
        """Xóa toàn bộ chunks của một học liệu."""
        stmt = delete(MaterialChunk).where(MaterialChunk.material_id == material_id)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return int(result.rowcount or 0)
