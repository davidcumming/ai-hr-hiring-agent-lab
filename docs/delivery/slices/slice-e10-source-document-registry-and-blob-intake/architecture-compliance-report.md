# Architecture Compliance Report: E10 Source Document Registry and Blob Intake Foundation

Verdict: **Clear for deterministic implementation under the E10 scope**

## Inputs

- User-approved E10 implementation plan in the Codex implementation turn.
- Buildout authority:
  `docs/hr_hiring_agent_mvp_workflow_azure_build_overlay_v0_1.md`.
- Current-state architecture:
  `docs/architecture/actual-technical-architecture.md`.
- Storage seam detail:
  `docs/architecture/provider-and-storage-seams.md`.
- Approved ADRs: none in `docs/architecture/`; the existing Foundry ADR draft
  is unrelated to deterministic source-document registry work.

## Compliance Surface

E10 introduces a narrow public FastAPI source-document facade over the E7/E8
workflow storage seam. It adds strict request/response schemas, deterministic
service logic, canonical role-source Blob writes, `SourceDocuments` metadata,
one `CaseEvents` row per registration, deterministic task/gate updates,
source OpenAPI coverage, tests, and current-state docs.

It does not add Copilot Studio actions, curated document Swagger, Power
Platform connector changes, applicant import, candidate documents, queues,
workers, notifications, Foundry/model calls, live Azure smoke, Azure resource
creation, production identity, or case-scoped authorization.

## Findings

| Area | Finding | Rationale |
|---|---|---|
| Workflow source-document intake | Compliant | The overlay identifies Blob document storage plus `SourceDocuments` as required before later posting, rubric, applicant, and assessment slices. E10 keeps this to one role-source intake capability. |
| Workflow storage seam usage | Compliant | The source-document service depends only on `WorkflowStorageBackend`. It writes through the Table and Blob protocol methods and imports no concrete local/Azure adapters or SDKs. |
| Canonical Blob path | Compliant | E10 uses the existing `role_source_raw_path(case_id, document_id)` path builder and adds no alternate document path convention. |
| Metadata-first tables | Compliant | `SourceDocuments` and `CaseEvents` store identifiers, labels, hashes, sizes, status, and safe details only. Raw source text is stored only in Blob and is not returned by GET/list APIs. |
| Task/gate behavior | Compliant | The implementation completes only the existing `attach_source_documents` task and satisfies only the existing `source_documents_required` gate. It does not fabricate missing rows or unlock downstream assessment gates. |
| Source OpenAPI vs curated Copilot Swagger | Compliant | The source OpenAPI adds E10 document routes. The curated Copilot Swagger remains evaluation-only with exactly `submitEvaluation`, `getEvaluation`, and `retrieveEvaluationForCopilot`. |
| Authorization model | Compliant for lab scope | E10 preserves simulated header identity and the global `hr` lab role requirement. Case-scoped ACLs and production identity are deferred. |
| Architecture guideline gap | Recorded non-blocking caveat | The repo currently has no formal architecture guideline docs or approved storage/case ADRs under `docs/architecture/`. E10 follows the established E7/E8 workflow storage seam and overlay without adding a new cloud service category or live runtime. |

## ADR Gap Disposition

No blocking ADR is required before E10 because it is deterministic facade work
over the already established workflow storage seam and does not add live cloud
behavior, production identity, workers, queue production, model execution, or
a new service category. A future ADR may still be useful before production
document intake, retention, document revisions, case authorization,
source-controlled Copilot ALM, or Azure resource provisioning.

## Handoff

Later source-document slices should preserve these boundaries unless
explicitly widened:

- Add normalized text extraction, queue processing, duplicate detection, and
  document revisions only as separate slices.
- Add applicant/candidate documents separately from role source documents.
- Add Copilot/Power Platform document actions only in a separate connector
  slice with curated Swagger and manual/source-control evidence.
