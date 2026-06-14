# Traceability: E10 Source Document Registry and Blob Intake Foundation

## Coverage Matrix

| ID | Requirement / Acceptance Criterion | Evidence | Status |
|---|---|---|---|
| FR-01 | Add source-document registration for existing synthetic-safe cases. | `SourceDocumentService.register_document`; `registerSourceDocument`; `test_e10_source_document_api_register_list_and_get_round_trip` | Covered |
| FR-02 | Accept only small synthetic inline text, not multipart/binary/metadata-only payloads. | `SourceDocumentRegisterRequest`; `test_e10_source_document_api_malformed_bodies_http_400` | Covered |
| FR-03 | Persist raw source text through the workflow Blob seam using the canonical role-source path. | `role_source_raw_path`; `write_blob_artifact`; `test_e10_register_document_writes_blob_metadata_event_and_task_gate_updates` | Covered |
| FR-04 | Persist source-document metadata in `SourceDocuments`. | `SourceDocument` row write; service/API tests assert row fields, hash, size, status, version | Covered |
| FR-05 | Write one `source_document_registered` `CaseEvents` row with safe metadata only. | `CaseEvent` row write; service/API tests assert event type and no raw text in safe details | Covered |
| FR-06 | Do not write `ArtifactVersions` for raw source documents in E10. | Service/API tests assert no `ArtifactVersion` rows | Covered |
| FR-07 | Deterministically complete `attach_source_documents` task and satisfy `source_documents_required` gate only when rows exist. | `test_e10_register_document_writes_blob_metadata_event_and_task_gate_updates`; `test_e10_partial_case_does_not_fabricate_task_or_gate_rows` | Covered |
| FR-08 | Add list/get document metadata endpoints without exposing raw document content. | `listCaseSourceDocuments`; `getCaseSourceDocument`; service/API metadata-only tests | Covered |
| FR-09 | Preserve E9 auth-first and HTTP/error envelope behavior. | API tests for auth-before-body-validation, role denial, unknown case, unknown document, malformed body | Covered |
| FR-10 | Add source OpenAPI coverage with stable operation IDs. | `tests/test_dt014_openapi.py`; `scripts/export_openapi.py --check` | Covered |
| FR-11 | Keep curated Copilot Swagger evaluation-only. | `tests/test_copilot_studio_openapi.py`; `scripts/export_copilot_openapi.py --check` | Covered |
| NG-01 | No provider/model calls, queue messages, applicant/candidate routes, Copilot changes, or Azure SDK imports on default app construction. | E10 API/service tests, E7/E8/E9 non-goal tests, full pytest suite | Covered |

## Coverage Summary

- Covered: 12
- Partial: 0
- Deferred: 0 within E10 scope
- Untested: 0

Live-model evals are not applicable for E10 because the slice adds
deterministic API/storage behavior only and no model, prompt, tool-routing, or
agentic behavior.

## Deferred To Later Slices

- Normalized text extraction and source-document processing queues.
- Role-intake artifact versioning with `ArtifactVersions`.
- Applicant import and candidate document registration.
- Candidate packages, assessment jobs, notification APIs, workers, and
  Foundry/model execution.
- Copilot Studio / Power Platform case or document actions.
- Production identity and case-scoped authorization.

## Issue Candidates

No new issue candidates are required for E10 closeout based on the implemented
scope and passing deterministic tests.
