# Knowledge graph API implementation

2026-11-08. Approved plan in D:/ILMS-AI/.docs/knowledge-graph-api-plan.md.

STATUS: PARTIAL
SUMMARY: Implemented BE and AI code for graph views, revision editing, node/edge changes, approval, same-source republishing, withdrawal, retry and audit. Runtime verification remains for the user.
FILES: KnowledgeGraphController, GraphDtos, GraphAccessService, GraphPermissionRepository, KnowledgeGraphRepository, GraphCodec, GraphAiClient, KnowledgeGraphService, legacy ingestion integration, one new migration and GraphAccessServiceTest. AI has internal graph routes, pure document/editor/view logic and publication lifecycle checks.
CHECKS: Java syntax checked. Python AST checked. Full compile, tests, build and Flyway not run under the user's instructions.
ASSUMPTIONS: Teachers can self-review their own uploads while teaching that course. Owners can manage shared material across the active linked classes they own. ADMIN has full module scope. USER permissions are seeded and still require class authorization.
RISKS / LIMITATIONS: Existing databases need the new audit/permission migration. No frontend changes in this request. Historic graph data outside the ingestion contract requires separate reconciliation.
DOCS: docs/knowledge-graph-api.md and task/architecture references updated.
DEPLOYMENT: Not deployed.
NEXT: Apply the migration on the intended database and exercise the API with admin, teacher, owner and student accounts.

## Review

Confirmed that public controllers use the authenticated User, resource ownership is verified in the service, node attributes are allowlisted in AI, mutation/review uses a revision/hash check, replay is bound to actor/material/request, and publisher activation checks current publication/generation. Destructive graph edits create revisions or lifecycle events and preserve source/history. Student graph DTOs omit solution steps, reviewer evidence and internal teaching fields.
