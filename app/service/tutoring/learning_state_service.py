from app.core.config import settings
from app.schema.tutoring_contracts import LearningSnapshot, StepProgress, Verdict


OBJECTIVES = ['MEANING', 'IDENTIFICATION', 'CONDITIONS', 'DISTINCTION', 'APPLICATION', 'EXPLANATION']


class LearningStateService:
    @staticmethod
    def step_progress(state):
        """Display progress only for a verified step of a stored exercise."""
        if state.mode != 'EXERCISE' or not state.step_id or not state.exercise_id:
            return None
        stored = state.context.get('stored_exercise') or {}
        if not isinstance(stored, dict) or not isinstance(stored.get('exercise'), dict):
            return None
        if (stored.get('exercise') or {}).get('id') != state.exercise_id:
            return None
        raw_steps = stored.get('steps')
        if not isinstance(raw_steps, list) or any(
                not isinstance(step, dict) or not isinstance(step.get('id'), str)
                or type(step.get('step_number')) is not int for step in raw_steps):
            return None
        if len({step['id'] for step in raw_steps}) != len(raw_steps):
            return None
        steps = sorted(raw_steps, key=lambda step: step['step_number'])
        numbers = [step['step_number'] for step in steps]
        if numbers != list(range(1, len(steps) + 1)):
            return None
        current = next((step for step in steps if step['id'] == state.step_id
                        and step['step_number'] == state.step_number), None)
        if current is None:
            return None
        return StepProgress(step_id=state.step_id, exercise_id=state.exercise_id,
            number=state.step_number, total=len(steps), instruction=current.get('instruction') or '',
            completed=state.completed).model_dump(mode='json')

    def start(self, state, bundle, action, evaluation=None):
        next_state = state.model_copy(deep=True)
        if next_state.mode == 'CONCEPT':
            next_state.completed = False
        changed = bool(bundle.canonical_code and bundle.canonical_code != state.canonical_code)
        if changed:
            next_state.pending = None
            next_state.process_id = next_state.exercise_id = next_state.step_id = None
            next_state.context = {}
            next_state.mode, next_state.step_number, next_state.completed = 'CONCEPT', 1, False
            next_state.hint_level = next_state.failed_attempts = 0
        next_state.canonical_code = bundle.canonical_code or state.canonical_code
        next_state.topic_id = bundle.topic_id
        next_state.strategy, next_state.objective = action.kind, action.objective
        next_state.hint_level = action.hint_level
        if evaluation and not changed:
            if evaluation.verdict == Verdict.INCORRECT:
                next_state.failed_attempts += 1
            elif evaluation.verdict == Verdict.CORRECT:
                next_state.failed_attempts = 0
        if action.kind == 'CLOSE':
            next_state.pending = None
        elif not action.preserve_pending:
            next_state.pending = None
        return next_state

    def next_objective(self, state, bundle, learner):
        available = [c.objective for c in bundle.rubric.criteria] if bundle.rubric else OBJECTIVES
        # Not a mandatory ladder: prefer an applicable objective without independent evidence.
        for objective in dict.fromkeys(available):
            if objective != state.objective and learner.get(objective, {}).get('status') != 'DEMONSTRATED':
                return objective
        return state.objective or 'APPLICATION'

    def push(self, current, code):
        visited = {f.get('canonical_code') for f in current.return_stack} | {current.canonical_code}
        if code in visited or len(current.return_stack) >= settings.SOCRATIC_MAX_STACK:
            return None
        frame = current.model_dump(mode='json', exclude={'return_stack'})
        return LearningSnapshot(canonical_code=code, mode='REVIEW',
            return_stack=[*current.return_stack, frame], version=current.version)

    def pop(self, state):
        if not state.return_stack:
            return state
        restored = LearningSnapshot.model_validate(state.return_stack[-1])
        restored.return_stack = state.return_stack[:-1]
        restored.version = state.version
        return restored
