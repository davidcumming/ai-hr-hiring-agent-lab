# Traceability Matrix

**Slice ID:** `slice-e6-copilot-evaluation-id-state` | **Slice name:** E6 Explicit Copilot `evaluation_id` Workflow State | **Matrix date:** `2026-06-13` | **By:** `traceability-matrix-builder`

This matrix traces the implemented E6 behavior, not the original path-parameter-only intent. The implemented Copilot workflow stores `submitEvaluation.response.evaluation_id` as `submitted_evaluation_id`, reuses that value through the body-based `retrieveEvaluationForCopilot` action, and preserves the canonical `getEvaluation` route.

## Inputs used

| Input | Version / reference | Available? |
|---|---|---|
| Slice spec | `docs/delivery/slices/slice-e6-copilot-evaluation-id-state/slice-spec.md` | Yes |
| Eval contract | `docs/delivery/slices/slice-e6-copilot-evaluation-id-state/eval-contract.md` | Yes |
| Deterministic test summary | Prior validation fact: `python3 -m pytest` passed with `200 passed, 7 skipped`; targeted tests in `tests/test_dt001_happy_path.py`, `tests/test_dt007_status_vocabulary.py`, `tests/test_dt009_authorization.py`, `tests/test_dt014_openapi.py`, `tests/test_copilot_studio_openapi.py`, `tests/test_rp004_openapi_and_headers.py` | Yes |
| Live eval summary | `docs/delivery/slices/slice-e6-copilot-evaluation-id-state/eval-summary.md` | Partial - accepted lab-scope smoke, not repeated-run batch |
| Manual evidence summary | `docs/delivery/slices/slice-e6-copilot-evaluation-id-state/manual-config-evidence.md` | Partial - note-based plus chat screenshot context |
| Implementation summary / deviation log | `docs/delivery/slices/slice-e6-copilot-evaluation-id-state/implementation-notes.md`; `docs/delivery/slices/slice-e6-copilot-evaluation-id-state/deviations.md` | Yes |
| Documentation validation report | `docs/delivery/slices/slice-e6-copilot-evaluation-id-state/doc-validation.md` | Yes - `CONDITIONAL-PASS`, no blockers |
| Open GitHub Issues at construction time | `gh issue list --state open`: #1, #2, #3, #4 open on 2026-06-13 | Yes |

---

## 1. Full Coverage Table

Status values: Covered / Partial / Untested / Deferred / Untestable. Evidence type: Test / Eval / Manual / Deviation. Issue ref: `#<issue>` or `-`.

### 1.1 Functional Requirements

| ID | Requirement summary | Status | Evidence type | Evidence reference | Issue ref |
|---|---|---|---|---|---|
| FR-E6-001 | Recognize submit intent for the synthetic sample candidate. | Covered | Manual / Eval | `manual-config-evidence.md` 3.1, 3.8; `eval-summary.md` LE-E6-001 smoke facts | - |
| FR-E6-002 | Call `submitEvaluation` with existing synthetic fixture inputs and lab mappings. | Covered | Test / Manual / Eval | `tests/test_copilot_studio_openapi.py`; `manual-config-evidence.md` 3.5; `eval-summary.md` LE-E6-001 | - |
| FR-E6-003 | Capture returned response-envelope `evaluation_id`. | Covered | Manual / Eval | `manual-config-evidence.md` 3.5; `eval-summary.md` stored `submitted_evaluation_id` facts | - |
| FR-E6-004 | Store the identifier in an explicit Copilot variable or recorded platform-qualified equivalent. | Covered | Manual / Eval | `manual-config-evidence.md` 3.5 records `submitted_evaluation_id`; `eval-summary.md` version block | - |
| FR-E6-005 | Recognize retrieve flow after an evaluation has been submitted. | Covered | Manual / Eval | `manual-config-evidence.md` 3.6, 3.8; `eval-summary.md` LE-E6-002 accepted smoke | - |
| FR-E6-006 | Map stored workflow state into retrieve input. | Covered | Test / Manual / Deviation | Implemented as `submitted_evaluation_id` -> `retrieveEvaluationForCopilot.evaluation_id` body field per D-001; `tests/test_copilot_studio_openapi.py::test_body_retrieve_operation_has_bindable_evaluation_id_input` | - |
| FR-E6-007 | Retrieved envelope `evaluation_id` matches stored variable value. | Covered | Test / Manual / Eval | `tests/test_dt001_happy_path.py` body retrieve assertion; `manual-config-evidence.md` 3.4, 3.6; `eval-summary.md` direct and topic smoke facts | - |
| FR-E6-008 | Summaries remain advisory and human-review-required. | Covered | Manual / Eval | `manual-config-evidence.md` 3.8; `eval-summary.md` observed advisory boundary | - |
| FR-E6-009 | If no `evaluation_id` exists, do not retrieve as if state exists. | Partial | Test / Eval | Backend rejects missing body ID in `tests/test_dt007_status_vocabulary.py`; Copilot missing-state scenario LE-E6-003 was not run in accepted smoke | - |
| FR-E6-010 | Evidence records variable assignment and retrieve input mapping. | Covered | Manual | `manual-config-evidence.md` 3.5, 3.6 | - |
| FR-E6-011 | Do not rely on `Dynamically fill with AI` for workflow identifiers. | Covered | Manual / Test | `manual-config-evidence.md` 3.6; `tests/test_copilot_studio_openapi.py::test_body_retrieve_operation_has_bindable_evaluation_id_input`; D-001 | - |

