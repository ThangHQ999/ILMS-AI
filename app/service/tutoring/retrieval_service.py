import logging
from app.core.config import settings
from app.repository.mysql.topic_repo import TopicRepository
from app.repository.neo4j.tutoring_repo import TutoringGraphRepository, strings
from app.repository.chroma.entity_vector_repo import EntityVectorRepository, embedding_identity
from app.schema.tutoring_contracts import KnowledgeBundle, SourceRef, Criterion, RubricSnapshot
from app.service.tutoring.context_cache import knowledge_cache
from app.service.tutoring.publication_retrieval import retrieve_published
from app.service.tutoring.topic_context_service import TopicContextService

logger = logging.getLogger(__name__)


class RetrievalService:
    def __init__(self, llm, vector):
        self.llm, self.vector = llm, vector
        self.topics, self.graph = TopicRepository(), TutoringGraphRepository()
        self.entities = EntityVectorRepository()

    async def retrieve(self, intent, state, teacher=None, subject=None, material_ids=None,
                       forced_code=None, exercise_id=None, bypass_cache=False, notify=None, student_id=None):
        continuation = (not intent.explicit_switch and intent.intent in {
            'ANSWER_PENDING', 'REQUEST_HINT', 'EXPRESS_CONFUSION', 'REQUEST_EXAMPLE',
            'REQUEST_DIAGRAM', 'REQUEST_EXERCISE', 'CLOSE_DISCUSSION'})
        code = forced_code or (state.canonical_code if continuation else None)
        query = intent.standalone_query or code or ''
        access = dict(teacher_id=teacher, subject=subject, material_ids=material_ids, student_id=student_id)
        publication_ids = sorted(await self.topics.publication_ids(**access))
        access['publication_ids'] = publication_ids

        async def entity_for(candidate_code):
            published = await self.graph.published_entities(publication_ids, code=candidate_code)
            return published[0] if published else await self.graph.entity(candidate_code)

        key = (tuple(publication_ids), code, query if not continuation else '', state.topic_id, student_id, teacher, subject,
               tuple(sorted(material_ids or [])), exercise_id, embedding_identity())
        cached = knowledge_cache.get(key) if not bypass_cache else None
        if cached:
            return cached
        bundle = KnowledgeBundle(canonical_code=code)
        candidates = []
        try:
            if code:
                entity = await entity_for(code)
                candidates = [entity] if entity else []
            else:
                candidates = await self.graph.published_entities(publication_ids, words=intent.mentions)
                candidates.extend(await self.graph.entities(intent.mentions, subject))
        except Exception:
            logger.warning('Socratic entity lookup unavailable', exc_info=True)
            bundle.warnings.append('GRAPH_UNAVAILABLE')
        hits = []
        embedding = None
        # Continuing a known concept first uses topic chunks; fetch semantic results if needed.
        if continuation and state.topic_id:
            rows = await self.topics.chunks(topic_id=state.topic_id, **access, limit=30)
            hits = [r for r in rows if not code or code in r['codes']][:settings.SOCRATIC_RAG_TOP_K_CHUNKS]
        if not hits and publication_ids and query:
            try:
                embedding = (await self.llm.embed_texts([query], provider=settings.EMBEDDING_PROVIDER, allow_fallback=False))[0]
                hits, published_entities = await retrieve_published(
                    self.topics, self.graph, embedding, publication_ids, access,
                    resolve_entities=not candidates,
                )
                candidates.extend(published_entities)
            except Exception:
                logger.warning('Published vector lookup unavailable', exc_info=True)
                bundle.warnings.append('PUBLICATION_INDEX_UNAVAILABLE')
        if not hits:
            try:
                metric = (self.vector._collection.metadata or {}).get('hnsw:space', 'l2')
                if metric != 'cosine':
                    raise ValueError('Socratic chunk retrieval requires a cosine collection')
                if (self.vector._collection.metadata or {}).get('embedding_identity') != embedding_identity():
                    raise ValueError(
                        f'Collection {settings.CHROMA_COLLECTION_NAME!r}: embedding_identity='
                        f'{(self.vector._collection.metadata or {}).get("embedding_identity")!r}, '
                        f'expected={embedding_identity()!r}. Seed a NEW versioned collection with '
                        'python -m app.seed_tutoring --target chunks, then restart backend.')
                if embedding is None:
                    embedding = (await self.llm.embed_texts([query], provider=settings.EMBEDDING_PROVIDER,
                                                          allow_fallback=False))[0]
                vector_hits = await self.vector.similarity_search(query_embedding=embedding,
                    top_k=settings.SOCRATIC_RETRIEVAL_K, subject=subject,
                    teacher_id=teacher, material_ids=material_ids)
                ids = [h.chunk_id for h in vector_hits if h.distance is not None
                       and 1 - h.distance >= settings.SOCRATIC_MIN_SIMILARITY]
                rows = await self.topics.chunks(ids=ids, teacher_id=teacher,
                    subject=subject, material_ids=material_ids, limit=100)
                by_id = {r['id']: r for r in rows}
                hits = [by_id[cid] for cid in ids if cid in by_id]
            except Exception:
                logger.warning('Socratic semantic chunk retrieval unavailable', exc_info=True)
                bundle.warnings.append('VECTOR_UNAVAILABLE')
        if not candidates and embedding is not None:
            try:
                for entity in await self.entities.search(embedding, subject):
                    resolved = await entity_for(entity['canonical_code'])
                    if resolved:
                        candidates.append(resolved)
            except Exception:
                logger.warning('Socratic entity vector index unavailable', exc_info=True)
                bundle.warnings.append('ENTITY_INDEX_UNAVAILABLE')
        if not candidates:
            for hit in hits[:4]:
                for candidate_code in hit['codes'][:4]:
                    try:
                        entity = await entity_for(candidate_code)
                        if entity and entity not in candidates:
                            candidates.append(entity)
                    except Exception:
                        break
        bundle.candidates = candidates[:settings.SOCRATIC_GRAPH_NODES]
        exact = [e for e in candidates if any(
            m.casefold() in {str(e.get('name', '')).casefold(), str(e['canonical_code']).casefold()}
            for m in intent.mentions)]
        if not code:
            if len(exact) == 1:
                code = exact[0]['canonical_code']
            elif intent.intent == 'COMPARE' and len(exact) >= 2:
                # Both entities were explicitly named; keep one focus, retrieve both definitions.
                code = next((e['canonical_code'] for m in intent.mentions for e in exact
                             if m.casefold() in {e['name'].casefold(), e['canonical_code'].casefold()}), None)
            elif len(candidates) == 1:
                code = candidates[0]['canonical_code']
            elif state.canonical_code and not intent.explicit_switch:
                code = state.canonical_code
            else:
                bundle.warnings.append('AMBIGUOUS_CONCEPT')
        bundle.canonical_code = code
        bundle.entity = next((e for e in candidates if e.get('canonical_code') == code), {})
        ids = [r['id'] for r in hits]
        topic_rows = await self.topics.for_hits(ids, **access)
        bundle.topic_id, bundle.topic_name = TopicContextService().choose(
            topic_rows, ids, code, state.topic_id, intent.explicit_switch)
        if continuation and not bundle.topic_id:
            bundle.topic_id = state.topic_id
        for hit in hits[:settings.SOCRATIC_RAG_TOP_K_CHUNKS]:
            bundle.sources.append(SourceRef(id=hit['id'], kind='CHUNK', text=hit['content'],
                scope=hit['scope'], version=hit['version']))
        summary = await self.topics.safe_summary(bundle.topic_id, **access)
        if not summary and publication_ids and bundle.topic_id:
            try:
                summary = await self.graph.published_topic_summary(publication_ids, bundle.topic_id)
            except Exception:
                bundle.warnings.append('TOPIC_SUMMARY_UNAVAILABLE')
        if summary:
            bundle.sources.append(SourceRef(id=bundle.topic_id, kind='TOPIC_SUMMARY', text=summary))
        if code:
            try:
                if notify:
                    await notify('connecting_concepts', 'Đang đối chiếu định nghĩa và các thực thể tri thức liên quan…')
                if not bundle.entity:
                    bundle.entity = await entity_for(code) or {}
                if bundle.entity.get('description'):
                    bundle.sources.append(SourceRef(id=code, kind='ENTITY', text=bundle.entity['description'], canonical_code=code))
                satellites = await self.graph.published_satellites(publication_ids, code)
                satellites.extend(await self.graph.satellites(code, teacher))
                for row in satellites:
                    node = row['node']
                    text = {k: node[k] for k in ['content', 'conditions', 'exceptions', 'title',
                        'explanation', 'hypothesis', 'evidence', 'conclusion', 'name', 'description'] if node.get(k)}
                    if 'Process' in row['labels']:
                        text['steps'] = [step for step in row['steps'] if step['action']]
                    import json
                    bundle.sources.append(SourceRef(id=str(node['id']), kind=row['labels'][0],
                        text=json.dumps(text, ensure_ascii=False, default=str), canonical_code=code,
                        scope=node.get('scope', 'GLOBAL'), version=str(node.get('updated_at', ''))))
                bundle.relations = await self.graph.published_relations(publication_ids, code)
                bundle.relations.extend(await self.graph.relations(code, teacher))
                if intent.intent == 'COMPARE':
                    for compared in [e for e in exact if e['canonical_code'] != code][:2]:
                        compared_rows = await self.graph.published_satellites(publication_ids, compared['canonical_code'])
                        compared_rows.extend(await self.graph.satellites(compared['canonical_code'], teacher))
                        for row in compared_rows:
                            node = row['node']
                            if 'Definition' in row['labels']:
                                bundle.sources.append(SourceRef(id=node['id'], kind='Definition',
                                    text=node.get('content', ''), canonical_code=compared['canonical_code'],
                                    scope=node.get('scope', 'GLOBAL')))
                if intent.intent in {'ASK_WHY', 'COMPARE'}:
                    allowed = {'CONTRASTS_WITH'} if intent.intent == 'COMPARE' else {'REQUIRES', 'DEPENDS_ON'}
                    for relation in [r for r in bundle.relations if r['label'] in allowed][:2]:
                        target_rows = await self.graph.published_satellites(publication_ids, relation['target'])
                        target_rows.extend(await self.graph.satellites(relation['target'], teacher))
                        for row in target_rows:
                            node = row['node']
                            if 'Definition' in row['labels']:
                                bundle.sources.append(SourceRef(id=node['id'], kind='Definition',
                                    text=node.get('content', ''), canonical_code=relation['target'], scope=node.get('scope','GLOBAL')))
                raw = await self.graph.rubric(code, teacher)
                if raw:
                    r = raw['rubric']
                    criteria = []
                    for c in raw['criteria']:
                        if c and c.get('expected_evidence'):
                            criteria.append(Criterion(code=c.get('criterion_code', c['id']),
                                objective=c.get('objective_code', 'MEANING'), description=c.get('description', ''),
                                expected_evidence=c['expected_evidence'], acceptable_variations=strings(c.get('acceptable_variations')),
                                misconception_codes=strings(c.get('misconception_codes')),
                                source_ids=strings(c.get('source_chunk_ids'))))
                    bundle.rubric = RubricSnapshot(id=r['id'], version=r.get('version'),
                        origin=r.get('origin', 'AUTHORED'), review_state=r.get('status', 'UNKNOWN'), criteria=criteria[:8])
                if notify:
                    await notify('connecting_concepts', 'Đã hoàn tất bước đối chiếu đồ thị tri thức.', 'completed')
            except Exception:
                logger.warning('Socratic graph context incomplete', exc_info=True)
                bundle.warnings.append('GRAPH_CONTEXT_INCOMPLETE')
                if notify:
                    await notify('connecting_concepts', 'Chưa lấy đủ ngữ cảnh đồ thị.', 'failed')
        if exercise_id or (code and intent.intent == 'REQUEST_EXERCISE'):
            try:
                bundle.exercise = await self.graph.published_exercise(publication_ids, exercise_id, code)
                if not bundle.exercise:
                    bundle.exercise = await self.graph.exercise(code, exercise_id, teacher)
            except Exception:
                bundle.warnings.append('EXERCISE_UNAVAILABLE')
        # Keep whole source records while bounding persisted snapshots and prompts.
        remaining, bounded, seen = settings.SOCRATIC_CONTEXT_CHARS, [], set()
        for source in bundle.sources:
            if source.id not in seen and len(source.text) <= remaining:
                bounded.append(source)
                remaining -= len(source.text)
                seen.add(source.id)
        bundle.sources = bounded
        knowledge_cache.put(key, bundle)
        return bundle
