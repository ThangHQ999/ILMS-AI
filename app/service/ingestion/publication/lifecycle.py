"""Publication compare-and-swap and audit inside the material transaction."""
import json

from sqlalchemy import text


class PublicationConflict(ValueError):
    pass


async def check_base(db, row, params):
    current = (await db.execute(text('''
        SELECT p.id,v.version_number FROM material_publications p
        JOIN material_versions v ON v.id=p.material_version_id
        WHERE p.material_id=:material AND p.is_current=1 AND p.status='PUBLISHED' FOR UPDATE
    '''), params)).mappings().first()
    value = (await db.execute(text('SELECT configuration FROM ingestion_jobs WHERE id=:job'), params)).scalar_one()
    config = json.loads(value) if isinstance(value, (str, bytes)) else value or {}
    if 'publication_generation' in config:
        generation = (await db.execute(text('''
            SELECT COALESCE(MAX(id),0) FROM knowledge_graph_events
            WHERE material_id=:material AND event_type IN ('PUBLISHED','WITHDRAWN')
        '''), params)).scalar_one()
        from uuid import UUID

        expected = config.get('expected_current_publication_id')
        actual = str(UUID(bytes=current['id'])) if current else None
        if actual != expected or generation != config['publication_generation']:
            raise PublicationConflict('The current publication changed after editing started')
    if not config.get('graph_edit') and current and current['version_number'] >= row['version_number']:
        raise PublicationConflict('A newer or equal source version is already current')


async def published_event(db, params):
    await db.execute(text('''
        INSERT INTO knowledge_graph_events(material_id,job_id,revision_id,publication_id,actor_id,event_type,metadata)
        VALUES(:material,:job,:draft,:id,:actor,'PUBLISHED',JSON_OBJECT())
    '''), params)
