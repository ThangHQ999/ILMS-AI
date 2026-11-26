# Material ingestion API

Spring Boot owns file storage, jobs, chunks and draft revisions. FastAPI receives authenticated file bytes and returns a draft in memory. The upload API produces no per-stage trace files. Use /materials or the Spring Boot endpoints below to verify the production workflow.

| Method | Route | Input |
|---|---|---|
| POST | /api/v1/materials | Multipart file, title, subject, courseId |
| GET | /api/v1/materials/ingestion/{jobId} | Job status and latest draft |
| POST | /api/v1/materials/ingestion/{jobId}/retry | Requeue a failed job |
| POST | /api/v1/materials/ingestion/{jobId}/drafts | JSON baseHash and edited graph |
| POST | /api/v1/materials/ingestion/{jobId}/review | JSON baseHash, decision and optional comment |
| GET | /api/v1/materials/{materialId}/ingestion/{jobId}/file | Original source download for the uploader or admin |

Use the existing authenticated Spring Boot session. A teacher needs an active teacher or owner role on a class linked to the course. An admin can omit courseId. Draft access is limited to the uploader and admins.

Upload returns HTTP 202 with materialId, versionId, jobId and status. Poll the job endpoint until AWAITING_REVIEW or FAILED. On AWAITING_REVIEW the response includes graph, source evidence, validation, revision and hash. Use the current hash as baseHash when saving or reviewing. Each save creates a separate revision.

The Spring Boot worker calls POST /api/v1/internal/ingestion/draft with application/octet-stream and material_id, version_id, filename and source_hash query parameters. It uses the existing FastAPI base URL and internal key configuration. Keep ingestion.storage-root on persistent storage accessible by every Spring Boot worker. The default is ./material-storage and the default upload limit is 30 MiB. The AI worker reads INGESTION_MAX_FILE_MB and INGESTION_API_PARALLEL_CHUNKS. Keep upload limits aligned.

MySQL stores materials, material_versions, ingestion_jobs, material_chunks and knowledge_graph_drafts. Uploaded sources are stored as immutable files on the Spring Boot host. Chunks from this path are marked as draft and excluded from the Socratic Topic reader. Keep existing Flyway schema compatible with the current migrations.

The review endpoint records a decision on a specific revision. Approval queues publication. The teacher UI can open the Neo4j draft graph before approval.

## Publication and teacher workspace

The teacher workspace is available at /materials. GET /api/v1/materials/ingestion lists recent jobs. Save and review accept baseRevisionId with baseHash. Approving a revision queues publication. The Spring Boot worker invokes POST /api/v1/internal/ingestion/publications/{jobId}, which stages Neo4j and Chroma before activating the current MySQL publication. Chat reads current publications allowed by material access. See .reports/2026-11-05-ingestion-publication.md for verification and remaining limitations.

Draft graph reads use GET /api/v1/materials/ingestion/{jobId}/drafts/{revisionId}/graph. Spring Boot checks job access before contacting FastAPI. MySQL retains immutable revisions and autosave concurrency checks. Neo4j stores the editable graph by revision, synchronized by a scheduled worker with on-demand catch-up. The Socratic reader continues to use current publications only.
