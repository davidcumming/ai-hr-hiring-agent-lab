# Implementation Notes: E10 Source Document Registry and Blob Intake Foundation

## What Changed

- Added the first source-document facade endpoints:
  - `POST /api/cases/{case_id}/source-documents` / `registerSourceDocument`
  - `GET /api/cases/{case_id}/source-documents` / `listCaseSourceDocuments`
  - `GET /api/cases/{case_id}/source-documents/{document_id}` /
    `getCaseSourceDocument`
- Added strict source-document request/response schemas in
  `src/hr_eval_lab/domain/schemas/cases.py`.
- Added `ids.new_document_id()` for deterministic `doc-*` id generation.
- Added `src/hr_eval_lab/cases/source_documents.py`, a focused service that
  depends only on `WorkflowStorageBackend`.
- Added `src/hr_eval_lab/api/routes_source_documents.py` and registered it
  from the app factory.
- Regenerated the source OpenAPI artifact at `openapi/evaluations-api.json`.
- Updated tests and the Copilot Swagger guard so the source OpenAPI contains
  the E10 paths while the curated Copilot artifact remains evaluation-only.

## Persisted Workflow State

Successful source-document registration writes through the workflow storage
seam:

- Blob: raw UTF-8 source text at
  `case-documents/cases/{case_id}/role-source/{document_id}/raw`.
- `SourceDocuments`: one metadata row with document type, origin, optional
  label/file metadata, canonical Blob path, hash, size, status `registered`,
  version `v1`, and `synthetic=true`.
- `CaseEvents`: one `source_document_registered` row with safe metadata only.
- `CaseTasks`: if `task#attach_source_documents` exists and is open/blocked,
  it is completed and linked to the event id.
- `WorkflowGates`: if `gate#source_documents_required` exists and is not
  already satisfied/waived, it is marked satisfied and linked to the event id.

E10 does not write `ArtifactVersions`, normalized text, applicant records,
candidate packages, queue messages, notifications, or assessment rows.

## API Behavior

- Routes authenticate/authorize first, then parse and validate bodies.
- Malformed bodies, missing fields, extra fields, unsupported MIME/types,
  `synthetic=false`, blank content, and oversized content return HTTP 400
  `malformed_request_body`.
- Unknown `case_id` returns HTTP 200 with `status="validation_failed"` and
  `errors=["unknown_case_id"]`.
- Unknown `document_id` returns HTTP 200 with `status="validation_failed"` and
  `errors=["unknown_document_id"]`.
- GET/list source-document routes return metadata summaries only and never
  expose raw document body text.

## Boundaries Preserved

- No Copilot Studio topic, connector action, or curated document Swagger was
  added.
- No queue worker, queue write, applicant import, candidate document route,
  notification API, model assessment launcher, Foundry call, live Azure smoke,
  Azure resource creation, or production identity behavior was added.
- Case/source-document endpoints continue to use the simulated lab identity
  model and require the global `hr` lab role.
- The source-document service does not import `LocalWorkflowStore`,
  `AzureWorkflowStorageBackend`, Azure SDKs, provider code, Copilot tooling,
  or queue writers.

## Design Notes

- E10 uses the existing `role_source_raw_path()` builder. No new Blob path
  convention was added.
- `ArtifactVersions` remain deferred because E10 registers raw source
  documents, not derived/versioned role-intake artifacts.
- The implementation intentionally does not unlock `assessment_unlocked`,
  update `RecruitmentCase.case_status`, or move the case to a later stage.
- Repeated POSTs are not idempotent in E10; each successful request creates a
  distinct document id and Blob path.
