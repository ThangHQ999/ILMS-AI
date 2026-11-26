"""Short MySQL transactions around long-running retrieval/LLM work."""
import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from app.core.config import settings
from app.db.mysql import mysql_manager
from app.model.mysql.socratic_chat_session import SocraticChatSession
from app.model.mysql.socratic_chat_message import SocraticChatMessage
from app.model.mysql.student_misconception import StudentMisconception
from app.model.mysql.tutoring import LearningState, TurnEvaluation, ConceptProgress
from app.schema.tutoring_contracts import LearningSnapshot, PendingQuestion, EvaluationResult
from app.service.tutoring.progress_service import ProgressService


class TurnError(Exception):
    def __init__(self, code: str, message: str, *, recoverable: bool = True):
        self.code, self.message = code, message
        self.recoverable = recoverable
        super().__init__(message)


@dataclass
class TurnReceipt:
    session_id: str
    turn_id: str
    user_message_id: str
    assistant_message_id: str
    owner: str
    state: LearningSnapshot
    title: str = ''
    subject: str | None = None
    teacher_id: str | None = None
    history: list[dict[str, str]] = field(default_factory=list)
    replay: dict[str, Any] | None = None


def snapshot(row: LearningState) -> LearningSnapshot:
    context = dict(row.assessment_context or {})
    pending = context.get('pending') if row.pending_question_message_id else None
    return LearningSnapshot(
        version=row.state_version, topic_id=row.active_topic_id,
        canonical_code=row.active_canonical_code, mode=row.learning_mode,
        objective=row.active_objective,
        pending=PendingQuestion.model_validate(pending) if pending else None,
        hint_level=row.hint_level, failed_attempts=row.failed_attempts,
        strategy=row.last_strategy, return_stack=row.return_stack or [],
        summary=row.conversation_summary or '', process_id=row.active_process_id,
        exercise_id=row.active_exercise_id, step_id=row.active_step_id,
        step_number=context.get('step_number', 1), completed=context.get('completed', False),
        context=context,
    )


