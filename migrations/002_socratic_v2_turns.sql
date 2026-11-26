-- Message-only upgrade for OLD schemas. Skip if final message DDL is already installed.
-- Inspect information_schema first if any of these columns/indexes already exist.
ALTER TABLE socratic_chat_messages
 ADD COLUMN turn_id BINARY(16) NULL,
 ADD COLUMN turn_status VARCHAR(24) NULL,
 ADD COLUMN content_status VARCHAR(16) NULL,
 ADD COLUMN turn_metadata JSON NULL,
 ADD UNIQUE KEY uq_msg_session_turn_role(session_id,turn_id,role);
-- student_misconceptions uses the final schema documented in .docs/data-contracts.md.
-- The earlier ALTER adding review_status is superseded; do not apply it.
-- Optional performance index: inspect existing indexes before applying.
-- CREATE INDEX idx_topic_chunks_reverse ON topic_chunks(chunk_id,topic_id);
-- No destructive rollback is supplied: disabling V2 preserves evidence/state.
