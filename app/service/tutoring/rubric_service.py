from app.schema.tutoring_contracts import QuestionPlan
from app.service.tutoring.prompt_builder import prompt, encode, source_context


class RubricService:
    def __init__(self, llm):
        self.llm = llm

    async def question(self, bundle, action, previous, provider=None, *, learner_message='', evaluation=None):
        if not action.ask_question or not bundle.canonical_code or not bundle.sources:
            return QuestionPlan()
        result = await self.llm.generate_structured_output(system_prompt=prompt('question'),
            user_prompt=encode({'concept': bundle.entity, 'action': action.model_dump(),
                'previous_question': previous.model_dump(mode='json') if previous else None,
                'learner_message': learner_message,
                'evaluation': evaluation.model_dump(mode='json') if evaluation else None,
                'rubric': bundle.rubric.model_dump(mode='json') if bundle.rubric else None,
                'sources': source_context(bundle)}), response_schema=QuestionPlan,
            task='question', provider=provider, temperature=0.1)
        ids = {s.id for s in bundle.sources if s.kind != 'TOPIC_SUMMARY'}
        if not result.question.strip() or not result.criteria:
            return QuestionPlan()
        if len({c.code for c in result.criteria}) != len(result.criteria):
            return QuestionPlan()
        if action.support_scope == 'SINGLE_STEP' and len(result.criteria) != 1:
            return QuestionPlan()
        # Explicit provenance is required, including criteria generated per question.
        if any(not c.source_ids or not set(c.source_ids) <= ids for c in result.criteria):
            return QuestionPlan()
        if previous and result.question.strip().casefold() == previous.text.strip().casefold():
            return QuestionPlan()
        return result