class TurnCoordinator:
    def __init__(self, factory=None):
        self._factory = factory

    @property
    def factory(self):
        return self._factory or mysql_manager.session_factory

    async def accept(self, req) -> TurnReceipt:
        # Deterministic first-session ID makes retry stable when caller supplies request ID.
        turn_id = req.client_request_id or str(uuid.uuid4())
        session_id = req.session_id or str(uuid.uuid5(uuid.NAMESPACE_URL, f'ilms:{req.student_id}:{turn_id}'))
        data = req.model_dump(mode='json', exclude={'protocol_version', 'expected_state_version'})
        fingerprint = hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        for attempt in range(2):
            try:
                return await self._accept(req, session_id, turn_id, fingerprint)
            except IntegrityError as exc:
                args = getattr(exc.orig, 'args', ())
                errno = args[0] if args else None
                if errno == 1452:
                    if 'fk_socratic_chat_sessions_student' in str(exc.orig):
                        raise TurnError('STUDENT_NOT_FOUND',
                            'Không tìm thấy học sinh theo student_id. Hãy dùng ID người dùng đã có trong hệ thống.',
                            recoverable=False) from exc
                    raise TurnError('INVALID_REFERENCE',
                        'Dữ liệu tham chiếu không tồn tại. Hãy kiểm tra các ID gửi trong yêu cầu.',
                        recoverable=False) from exc
                # Only duplicate-key races may succeed after another transaction commits.
                if errno != 1062:
                    raise
                if attempt:
                    raise TurnError('TURN_CONFLICT', 'Phiên đang được cập nhật, hãy thử lại cùng mã yêu cầu.') from exc
        raise AssertionError('unreachable')

    async def _accept(self, req, session_id, turn_id, fingerprint):
        async with self.factory() as db, db.begin():
            session = (await db.execute(select(SocraticChatSession).where(
                SocraticChatSession.id == session_id).with_for_update())).scalar_one_or_none()
            if session is None:
                # users belongs to the identity service and has no ORM model here.
                # Bind the same UUID bytes as BinaryUUID; never create placeholder users.
                student = await db.scalar(text('SELECT id FROM users WHERE id = :student_id'),
                    {'student_id': uuid.UUID(str(req.student_id)).bytes})
                if student is None:
                    raise TurnError('STUDENT_NOT_FOUND',
                        'Không tìm thấy học sinh theo student_id. Hãy dùng ID người dùng đã có trong hệ thống.',
                        recoverable=False)
                session = SocraticChatSession(id=session_id, student_id=req.student_id,
                    teacher_id=req.teacher_id, subject=req.subject, title=req.message.strip()[:60],
                    current_step_number=1, is_completed=False, stuck_count=0)
                db.add(session)
                await db.flush()
            if session.student_id != req.student_id:
                raise TurnError('SESSION_NOT_FOUND', 'Không tìm thấy phiên hội thoại của em.')
            row = await db.get(LearningState, session_id)
            if row is None:
                row = LearningState(session_id=session_id,
                    active_canonical_code=session.active_canonical_code,
                    active_process_id=session.active_process_id,
                    active_exercise_id=session.active_exercise_id,
                    learning_mode='EXERCISE' if session.active_exercise_id else 'CONCEPT',
                    assessment_context={'step_number': session.current_step_number,
                                        'completed': session.is_completed},
                    hint_level=0, failed_attempts=session.stuck_count or 0, state_version=0)
                db.add(row)
                await db.flush()
            existing = (await db.execute(select(SocraticChatMessage).where(
                SocraticChatMessage.session_id == session_id,
                SocraticChatMessage.turn_id == turn_id,
                SocraticChatMessage.role == 'USER'))).scalar_one_or_none()
            owner = str(uuid.uuid4())
            receipt = TurnReceipt(session_id, turn_id, existing.id if existing else str(uuid.uuid4()),
                str(uuid.uuid5(uuid.UUID(turn_id), 'assistant')), owner, snapshot(row),
                session.title, req.subject or session.subject, req.teacher_id or session.teacher_id)
            now = datetime.utcnow()
            if existing:
                if (existing.turn_metadata or {}).get('fingerprint') != fingerprint:
                    raise TurnError('REQUEST_ID_REUSED', 'Mã yêu cầu đã được dùng cho nội dung khác.')
                if existing.turn_status == 'COMPLETED':
                    reply = (await db.execute(select(SocraticChatMessage).where(
                        SocraticChatMessage.session_id == session_id,
                        SocraticChatMessage.turn_id == turn_id,
                        SocraticChatMessage.role == 'ASSISTANT'))).scalar_one()
                    receipt.replay = (reply.turn_metadata or {}).get('public', {}) | {
                        'full_content': reply.content, 'assistant_message_id': reply.id}
                    return receipt
            if row.active_turn_id and row.lease_expires_at and row.lease_expires_at > now:
                raise TurnError('TURN_IN_PROGRESS', 'Một lượt đang được xử lý. Hãy chờ hoặc lấy lại kết quả lượt đó.')
            if row.active_turn_id and row.active_turn_id != turn_id:
                abandoned = (await db.execute(select(SocraticChatMessage).where(
                    SocraticChatMessage.session_id == session_id,
                    SocraticChatMessage.turn_id == row.active_turn_id,
                    SocraticChatMessage.role == 'USER'))).scalar_one_or_none()
                if abandoned and abandoned.turn_status == 'PROCESSING':
                    abandoned.turn_status = 'FAILED'
            if req.expected_state_version is not None and req.expected_state_version != row.state_version:
                raise TurnError('STALE_STATE', 'Phiên đã thay đổi. Hãy tải lại trước khi gửi lượt mới.')
            if existing is None:
                existing = SocraticChatMessage(id=receipt.user_message_id, session_id=session_id,
                    role='USER', content=req.message, turn_id=turn_id,
                    turn_metadata={'fingerprint': fingerprint})
                db.add(existing)
            existing.turn_status = 'PROCESSING'
            existing.content_status = 'FINAL'
            row.active_turn_id, row.lease_token = turn_id, owner
            row.lease_expires_at = now + timedelta(seconds=settings.SOCRATIC_LEASE_SECONDS)
            history = (await db.execute(select(SocraticChatMessage).where(
                SocraticChatMessage.session_id == session_id,
                SocraticChatMessage.id != receipt.user_message_id,
                SocraticChatMessage.role.in_(['USER', 'ASSISTANT']),
                (SocraticChatMessage.turn_status.is_(None)) | (SocraticChatMessage.turn_status == 'COMPLETED'),
            ).order_by(SocraticChatMessage.created_at.desc(), SocraticChatMessage.id.desc())
                .limit(settings.SOCRATIC_MAX_HISTORY_MESSAGES))).scalars().all()
            receipt.history = [{'role': m.role.lower(), 'content': m.content} for m in reversed(history)]
            return receipt

    async def renew(self, receipt):
        async with self.factory() as db, db.begin():
            row = (await db.execute(select(LearningState).where(
                LearningState.session_id == receipt.session_id).with_for_update())).scalar_one()
            if row.lease_token != receipt.owner or row.active_turn_id != receipt.turn_id:
                raise TurnError('LEASE_LOST', 'Lượt này đã được thay thế, hãy tải lại phiên.')
            row.lease_expires_at = datetime.utcnow() + timedelta(seconds=settings.SOCRATIC_LEASE_SECONDS)

    async def fail(self, receipt):
        async with self.factory() as db, db.begin():
            row = (await db.execute(select(LearningState).where(
                LearningState.session_id == receipt.session_id).with_for_update())).scalar_one_or_none()
            if row and row.lease_token == receipt.owner:
                row.active_turn_id = row.lease_token = row.lease_expires_at = None
                message = await db.get(SocraticChatMessage, receipt.user_message_id)
                if message:
                    message.turn_status = 'FAILED'

    async def learner(self, user_id, code):
        if not code:
            return {}, []
        async with self.factory() as db:
            progress = (await db.execute(select(ConceptProgress).where(
                ConceptProgress.user_id == user_id, ConceptProgress.canonical_code == code))).scalar_one_or_none()
            misconceptions = (await db.execute(select(StudentMisconception).where(
                StudentMisconception.student_id == user_id, StudentMisconception.canonical_code == code,
                StudentMisconception.misconception_status.in_(("SUSPECTED", "CONFIRMED"))).order_by(StudentMisconception.created_at.desc()).limit(3))).scalars().all()
            return (progress.objective_progress or {} if progress else {}), [
                {'code': m.misconception_code, 'note': m.misconception_summary} for m in misconceptions]

    async def finalize(self, receipt, user_id, next_state, content, public,
                       evaluation=None, pending=None, action=None):
        async with self.factory() as db, db.begin():
            # Session lock order is the same as accept, followed by learning state.
            session = (await db.execute(select(SocraticChatSession).where(
                SocraticChatSession.id == receipt.session_id).with_for_update())).scalar_one()
            row = (await db.execute(select(LearningState).where(
                LearningState.session_id == receipt.session_id).with_for_update())).scalar_one()
            if (row.lease_token != receipt.owner or row.active_turn_id != receipt.turn_id
                    or row.state_version != receipt.state.version or not row.lease_expires_at
                    or row.lease_expires_at <= datetime.utcnow()):
                raise TurnError('STALE_STATE', 'Trạng thái đã đổi, phản hồi này chưa được lưu.')
            public = dict(public, state_version=row.state_version + 1)
            answer = SocraticChatMessage(id=receipt.assistant_message_id, session_id=receipt.session_id,
                turn_id=receipt.turn_id, role='ASSISTANT', content=content, turn_status='COMPLETED',
                content_status='FINAL', turn_metadata={'public': public},
                referenced_chunk_ids=public.get('referenced_chunk_ids', []),
                referenced_node_ids=public.get('referenced_node_ids', []),
                step_number_at_turn=public.get('step_number_at_turn'))
            db.add(answer)
            await db.flush()
            if evaluation and pending:
                evaluated = (await db.execute(select(TurnEvaluation).where(
                    TurnEvaluation.student_message_id == receipt.user_message_id,
                    TurnEvaluation.canonical_code == pending.canonical_code,
                    TurnEvaluation.objective_code == pending.objective))).scalar_one_or_none()
                if evaluated is None:
                    evaluated = TurnEvaluation(id=str(uuid.uuid4()), session_id=receipt.session_id,
                        student_message_id=receipt.user_message_id, question_message_id=pending.assistant_message_id,
                        canonical_code=pending.canonical_code, objective_code=pending.objective,
                        verdict=evaluation.verdict.value, assessment_origin=pending.rubric.origin,
                        rubric_id=pending.rubric.id, rubric_version=pending.rubric.version,
                        rubric_snapshot=pending.rubric.model_dump(mode='json'),
                        criteria_results=[r.model_dump() for r in evaluation.criteria_results],
                        evidence=evaluation.model_dump(mode='json'), hint_level_used=pending.hint_level_used,
                        feedback_action=action.kind if action else None,
                        evaluator_version='socratic-evaluator-1')
                    db.add(evaluated)
                    await db.flush()
                    await ProgressService().apply(db, user_id, evaluated, pending, evaluation)
                    await self._misconceptions(db, user_id, receipt, pending, evaluation, evaluated.id)
            row.active_topic_id, row.active_canonical_code = next_state.topic_id, next_state.canonical_code
            row.learning_mode, row.active_objective = next_state.mode, next_state.objective
            row.active_process_id, row.active_exercise_id, row.active_step_id = (
                next_state.process_id, next_state.exercise_id, next_state.step_id)
            row.pending_question_message_id = next_state.pending.assistant_message_id if next_state.pending else None
            row.hint_level, row.failed_attempts, row.last_strategy = (
                next_state.hint_level, next_state.failed_attempts, next_state.strategy)
            row.assessment_context = next_state.context | {
                'schema_version': 1, 'pending': next_state.pending.model_dump(mode='json') if next_state.pending else None,
                'step_number': next_state.step_number, 'completed': next_state.completed}
            row.return_stack, row.conversation_summary = next_state.return_stack, next_state.summary
            row.state_version += 1
            row.active_turn_id = row.lease_token = row.lease_expires_at = None
            # Read-only compatibility projection for existing sidebar/API consumers.
            session.active_canonical_code = next_state.canonical_code
            session.current_step_number = next_state.step_number
            session.is_completed = next_state.completed
            session.stuck_count = next_state.failed_attempts
            # Legacy columns are BinaryUUID; Socratic supports arbitrary graph property IDs.
            def legacy_uuid(value):
                try:
                    return str(uuid.UUID(value)) if value else None
                except (ValueError, TypeError, AttributeError):
                    return None
            session.active_process_id = legacy_uuid(next_state.process_id)
            session.active_exercise_id = legacy_uuid(next_state.exercise_id)
            session.updated_at = datetime.utcnow()
            session.teacher_id = receipt.teacher_id
            session.subject = receipt.subject
            user_message = await db.get(SocraticChatMessage, receipt.user_message_id)
            user_message.turn_status = 'COMPLETED'
            return row.state_version

    async def _misconceptions(self, db, user_id, receipt, pending, result, evaluation_id):
        allowed = {c for criterion in pending.rubric.criteria for c in criterion.misconception_codes}
        for code in set(result.misconception_codes) & allowed:
            if result.verdict.value != 'INCORRECT' or not result.misconception_note:
                continue
            item = (await db.execute(select(StudentMisconception).where(
                StudentMisconception.student_id == user_id,
                StudentMisconception.canonical_code == pending.canonical_code,
                StudentMisconception.misconception_code == code,
                StudentMisconception.misconception_status.in_(("SUSPECTED", "CONFIRMED")))
                .order_by(StudentMisconception.created_at.desc(), StudentMisconception.id.desc())
                .limit(1).with_for_update())).scalar_one_or_none()
            if item is None:
                db.add(StudentMisconception(id=str(uuid.uuid4()), student_id=user_id,
                    session_id=receipt.session_id, canonical_code=pending.canonical_code,
                    misconception_code=code, misconception_summary=result.misconception_note,
                    misconception_status='SUSPECTED', evidence={'detected_by': [evaluation_id]}))
            else:
                prior = (item.evidence or {}).get('detected_by', [])
                prior = prior if isinstance(prior, list) else [prior]
                item.evidence = (item.evidence or {}) | {'detected_by': [*prior, evaluation_id][-5:]}
                if item.misconception_status == 'CONFIRMED' or any(ref != evaluation_id for ref in prior):
                    item.misconception_status = 'CONFIRMED'
        if result.verdict.value == 'CORRECT' and pending.hint_level_used <= 1:
            for code in set(result.resolved_misconception_codes) & allowed:
                items = (await db.execute(select(StudentMisconception).where(
                    StudentMisconception.student_id == user_id,
                    StudentMisconception.canonical_code == pending.canonical_code,
                    StudentMisconception.misconception_code == code,
                    StudentMisconception.misconception_status.in_(("SUSPECTED", "CONFIRMED"))).with_for_update())).scalars().all()
                for item in items:
                    item.misconception_status = 'RESOLVED'
                    item.evidence = (item.evidence or {}) | {'resolved_by': evaluation_id}

    async def result(self, session_id, turn_id, student_id):
        async with self.factory() as db:
            owned = await db.scalar(select(SocraticChatSession.id).where(
                SocraticChatSession.id == session_id, SocraticChatSession.student_id == student_id))
            if not owned:
                raise TurnError('SESSION_NOT_FOUND', 'Không tìm thấy phiên hội thoại của em.')
            messages = (await db.execute(select(SocraticChatMessage).where(
                SocraticChatMessage.session_id == session_id, SocraticChatMessage.turn_id == turn_id))).scalars().all()
            reply = next((m for m in messages if m.role == 'ASSISTANT'), None)
            user = next((m for m in messages if m.role == 'USER'), None)
            if not user:
                raise TurnError('TURN_NOT_FOUND', 'Không tìm thấy lượt chat.')
            turn_status = user.turn_status
            if turn_status == 'PROCESSING':
                current = await db.get(LearningState, session_id)
                if (not current or current.active_turn_id != turn_id or not current.lease_expires_at
                        or current.lease_expires_at <= datetime.utcnow()):
                    turn_status = 'FAILED'
            return {'turn_id': turn_id, 'status': turn_status,
                    'result': ((reply.turn_metadata or {}).get('public', {}) | {'full_content': reply.content}) if reply else None}
