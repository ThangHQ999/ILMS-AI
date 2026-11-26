"""Socratic ORM. Migrations are supplied separately; startup never creates these tables."""
from datetime import datetime
from decimal import Decimal
from typing import Any
from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.model.mysql.base import Base, BinaryUUID, TimestampMixin


class Topic(Base):
    __tablename__ = 'topics'
    id: Mapped[str] = mapped_column(BinaryUUID, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text)
    concepts_included: Mapped[list[str] | None] = mapped_column(JSON)


class TopicChunk(Base):
    __tablename__ = 'topic_chunks'
    topic_id: Mapped[str] = mapped_column(BinaryUUID, ForeignKey('topics.id', ondelete='CASCADE'), primary_key=True)
    chunk_id: Mapped[str] = mapped_column(BinaryUUID, ForeignKey('material_chunks.id', ondelete='CASCADE'), primary_key=True)


class LearningState(Base, TimestampMixin):
    __tablename__ = 'socratic_learning_state'
    session_id: Mapped[str] = mapped_column(BinaryUUID, ForeignKey('socratic_chat_sessions.id', ondelete='CASCADE'), primary_key=True)
    active_topic_id: Mapped[str | None] = mapped_column(BinaryUUID, ForeignKey('topics.id', ondelete='SET NULL'))
    active_canonical_code: Mapped[str | None] = mapped_column(String(128))
    learning_mode: Mapped[str] = mapped_column(String(24), default='CONCEPT')
    active_objective: Mapped[str | None] = mapped_column(String(32))
    pending_question_message_id: Mapped[str | None] = mapped_column(BinaryUUID, ForeignKey('socratic_chat_messages.id', ondelete='SET NULL'))
    active_process_id: Mapped[str | None] = mapped_column(String(64))
    active_exercise_id: Mapped[str | None] = mapped_column(String(64))
    active_step_id: Mapped[str | None] = mapped_column(String(64))
    hint_level: Mapped[int] = mapped_column(Integer, default=0)
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_strategy: Mapped[str | None] = mapped_column(String(48))
    assessment_context: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    return_stack: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON)
    conversation_summary: Mapped[str | None] = mapped_column(Text)
    state_version: Mapped[int] = mapped_column(Integer, default=0)
    active_turn_id: Mapped[str | None] = mapped_column(BinaryUUID)
    lease_token: Mapped[str | None] = mapped_column(BinaryUUID)
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime)


class TurnEvaluation(Base):
    __tablename__ = 'socratic_turn_evaluations'
    id: Mapped[str] = mapped_column(BinaryUUID, primary_key=True)
    session_id: Mapped[str] = mapped_column(BinaryUUID, ForeignKey('socratic_chat_sessions.id', ondelete='CASCADE'))
    student_message_id: Mapped[str] = mapped_column(BinaryUUID, ForeignKey('socratic_chat_messages.id', ondelete='CASCADE'))
    question_message_id: Mapped[str | None] = mapped_column(BinaryUUID, ForeignKey('socratic_chat_messages.id', ondelete='SET NULL'))
    canonical_code: Mapped[str] = mapped_column(String(128))
    objective_code: Mapped[str] = mapped_column(String(32))
    verdict: Mapped[str] = mapped_column(String(32))
    assessment_origin: Mapped[str] = mapped_column(String(24))
    rubric_id: Mapped[str | None] = mapped_column(String(64))
    rubric_version: Mapped[int | None] = mapped_column(Integer)
    rubric_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
    criteria_results: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    evidence: Mapped[dict[str, Any]] = mapped_column(JSON)
    hint_level_used: Mapped[int] = mapped_column(Integer, default=0)
    feedback_action: Mapped[str | None] = mapped_column(String(48))
    evaluator_model: Mapped[str | None] = mapped_column(String(128))
    evaluator_version: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('student_message_id', 'canonical_code', 'objective_code', name='uq_ste_message_objective'),)


class ConceptProgress(Base, TimestampMixin):
    __tablename__ = 'student_concept_progress'
    id: Mapped[str] = mapped_column(BinaryUUID, primary_key=True)
    user_id: Mapped[str] = mapped_column(BinaryUUID)
    canonical_code: Mapped[str] = mapped_column(String(128))
    mastery_level: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    mastery_status: Mapped[str] = mapped_column(String(24), default='NOT_ASSESSED')
    assessment_count: Mapped[int] = mapped_column(Integer, default=0)
    independent_success_count: Mapped[int] = mapped_column(Integer, default=0)
    objective_progress: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    last_evaluation_id: Mapped[str | None] = mapped_column(BinaryUUID, ForeignKey('socratic_turn_evaluations.id', ondelete='SET NULL'))
    scoring_version: Mapped[str | None] = mapped_column(String(64))
    last_assessed_at: Mapped[datetime | None] = mapped_column(DateTime)
    progress_version: Mapped[int] = mapped_column(Integer, default=0)
    __table_args__ = (UniqueConstraint('user_id', 'canonical_code', name='uq_scp_user_concept'), Index('idx_scp_concept', 'canonical_code'))