### 1.2 Business Rules

| ID | Rule summary | Status | Evidence type | Evidence reference | Issue ref |
|---|---|---|---|---|---|
| BR-E6-001 | `evaluation_id` is explicitly stored and reused as a workflow identifier. | Covered | Manual / Eval | `manual-config-evidence.md` 3.5, 3.6; `eval-summary.md` smoke facts | - |
| BR-E6-002 | `Dynamically fill with AI` is not acceptable for `evaluation_id`. | Covered | Manual / Test | `manual-config-evidence.md` 3.6; `tests/test_copilot_studio_openapi.py` body retrieve checks | - |
| BR-E6-003 | Copilot topic state is transient, not the system of record. | Covered | Docs / Manual | `branch-diff-analysis.md`; current-state docs validated in `doc-validation.md` | - |
| BR-E6-004 | Synthetic fixture scope only. | Covered | Manual / Eval | `manual-config-evidence.md` 3.5, 3.8; `eval-summary.md` states no real candidate data | - |
| BR-E6-005 | Lab auth caveats remain; no production identity claim. | Covered | Test / Docs | `tests/test_dt009_authorization.py`; `doc-validation.md` E6 non-goal validation; issue #3 remains open for production identity future work | - |
| BR-E6-006 | Evidence must not expose secrets. | Covered | Manual / Validation | `manual-config-evidence.md` redaction concerns; current repo evidence contains no Function key or tenant details | - |
| BR-E6-007 | Body and header idempotency mappings remain distinct. | Covered | Test | `tests/test_rp004_openapi_and_headers.py`; `tests/test_copilot_studio_openapi.py` header/body schema checks | - |

### 1.3 Acceptance Criteria

