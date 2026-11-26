-- Each edit produces a new revision; approval is tied to the canonical payload hash.
CREATE TABLE knowledge_graph_drafts (
    id BINARY(16) NOT NULL,
    job_id BINARY(16) NOT NULL,
    revision_number INT UNSIGNED NOT NULL,
    payload_schema_version VARCHAR(32) NOT NULL DEFAULT 'knowledge-graph-1',
    graph_payload JSON NOT NULL
        COMMENT 'Nodes, relations, topics and proposed topic-to-chunk links with IDs',
    validation_report JSON DEFAULT NULL,
    source_manifest JSON DEFAULT NULL
        COMMENT 'Source IDs, excerpts, document/external/AI-generated origins',
    payload_hash CHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL
        COMMENT 'SHA-256 of canonical application serialization of graph_payload',
    review_status VARCHAR(24) NOT NULL DEFAULT 'DRAFT',
    reviewed_by BINARY(16) DEFAULT NULL,
    reviewed_at DATETIME(6) DEFAULT NULL,
    reviewed_payload_hash CHAR(64) CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL,
    review_comment TEXT DEFAULT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),

    PRIMARY KEY (id),
    UNIQUE KEY uq_graph_draft_revision (job_id, revision_number),
    UNIQUE KEY uq_graph_draft_job_identity (job_id, id),
    KEY idx_graph_draft_review (review_status, created_at),
    KEY idx_graph_draft_reviewer (reviewed_by),
    CONSTRAINT fk_graph_draft_job FOREIGN KEY (job_id)
        REFERENCES ingestion_jobs(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_graph_draft_reviewer FOREIGN KEY (reviewed_by)
        REFERENCES users(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT chk_graph_draft_revision CHECK (revision_number >= 1),
    CONSTRAINT chk_graph_draft_status CHECK (review_status IN (
        'DRAFT', 'PENDING_REVIEW', 'APPROVED', 'REJECTED', 'CHANGES_REQUESTED')),
    CONSTRAINT chk_graph_draft_review_record CHECK (
        review_status NOT IN ('APPROVED', 'REJECTED', 'CHANGES_REQUESTED')
        OR (reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL
            AND reviewed_payload_hash IS NOT NULL AND reviewed_payload_hash = payload_hash))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
