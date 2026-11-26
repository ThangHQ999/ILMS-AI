-- ONLY for installations that created learning_state from the EARLY chat SQL draft.
-- SKIP if you used 001_socratic_v2_tables.sql in this repository.
ALTER TABLE socratic_learning_state
 ADD COLUMN active_turn_id BINARY(16) NULL,
 ADD COLUMN lease_token BINARY(16) NULL,
 ADD COLUMN lease_expires_at DATETIME(6) NULL;
