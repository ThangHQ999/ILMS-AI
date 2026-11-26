-- Source policy, processing checkpoints and worker leases. Publication selection is stored separately.
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
    UNIQUE KEY uq_ingestion_version_job (material_version_id, id),
    KEY idx_ingestion_worker (status, lease_expires_at, created_at),
    CONSTRAINT fk_ingestion_version FOREIGN KEY (material_version_id)
        REFERENCES material_versions(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_ingestion_requester FOREIGN KEY (requested_by)
        REFERENCES users(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT chk_ingestion_source_policy
        CHECK (source_policy IN ('DOCUMENT_ONLY', 'EXTERNAL_ALLOWED')),
    CONSTRAINT chk_ingestion_status CHECK (status IN (
        'QUEUED', 'PROCESSING', 'AWAITING_REVIEW', 'PUBLISHING',
        'COMPLETED', 'FAILED', 'CANCELLED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
