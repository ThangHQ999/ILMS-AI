import re
import logging
from app.core.config import settings
from app.schema.tutoring_contracts import GuidanceCheck
from app.service.tutoring.prompt_builder import PromptBuilder, prompt, encode, source_context

logger = logging.getLogger(__name__)


class ResponseGenerator:
    def __init__(self, llm):
        self.llm = llm

    async def generate(self, receipt, req, bundle, action, question, evaluation, learner, provider=None,
                       on_delta=None):
        system = PromptBuilder().response(bundle, action, question, evaluation, learner, receipt.state.pending)
        history = receipt.history[-settings.SOCRATIC_MAX_HISTORY_MESSAGES:]
        # Bound history separately; preserve pending text in system even when older turns are dropped.
        budget, selected = settings.SOCRATIC_CONTEXT_CHARS // 2, []
        for msg in reversed(history):
            if len(msg['content']) <= budget:
                selected.append(msg)
                budget -= len(msg['content'])
        messages = list(reversed(selected)) + [{'role': 'user', 'content': req.message}]
        restricted = action.support_scope == 'SINGLE_STEP'
        for attempt in range(2 if restricted else 1):
            body = await self._body(system, messages, provider, None if restricted else on_delta)
            if not restricted:
                break
            check = await self.llm.generate_structured_output(
                system_prompt=prompt('guidance_check'),
                user_prompt=encode({'learner_message': req.message, 'body': body,
                    'next_question': question, 'action': action.model_dump(),
                    'previous_question': receipt.state.pending.model_dump(mode='json') if receipt.state.pending else None,
                    'evaluation': evaluation.model_dump(mode='json') if evaluation else None,
                    'sources': source_context(bundle)}),
                response_schema=GuidanceCheck, task='evaluation', provider=provider, temperature=0)
            accepted = (check.within_one_step and not check.reveals_final_answer
                        and not check.answers_next_question
                        and not (question and ('?' in body or '？' in body)))
            logger.info('Socratic guidance_check turn=%s action=%s attempt=%d accepted=%s',
                        receipt.turn_id, action.kind, attempt + 1, accepted)
            if accepted:
                break
            if attempt == 1:
                raise ValueError('Guidance exceeded the single-step disclosure policy')
            system += ('\nBản nháp trước không đạt giới hạn hỗ trợ. Viết lại ngắn hơn: '
                       'chỉ nhắc một quy tắc giúp người học tự làm bước tới, không tính hộ '
                       'kết quả hoặc trả lời câu hỏi server. Không nhắc đến kiểm tra nội bộ.')
        # Live output is provisional until validation and the final DB commit succeed.
        allowed = {s.id for s in bundle.sources}
        if any(ref not in allowed for ref in re.findall(r'\[S:([^\]]+)\]', body)):
            raise ValueError('Response contains unknown source references')
        if question and ('?' in body or '？' in body):
            # Deterministic fallback rather than silently storing criteria for a different question.
            body = {'ADVANCE': 'Em đã thể hiện được yêu cầu vừa kiểm tra. Mình thử một tình huống khác nhé.',
                    'FOCUS_GAP': 'Phần em nêu đã có ý đúng. Mình làm rõ thêm điểm còn thiếu nhé.',
                    'COUNTEREXAMPLE': 'Mình cùng kiểm tra lại điều kiện đang gây vướng bằng một câu hỏi nhỏ hơn nhé.'
                    }.get(action.kind, 'Mình cùng xem một câu hỏi ngắn để làm rõ nội dung này nhé.')
        if restricted and on_delta is not None:
            # These short hints are checked before display; a later replacement cannot
            # undo a solution already disclosed to the learner in a live draft.
            await on_delta(body)
        return body + ('\n\n**' + question + '**' if question else '')

    async def _body(self, system, messages, provider, on_delta):
        output, count = [], 0
        async for delta in self.llm.stream_chat_completion(system_prompt=system, messages=messages,
                                                          provider=provider, temperature=0.3):
            count += len(delta)
            if count > settings.SOCRATIC_MAX_OUTPUT_CHARS:
                raise ValueError('Response exceeded configured output limit')
            output.append(delta)
            if on_delta is not None:
                await on_delta(delta)
        body = ''.join(output).strip()
        if not body:
            raise ValueError('Empty tutor response')
        return body
