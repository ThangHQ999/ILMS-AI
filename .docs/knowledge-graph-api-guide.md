# Knowledge graph management API

Implemented 2026-11-08. Public endpoints are authenticated Spring Boot APIs under /api/v1/knowledge-graphs. Internal FastAPI routes require the existing service key. The module uses ADMIN/USER at system level and ACTIVE class_members roles at resource level.

## Setup

Apply V20261108120000__knowledge_graph_events_and_permissions.sql on the intended database before enabling this module. It creates one audit table and seeds KNOWLEDGE_GRAPH_READ, EDIT, REVIEW, WITHDRAW and AUDIT permissions for the existing USER and ADMIN roles. No new system role is introduced. Removing a USER permission disables that module action even when the class role would otherwise allow it. ADMIN retains full management scope.

## Access policy

| Actor | Read published | Manage draft and review | Withdraw |
|---|---|---|---|
| ADMIN | All materials | All materials | All materials |
| ACTIVE OWNER | Enrolled course materials | Material linked to classes the actor owns across the active course scope | Same managed scope |
| ACTIVE TEACHER | Enrolled course materials | Own uploads while still teaching that course | Denied |
| ACTIVE STUDENT | Enrolled course materials | Denied | Denied |
| Authenticated USER outside class | Explicit GLOBAL material with READ permission | Denied | Denied |

For a course shared by multiple active classes, ownership of one class does not grant management of other teachers' shared uploads. An OWNER must own all active linked classes to manage that shared scope. A teacher uploader can review their own material. Archived/deleted classes and deleted courses do not grant access. Decisions are evaluated from current database records, rather than global teacher/student authorities.

## Endpoints

| Method | Path | Result |
|---|---|---|
| GET | /published | Cursor page of accessible published materials |
| GET | /published/materials/{materialId} | Current graph, capabilities and scoped node/edge page |
| GET | /published/concepts/{canonicalCode} | Contributions from accessible materials |
| GET | /materials/{materialId}/revisions | Revision metadata without full graph payloads |
| GET | /drafts/{jobId} | Latest revision ID/hash for conflict recovery |
| GET | /drafts/{jobId}/revisions/{revisionId} | Typed graph view and validation issues |
| POST | /materials/{materialId}/drafts | Create an edit session from current or historical revision |
| POST | /drafts/{jobId}/changes | Apply operations and create a new revision |
| POST | /drafts/{jobId}/review | Approve, reject or request changes |
| DELETE | /drafts/{jobId} | Cancel an open draft session |
| POST | /materials/{materialId}/publications/{publicationId}/withdraw | Withdraw the exact current publication |
| GET | /publications/{publicationId} | Publication state, stage and retryability |
| POST | /publications/{publicationId}/retry | Resume a retryable failed publication |
| GET | /materials/{materialId}/audit | Cursor page of audit events |

All public responses use ApiResponse with the payload under data. List queries accept limit and after. Published catalog also accepts courseId, subject and q. Revision history uses the UUID cursor returned by the server. Audit uses a numeric event cursor. Graph views accept nodeId, depth (0..4), limit (1..500), and after. Pagination includes only edges with both endpoints on the returned node page; fetch a neighborhood around a selected node to explore related nodes. The concept response has a material cursor; each contribution may also have its own node cursor.

## Frontend sequence

1. Use the published catalog or an ingestion job to obtain material/job/revision IDs.
2. GET the draft view to receive stable business node IDs and validationIssues. Node IDs are scoped to the revision and are not Neo4j internal IDs. The legacy canvas endpoint still exposes its older projection IDs; use IDs from the new API for new mutations.
3. Start an editing session for an already published material, passing the expected current publication ID. The file source version is reused. An explicit historical baseRevisionId restores that snapshot into a new draft.
4. Submit changes with baseRevisionId, baseHash and a unique clientRequestId. Store the new revision/hash from the response after every save. A replay returns the original revision and idMappings, rather than another write.
5. On HTTP 409 retain local edits and GET /drafts/{jobId} for the latest base before presenting a merge or reload choice.
6. Fix BLOCKER issues before approval. Acknowledge WARNING issue IDs explicitly in review. Poll the returned publicationId until PUBLISHED or FAILED. Use retryable before offering Retry.

Example start request.

