# Implementation Notes: E11 Role Intake and Approved Rubric Foundation

## What Changed

- Added role-intake endpoints:
  - `POST /api/cases/{case_id}/role-intake` /
    `createRoleIntakeArtifact`
  - `GET /api/cases/{case_id}/role-intake` / `getCaseRoleIntake`
- Added approved-rubric endpoints:
  - `POST /api/cases/{case_id}/rubrics` / `registerApprovedRubric`
  - `GET /api/cases/{case_id}/rubrics` / `listCaseRubrics`
  - `GET /api/cases/{case_id}/rubrics/{rubric_version}` /
    `getCaseRubric`
- Added strict role-intake and rubric request schemas in
  `src/hr_eval_lab/domain/schemas/cases.py`.
- Added `role_intake_artifact_path(case_id, version)` for the overlay path
  `case-artifacts/cases/{case_id}/intake/{version}/intake.json`.
- Added `src/hr_eval_lab/cases/role_intake_rubrics.py`, a focused service
  that depends only on `WorkflowStorageBackend`.
- Added `src/hr_eval_lab/api/routes_role_intake_rubrics.py` and registered it
  from the app factory.
- Regenerated the source OpenAPI artifact at `openapi/evaluations-api.json`.
- Updated tests and the Copilot Swagger guard so the source OpenAPI contains
  E11 paths while the curated Copilot artifact remains evaluation-only.

## Persisted Workflow State

Successful role-intake creation writes through the workflow storage seam:

- Blob:
  `case-artifacts/cases/{case_id}/intake/{version}/intake.json`.
- `ArtifactVersions`: one approved `role_intake` row with canonical path,
  hash, source-document ids, and `approved_version_required=true`.
- `CaseEvents`: one `role_intake_artifact_created` row.
- `RecruitmentCases`: `active_intake_version`.
- `CaseTasks` / `WorkflowGates`: if existing role-intake task/gate rows are
  open/blocked and not satisfied/waived, they are completed/satisfied and
  linked to the event id.

Successful rubric registration writes:

- Blob:
  `case-artifacts/cases/{case_id}/rubric/{version}/rubric.json`.
- `ArtifactVersions`: one approved `screening_rubric` row.
- `Approvals`: one synthetic HR approval row tied to the rubric version.
- `CaseEvents`: one `rubric_approved` row.
- `RecruitmentCases`: `active_rubric_version`.
- `WorkflowGates`: if the existing `rubric_approval_required` gate is not
  satisfied/waived, it is marked satisfied and linked to the event id.

E11 does not write applicants, candidate packages, model assessment jobs,
queue messages, notifications, normalized text, readiness results, or
Copilot state.

## API Behavior

- Routes authenticate/authorize first, then parse and validate bodies.
- Malformed bodies, missing fields, extra fields, unsupported shapes,
  duplicate criterion/source ids, unsafe versions, and `synthetic=false`
  return HTTP 400 `malformed_request_body`.
- Unknown `case_id` returns HTTP 200 with `status="validation_failed"` and
  `errors=["unknown_case_id"]`.
- Missing source documents for role intake returns
  `errors=["source_documents_required"]`.
- Duplicate role-intake or rubric versions return
  `role_intake_version_exists` or `rubric_version_exists`.
- Unknown rubric versions return `errors=["unknown_rubric_version"]`.
- GET responses return artifact payloads and metadata only; raw source-document
  text is not read or returned.

## Manual Gate A Troubleshooting Diagnostic

After E11 deployment, hosted Manual Gate A troubleshooting may use
`GET /api/diagnostics/workflow-storage` to isolate workflow Table, Blob, and
Queue connectivity from the normal case-creation path. This endpoint is
guarded troubleshooting-only behavior, not product behavior and not a Copilot
tool surface.

- It is disabled unless `HRHA_ENABLE_DIAGNOSTICS=true`.
- It is hidden from source OpenAPI and the curated Copilot Swagger.
- It still requires the simulated lab auth headers `X-Lab-Actor-Id` and
  `X-Lab-Roles: hr`.
- It reports only safe booleans and class names for selected workflow storage
  configuration; it does not return account URLs, function keys, SAS tokens,
  account keys, connection strings, client IDs, or raw credential values.
- It writes, reads, and deletes only synthetic diagnostic workflow storage
  state for `case-diag-workflow-storage`.
- The Queue probe skips receive/delete when the configured workflow queue is
  not empty, so it does not delete existing workflow messages.

Manual Gate A also surfaced an Azure Table key compatibility issue: logical
workflow RowKeys intentionally contain `#` separators, but Azure Table
Storage rejects `#` in `PartitionKey` and `RowKey`. The Azure workflow
storage adapter now percent-encodes Table keys only at the Azure boundary and
decodes them before returning domain objects. Local workflow storage and the
domain RowKey conventions remain unchanged.

## Boundaries Preserved

- No Copilot Studio topic, connector action, or curated role/rubric Swagger was
  added.
- No queue worker, queue write, applicant import, candidate document route,
  notification API, assessment launcher, assessment readiness unlock,
  Foundry/model call, live Azure smoke, Azure resource creation, or production
  identity behavior was added.
- The services do not import `LocalWorkflowStore`, `AzureWorkflowStorageBackend`,
  Azure SDKs, provider code, queue writers, applicant/candidate package code,
  or Copilot tooling.

## Design Notes

- Duplicate version checks run before Blob writes so repeated same-version
  POSTs do not create extra artifacts.
- New versions of the same artifact type supersede prior approved versions,
  but this remains Table-row state rather than a cross-Blob/Table transaction.
- Rubric approval is a single synthetic HR lab approval, not the full
  future HR plus hiring-manager approval workflow.
- `assessment_unlocked` remains locked; a future readiness slice should own
  deterministic assessment unlock after applicant/package prerequisites exist.
