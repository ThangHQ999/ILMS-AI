"""Socratic read adapter for the graph supplied by ingestion; no writes/publication here."""
import json
from app.core.config import settings
from app.db.neo4j import neo4j_manager


VISIBLE = "(n.scope = 'GLOBAL' OR (n.scope = 'TEACHER' AND n.owner_id = $teacher))"


def strings(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, str) and value.startswith('['):
        try:
            return [str(v) for v in json.loads(value)]
        except (ValueError, TypeError):
            pass
    return [str(value)]


class TutoringGraphRepository:
    async def query(self, cypher, **params):
        async with neo4j_manager.driver.session(database=settings.NEO4J_DATABASE) as session:
            result = await session.run(cypher, params)
            return json.loads(json.dumps(await result.data(), default=str))

    async def published_entities(self, publication_ids, *, code=None, words=()):
        if not publication_ids or (not code and not words):
            return []
        rows = await self.query('''
            MATCH (e:IngestedKnowledge {node_kind:'KnowledgeEntitySnapshot'})
            WHERE e.publication_id IN $publications
              AND (($code IS NOT NULL AND e.canonical_code=$code)
                   OR ($code IS NULL AND any(word IN $words WHERE toLower(e.name)=toLower(word))))
            RETURN properties(e) AS entity ORDER BY e.id LIMIT $limit
        ''', publications=publication_ids, code=code, words=list(words)[:8],
            limit=settings.SOCRATIC_GRAPH_NODES)
        return list({row['entity']['canonical_code']: row['entity'] for row in rows}.values())

    async def published_satellites(self, publication_ids, code):
        if not publication_ids:
            return []
        return await self.query('''
            MATCH (e:IngestedKnowledge {canonical_code:$code})-[r:INGESTED_RELATION]->(n:IngestedKnowledge)
            WHERE e.publication_id IN $publications AND n.publication_id=e.publication_id
              AND n.node_kind IN ['Definition','Example','Argument','Process']
            OPTIONAL MATCH (n)-[:INGESTED_RELATION]->(s:IngestedKnowledge {node_kind:'ProcessStep'})
            WHERE s.publication_id=n.publication_id
            WITH n,s,r ORDER BY s.step_number
            RETURN [n.node_kind] AS labels, properties(n) AS node, r.kind AS relation,
                   collect({action:s.action, step_number:s.step_number}) AS steps
            LIMIT $limit
        ''', publications=publication_ids, code=code, limit=settings.SOCRATIC_GRAPH_NODES)

    async def published_topic_summary(self, publication_ids, topic_id):
        if not publication_ids or not topic_id:
            return None
        rows = await self.query('''
            MATCH (n:IngestedKnowledge {node_kind:'TopicSnapshot',topic_id:$topic})
            WHERE n.publication_id IN $publications AND n.description <> ''
            RETURN n.description AS summary ORDER BY n.id LIMIT 1
        ''', publications=publication_ids, topic=topic_id)
        return rows[0]['summary'] if rows else None

    async def published_relations(self, publication_ids, code):
        if not publication_ids:
            return []
        return await self.query('''
            MATCH (e:IngestedKnowledge {canonical_code:$code})-[r:INGESTED_RELATION]->(n:IngestedKnowledge)
            WHERE e.publication_id IN $publications AND n.publication_id=e.publication_id
              AND n.node_kind='KnowledgeEntitySnapshot' AND r.kind IN $edges
            RETURN r.kind AS label, n.canonical_code AS target, n.name AS name,
                   r.description AS description
            LIMIT $limit
        ''', publications=publication_ids, code=code, edges=settings.SOCRATIC_SEMANTIC_EDGES,
            limit=settings.SOCRATIC_GRAPH_NODES)

    async def published_exercise(self, publication_ids, exercise_id, code=None):
        if not publication_ids:
            return None
        rows = await self.query('''
            MATCH (n:IngestedKnowledge {node_kind:'Exercise'})
            WHERE n.publication_id IN $publications AND
              (($id IS NOT NULL AND n.id=$id) OR
               ($id IS NULL AND EXISTS {
                  MATCH (:IngestedKnowledge {canonical_code:$code})-[:INGESTED_RELATION {kind:'HAS_EXERCISE'}]->(n)
                }))
            WITH n ORDER BY n.id LIMIT 1
            OPTIONAL MATCH (n)-[:INGESTED_RELATION]->(s:IngestedKnowledge {node_kind:'ExerciseStep'})
            WHERE s.publication_id=n.publication_id
            WITH n,s ORDER BY s.step_number
            RETURN properties(n) AS exercise, collect(properties(s)) AS steps
        ''', publications=publication_ids, id=exercise_id, code=code)
        return rows[0] if rows else None

    async def entities(self, keywords, subject=None):
        words = [str(k).strip() for k in keywords if str(k).strip()][:8]
        if not words:
            return []
        return [r['entity'] for r in await self.query('''
            MATCH (ke:KnowledgeEntity)
            WHERE ($subject IS NULL OR ke.subject = $subject)
              AND any(k IN $words WHERE toLower(ke.canonical_code) = toLower(k)
                OR toLower(ke.name) CONTAINS toLower(k)
                OR any(a IN coalesce(ke.aliases, []) WHERE toLower(a) = toLower(k)))
            RETURN properties(ke) AS entity LIMIT $limit
        ''', subject=subject, words=words, limit=settings.SOCRATIC_GRAPH_NODES)
        ]

    async def entity(self, code):
        rows = await self.query('MATCH (ke:KnowledgeEntity {canonical_code:$code}) RETURN properties(ke) AS entity', code=code)
        return rows[0]['entity'] if rows else None

    async def satellites(self, code, teacher=None):
        # Relationship labels are parameterized values, not Cypher interpolated identifiers.
        return await self.query('''
            MATCH (ke:KnowledgeEntity {canonical_code:$code})-[r]->(n)
            WHERE type(r) IN $edges AND any(l IN labels(n) WHERE l IN $labels)
              AND ''' + VISIBLE + '''
            RETURN labels(n) AS labels, properties(n) AS node, type(r) AS relation
            ORDER BY CASE WHEN n.scope='TEACHER' THEN 0 ELSE 1 END
            LIMIT $limit
        ''', code=code, teacher=teacher, edges=settings.SOCRATIC_SATELLITE_EDGES,
            labels=['Definition', 'Example', 'Argument'], limit=settings.SOCRATIC_GRAPH_NODES)

    async def relations(self, code, teacher=None):
        return await self.query('''
            MATCH (ke:KnowledgeEntity {canonical_code:$code})-[r]->(n:KnowledgeEntity)
            WHERE type(r) IN $edges
              AND (r.scope='GLOBAL' OR (r.scope='TEACHER' AND r.owner_id=$teacher))
            RETURN type(r) AS label, n.canonical_code AS target, n.name AS name,
                   r.description AS description
            LIMIT $limit
        ''', code=code, teacher=teacher, edges=settings.SOCRATIC_SEMANTIC_EDGES,
            limit=settings.SOCRATIC_GRAPH_NODES)

    async def rubric(self, code, teacher=None):
        rows = await self.query('''
            MATCH (ke:KnowledgeEntity {canonical_code:$code})-[r]->(n:ConceptRubric)
            WHERE type(r)=$edge AND ''' + VISIBLE + ''' AND n.status IN $statuses
            WITH n ORDER BY CASE WHEN n.scope='TEACHER' THEN 0 ELSE 1 END, n.version DESC
            LIMIT 1
            OPTIONAL MATCH (n)-[c]->(criterion:ConceptCriterion) WHERE type(c)=$criterion_edge
            RETURN properties(n) AS rubric, collect(properties(criterion)) AS criteria
        ''', code=code, teacher=teacher, statuses=settings.SOCRATIC_RUBRIC_STATUSES,
            edge=settings.SOCRATIC_RUBRIC_EDGE, criterion_edge=settings.SOCRATIC_CRITERION_EDGE)
        return rows[0] if rows else None

    async def exercise(self, code=None, exercise_id=None, teacher=None):
        rows = await self.query('''
            MATCH (n:Exercise)
            WHERE ''' + VISIBLE + ''' AND
              (($id IS NOT NULL AND n.id=$id) OR
               ($id IS NULL AND EXISTS {
                  MATCH (:KnowledgeEntity {canonical_code:$code})-[r]->(n)
                  WHERE type(r)=$exercise_edge }))
            WITH n ORDER BY CASE WHEN n.scope='TEACHER' THEN 0 ELSE 1 END, n.id LIMIT 1
            OPTIONAL MATCH (s:ExerciseStep)
            WHERE s.exercise_id=n.id AND
              (s.scope='GLOBAL' OR (s.scope='TEACHER' AND s.owner_id=$teacher))
            WITH n,s ORDER BY s.step_number
            RETURN properties(n) AS exercise, collect(properties(s)) AS steps
        ''', code=code, id=exercise_id, teacher=teacher, exercise_edge=settings.SOCRATIC_EXERCISE_EDGE)
        return rows[0] if rows else None

    async def all_entities(self, after='', limit=100):
        rows = await self.query('''MATCH (ke:KnowledgeEntity) WHERE ke.canonical_code > $after
            RETURN properties(ke) AS entity ORDER BY ke.canonical_code LIMIT $limit''', after=after, limit=limit)
        return [r['entity'] for r in rows]
