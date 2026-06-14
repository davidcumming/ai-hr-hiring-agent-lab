# Traceability Matrix: E9 Case State Foundation API

**Slice ID:** `slice-e9-case-state-foundation-api`
**Slice name:** E9 Case State Foundation API
**Matrix date:** `2026-06-13`

## Coverage Table

| Requirement | Implementation evidence | Test evidence | Status |
|---|---|---|---|
| Add `POST /api/cases`, `GET /api/cases/{case_id}`, and `GET /api/cases/{case_id}/next-actions` with stable operation IDs. | `src/hr_eval_lab/api/routes_cases.py`; `src/hr_eval_lab/api/app.py`; `openapi/evaluations-api.json` | `tests/test_dt014_openapi.py`; `tests/test_e9_case_api.py` | Covered |
| Use the standard envelope shape while preserving the existing evaluation `Envelope`. | `src/hr_eval_lab/domain/schemas/cases.py` | `tests/test_dt014_openapi.py`; `tests/test_e9_case_api.py` | Covered |
| Accept only minimal synthetic-safe case creation input and reject extra fields. | `src/hr_eval_lab/domain/schemas/cases.py`; `src/hr_eval_lab/api/routes_cases.py` | `tests/test_e9_case_api.py` | Covered |
| Use `WorkflowStorageBackend` through `app.state.workflow_storage`; do not depend on concrete local/Azure adapters. | `src/hr_eval_lab/cases/service.py`; `src/hr_eval_lab/api/routes_cases.py` | `tests/test_e9_case_service.py`; `tests/test_e9_case_api.py`; `tests/test_e8_non_goals.py` | Covered |
| Persist `RecruitmentCases`, `CaseParticipants`, `CaseTasks`, `CaseEvents`, and `WorkflowGates` on create. | `src/hr_eval_lab/cases/service.py` | `tests/test_e9_case_service.py`; `tests/test_e9_case_api.py` | Covered |
| Map simulated HR identity to created-by actor, HR owner, participant, and event role. | `src/hr_eval_lab/cases/service.py` | `tests/test_e9_case_service.py`; `tests/test_e9_case_api.py` | Covered |
| Return persisted case summary, participants, open tasks, gate status, events, and next actions. | `src/hr_eval_lab/cases/service.py`; `src/hr_eval_lab/domain/schemas/cases.py` | `tests/test_e9_case_service.py`; `tests/test_e9_case_api.py` | Covered |
| Unknown case ids return `validation_failed` without fabricated state. | `src/hr_eval_lab/cases/service.py`; `src/hr_eval_lab/api/routes_cases.py` | `tests/test_e9_case_service.py`; `tests/test_e9_case_api.py` | Covered |
| Next actions are deterministic business-language mappings from persisted tasks and gates. | `src/hr_eval_lab/cases/service.py` | `tests/test_e9_case_service.py`; `tests/test_e9_case_api.py` | Covered |
| Preserve auth-before-body behavior and simulated `hr` role requirement. | `src/hr_eval_lab/api/routes_cases.py` | `tests/test_e9_case_api.py` | Covered |
| Keep curated Copilot Swagger evaluation-only. | `scripts/export_copilot_openapi.py`; `openapi/copilot-studio/evaluations-tool.swagger.json` | `tests/test_copilot_studio_openapi.py` | Covered |
| Preserve no-Azure-SDK/default-local boundary. | `src/hr_eval_lab/api/app.py`; `src/hr_eval_lab/cases/service.py`; workflow storage selector | `tests/test_e8_non_goals.py`; `scripts/smoke_workflow_storage_config.py` | Covered |

## Deferred

Case search, body-friendly case retrieve wrapper, curated Copilot case Swagger,
Copilot Studio topics, Power Platform connector changes, notification APIs,
source documents, applicant import, artifact-versioning APIs, approval APIs,
assessment readiness APIs, queue workers, Foundry/model execution, human
review APIs, final aggregation, production identity, case-scoped
authorization, concurrency/ETag policy, retention/cleanup, and Azure resource
creation remain deferred to E10+.

## Caveats

- E9 is the first public use of the workflow storage Table seam; deterministic
  tests pin that default app construction still uses local workflow storage
  and does not import Azure SDKs.
- No formal architecture guideline docs or approved storage/case ADRs exist
  under `docs/architecture/`; see the E9 architecture compliance report for
  the non-blocking disposition.
