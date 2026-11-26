import uuid
from app.schema.tutoring_contracts import DiagramPlan, ExerciseDraft, ArtifactValidation
from app.service.tutoring.prompt_builder import encode, source_context


class ArtifactService:
    def __init__(self, llm):
        self.llm = llm

    async def diagram(self, bundle, goal, provider=None):
        result = await self.llm.generate_structured_output(
            system_prompt='Tạo sơ đồ khái niệm 2D bằng nodes/edges theo schema. '
                'Không HTML, URL, script hoặc lời giải bài tập. Dựa đúng nguồn, giữ số node nhỏ.',
            user_prompt=encode({'goal': goal, 'sources': source_context(bundle)}),
            response_schema=DiagramPlan, task='artifact', provider=provider)
        ids = [n.id for n in result.nodes]
        if len(ids) != len(set(ids)) or any(e.source not in ids or e.target not in ids for e in result.edges):
            raise ValueError('Invalid diagram graph')
        if not result.source_ids or not set(result.source_ids) <= {s.id for s in bundle.sources}:
            raise ValueError('Diagram sources not found')
        return {'artifact_id': str(uuid.uuid4()), 'schema_version': 1,
                'type': 'concept_graph_2d', **result.model_dump()}

    async def exercise(self, bundle, objective, provider=None):
        draft = await self.llm.generate_structured_output(
            system_prompt='Tạo một bài tập nhận diện/phân biệt/vận dụng ngắn, đầy đủ dữ kiện, '
                'có lời giải nội bộ để đối chiếu. Không sao lại bài người học đang làm. '
                'Mọi tiêu chí cần source_ids từ nguồn. Không đưa lời giải vào statement.',
            user_prompt=encode({'objective': objective, 'sources': source_context(bundle)}),
            response_schema=ExerciseDraft, task='artifact', provider=provider)
        if any(not c.source_ids or not set(c.source_ids) <= {s.id for s in bundle.sources} for c in draft.criteria):
            raise ValueError('Exercise lacks source evidence')
        checked = await self.llm.generate_structured_output(
            system_prompt='Kiểm tra độc lập đề bài có đủ dữ kiện, đáp án nội bộ đúng/nhất quán, '
                'statement không tiết lộ lời giải và các tiêu chí phù hợp. Không chắc thì valid=false. '
                'Đây là kiểm tra AI, không phải xác nhận giáo viên.',
            user_prompt=encode({'draft': draft.model_dump(), 'sources': source_context(bundle)}),
            response_schema=ArtifactValidation, task='artifact', provider=provider, temperature=0)
        if not checked.valid:
            raise ValueError('Generated exercise did not pass model review')
        artifact_id = str(uuid.uuid4())
        public = {'artifact_id': artifact_id, 'schema_version': 1, 'type': 'practice_exercise',
                  'title': draft.title, 'statement': draft.statement,
                  'objective': draft.objective, 'origin': 'AI_GENERATED', 'review': 'AI_CHECKED'}
        return public, draft