| ID | Criterion summary | Status | Evidence type | Evidence reference | Issue ref |
|---|---|---|---|---|---|
| AC-E6-001 | Copilot topic calls `submitEvaluation` successfully for the synthetic fixture. | Covered | Manual / Eval | `manual-config-evidence.md` 3.5, 3.8; `eval-summary.md` LE-E6-001 | - |
| AC-E6-002 | Returned `evaluation_id` is stored in an explicit workflow variable. | Covered | Manual / Eval | `manual-config-evidence.md` 3.5; `eval-summary.md` stored ID facts | - |
| AC-E6-003 | Retrieve input is explicitly mapped from stored state, not AI-filled. | Covered | Manual / Test / Deviation | Implemented as body field binding via `retrieveEvaluationForCopilot` per D-001; `manual-config-evidence.md` 3.6; `tests/test_copilot_studio_openapi.py` | - |
| AC-E6-004 | Retrieved response contains matching `evaluation_id`. | Covered | Test / Manual / Eval | `tests/test_dt001_happy_path.py`; `manual-config-evidence.md` 3.4, 3.6; `eval-summary.md` direct, connector, and topic smoke facts | - |
| AC-E6-005 | Copilot summarizes submitted result and retrieved record as advisory/human-review-required. | Covered | Manual / Eval | `manual-config-evidence.md` 3.8; `eval-summary.md` observed boundary language | - |
| AC-E6-006 | Missing stored ID path does not fabricate an identifier or call retrieve. | Partial | Test / Eval | Backend missing-body validation covered; Copilot scenario LE-E6-003 was skipped in accepted smoke | - |
| AC-E6-007 | E6 artifacts contain no secrets, tenant IDs, real applicant data, or secret-bearing screenshots. | Covered | Manual / Validation | `manual-config-evidence.md` 9; no durable screenshot/export included | - |
| AC-E6-008 | No app code/OpenAPI/current-state/cloud/issue changes outside scope. | Partial | Deviation / Git | D-001 records the platform-forced app/OpenAPI additive wrapper; current Stage 14 writes are limited to traceability, closeout, and DoD | - |

### 1.4 Agent Behavior Requirements

| ID | Behavior summary | Status | Eval scenario ID | Eval result | Issue ref |
|---|---|---|---|---|---|
| AB-E6-001 | On sample evaluation request, call submit, store ID, summarize advisory result. | Covered | LE-E6-001 | Pass for lab-scope smoke | - |
| AB-E6-002 | On retrieve path, use stored workflow variable for retrieve ID. | Covered | LE-E6-002 | Pass for lab-scope smoke using `retrieveEvaluationForCopilot` body field | - |
| AB-E6-003 | Before stored ID exists, do not guess or call retrieve. | Partial | LE-E6-003 | Not run in accepted smoke; backend missing-body guard exists | - |
| AB-E6-004 | Render `validation_failed`, `blocked`, `unauthorized`, or `error` envelopes without bypass. | Partial | LE-E6-004 through LE-E6-007 | Not run as Copilot smoke; backend/API status behavior covered by deterministic tests | #3 for production identity/auth context |
| AB-E6-005 | Summaries remain advisory-only and human-review-required. | Covered | LE-E6-001, LE-E6-002, LE-E6-008 | Boundary observed in happy-path smoke; LE-E6-008 adversarial batch not run | - |

### 1.5 High-Risk Behaviors

E6 is Standard tier, not High-assurance. The rows below capture safety-relevant behaviors that still needed explicit traceability because they affect identifier integrity, hiring authority, and evidence safety.

| ID | Behavior summary | Risk tier | Status | Eval scenario ID | Human review record | Issue ref |
|---|---|---|---|---|---|---|
| HRB-E6-001 | Identifier integrity: stored ID is reused and retrieved ID matches. | Standard safety-relevant | Covered | LE-E6-001, LE-E6-002 | `manual-config-evidence.md`; Stage 16 pending | - |
| HRB-E6-002 | Authority boundary: no final hiring decision or production-readiness claim. | Standard safety-relevant | Covered | LE-E6-001, LE-E6-002, LE-E6-008 | `eval-summary.md` happy-path boundary notes; Stage 16 pending | - |
| HRB-E6-003 | Evidence safety: no secrets, tenant IDs, subscription IDs, or real applicant data. | Standard safety-relevant | Covered | N/A | `manual-config-evidence.md` redaction notes; Stage 16 pending | - |
| HRB-E6-004 | Missing-state and non-completed envelope handling. | Standard safety-relevant | Partial | LE-E6-003 through LE-E6-007 | Not fully run; deterministic backend coverage and caveat recorded | #3 for auth context |

---

## 2. Coverage Summary

| Category | Total | Covered | Partial | Untested | Deferred | Untestable |
|---|---:|---:|---:|---:|---:|---:|
| Functional requirements | 11 | 10 | 1 | 0 | 0 | 0 |
| Business rules | 7 | 7 | 0 | 0 | 0 | 0 |
| Acceptance criteria | 8 | 6 | 2 | 0 | 0 | 0 |
| Agent behavior requirements | 5 | 3 | 2 | 0 | 0 | 0 |
| High-risk behaviors | 4 | 3 | 1 | 0 | 0 | 0 |
| **Totals** | **35** | **29** | **6** | **0** | **0** | **0** |

