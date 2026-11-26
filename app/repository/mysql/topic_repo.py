"""Read-only, scoped Topic lookup; topics are inferred by the backend."""
from uuid import UUID

from sqlalchemy import select, or_, and_, func, table, column, exists, text
from app.model.mysql.base import BinaryUUID
from app.db.mysql import mysql_manager
from app.model.mysql.material_chunk import MaterialChunk
from app.model.mysql.tutoring import Topic, TopicChunk
from app.model.enums import ScopeEnum


publications = table('material_publications', column('id', BinaryUUID),
                     column('material_id', BinaryUUID), column('material_version_id', BinaryUUID),
                     column('status'), column('is_current'))


def active_publication():
    return and_(publications.c.status == 'PUBLISHED', publications.c.is_current == 1,
                publications.c.material_version_id == MaterialChunk.material_version_id,
                publications.c.material_id == MaterialChunk.material_id)


def chunk_scope(teacher_id=None, subject=None, material_ids=None, student_id=None, publication_ids=None):
    access = MaterialChunk.scope == ScopeEnum.GLOBAL
    if student_id:
        enrolled = text("""
            EXISTS (SELECT 1 FROM materials m
              JOIN class_courses cc ON cc.course_id=m.course_id AND cc.status='ACTIVE'
              JOIN classes c ON c.id=cc.class_id
              JOIN courses co ON co.id=m.course_id
              WHERE m.id=material_chunks.material_id AND c.deleted_at IS NULL
                AND COALESCE(c.is_archived,FALSE)=FALSE AND co.deleted_at IS NULL
                AND EXISTS (
                  SELECT 1 FROM class_members cm WHERE cm.class_id=c.id
                    AND cm.user_id=:student AND UPPER(cm.status)='ACTIVE'))
        """).bindparams(student=UUID(student_id).bytes)
        private = and_(MaterialChunk.scope == ScopeEnum.TEACHER,
                       enrolled)
        if teacher_id:
            private = and_(private, MaterialChunk.owner_id == teacher_id)
        access = or_(access, private)
    publication_filter = active_publication()
    if publication_ids is not None:
        publication_filter = and_(publication_filter, publications.c.id.in_(publication_ids))
    conditions = [access, exists(select(1).select_from(publications).where(publication_filter)
                                 .correlate(MaterialChunk))]
    if subject:
        conditions.append(MaterialChunk.subject == subject.strip().upper())
    if material_ids:
        conditions.append(MaterialChunk.material_id.in_(material_ids))
    return conditions

class TopicRepository:
    async def publication_ids(self, teacher_id=None, subject=None, material_ids=None, *, student_id=None):
        async with mysql_manager.session_factory() as db:
            result = await db.scalars(select(publications.c.id).distinct()
                .select_from(publications).join(MaterialChunk, active_publication())
                .where(*chunk_scope(teacher_id, subject, material_ids, student_id)))
            return list(result)

    async def safe_summary(self, topic_id, teacher_id=None, subject=None, material_ids=None, *, student_id=None, publication_ids=None):
        """A generated summary can combine private chunks; expose it only if all are in scope."""
        if not topic_id:
            return None
        async with mysql_manager.session_factory() as db:
            base = select(func.count()).select_from(TopicChunk).join(
                MaterialChunk, MaterialChunk.id == TopicChunk.chunk_id).where(TopicChunk.topic_id == topic_id)
            total = await db.scalar(base)
            visible = await db.scalar(base.where(*chunk_scope(teacher_id, subject, material_ids, student_id, publication_ids)))
            if not total or total != visible:
                return None
            topic = await db.get(Topic, topic_id)
            # Ingested topics are deterministic shared identities. Their evidence is
            # delivered as published chunks, avoiding stale cross-publication summaries.
            return topic.summary if topic and not any(
                str(code).startswith('INGESTION_') for code in (topic.concepts_included or [])
            ) else None

    async def for_hits(self, hits, teacher_id=None, subject=None, material_ids=None, *, student_id=None, publication_ids=None):
        if not hits:
            return []
        async with mysql_manager.session_factory() as db:
            rows = (await db.execute(select(Topic, TopicChunk.chunk_id).join(
                TopicChunk, TopicChunk.topic_id == Topic.id).join(
                MaterialChunk, MaterialChunk.id == TopicChunk.chunk_id).where(
                TopicChunk.chunk_id.in_(hits[:100]), *chunk_scope(teacher_id, subject, material_ids, student_id, publication_ids)))).all()
            return [{'id': t.id, 'name': t.name, 'concepts': t.concepts_included or [],
                     'chunk_id': cid} for t, cid in rows]

    async def chunks(self, ids=None, topic_id=None, teacher_id=None, subject=None,
                     material_ids=None, limit=50, *, student_id=None, publication_ids=None):
        stmt = select(MaterialChunk).where(*chunk_scope(teacher_id, subject, material_ids, student_id, publication_ids))
        if ids is not None:
            if not ids:
                return []
            stmt = stmt.where(MaterialChunk.id.in_(ids[:100]))
        if topic_id:
            stmt = stmt.join(TopicChunk, TopicChunk.chunk_id == MaterialChunk.id).where(TopicChunk.topic_id == topic_id)
        async with mysql_manager.session_factory() as db:
            rows = (await db.execute(stmt.order_by(MaterialChunk.chunk_index).limit(limit))).scalars().all()
            return [{'id': r.id, 'content': r.content, 'codes': r.canonical_codes or [],
                     'scope': r.scope.value, 'subject': r.subject,
                     'version': str(r.updated_at)} for r in rows]

    async def progress(self, user_id):
        from app.model.mysql.tutoring import ConceptProgress
        async with mysql_manager.session_factory() as db:
            rows = (await db.execute(select(ConceptProgress).where(ConceptProgress.user_id == user_id)
                                     .order_by(ConceptProgress.updated_at.desc()).limit(200))).scalars().all()
            return [{'canonical_code': r.canonical_code, 'mastery_level': r.mastery_level,
                     'status': r.mastery_status, 'objective_progress': r.objective_progress,
                     'assessment_count': r.assessment_count,
                     'last_assessed_at': r.last_assessed_at} for r in rows]
