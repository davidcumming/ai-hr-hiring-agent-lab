# Architecture Compliance Report: E9 Case State Foundation API

Verdict: **Clear for deterministic local implementation under the E9 scope**

## Inputs

- User-provided E9 implementation plan in the Codex implementation turn.
- Buildout authority:
  `docs/hr_hiring_agent_mvp_workflow_azure_build_overlay_v0_1.md`.
- Current-state architecture:
  `docs/architecture/actual-technical-architecture.md`.
- Storage seam detail:
  `docs/architecture/provider-and-storage-seams.md`.
- Approved ADRs: none in `docs/architecture/`; the existing Foundry ADR draft
  is unrelated to this deterministic storage/API foundation.

## Compliance Surface

E9 introduces a narrow public FastAPI case facade over the E7/E8 workflow
storage Table seam. It adds request/response schemas, deterministic service
logic, source OpenAPI coverage, focused tests, and current-state docs.

It does not add Copilot Studio actions, curated case Swagger, Power Platform
connector changes, search, documents, applicant import, notifications, queue
workers, Blob artifact writes, Foundry/model calls, live Azure smoke, Azure
resource creation, production identity, or case-scoped authorization.

## Findings

| Area | Finding | Rationale |
|---|---|---|
| Start/continue recruitment case workflow | Compliant | The overlay identifies Stage 1 as starting or continuing a recruitment case. E9 creates the initial case state, owner/participant rows, tasks, gates, and event without moving into documents, applicants, assessment, or review. |
| Workflow storage seam usage | Compliant | The case service depends only on `WorkflowStorageBackend` and writes Table-shaped workflow entities. It does not import concrete local/Azure adapters or Azure SDKs. |
| Local deterministic default | Compliant | `create_app()` continues to select `LocalWorkflowStore` by default. Tests pin no Azure SDK imports on clean default app construction. |
| Source OpenAPI vs curated Copilot Swagger | Compliant | The source OpenAPI adds E9 case routes. The curated Copilot Swagger remains evaluation-only with exactly `submitEvaluation`, `getEvaluation`, and `retrieveEvaluationForCopilot`. |
| Authorization model | Compliant for lab scope | E9 preserves simulated header identity and the global `hr` lab role requirement. Case-scoped ACLs and production identity are deferred. |
| Architecture guideline gap | Recorded non-blocking caveat | The repo currently has no formal architecture guideline docs or approved case/storage ADRs under `docs/architecture/`. The user explicitly approved the E9 implementation plan, and E9 follows the E7/E8 workflow storage seam plus the overlay. No new cloud service category or live model path is introduced. |

## ADR Gap Disposition

No blocking ADR is required before E9 because it is a deterministic facade over
the already established E7/E8 workflow storage seam and does not add live
cloud behavior, production identity, queue workers, model execution, or a new
service category. A future ADR may still be useful before production case
authorization, concurrency/ETag policy, retention, live workflow workers,
source-controlled Copilot ALM, or Azure resource provisioning.

## Handoff

E10+ work should preserve these boundaries until explicitly widened:

- Keep case logic behind the workflow storage seam.
- Add a Copilot case wrapper or curated case Swagger only in a separate
  Copilot case-tool slice.
- Add workers, queue writes, document APIs, applicant import, and notification
  APIs only as separately scoped slices with deterministic tests and current
  docs updates.