~~~json
{
  "expectedCurrentPublicationId": "<current-publication-uuid>",
  "clientRequestId": "<new-request-uuid>",
  "reason": "Correct definition and exercise ownership"
}
~~~

Example changes. A CREATE_NODE may use nodeId as a temporary alias. Later operations in the same batch can refer to it; the server returns the actual UUID in idMappings.

~~~json
{
  "baseRevisionId": "<revision-uuid>",
  "baseHash": "<hash>",
  "clientRequestId": "<new-request-uuid>",
  "operations": [
    {"op": "UPDATE_NODE", "nodeId": "<definition-id>", "fields": {"content": "Corrected definition"}},
    {"op": "MOVE_NODE", "nodeId": "<exercise-id>", "newParentId": "<concept-id>"},
    {"op": "CREATE_NODE", "nodeId": "new-example", "kind": "EXAMPLE", "parentId": "<concept-id>",
     "fields": {"title": "Example", "explanation": "Teacher-authored example"}}
  ]
}
~~~

Other operations are DELETE_NODE, CREATE_EDGE, UPDATE_EDGE, DELETE_EDGE, LINK_TOPIC_CHUNK and UNLINK_TOPIC_CHUNK. Semantic edges require two concept IDs and an allowed relation kind. Structural ownership is changed with MOVE_NODE. DELETE_NODE rejects children unless cascade is explicit. CHUNK source text is read-only through graph APIs. Node fields are allowlisted by kind. Owner, scope, canonical code and publication IDs are server-managed. Renaming an existing concept preserves its canonical code.

Example review.

~~~json
{
  "revisionId": "<saved-revision-uuid>",
  "baseHash": "<hash>",
  "decision": "APPROVED",
  "acknowledgedIssueIds": ["<warning-id>"],
  "comment": "Source and ownership reviewed"
}
~~~

## Persistence and recovery

Spring Boot owns authorization, audit, short MySQL transactions and current-pointer changes. FastAPI validates/applies graph transformations without calling an LLM and prepares Neo4j/Chroma publication data. HTTP requests to AI occur before the BE transaction locks; the BE checks the base again under locks before committing. Material locks precede job locks.

Draft snapshots remain immutable in MySQL and are synchronized into Neo4j by the existing projection worker. Typed graph DTOs are derived from the exact persisted snapshot, while the existing Neo4j canvas endpoint remains available. Node mutations never write directly into a published graph.

Approval captures the current publication and material generation. Publisher activation checks both under the material lock, allowing graph edits on the same source version and preventing an older job from overwriting a publish/withdraw that occurred meanwhile. Failed index preparation retains the existing publication. Conflict and invalid-graph failures require a new edit session, rather than retrying an obsolete base.

Withdrawal marks the current row SUPERSEDED and records WITHDRAWN, retains history, and removes active topic links for that material. Purging historical data is outside this CRUD workflow. Graph deletion does not remove source chunks from the uploaded material.

## Internal concept catalog for assessments

`POST /api/v1/internal/knowledge-graphs/concept-catalog` uses the existing internal service key. Spring Boot authorizes its caller for the course and selects the visible current publications before requesting the catalog. The request contains `courseId` and `publicationIds`, both UUIDs, with at most 100 publication IDs per batch. An empty selection returns an empty catalog.

The response contains `courseId` and `concepts`, a list of `{canonicalCode, label}` sorted by code. When several publications contain one code, the most recently published label takes precedence. Only current approved publications that resolve to the requested course qualify. A stale or out-of-scope publication returns HTTP 404 `CONCEPT_CATALOG_PUBLICATION_NOT_FOUND` for the whole batch. An invalid graph payload returns HTTP 422 `INVALID_PUBLISHED_CONCEPT_GRAPH`.

The catalog reads the approved MySQL payload. It accepts the canonical code in the nested ingestion and flat imported graph formats. Older ingestion records with absent codes use the same deterministic calculation as publication when their source chunk scope is available. A node without a canonical identity is omitted. The catalog carries no question, answer, student result or graph source text. Spring Boot retains responsibility for question mapping, attempt scoring and the knowledge heatmap.

## Validation status

Code was reviewed statically. Python AST and Java source syntax were checked. GraphAccessServiceTest covers the two-tier permission rules but has not been executed. Application startup, build, database migration, DB/API/LLM calls and runtime behavior remain unverified.
