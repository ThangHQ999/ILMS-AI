-- MANUAL CUTOVER ONLY, after 004-006 and the new writer/reader code is ready.
-- Existing writers that omit material_version_id will fail after this step.
-- Do not run while old ingestion is active.

-- Inspect the result first: chunks_without_version must be 0.
SELECT COUNT(*) AS chunks_without_version
FROM material_chunks WHERE material_version_id IS NULL;

-- New readers must select the published material version. Old readers see all versions.
-- ALTER fails if NULL values still exist. Confirm the old index name from SHOW CREATE TABLE.
ALTER TABLE material_chunks
    MODIFY COLUMN material_version_id BINARY(16) NOT NULL,
    DROP INDEX uk_doc_chunk_index;

-- uq_chunk_version_index(material_version_id, chunk_index) is now the identity constraint.
-- idx_chunk_material_version still supports the existing material FK after dropping its old index.
