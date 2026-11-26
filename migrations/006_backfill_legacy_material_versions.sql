-- Run after 004 + 005 with ingestion/chunk writers paused.
-- Preserve all existing chunk IDs and topic_chunks links.
-- UUID() is used only for legacy surrogate keys; new code should generate UUIDs itself.
-- No UUID_TO_BIN dependency. Original file hash/snapshot cannot be invented by SQL.

START TRANSACTION;

INSERT INTO material_versions (
    id, material_id, version_number, source_hash, source_snapshot_url,
    parser_version, chunker_version, created_by, created_at
)
SELECT
    UNHEX(REPLACE(UUID(), '-', '')), m.id, 1, NULL, NULL,
    'legacy', 'legacy', m.uploaded_by, CURRENT_TIMESTAMP(6)
FROM materials m
WHERE EXISTS (SELECT 1 FROM material_chunks c WHERE c.material_id = m.id)
  AND NOT EXISTS (
      SELECT 1 FROM material_versions v WHERE v.material_id = m.id AND v.version_number = 1
  );

UPDATE material_chunks c
JOIN material_versions v ON v.material_id = c.material_id AND v.version_number = 1
SET c.material_version_id = v.id
WHERE c.material_version_id IS NULL;

COMMIT;

-- Must return 0 before 007.
SELECT COUNT(*) AS chunks_without_version
FROM material_chunks WHERE material_version_id IS NULL;

-- Must return no rows before 007.
SELECT material_version_id, chunk_index, COUNT(*) AS duplicate_count
FROM material_chunks
GROUP BY material_version_id, chunk_index
HAVING COUNT(*) > 1;

-- Remains NULL deliberately: imported data has not been teacher-approved by this SQL.
SELECT COUNT(*) AS materials_without_selected_publication
FROM materials WHERE published_version_id IS NULL;
