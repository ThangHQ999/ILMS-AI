-- One publication attempt per job; multiple historical publications per material.
-- is_current is NULL for all non-current rows, permitting history with a unique active pointer.
CREATE TABLE material_publications (
    id BINARY(16) NOT NULL,
    material_id BINARY(16) NOT NULL,
    material_version_id BINARY(16) NOT NULL,
    job_id BINARY(16) NOT NULL,
    draft_id BINARY(16) NOT NULL,
    status VARCHAR(24) NOT NULL DEFAULT 'PREPARING',
    is_current TINYINT UNSIGNED DEFAULT NULL,
    created_by BINARY(16) NOT NULL,
    published_by BINARY(16) DEFAULT NULL,
    published_at DATETIME(6) DEFAULT NULL,
    superseded_at DATETIME(6) DEFAULT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
        ON UPDATE CURRENT_TIMESTAMP(6),

    PRIMARY KEY (id),
    UNIQUE KEY uq_publication_job (job_id),
    UNIQUE KEY uq_material_current_publication (material_id, is_current),
    KEY idx_publication_material_version (material_id, material_version_id),
    KEY idx_publication_version_job (material_version_id, job_id),
    KEY idx_publication_job_draft (job_id, draft_id),
    KEY idx_publication_creator (created_by),
    KEY idx_publication_publisher (published_by),
    CONSTRAINT fk_publication_material_version
        FOREIGN KEY (material_id, material_version_id)
        REFERENCES material_versions(material_id, id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_publication_version_job
        FOREIGN KEY (material_version_id, job_id)
        REFERENCES ingestion_jobs(material_version_id, id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_publication_job_draft
        FOREIGN KEY (job_id, draft_id)
        REFERENCES knowledge_graph_drafts(job_id, id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_publication_creator FOREIGN KEY (created_by)
        REFERENCES users(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_publication_publisher FOREIGN KEY (published_by)
        REFERENCES users(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT chk_publication_status CHECK (
        status IN ('PREPARING', 'PUBLISHED', 'SUPERSEDED', 'FAILED')),
    CONSTRAINT chk_publication_current_value CHECK (is_current IS NULL OR is_current = 1),
    CONSTRAINT chk_publication_current_state CHECK (
        (status = 'PUBLISHED' AND is_current IS NOT NULL AND is_current = 1)
        OR (status <> 'PUBLISHED' AND is_current IS NULL)),
    CONSTRAINT chk_publication_audit CHECK (
        status NOT IN ('PUBLISHED', 'SUPERSEDED')
        OR (published_by IS NOT NULL AND published_at IS NOT NULL)),
    CONSTRAINT chk_publication_superseded CHECK (
        status <> 'SUPERSEDED' OR superseded_at IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
