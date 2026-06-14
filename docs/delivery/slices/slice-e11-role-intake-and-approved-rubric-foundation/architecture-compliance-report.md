# Architecture Compliance Report: E11 Role Intake and Approved Rubric Foundation

Verdict: **Clear for deterministic implementation under the E11 scope**

## Inputs

- User-approved E11 implementation plan in the Codex implementation turn.
- Buildout authority:
  `docs/hr_hiring_agent_mvp_workflow_azure_build_overlay_v0_1.md`.
- Current-state architecture:
  `docs/architecture/actual-technical-architecture.md`.
- Storage seam detail:
  `docs/architecture/provider-and-storage-seams.md`.
- Approved ADRs: none in `docs/architecture/`; the existing Foundry ADR draft
  is unrelated to deterministic role-intake/rubric artifact registration.

## Compliance Surface

E11 adds a narrow public FastAPI facade for deterministic role-intake artifact
creation/retrieval and approved synthetic rubric registration/retrieval. It
adds strict request/response schemas, one role-intake Blob path builder, a
service over `WorkflowStorageBackend`, `ArtifactVersions` and rubric
`Approvals` writes, case active-version updates, deterministic task/gate
updates, source OpenAPI coverage, tests, and current-state docs.

It does not add Copilot Studio actions, curated role/rubric Swagger, Power
Platform connector changes, applicant import, candidate packages, queues,
workers, notifications, Foundry/model calls, live Azure smoke, Azure resource
creation, production identity, or case-scoped authorization.

## Findings

| Area | Finding | Rationale |
|---|---|---|
| Role-intake artifact foundation | Compliant | The overlay identifies structured intake artifacts under `case-artifacts/cases/{case_id}/intake/{version}/intake.json` and `ArtifactVersions` as required before later rubric, readiness, and assessment work. |
| Approved rubric foundation | Compliant | The overlay identifies approved rubric artifacts under `case-artifacts/cases/{case_id}/rubric/{version}/rubric.json`, version metadata, approvals, and an assessment-blocking rubric gate. |
| Workflow storage seam usage | Compliant | The E11 service depends only on `WorkflowStorageBackend`; routes obtain storage from `request.app.state.workflow_storage`. |
| Canonical Blob paths | Compliant | E11 reuses `rubric_artifact_path()` and adds only the missing overlay-aligned `role_intake_artifact_path()`. |
| Metadata-first tables | Compliant | Full synthetic artifacts are stored in Blob; Table rows store artifact metadata, hashes, versions, approvals, events, and active case version pointers. |
| Task/gate behavior | Compliant | E11 completes/satisfies only existing role-intake and rubric prerequisite rows and does not fabricate missing tasks/gates or unlock assessment. |
| Source OpenAPI vs curated Copilot Swagger | Compliant | Source OpenAPI includes E11 routes; curated Copilot Swagger remains evaluation-only. |
| Authorization model | Compliant for lab scope | E11 preserves simulated header identity and the global `hr` lab role requirement. Case-scoped ACLs and production identity remain deferred. |
| Architecture guideline gap | Recorded non-blocking caveat | The repo currently has no formal architecture guideline docs or approved storage/case ADRs under `docs/architecture/`. E11 follows the established deterministic workflow storage seam and overlay without adding a new cloud service category or live runtime. |

## ADR Gap Disposition

No blocking ADR is required before E11 because it is deterministic facade work
over the already established workflow storage seam and does not add live cloud
behavior, production identity, queue production, model execution, or a new
service category. A future ADR may still be useful before production document
retention/revision policy, case-scoped authorization, readiness unlock policy,
source-controlled Copilot ALM, or Azure resource provisioning.

## Handoff

Later slices should preserve these boundaries unless explicitly widened:

- Add applicant import and candidate package assembly separately.
- Add deterministic assessment readiness/unlock as a separate slice.
- Add Copilot/Power Platform role/rubric actions only in a separate connector
  slice with curated Swagger and manual/source-control evidence.
