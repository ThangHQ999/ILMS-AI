from contextlib import asynccontextmanager
import json
import sys
from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import create_engine, text

from app.schema.knowledge_graph import ConceptCatalogRequest
from app.service.ingestion.publication.records import ingested_canonical_code
from app.service.knowledge_graph.concept_catalog import load_concept_catalog


class ConceptCatalogTest(IsolatedAsyncioTestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://')
        self.addCleanup(self.engine.dispose)
        self.course = UUID(int=1)
        self.other_course = UUID(int=2)
        self.chapter = UUID(int=3)
        self.lesson = UUID(int=4)
        self.owner = UUID(int=5)

        with self.engine.begin() as db:
            for statement in (
                'CREATE TABLE courses(id BLOB, deleted_at TEXT)',
                'CREATE TABLE chapters(id BLOB, course_id BLOB, deleted_at TEXT)',
                'CREATE TABLE lessons(id BLOB, chapter_id BLOB, deleted_at TEXT)',
                'CREATE TABLE materials(id BLOB, course_id BLOB, lesson_id BLOB)',
                '''CREATE TABLE material_publications(id BLOB, material_id BLOB,
                    material_version_id BLOB, job_id BLOB, draft_id BLOB,
                    status TEXT, is_current INT, published_at TEXT)''',
                '''CREATE TABLE knowledge_graph_drafts(id BLOB, job_id BLOB, graph_payload TEXT,
                    review_status TEXT, reviewed_payload_hash TEXT, payload_hash TEXT)''',
                '''CREATE TABLE material_chunks(id BLOB, material_version_id BLOB, chunk_index INT,
                    owner_id BLOB, subject TEXT, scope TEXT)''',
            ):
                db.exec_driver_sql(statement)
            db.exec_driver_sql('INSERT INTO courses VALUES (?, NULL), (?, NULL)',
                               (self.course.bytes, self.other_course.bytes))
            db.exec_driver_sql('INSERT INTO chapters VALUES (?, ?, NULL)', (self.chapter.bytes, self.course.bytes))
            db.exec_driver_sql('INSERT INTO lessons VALUES (?, ?, NULL)', (self.lesson.bytes, self.chapter.bytes))

        @asynccontextmanager
        async def session_factory():
            with self.engine.connect() as db:
                yield SimpleNamespace(execute=AsyncMock(side_effect=db.execute))

        db_module = SimpleNamespace(mysql_manager=SimpleNamespace(session_factory=session_factory))
        patcher = patch.dict(sys.modules, {'app.db.mysql': db_module})
        patcher.start()
        self.addCleanup(patcher.stop)

    def store_publication(self, number, graph, course=None, lesson=None,
                          status='PUBLISHED', reviewed_hash='current', chunk_scope=None):
        publication = UUID(int=number)
        with self.engine.begin() as db:
            db.execute(text('INSERT INTO materials VALUES (:id, :course, :lesson)'), {
                'id': publication.bytes,
                'course': course.bytes if course else None,
                'lesson': lesson.bytes if lesson else None,
            })
            db.exec_driver_sql('INSERT INTO knowledge_graph_drafts VALUES (?, ?, ?, ?, ?, ?)', (
                publication.bytes, publication.bytes, json.dumps(graph), 'APPROVED', reviewed_hash, 'current',
            ))
            db.exec_driver_sql('INSERT INTO material_publications VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (
                publication.bytes, publication.bytes, publication.bytes, publication.bytes, publication.bytes,
                status, 1 if status == 'PUBLISHED' else None, f'2026-11-{number - 10:02d}',
            ))
            if chunk_scope:
                db.exec_driver_sql('INSERT INTO material_chunks VALUES (?, ?, 0, ?, ?, ?)', (
                    publication.bytes, publication.bytes, self.owner.bytes, ' algebra ', chunk_scope,
                ))
        return publication

    def request(self, *ids):
        return ConceptCatalogRequest(courseId=self.course, publicationIds=list(ids))

    async def test_projects_sorted_codes_newest_label_and_exact_legacy_identity(self):
        older = self.store_publication(21, {'entities': [
            {'id': 'quiz-independent-node-id', 'name': 'Old label', 'canonical_code': 'Z_CODE'},
            {'id': 'internal-id', 'name': '  Số chính phương  '},
        ]}, lesson=self.lesson, chunk_scope='TEACHER')
        newer = self.store_publication(22, {'nodes': [
            {'id': 'display-node', 'canonicalCode': 'A_CODE', 'label': 'First'},
            {'id': 'different-node-id', 'canonicalCode': 'Z_CODE', 'label': 'New label'},
            {'id': 'has-no-canonical-code', 'label': 'No canonical identity'},
            {'type': 'CONCEPT', 'code': 'B_OLD_CODE', 'name': 'Saved concept'},
            {'kind': 'DEFINITION', 'id': 'definition', 'canonicalCode': 'NOT_A_CONCEPT'},
        ]}, course=self.course, lesson=self.lesson)
        result = await load_concept_catalog(self.request(older, newer, older))
        legacy = ingested_canonical_code(str(self.owner), 'ALGEBRA', 'TEACHER', 'Số chính phương')
        self.assertEqual(result.model_dump(mode='json'), {
            'courseId': str(self.course),
            'concepts': [
                {'canonicalCode': 'A_CODE', 'label': 'First'},
                {'canonicalCode': 'B_OLD_CODE', 'label': 'Saved concept'},
                {'canonicalCode': legacy, 'label': 'Số chính phương'},
                {'canonicalCode': 'Z_CODE', 'label': 'New label'},
            ],
        })

    async def test_rejects_entire_batch_if_a_publication_has_wrong_course_or_unapproved_payload(self):
        expected = self.store_publication(23, {'entities': []}, course=self.course)
        other_course = self.store_publication(24, {'entities': []}, course=self.other_course)
        mismatched_links = self.store_publication(25, {'entities': []}, course=self.other_course, lesson=self.lesson)
        retired = self.store_publication(26, {'entities': []}, course=self.course, status='SUPERSEDED')
        changed_after_review = self.store_publication(27, {'entities': []}, course=self.course, reviewed_hash='old')
        for excluded in (other_course, mismatched_links, retired, changed_after_review, UUID(int=12345)):
            with self.subTest(publication=excluded):
                self.assertIsNone(await load_concept_catalog(self.request(expected, excluded)))

    async def test_unlinked_and_deleted_source_fail_closed(self):
        from_lesson = self.store_publication(28, {'entities': []}, lesson=self.lesson)
        missing_course = self.store_publication(29, {'entities': []})
        self.assertIsNone(await load_concept_catalog(self.request(missing_course)))
        with self.engine.begin() as db:
            db.exec_driver_sql("UPDATE lessons SET deleted_at = '2026-11-25' WHERE id = ?", (self.lesson.bytes,))
        self.assertIsNone(await load_concept_catalog(self.request(from_lesson)))

    async def test_empty_selection_and_request_limits(self):
        result = await load_concept_catalog(self.request())
        self.assertEqual(result.concepts, [])
        with self.assertRaises(ValidationError):
            self.request(*(UUID(int=n) for n in range(101)))
