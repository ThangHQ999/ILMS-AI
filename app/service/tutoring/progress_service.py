"""Evidence aggregation, inside the caller's transaction; no calibrated numeric score."""
import uuid
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from app.core.config import settings
from app.model.mysql.tutoring import ConceptProgress, TurnEvaluation
from app.schema.tutoring_contracts import EvaluationResult, PendingQuestion, Verdict


class ProgressService:
    async def apply(self, db, user_id: str, row: TurnEvaluation,
                    pending: PendingQuestion, result: EvaluationResult) -> None:
        if result.verdict not in {Verdict.CORRECT, Verdict.PARTIAL, Verdict.INCORRECT}:
            return
        # UPSERT followed by row lock serializes different sessions for the same concept.
        stmt = insert(ConceptProgress).values(
            id=str(uuid.uuid4()), user_id=user_id, canonical_code=row.canonical_code,
            mastery_status='NOT_ASSESSED', assessment_count=0,
            independent_success_count=0, progress_version=0,
        )
        await db.execute(stmt.on_duplicate_key_update(user_id=stmt.inserted.user_id))
        progress = (await db.execute(select(ConceptProgress).where(
            ConceptProgress.user_id == user_id,
            ConceptProgress.canonical_code == row.canonical_code,
        ).with_for_update())).scalar_one()
        objectives = dict(progress.objective_progress or {})
        objective = dict(objectives.get(row.objective_code, {}))
        objective['assessment_count'] = objective.get('assessment_count', 0) + 1
        independent = result.verdict == Verdict.CORRECT and pending.hint_level_used <= 1
        objective['independent_success_count'] = objective.get('independent_success_count', 0) + int(independent)
        objective['supported_success_count'] = objective.get('supported_success_count', 0) + int(
            result.verdict == Verdict.CORRECT and not independent)
        objective['last_verdict'] = result.verdict.value
        objective['last_evaluation_id'] = row.id
        objective['rubric_origin'] = pending.rubric.origin
        objective['rubric_review_state'] = pending.rubric.review_state
        objective['criteria'] = {r.code: r.status for r in result.criteria_results}
        # Preserve historical observations; a new question only assesses its own criteria.
        criterion_history = dict(objective.get('criterion_history', {}))
        for item in result.criteria_results:
            entry = dict(criterion_history.get(item.code, {}))
            entry['observations'] = entry.get('observations', 0) + 1
            entry['independent_successes'] = entry.get('independent_successes', 0) + int(
                independent and item.status == 'MET')
            entry['last_status'] = item.status
            entry['last_evaluation_id'] = row.id
            entry['status'] = ('DEMONSTRATED' if entry['independent_successes'] >=
                               settings.SOCRATIC_INDEPENDENT_SUCCESSES else 'DEVELOPING')
            criterion_history[item.code] = entry
        objective['criterion_history'] = criterion_history
        objective['status'] = 'DEVELOPING'
        objective['assessment_scope'] = 'OBSERVED_CRITERIA_ONLY'
        objectives[row.objective_code] = objective
        progress.objective_progress = objectives
        progress.assessment_count += 1
        progress.independent_success_count += int(independent)
        # Evidence for one objective never certifies the entire concept.
        progress.mastery_status = 'DEVELOPING'
        progress.mastery_level = None
        progress.scoring_version = 'evidence-v1-no-numeric-score'
        progress.last_evaluation_id = row.id
        progress.last_assessed_at = datetime.utcnow()
        progress.progress_version += 1
