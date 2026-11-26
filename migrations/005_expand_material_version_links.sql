-- Run once after 004. Additive phase; existing writers may still omit the nullable key.

ALTER TABLE materials
    ADD COLUMN published_version_id BINARY(16) DEFAULT NULL
        COMMENT 'Current published version; NULL means no version selected',
    ADD KEY idx_material_published_version (id, published_version_id),
    ADD CONSTRAINT fk_material_published_version
        FOREIGN KEY (id, published_version_id)
        REFERENCES material_versions(material_id, id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE material_chunks
    ADD COLUMN material_version_id BINARY(16) DEFAULT NULL,
    ADD KEY idx_chunk_material_version (material_id, material_version_id),
    ADD UNIQUE KEY uq_chunk_version_index (material_version_id, chunk_index),
    ADD CONSTRAINT fk_chunk_material_version
        FOREIGN KEY (material_id, material_version_id)
        REFERENCES material_versions(material_id, id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;

-- Composite FKs prevent assigning a version from another material.
-- Existing uk_doc_chunk_index remains until 007: no multiple-version writes yet.
-- No published_version_id is inferred or selected by this migration.