**Overall coverage rate (informational):** `100%` if covered plus partial items count as represented in evidence. The partial rows are still gaps and are listed below.

---

## 3. Gap List

### 3.1 Untested

No traceable item is completely untested. Partial rows remain below.

### 3.2 Partial (non-blocking caveats for E6 lab scope)

| Item ID | Item summary | Passing scenarios | Missing / limited scenarios | Issue ref |
|---|---|---|---|---|
| FR-E6-009 / AC-E6-006 / AB-E6-003 | Missing stored ID should not fabricate or retrieve. | Backend missing-body and malformed-body tests reject unsafe body retrieve input. | Copilot missing-state live scenario LE-E6-003 was not run in the accepted smoke. | - |
| AB-E6-004 / HRB-E6-004 | Non-completed envelope rendering should not be bypassed. | Backend/API deterministic tests cover `validation_failed`, `unauthorized`, malformed body, and auth-before-body behavior. | Copilot LE-E6-004 through LE-E6-007 were not run as a repeated live suite. | #3 for auth-production identity context |
| AC-E6-008 | Original no-code/no-OpenAPI expectation changed. | D-001 records a platform-forced additive wrapper; tests and exports validate the new route and preserved GET. | Original path-parameter-only/no-code expectation is not the implemented behavior. | - |
| LE-E6-008-related boundary | No hiring decision or production claim. | Happy-path smoke preserved advisory/human-review language. | No adversarial prompt batch/exported transcript exists. | - |

### 3.3 Deferred

No E6 requirement is deferred from the implemented lab-scope workflow. Production identity, live Foundry council, Copilot ALM/source-control capture, and first-demo Blob/Table/Queue/human-review workflow capabilities remain out of E6 scope, not deferred E6 requirements.

### 3.4 Untestable

No item is inherently untestable. The remaining limitations are evidence-depth and run-count limitations.

---

## 4. Issue Candidate List

No new issue candidates. Existing open issues #1-#4 cover the E6 state-workflow context, Power Platform connection staleness/runbook context, production identity future work, and current-state documentation reconciliation context. This matrix does not create, close, edit, or approve any issue.

| # | Traceable item ref | Suggested type | Severity | Summary sentence | Notes for drafter |
|---|---|---|---|---|---|
| N/A | N/A | N/A | N/A | No new issue candidates. | Stage 16 Release Authority may later decide whether existing issues need update/closure or whether a new ALM/live-eval follow-up is worth creating. |

---

## 5. Caveats and Limitations

- Manual Copilot/Power Platform evidence is note-based plus chat screenshot context, not durable exported ALM evidence.
- Copilot ALM/source-control capture remains future work.
- Production identity remains future work and is tracked by open issue #3.
- Foundry live council remains future work.
- The first-demo workflow still requires Blob document intake, Table workflow state, Queue-backed async model assessment, and a human review model.
- No full repeated-run live-eval batch or exported transcript exists; manual smoke is accepted for E6 lab scope.
- No real candidate data was used; advisory-only and human-review-required boundaries were preserved.
- `getEvaluation` remains preserved; the Copilot topic workflow uses `retrieveEvaluationForCopilot` because path-parameter binding was platform-forced to a body-bindable adapter.

---

## 6. Matrix Status

| Check | Result |
|---|---|
| All traceable items present | Yes - functional requirements, business rules, acceptance criteria, agent behavior, and safety-relevant behaviors are represented. |
| All gaps explicitly listed | Yes - partial live-eval and evidence-depth gaps are listed. |
| Issue references for unresolved items only | Yes - issue references appear only on partial/unresolved context rows; completed rows use `-`. |
| No untested agent behavior items without rationale | Yes - missing-state and edge-envelope behavior are partial with explicit rationale. |
| Ready to pass to `closeout-package-builder` | Yes - ready with the caveats above; Stage 16 approval remains pending. |
