import logging
from app.schema.tutoring_contracts import EvaluationResult, Verdict
from app.service.tutoring.prompt_builder import prompt, encode

logger = logging.getLogger(__name__)


class UnderstandingEvaluator:
    def __init__(self, llm):
        self.llm = llm

    async def evaluate(self, answer, pending, provider=None):
        if not pending.rubric.criteria or not pending.sources:
            return EvaluationResult(verdict=Verdict.INSUFFICIENT_EVIDENCE, needs_more_evidence=True)
        try:
            result = await self.llm.generate_structured_output(system_prompt=prompt('evaluation'),
                user_prompt=encode({'answer': answer, 'pending': pending.model_dump(mode='json')}),
                response_schema=EvaluationResult, task='evaluation', provider=provider, temperature=0)
            allowed = {c.code for c in pending.rubric.criteria}
            observed = [c.code for c in result.criteria_results]
            if len(observed) != len(set(observed)) or not set(observed) <= allowed:
                raise ValueError('Unknown or duplicated criteria')
            if result.verdict in {Verdict.CORRECT, Verdict.PARTIAL, Verdict.INCORRECT} and not observed:
                raise ValueError('A grading decision requires criterion-level evidence')
            for criterion in result.criteria_results:
                if criterion.status in {'MET', 'NOT_MET'} and (
                        not criterion.student_excerpt or criterion.student_excerpt not in answer):
                    raise ValueError('Unsupported grading evidence')
            met = {c.code for c in result.criteria_results if c.status == 'MET'}
            if result.verdict == Verdict.CORRECT and met != allowed:
                result.verdict = Verdict.PARTIAL if met else Verdict.UNCLEAR
            if result.verdict == Verdict.INCORRECT and met:
                result.verdict = Verdict.PARTIAL
            if result.needs_more_evidence:
                result.verdict = Verdict.INSUFFICIENT_EVIDENCE
            return result
        except Exception:
            logger.warning('Evaluation unavailable or invalid; no negative score applied', exc_info=True)
            return EvaluationResult(verdict=Verdict.UNCLEAR)
