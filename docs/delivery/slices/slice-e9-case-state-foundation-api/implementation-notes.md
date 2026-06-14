# Implementation Notes: E9 Case State Foundation API

## What Changed

- Added the first recruitment-case facade endpoints:
  - `POST /api/cases` / `createRecruitmentCase`
  - `GET /api/cases/{case_id}` / `getRecruitmentCase`
  - `GET /api/cases/{case_id}/next-actions` / `getCaseNextActions`
- Added strict case request/response schemas in
  `src/hr_eval_lab/domain/schemas/cases.py`, including a case-specific
  envelope that preserves the standard envelope shape without changing the
  existing evaluation `Envelope`.
- Added deterministic case identity helpers in `src/hr_eval_lab/domain/ids.py`.
- Added `src/hr_eval_lab/cases/service.py`, a service layer that depends only
  on `WorkflowStorageBackend`.
- Added `src/hr_eval_lab/api/routes_cases.py` and registered it from the app
  factory. The routes authenticate first, validate second, then call the case
  service through `request.app.state.workflow_storage`.
- Regenerated the source OpenAPI artifact at `openapi/evaluations-api.json`.
- Updated the Copilot Swagger exporter and tests so the source OpenAPI can
  contain case paths while the curated Copilot artifact remains
  evaluation-only.

## Persisted Workflow State

Case creation writes only Table-shaped workflow entities through the workflow
storage seam:

- `RecruitmentCases`: one case row with `case_status="intake_pending"`,
  `current_stage="stage_1_start_or_continue"`, and
  `current_gate="role_intake_required"`.
- `CaseParticipants`: one HR owner row and, when supplied, one hiring-manager
  row.
- `CaseTasks`: `complete_role_intake`, `attach_source_documents`, and
  `confirm_hiring_manager` only when the hiring manager is missing or
  unconfirmed.
- `WorkflowGates`: `role_intake_required`, `source_documents_required`,
  `rubric_approval_required`, `applicant_set_confirmation_required`, and
  `assessment_unlocked`.
- `CaseEvents`: one `case_created` event.

GET case and GET next-actions are read-only in E9.

## Boundaries Preserved

- No Copilot Studio topic, connector action, or curated case Swagger was
  added.
- No queue worker, queue write, Blob artifact write, document upload,
  applicant import, notification API, model assessment launcher, Foundry call,
  live Azure smoke, Azure resource creation, or production identity behavior
  was added.
- Case endpoints continue to use the simulated lab identity model and require
  the global `hr` lab role.
- The case service does not import `LocalWorkflowStore`,
  `AzureWorkflowStorageBackend`, Azure SDKs, provider code, Copilot tooling,
  or queue/blob writers.

## Design Notes

- Path-based `case_id` retrieval is sufficient for E9 because no Copilot case
  topic or connector slice exists yet. A body-bindable wrapper should wait for
  a separate Copilot case-tool slice if platform binding requires it.
- `RecruitmentCase.primary_hiring_manager_actor_id` now allows `None` so E9
  can represent a missing hiring manager without fabricating `"unassigned"`.
- Next actions are deterministic business-language mappings from persisted
  tasks and gates. They are not model recommendations.
- Unknown case ids return HTTP 200 with `status="validation_failed"`,
  `result=null`, and `errors=["unknown_case_id"]`.

## Operational Handoff Note

- No commit, push, merge, GitHub issue, Azure resource creation, portal
  change, Copilot Studio change, Power Platform connector change, live Foundry
  action, or live Azure smoke was performed for E9.
