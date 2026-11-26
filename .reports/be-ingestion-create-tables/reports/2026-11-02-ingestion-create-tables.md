# Complete ingestion CREATE TABLE migrations

Date: 2026-11-02
STATUS: PARTIAL (database execution not verified)
AUTHORIZATION: The user explicitly requested editing the original CREATE migrations instead of ALTER migrations, and selected an additional material_publications table to remove FK cycles. This supersedes the repository's default migration-immutability restriction for these files only.

SUMMARY: Added complete material_versions, ingestion_jobs, knowledge_graph_drafts and material_publications CREATE TABLE migrations immediately after materials and before material_chunks. Updated the original materials/chunks CREATE statements; chunks now require a matching material version and have UNIQUE(material_version_id, chunk_index). No ALTER or disabled FK checks in these changed DDL files. Publication rows replace materials.published_version_id and jobs.selected_draft_id, eliminating cyclic FKs.

PUBLICATION: One attempt per job and at most one current PUBLISHED row per material via UNIQUE(material_id, is_current), using NULL for non-current rows. Composite FKs ensure material/version/job/draft consistency. Approval roles/hash validation and safe multi-store publication remain service rules. Lock the materials row when switching current publication, supersede the old row and activate the new row in one MySQL transaction. Never unpublish the previous revision just to create a PREPARING attempt.

SEED: Existing seed chunks receive a version-1 fixture reference without changing their IDs or content. Source hashes/snapshots stay NULL rather than claiming real source verification; no automatic publication/teacher approval is generated.

CHECKS: Static table/FK order, identifier/constraint uniqueness and seed field counts; no Gradle, Flyway, tests, app or database calls. Existing DBs are NOT upgraded by editing historical files; no repair/checksum/history changes performed. Fresh-schema definitions only.

LIMITATIONS: Entities, ingestion writers and published-version retrieval have not been implemented by this SQL-only request. RESTRICT prevents accidental loss of review history and may block prior hard-delete cascades. CHECK enforcement depends on server version; backend validation is still required.

DOCS: ARCHITECTURE, docs/api-spec and TASKS updated.
DEPLOYMENT: not deployed.
NEXT: Review/apply on a fresh schema manually; implement version-aware writer/reviewer/publisher/reader before using the new workflow.

## Review
No topics/topic_chunks changes, source UUID encoding changes, secret/config edits, DB resets or automatic approvals. Cyclic selected/publication pointers are absent. Existing numbered Flyway migrations were edited only within the user's explicit authorization.
