"""Socratic orchestration. All long-running work is outside MySQL transactions."""
import asyncio
import json
import logging
import time
import uuid
import hashlib
from contextlib import suppress
from app.core.config import settings
from app.schema.tutoring_contracts import (
    IntentAnalysis, Criterion, RubricSnapshot, PendingQuestion, QuestionPlan, Verdict, KnowledgeBundle, SourceRef,
)
from app.service.tutoring.turn_coordinator import TurnCoordinator, TurnError
from app.service.tutoring.intent_service import IntentService
from app.service.tutoring.retrieval_service import RetrievalService
from app.service.tutoring.understanding_evaluator import UnderstandingEvaluator
from app.service.tutoring.pedagogical_policy import PedagogicalPolicy
from app.service.tutoring.learning_state_service import LearningStateService
from app.service.tutoring.rubric_service import RubricService
from app.service.tutoring.artifact_service import ArtifactService
from app.service.tutoring.response_generator import ResponseGenerator

logger = logging.getLogger(__name__)


class SocraticChatService:
    def __init__(self, llm, vector):
        self.llm = llm
        self.turns = TurnCoordinator()
        self.intent = IntentService(llm)
        self.retrieval = RetrievalService(llm, vector)
        self.evaluator = UnderstandingEvaluator(llm)
        self.policy = PedagogicalPolicy()
        self.states = LearningStateService()
        self.rubrics = RubricService(llm)
        self.artifacts = ArtifactService(llm)
        self.responses = ResponseGenerator(llm)

    async def stream_socratic_chat(self, req, preferred_provider=None):
        queue = asyncio.Queue(maxsize=64)
        receipt = None
        committed = False
        sequence = 0
        started = time.monotonic()
        partial_response = False

        async def emit(event, data):
            nonlocal sequence
            sequence += 1
            if req.protocol_version >= 2:
                data = dict(data, turn_id=receipt.turn_id if receipt else req.client_request_id,
                            sequence=sequence)
            if req.protocol_version == 1 and event in {'status', 'diagram_ready', 'exercise_ready'}:
                return
            await queue.put(f'event: {event}\ndata: {json.dumps(data, ensure_ascii=False, default=str)}\n\n')

        async def status(stage, text, state='running'):
            await emit('status', {'stage': stage, 'state': state, 'message': text})

        async def renew():
            while True:
                await asyncio.sleep(settings.SOCRATIC_LEASE_SECONDS / 3)
                await self.turns.renew(receipt)

        async def work():
            nonlocal receipt, committed
            receipt = await self.turns.accept(req)
            await emit('session_init', {'session_id': receipt.session_id, 'user_message_id': receipt.user_message_id,
                'assistant_message_id': receipt.assistant_message_id, 'title': receipt.title,
                'current_step_number': receipt.state.step_number,
                'step_progress': self.states.step_progress(receipt.state),
                'active_canonical_code': receipt.state.canonical_code})
            if receipt.replay is not None:
                await emit('done', dict(receipt.replay, session_id=receipt.session_id,
                                        replayed=True, content_status='FINAL',
                                        state_version=receipt.replay.get('state_version', receipt.state.version)))
                committed = True
                return
            # TaskGroup cancels the work immediately if lease renewal loses ownership.
            async with asyncio.TaskGroup() as group:
                keeper = group.create_task(renew())
                try:
                    await process()
                finally:
                    keeper.cancel()

        async def process():
            nonlocal committed, partial_response
            state = receipt.state
            provider = preferred_provider
            materials = req.material_ids if req.material_ids is not None else state.context.get('material_ids')
            scope_key = hashlib.sha256(json.dumps([receipt.teacher_id, receipt.subject,
                sorted(materials or [])], ensure_ascii=False).encode()).hexdigest()
            old_scope = state.context.get('access_scope_key')
            if old_scope and old_scope != scope_key:
                state = state.model_copy(deep=True)
                state.pending = None
                state.return_stack = []
                state.context = {}
                state.exercise_id = state.process_id = state.step_id = None
                state.mode = 'CONCEPT'
                receipt.state = state
                receipt.history = []
            await status('understanding_request', 'Đang xác định nội dung em muốn tìm hiểu…')
            intent = await self.intent.analyze(req, state, receipt.history, provider)
            await status('understanding_request', 'Đã xác định yêu cầu của lượt này.', 'completed')
            if intent.intent == 'CLOSE_DISCUSSION':
                bundle = KnowledgeBundle(
                    canonical_code=state.canonical_code, topic_id=state.topic_id)
            else:
                await status('retrieving_materials', 'Đang đối chiếu ngữ cảnh và học liệu liên quan…')
                bundle = await self.retrieval.retrieve(intent, state, receipt.teacher_id, receipt.subject,
                    materials, req.active_canonical_code,
                    req.active_exercise_id or state.exercise_id,
                    bypass_cache=intent.intent == 'CHALLENGE_TUTOR', notify=status, student_id=req.student_id)
                await status('retrieving_materials', 'Đã hoàn tất bước truy xuất học liệu.', 'completed')
            evaluation = None
            pending = state.pending
            if (intent.intent == 'ANSWER_PENDING' and intent.refers_to_pending and pending
                    and not intent.explicit_switch
                    and req.active_canonical_code in (None, pending.canonical_code)):
                # The answer is graded against the question's original snapshot, not a new retrieval guess.
                await status('evaluating_answer', 'Đang đối chiếu câu trả lời của em với câu hỏi vừa rồi…')
                evaluation = await self.evaluator.evaluate(req.message, pending, provider)
                await status('evaluating_answer', 'Đã hoàn tất bước đối chiếu câu trả lời.', 'completed')
            learner, misconceptions = await self.turns.learner(req.student_id, bundle.canonical_code)
            action = self.policy.decide(intent, evaluation, state, bundle, learner)
            next_state = self.states.start(state, bundle, action, evaluation)
            if action.kind == 'CLARIFY':
                next_state.context['awaiting_clarification'] = True
            if action.advance:
                action.objective = self.states.next_objective(state, bundle, learner)
                next_state.objective = action.objective
            # Targeted remediation only follows a verified prerequisite edge, after repeated evidence.
            if evaluation and evaluation.verdict == Verdict.INCORRECT and next_state.failed_attempts >= 2:
                foundations = {r['target'] for r in bundle.relations if r['label'] in {'REQUIRES', 'DEPENDS_ON'}}
                if evaluation.prerequisite_code in foundations and state.hint_level >= 2:
                    repair = self.states.push(state, evaluation.prerequisite_code)
                    if repair:
                        await status('connecting_concepts', 'Đang tìm phần kiến thức nền cần ôn lại…')
                        repair_bundle = await self.retrieval.retrieve(
                            IntentAnalysis(intent='ASK_DEFINITION', standalone_query=evaluation.prerequisite_code), repair,
                            receipt.teacher_id, receipt.subject, materials, evaluation.prerequisite_code, student_id=req.student_id)
                        if repair_bundle.sources:
                            next_state, bundle = repair, repair_bundle
                            next_state.topic_id = state.topic_id
                            action.kind, action.ask_question = 'REMEDIATE', True
                            action.support_scope = 'SINGLE_STEP'
                            action.directive = 'Ôn ngắn phần nền cần thiết, giải thích liên hệ rồi sẽ quay lại câu hỏi gốc.'
                            action.objective = 'MEANING'
            if (state.mode == 'REVIEW' and state.return_stack and evaluation
                    and evaluation.verdict == Verdict.CORRECT and pending and pending.hint_level_used <= 1):
                restored = self.states.pop(state)
                restored_bundle = await self.retrieval.retrieve(
                    IntentAnalysis(intent='REQUEST_HINT', standalone_query=restored.canonical_code or ''), restored,
                    receipt.teacher_id, receipt.subject, materials, restored.canonical_code,
                    restored.exercise_id, bypass_cache=True, student_id=req.student_id)
                if restored_bundle.sources:
                    bundle, next_state = restored_bundle, restored
                    action.kind, action.ask_question, action.preserve_pending = 'RETURN', False, True
                    action.directive = 'Kết nối phần nền vừa ôn với câu hỏi gốc; không bắt đầu lại từ đầu.'
            artifact_events = []
            public_artifacts = []
            question_plan = QuestionPlan()
            # A stored/generated exercise has a rubric for its exact question.
            wants_exercise = intent.intent == 'REQUEST_EXERCISE' or (
                req.active_exercise_id is not None and req.active_exercise_id != state.exercise_id)
            if wants_exercise and bundle.canonical_code and bundle.sources:
                await status('generating_exercise', 'Đang chuẩn bị bài tập phù hợp…')
                try:
                    stored = bundle.exercise or await self.retrieval.graph.exercise(
                        bundle.canonical_code, req.active_exercise_id, receipt.teacher_id)
                    if stored and stored.get('steps'):
                        next_state.mode = 'EXERCISE'
                        next_state.exercise_id = stored['exercise']['id']
                        next_state.process_id = stored['exercise'].get('process_id')
                        next_state.context['stored_exercise'] = stored
                        next_state.context.pop('generated_exercise', None)
                        next_state.step_id = None
                        next_state.completed = False
                        next_state.step_number = 1
                        exercise_public = {'artifact_id': stored['exercise']['id'], 'schema_version': 1,
                            'type': 'practice_exercise', 'title': stored['exercise'].get('title', ''),
                            'statement': stored['exercise'].get('content', ''), 'origin': 'KNOWLEDGE_GRAPH'}
                        public_artifacts.append(exercise_public)
                        artifact_events.append(('exercise_ready', exercise_public))
                    else:
                        await status('validating_exercise', 'Đang tạo và kiểm tra tính nhất quán của bài tập…')
                        public, draft = await self.artifacts.exercise(bundle, action.objective, provider)
                        next_state.mode = 'EXERCISE'
                        next_state.context['generated_exercise'] = draft.model_dump()
                        next_state.context.pop('stored_exercise', None)
                        next_state.completed = False
                        next_state.exercise_id = next_state.step_id = next_state.process_id = None
                        question_plan = QuestionPlan(question=draft.statement, objective=draft.objective, criteria=draft.criteria)
                        public_artifacts.append(public)
                        artifact_events.append(('exercise_ready', public))
                        await status('validating_exercise', 'Đã hoàn tất bước kiểm tra bằng AI.', 'completed')
                    await status('generating_exercise', 'Đã chuẩn bị bài tập.', 'completed')
                except Exception:
                    logger.warning('Exercise preparation failed', exc_info=True)
                    await status('generating_exercise', 'Chưa chuẩn bị được bài tập đủ tin cậy.', 'failed')
                    action.ask_question = False
                    action.directive = 'Nêu chưa tạo được bài đủ tin cậy; giải thích bằng nguồn sẵn có, không bịa đề.'
            stored = next_state.context.get('stored_exercise')
            completes_step = False
            if (next_state.mode == 'EXERCISE' and stored and not next_state.completed
                    and (wants_exercise or action.advance)):
                steps = sorted(stored['steps'], key=lambda s: s['step_number'])
                current_index = next((i for i,s in enumerate(steps) if s['id'] == next_state.step_id), 0)
                if action.advance and pending and pending.exercise_step_id and pending.completes_exercise_step:
                    current_index += 1
                if current_index >= len(steps):
                    next_state.completed = True
                    next_state.pending = None
                    action.ask_question = False
                    action.directive = 'Tóm tắt điều người học đã tự làm được; không coi là thành thạo toàn khái niệm.'
                else:
                    step = steps[current_index]
                    next_state.step_id, next_state.step_number = step['id'], step['step_number']
                    question_plan = QuestionPlan(question=step.get('socratic_question') or step['instruction'],
                        objective='APPLICATION', criteria=[Criterion(code=f"STEP_{step['id']}", objective='APPLICATION',
                            description=step['instruction'], expected_evidence=step['expected_outcome'],
                            source_ids=[s.id for s in bundle.sources])])
                    completes_step = True
            if (action.advance and pending and pending.completes_exercise_step
                    and state.mode == 'EXERCISE' and state.context.get('generated_exercise')
                    and not stored):
                next_state.completed, next_state.pending, action.ask_question = True, None, False
            elif (action.advance and pending and not pending.completes_exercise_step
                    and next_state.mode == 'EXERCISE' and next_state.context.get('generated_exercise')):
                draft = next_state.context['generated_exercise']
                question_plan = QuestionPlan(question=draft['statement'], objective=draft['objective'],
                    criteria=[Criterion.model_validate(c) for c in draft['criteria']])
                completes_step = True
            if intent.intent == 'REQUEST_DIAGRAM' and bundle.sources:
                await status('generating_diagram', 'Đang dựng sơ đồ 2D minh họa…')
                try:
                    diagram = await self.artifacts.diagram(bundle, req.message, provider)
                    artifact_events.append(('diagram_ready', diagram))
                    public_artifacts.append(diagram)
                    await status('generating_diagram', 'Đã chuẩn bị dữ liệu sơ đồ.', 'completed')
                except Exception:
                    logger.warning('Diagram generation failed', exc_info=True)
                    await status('generating_diagram', 'Chưa tạo được sơ đồ phù hợp; sẽ giải thích bằng lời.', 'failed')
            if not question_plan.question and action.ask_question:
                await status('preparing_explanation', 'Đang chuẩn bị gợi ý và câu hỏi phù hợp…')
                try:
                    question_plan = await self.rubrics.question(bundle, action, pending, provider,
                        learner_message=req.message, evaluation=evaluation)
                except Exception:
                    logger.warning('Question planning failed; no ungrounded pending question created', exc_info=True)
            if action.support_scope == 'SINGLE_STEP' and action.ask_question and not question_plan.question:
                # Do not replace a failed focused question with an unrestricted explanation.
                raise ValueError('A single-step guidance turn requires a grounded next question')
            if action.kind == 'RETURN' and next_state.pending:
                question_plan.question = next_state.pending.text
            if wants_exercise and question_plan.question and not stored:
                completes_step = True
            exercise_statement = ''
            if next_state.context.get('stored_exercise'):
                exercise_statement = next_state.context['stored_exercise']['exercise'].get('content', '')
            elif next_state.context.get('generated_exercise'):
                exercise_statement = next_state.context['generated_exercise']['statement']
            if exercise_statement:
                bundle.sources.append(SourceRef(id=next_state.exercise_id or f'practice-{receipt.turn_id}',
                    kind='Exercise', text=exercise_statement, canonical_code=bundle.canonical_code))
            await status('preparing_explanation', 'Đang chuẩn bị lời giải thích theo ngữ cảnh…')
            logger.info('Socratic turn=%s intent=%s verdict=%s action=%s support_scope=%s',
                receipt.turn_id, intent.intent, evaluation.verdict.value if evaluation else 'NOT_GRADED',
                action.kind, action.support_scope)
            streamed = []

            async def forward_delta(delta):
                nonlocal partial_response
                streamed.append(delta)
                partial_response = True
                await emit('token', {'delta': delta, 'content_status': 'DRAFT'})

            content = await self.responses.generate(receipt, req, bundle, action,
                question_plan.question, evaluation, {'progress': learner, 'misconceptions': misconceptions}, provider,
                on_delta=forward_delta if req.protocol_version >= 2 else None)
            if req.protocol_version >= 2:
                draft = ''.join(streamed)
                if content.startswith(draft):
                    if content[len(draft):]:
                        await forward_delta(content[len(draft):])
                elif content != draft:
                    # Post-validation may replace the body or normalize whitespace.
                    # Never append a corrected answer onto an incompatible draft.
                    await emit('content_replace', {'full_content': content, 'content_status': 'DRAFT',
                        'assistant_message_id': receipt.assistant_message_id})
            if question_plan.question and question_plan.criteria and bundle.canonical_code:
                rubric = RubricSnapshot(criteria=question_plan.criteria)
                # Only preserve reviewed provenance if the exact original criteria are reused.
                if bundle.rubric and all(c.model_dump() in [r.model_dump() for r in bundle.rubric.criteria]
                                         for c in question_plan.criteria):
                    rubric = bundle.rubric.model_copy(update={'criteria': question_plan.criteria})
                next_state.pending = PendingQuestion(question_id=str(uuid.uuid4()),
                    assistant_message_id=receipt.assistant_message_id, text=question_plan.question,
                    canonical_code=bundle.canonical_code, objective=question_plan.objective,
                    rubric=rubric, sources=bundle.sources, hint_level_used=action.hint_level,
                    exercise_step_id=next_state.step_id if next_state.mode == 'EXERCISE' else None,
                    completes_exercise_step=completes_step)
                next_state.objective = question_plan.objective
                next_state.context.pop('awaiting_clarification', None)
            next_state.summary = f"Khái niệm: {next_state.canonical_code or 'chưa rõ'}; mục tiêu: {next_state.objective or 'giải thích'}; hành động: {action.kind}."
            next_state.context['access_scope_key'] = scope_key
            next_state.context['material_ids'] = materials
            next_state.strategy = action.kind
            step_progress = self.states.step_progress(next_state)
            public = {'session_id': receipt.session_id, 'assistant_message_id': receipt.assistant_message_id,
                'full_content': content,
                'step_number_at_turn': step_progress['number'] if step_progress else None,
                'step_progress': step_progress,
                'is_completed': next_state.completed, 'active_strategy': action.kind,
                'referenced_chunk_ids': [s.id for s in bundle.sources if s.kind == 'CHUNK'],
                'referenced_node_ids': [s.id for s in bundle.sources if s.kind != 'CHUNK'],
                'artifacts': public_artifacts, 'active_topic_id': next_state.topic_id,
                'active_canonical_code': next_state.canonical_code}
            await status('saving_response', 'Đang lưu cuộc trò chuyện…')
            version = await self.turns.finalize(receipt, req.student_id, next_state, content,
                public, evaluation, pending if evaluation else None, action)
            committed = True
            await status('saving_response', 'Đã lưu cuộc trò chuyện.', 'completed')
            await status('preparing_explanation', 'Đã chuẩn bị xong phản hồi.', 'completed')
            await emit('context_ref', {'referenced_chunk_ids': public['referenced_chunk_ids'],
                'referenced_node_ids': public['referenced_node_ids'], 'matched_canonical_codes':
                    [bundle.canonical_code] if bundle.canonical_code else [], 'active_strategy': action.kind})
            for name, payload in artifact_events:
                await emit(name, payload)
            if next_state.step_number != state.step_number or next_state.completed != state.completed:
                await emit('step_update', {'previous_step_number': state.step_number,
                    'current_step_number': next_state.step_number, 'is_completed': next_state.completed,
                    'step_progress': step_progress})
            # Protocol 1 retains its buffered transport; protocol 2 already sent live deltas.
            if req.protocol_version == 1:
                for start in range(0, len(content), 160):
                    await emit('token', {'delta': content[start:start+160]})
            await emit('done', dict(public, state_version=version, content_status='FINAL'))

        async def produce():
            try:
                async with asyncio.timeout(settings.SOCRATIC_REQUEST_TIMEOUT):
                    await work()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.exception('Socratic turn failed: %s', receipt.turn_id if receipt else 'not accepted')
                # TaskGroup may wrap errors; public output never includes raw exception strings.
                error = exc if isinstance(exc, TurnError) else None
                await emit('error', {'code': error.code if error else 'SOCRATIC_ERROR',
                    'message': error.message if error else 'Lượt này chưa hoàn tất. Em có thể thử lại cùng mã yêu cầu.',
                    'recoverable': error.recoverable if error else True,
                    'partial_response': partial_response,
                    'content_status': 'INCOMPLETE' if partial_response else None,
                    'assistant_message_id': receipt.assistant_message_id if receipt else None})
            finally:
                if receipt and not committed:
                    with suppress(Exception):
                        await asyncio.shield(self.turns.fail(receipt))
                logger.info('Socratic turn duration_ms=%d completed=%s', int((time.monotonic()-started)*1000), committed)
                if asyncio.current_task().cancelling():
                    with suppress(asyncio.QueueFull):
                        queue.put_nowait(None)
                else:
                    await queue.put(None)

        producer = asyncio.create_task(produce())
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), settings.SSE_PING_INTERVAL_SECONDS)
                except asyncio.TimeoutError:
                    yield ': ping\n\n'
                    continue
                if event is None:
                    break
                yield event
        finally:
            producer.cancel()
            with suppress(asyncio.CancelledError):
                await producer
