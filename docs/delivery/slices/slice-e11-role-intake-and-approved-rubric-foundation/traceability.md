# Traceability: E11 Role Intake and Approved Rubric Foundation

| Requirement | Evidence |
|---|---|
| Add role-intake creation/retrieval APIs for existing cases. | `tests/test_e11_role_intake_rubric_api.py::test_e11_role_intake_and_rubric_api_round_trip_metadata_safe`; source OpenAPI operation ids `createRoleIntakeArtifact` and `getCaseRoleIntake`. |
| Require existing case and prerequisite source documents for role intake. | `tests/test_e11_role_intake_rubric_service.py::test_e11_role_intake_requires_existing_case_and_source_documents`; API semantic validation test. |
| Store role intake in Blob and `ArtifactVersions`, then update existing task/gate rows. | `tests/test_e11_role_intake_rubric_service.py::test_e11_role_intake_writes_blob_artifact_metadata_event_and_task_gate_updates`. |
| Do not fabricate missing task/gate rows on partial cases. | `tests/test_e11_role_intake_rubric_service.py::test_e11_role_intake_does_not_fabricate_missing_task_or_gate_rows`. |
| Add approved-rubric registration/list/get APIs. | `tests/test_e11_role_intake_rubric_api.py::test_e11_role_intake_and_rubric_api_round_trip_metadata_safe`; source OpenAPI operation ids `registerApprovedRubric`, `listCaseRubrics`, and `getCaseRubric`. |
| Store rubric in Blob, `ArtifactVersions`, `Approvals`, and `CaseEvents`; satisfy rubric gate. | `tests/test_e11_role_intake_rubric_service.py::test_e11_rubric_writes_blob_artifact_approval_event_and_gate_update`. |
| Keep assessment locked and do not enqueue work or call providers. | E11 service/API tests assert no queue messages and no provider calls; rubric service test asserts `assessment_unlocked` remains locked. |
| Reject duplicate role/rubric versions. | `tests/test_e11_role_intake_rubric_service.py::test_e11_role_intake_rejects_duplicate_version_before_extra_blob_write`; `test_e11_rubric_rejects_duplicate_version_and_actor_mismatch`. |
| Preserve auth-first and strict validation behavior. | `tests/test_e11_role_intake_rubric_api.py::test_e11_api_auth_runs_before_body_validation`; `test_e11_api_malformed_bodies_http_400`. |
| Keep raw source-document text out of E11 responses/artifacts. | E11 service/API metadata-safety assertions. |
| Keep curated Copilot Swagger evaluation-only. | `tests/test_copilot_studio_openapi.py::test_only_three_intended_actions_are_exposed`. |
| Update source OpenAPI with stable request components and no nested `$defs`. | `tests/test_dt014_openapi.py::test_routes_and_status_vocabulary_conform`. |

## Deferred

- Applicant import and candidate documents.
- Candidate package generation.
- Assessment readiness check and `assessment_unlocked` transition.
- Model assessment jobs, queues, and workers.
- Copilot Studio / Power Platform role-intake or rubric connector actions.
- Production identity and case-scoped authorization.
