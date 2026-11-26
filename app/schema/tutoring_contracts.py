"""Internal Socratic contracts. These objects are never serialized directly to public APIs."""
from enum import StrEnum
from typing import Any, Literal
from pydantic import BaseModel, Field


class Verdict(StrEnum):
    CORRECT = 'CORRECT'
    PARTIAL = 'PARTIAL'
    INCORRECT = 'INCORRECT'
    UNCLEAR = 'UNCLEAR'
    NOT_AN_ATTEMPT = 'NOT_AN_ATTEMPT'
    INSUFFICIENT_EVIDENCE = 'INSUFFICIENT_EVIDENCE'


class IntentAnalysis(BaseModel):
    intent: Literal['ASK_DEFINITION', 'ASK_WHY', 'COMPARE', 'REQUEST_EXAMPLE',
                    'ANSWER_PENDING', 'REQUEST_HINT', 'EXPRESS_CONFUSION',
                    'CHALLENGE_TUTOR', 'REQUEST_EXERCISE', 'REQUEST_DIAGRAM',
                    'SWITCH_TOPIC', 'CLOSE_DISCUSSION', 'CLARIFY'] = 'CLARIFY'
    standalone_query: str = ''
    mentions: list[str] = Field(default_factory=list, max_length=6)
    explicit_switch: bool = False
    refers_to_pending: bool = False
    practice_requested: bool = False
    is_practice_attempt: bool = False
    asks_for_solution: bool = False


class SourceRef(BaseModel):
    id: str
    kind: str
    text: str
    canonical_code: str | None = None
    scope: str = 'GLOBAL'
    version: str | None = None


class Criterion(BaseModel):
    code: str
    objective: str = 'MEANING'
    description: str
    expected_evidence: str
    acceptable_variations: list[str] = Field(default_factory=list)
    misconception_codes: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)


class RubricSnapshot(BaseModel):
    id: str | None = None
    version: int | None = None
    origin: str = 'SESSION_DRAFT'
    review_state: str = 'UNREVIEWED'
    criteria: list[Criterion] = Field(default_factory=list, max_length=8)


class PendingQuestion(BaseModel):
    question_id: str
    assistant_message_id: str
    text: str
    canonical_code: str
    objective: str
    rubric: RubricSnapshot
    sources: list[SourceRef] = Field(default_factory=list)
    hint_level_used: int = Field(default=0, ge=0, le=4)
    exercise_step_id: str | None = None
    completes_exercise_step: bool = False


class LearningSnapshot(BaseModel):
    version: int = 0
    topic_id: str | None = None
    canonical_code: str | None = None
    mode: str = 'CONCEPT'
    objective: str | None = None
    pending: PendingQuestion | None = None
    hint_level: int = 0
    failed_attempts: int = 0
    strategy: str | None = None
    return_stack: list[dict[str, Any]] = Field(default_factory=list)
    summary: str = ''
    process_id: str | None = None
    exercise_id: str | None = None
    step_id: str | None = None
    step_number: int = 1
    completed: bool = False
    context: dict[str, Any] = Field(default_factory=dict)


class StepProgress(BaseModel):
    step_id: str
    exercise_id: str
    number: int = Field(ge=1)
    total: int = Field(ge=1)
    instruction: str = ''
    completed: bool = False


class KnowledgeBundle(BaseModel):
    topic_id: str | None = None
    topic_name: str | None = None
    canonical_code: str | None = None
    entity: dict[str, Any] = Field(default_factory=dict)
    candidates: list[dict[str, Any]] = Field(default_factory=list)
    sources: list[SourceRef] = Field(default_factory=list)
    relations: list[dict[str, Any]] = Field(default_factory=list)
    rubric: RubricSnapshot | None = None
    exercise: dict[str, Any] | None = None
    warnings: list[str] = Field(default_factory=list)
    cache_hit: bool = False


class CriterionResult(BaseModel):
    code: str
    status: Literal['MET', 'NOT_MET', 'UNCLEAR']
    student_excerpt: str = ''


class EvaluationResult(BaseModel):
    verdict: Verdict = Verdict.UNCLEAR
    criteria_results: list[CriterionResult] = Field(default_factory=list)
    missing_elements: list[str] = Field(default_factory=list)
    misconception_codes: list[str] = Field(default_factory=list)
    misconception_note: str | None = None
    resolved_misconception_codes: list[str] = Field(default_factory=list)
    prerequisite_code: str | None = None
    needs_more_evidence: bool = False


class TeachingAction(BaseModel):
    kind: str
    directive: str
    objective: str = 'MEANING'
    hint_level: int = 0
    ask_question: bool = False
    preserve_pending: bool = False
    advance: bool = False
    backtrack_code: str | None = None
    support_scope: Literal['EXPLANATION', 'SINGLE_STEP'] = 'EXPLANATION'


class GuidanceCheck(BaseModel):
    within_one_step: bool
    reveals_final_answer: bool
    answers_next_question: bool
    reason: str = Field(default='', max_length=400)


class QuestionPlan(BaseModel):
    question: str = Field(default='', max_length=1200)
    objective: str = 'MEANING'
    criteria: list[Criterion] = Field(default_factory=list, max_length=4)


class DiagramNode(BaseModel):
    id: str = Field(pattern=r'^[A-Za-z][A-Za-z0-9_]{0,31}$')
    label: str = Field(min_length=1, max_length=160)


class DiagramEdge(BaseModel):
    source: str
    target: str
    label: str = Field(default='', max_length=160)


class DiagramPlan(BaseModel):
    title: str = Field(max_length=180)
    nodes: list[DiagramNode] = Field(min_length=1, max_length=16)
    edges: list[DiagramEdge] = Field(default_factory=list, max_length=28)
    source_ids: list[str] = Field(default_factory=list)


class ExerciseDraft(BaseModel):
    title: str = Field(max_length=180)
    statement: str = Field(min_length=10, max_length=4000)
    objective: str
    internal_solution: str = Field(min_length=1, max_length=4000)
    criteria: list[Criterion] = Field(min_length=1, max_length=4)


class ArtifactValidation(BaseModel):
    valid: bool
    reason: str
