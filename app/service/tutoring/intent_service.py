import logging
from app.schema.tutoring_contracts import IntentAnalysis
from app.service.tutoring.prompt_builder import prompt, encode

logger = logging.getLogger(__name__)


class IntentService:
    def __init__(self, llm):
        self.llm = llm

    async def analyze(self, req, state, history, provider=None):
        chips = {'REQUEST_METAPHOR': 'REQUEST_EXAMPLE', 'SIMPLIFY_STEP': 'REQUEST_HINT',
                 'CHECK_CONDITION': 'ASK_WHY', 'FEYNMAN_CHALLENGE': 'REQUEST_EXERCISE'}
        if req.forced_action in chips and state.canonical_code:
            return IntentAnalysis(intent=chips[req.forced_action],
                standalone_query=f'{state.canonical_code}: {req.message}', practice_requested=True)
        if req.message.strip().casefold() in {'cảm ơn', 'cảm ơn ạ', 'tạm biệt', 'dừng lại', 'bye'}:
            return IntentAnalysis(intent='CLOSE_DISCUSSION', standalone_query=req.message)
        try:
            result = await self.llm.generate_structured_output(system_prompt=prompt('intent'),
                user_prompt=encode({'message': req.message, 'active_concept': state.canonical_code,
                    'pending_question': state.pending.text if state.pending and not state.context.get('awaiting_clarification') else None,
                    'learning_mode': state.mode,
                    'has_active_exercise': state.mode == 'EXERCISE' and not state.completed,
                    'summary': state.summary, 'history': history[-4:]}),
                response_schema=IntentAnalysis, task='intent', provider=provider, temperature=0)
            if not result.standalone_query.strip():
                result.standalone_query = req.message
            if not state.pending or state.context.get('awaiting_clarification'):
                result.refers_to_pending = False
                if result.intent == 'ANSWER_PENDING':
                    result.intent = 'CLARIFY'
            return result
        except Exception:
            logger.warning('Intent analysis failed; retaining context without grading', exc_info=True)
            return IntentAnalysis(intent='CLARIFY', standalone_query=f'{state.canonical_code or ""}: {req.message}')
