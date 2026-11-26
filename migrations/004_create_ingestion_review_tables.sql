-- Run once on the intended database. Does not start ingestion or publish data.
-- Prerequisites: users(id), materials(id), both BINARY(16).

CREATE TABLE material_versions (
    id BINARY(16) NOT NULL,
    material_id BINARY(16) NOT NULL,
    version_number INT UNSIGNED NOT NULL,
    source_hash CHAR(64) CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL
        COMMENT 'SHA-256 of original file bytes; NULL for unmigrated legacy source',
    source_snapshot_url VARCHAR(2048) DEFAULT NULL
        COMMENT 'Immutable source snapshot, not an overwritten materials.file_url',
    parser_version VARCHAR(64) NOT NULL,
    chunker_version VARCHAR(64) NOT NULL,
    created_by BINARY(16) NOT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),

    PRIMARY KEY (id),
    UNIQUE KEY uq_material_version_number (material_id, version_number),
    UNIQUE KEY uq_material_version_owner (material_id, id),
    KEY idx_material_version_source (material_id, source_hash),
    KEY idx_material_version_creator (created_by),
    CONSTRAINT fk_material_version_material FOREIGN KEY (material_id)
        REFERENCES materials(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_material_version_creator FOREIGN KEY (created_by)
        REFERENCES users(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT chk_material_version_number CHECK (version_number >= 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE ingestion_jobs (
    id BINARY(16) NOT NULL,
    material_version_id BINARY(16) NOT NULL,
    requested_by BINARY(16) NOT NULL,
    idempotency_key VARCHAR(128) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    source_policy VARCHAR(24) NOT NULL DEFAULT 'DOCUMENT_ONLY'
        COMMENT 'DOCUMENT_ONLY, EXTERNAL_ALLOWED; permission checked by backend',
    status VARCHAR(32) NOT NULL DEFAULT 'QUEUED',
    current_stage VARCHAR(64) DEFAULT NULL,
    pipeline_version VARCHAR(64) NOT NULL,
    configuration JSON DEFAULT NULL
        COMMENT 'Model/parser/prompt options; never store API keys',
    checkpoint JSON DEFAULT NULL,
    publication_state JSON DEFAULT NULL
        COMMENT 'Per-store progress/retry for MySQL, Neo4j, Chroma',
    selected_draft_id BINARY(16) DEFAULT NULL
        COMMENT 'Exact approved revision selected for publication',
    attempt_count INT UNSIGNED NOT NULL DEFAULT 0,
    lease_token BINARY(16) DEFAULT NULL,
    lease_expires_at DATETIME(6) DEFAULT NULL,
    error_code VARCHAR(64) DEFAULT NULL,
    error_message TEXT DEFAULT NULL,
    started_at DATETIME(6) DEFAULT NULL,
    finished_at DATETIME(6) DEFAULT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
        ON UPDATE CURRENT_TIMESTAMP(6),

    PRIMARY KEY (id),
    UNIQUE KEY uq_ingestion_request (requested_by, idempotency_key),
    KEY idx_ingestion_version (material_version_id, created_at),
    KEY idx_ingestion_worker (status, lease_expires_at, created_at),
    KEY idx_ingestion_selected_draft (id, selected_draft_id),
    CONSTRAINT fk_ingestion_version FOREIGN KEY (material_version_id)
        REFERENCES material_versions(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_ingestion_requester FOREIGN KEY (requested_by)
        REFERENCES users(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT chk_ingestion_source_policy
        CHECK (source_policy IN ('DOCUMENT_ONLY', 'EXTERNAL_ALLOWED')),
    CONSTRAINT chk_ingestion_status CHECK (status IN (
        'QUEUED', 'PROCESSING', 'AWAITING_REVIEW', 'PUBLISHING',
        'COMPLETED', 'FAILED', 'CANCELLED')),
    CONSTRAINT chk_ingestion_selected_revision CHECK (
        status NOT IN ('PUBLISHING', 'COMPLETED') OR selected_draft_id IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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

-- A job can only select one of its own draft revisions.
ALTER TABLE ingestion_jobs
    ADD CONSTRAINT fk_ingestion_selected_draft
    FOREIGN KEY (id, selected_draft_id)
    REFERENCES knowledge_graph_drafts(job_id, id)
    ON DELETE RESTRICT ON UPDATE RESTRICT;

-- Approval roles, immutable payloads and valid state transitions are service rules.
-- Selecting a revision does not itself approve/publish it.
