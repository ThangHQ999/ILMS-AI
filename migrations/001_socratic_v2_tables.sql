-- Review before applying. UUID bytes follow Python uuid.UUID(...).bytes (no byte swap).
-- Requires existing topics, material_chunks, users, socratic_chat_sessions/messages.
-- CREATE IF NOT EXISTS does not upgrade tables created from the earlier draft: see 003.
CREATE TABLE IF NOT EXISTS socratic_learning_state (
 session_id BINARY(16) NOT NULL PRIMARY KEY,
 active_topic_id BINARY(16) NULL,
 active_canonical_code VARCHAR(128) CHARACTER SET ascii COLLATE ascii_bin NULL,
 learning_mode VARCHAR(24) NOT NULL DEFAULT 'CONCEPT',
 active_objective VARCHAR(32) NULL,
 pending_question_message_id BINARY(16) NULL,
 active_process_id VARCHAR(64) NULL, active_exercise_id VARCHAR(64) NULL,
 active_step_id VARCHAR(64) NULL,
 hint_level TINYINT UNSIGNED NOT NULL DEFAULT 0,
 failed_attempts INT UNSIGNED NOT NULL DEFAULT 0, last_strategy VARCHAR(48) NULL,
 assessment_context JSON NULL, return_stack JSON NULL, conversation_summary TEXT NULL,
 state_version INT UNSIGNED NOT NULL DEFAULT 0,
 active_turn_id BINARY(16) NULL, lease_token BINARY(16) NULL,
 lease_expires_at DATETIME(6) NULL,
 created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
 updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
 CONSTRAINT fk_sls_session FOREIGN KEY(session_id) REFERENCES socratic_chat_sessions(id) ON DELETE CASCADE,
 CONSTRAINT fk_sls_topic FOREIGN KEY(active_topic_id) REFERENCES topics(id) ON DELETE SET NULL,
 CONSTRAINT fk_sls_pending_question FOREIGN KEY(pending_question_message_id) REFERENCES socratic_chat_messages(id) ON DELETE SET NULL,
 CHECK(hint_level BETWEEN 0 AND 4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS socratic_turn_evaluations (
 id BINARY(16) NOT NULL PRIMARY KEY, session_id BINARY(16) NOT NULL,
 student_message_id BINARY(16) NOT NULL, question_message_id BINARY(16) NULL,
 canonical_code VARCHAR(128) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
 objective_code VARCHAR(32) NOT NULL, verdict VARCHAR(32) NOT NULL,
 assessment_origin VARCHAR(24) NOT NULL DEFAULT 'SESSION_DRAFT',
 rubric_id VARCHAR(64) NULL, rubric_version INT UNSIGNED NULL,
 rubric_snapshot JSON NOT NULL, criteria_results JSON NOT NULL, evidence JSON NOT NULL,
 hint_level_used TINYINT UNSIGNED NOT NULL DEFAULT 0, feedback_action VARCHAR(48) NULL,
 evaluator_model VARCHAR(128) NULL, evaluator_version VARCHAR(64) NOT NULL,
 created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
 UNIQUE KEY uq_ste_message_objective(student_message_id, canonical_code, objective_code),
 KEY idx_ste_session_created(session_id,created_at),
 CONSTRAINT fk_ste_session FOREIGN KEY(session_id) REFERENCES socratic_chat_sessions(id) ON DELETE CASCADE,
 CONSTRAINT fk_ste_student_message FOREIGN KEY(student_message_id) REFERENCES socratic_chat_messages(id) ON DELETE CASCADE,
 CONSTRAINT fk_ste_question_message FOREIGN KEY(question_message_id) REFERENCES socratic_chat_messages(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS student_concept_progress (
 id BINARY(16) NOT NULL PRIMARY KEY, user_id BINARY(16) NOT NULL,
 canonical_code VARCHAR(128) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
 mastery_level DECIMAL(4,3) NULL, mastery_status VARCHAR(24) NOT NULL DEFAULT 'NOT_ASSESSED',
 assessment_count INT UNSIGNED NOT NULL DEFAULT 0,
 independent_success_count INT UNSIGNED NOT NULL DEFAULT 0,
 objective_progress JSON NULL, last_evaluation_id BINARY(16) NULL,
 scoring_version VARCHAR(64) NULL, last_assessed_at DATETIME(6) NULL,
 progress_version INT UNSIGNED NOT NULL DEFAULT 0,
 created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
 updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
 UNIQUE KEY uq_scp_user_concept(user_id,canonical_code),
 KEY idx_scp_concept(canonical_code),
 CONSTRAINT fk_scp_user FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
 CONSTRAINT fk_scp_last_evaluation FOREIGN KEY(last_evaluation_id) REFERENCES socratic_turn_evaluations(id) ON DELETE SET NULL,
 CHECK(mastery_level IS NULL OR mastery_level BETWEEN 0 AND 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
