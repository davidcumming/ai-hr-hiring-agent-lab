# Deviation Log: slice-e6-copilot-evaluation-id-state

## 1. Report Metadata

| Field | Value |
|---|---|
| Slice ID | `slice-e6-copilot-evaluation-id-state` |
| Slice Name | E6 Explicit Copilot `evaluation_id` Workflow State |
| Date | 2026-06-13 |
| Agent / Author | Codex using Coding Agent scope |
| Branch | `slice-e6-copilot-evaluation-id-state` |
| Slice Spec Reference | `docs/delivery/slices/slice-e6-copilot-evaluation-id-state/slice-spec.md` |
| Eval Contract Reference | `docs/delivery/slices/slice-e6-copilot-evaluation-id-state/eval-contract.md` |
| Status | Final for implementation pass |

## 2. Deviation Summary

| Classification | Count | Highest Severity |
|---|---:|---|
| `requirement-removed` | 0 | N/A |
| `requirement-deferred` | 0 | N/A |
| `approach-substituted` | 0 | N/A |
| `scope-reduced` | 0 | N/A |
| `interpretation-applied` | 0 | N/A |
| `platform-forced` | 1 | Medium |
| `architecture-driven` | 0 | N/A |
| `eval-gap` | 0 | N/A |
| **Total** | 1 | Medium |

**Compliance flags:** None. **Lesson flags:** 1. **GitHub Issue recommendations:** 0.

## 3. Deviation Entries

| # | Classification | Severity | Spec Section Affected | Brief Description | Doc Impact | Lesson Flag | Issue Recommended |
|---|---|---|---|---|---|---|---|
| D-001 | `platform-forced` | Medium | Slice spec sections 4, 5, 9, 11, 22; eval contract sections 6, 16, 17 | Added a body-based retrieve wrapper after Copilot Studio stripped path-parameter variable bindings. | Yes | Yes | No |

### D-001 - Body-Based Retrieve Wrapper Added For Copilot Studio Binding

- **Classification / Severity:** `platform-forced` / Medium
- **Spec section / requirement:** E6 intended explicit variable mapping into `getEvaluation.evaluation_id` and expected no app code or Swagger change unless implementation discovered a blocker.
- **What the spec intended:** Configure Copilot Studio to store `submitEvaluation.response.evaluation_id` in a topic/workflow variable and bind that variable into the existing `getEvaluation` path-parameter input.
- **What was implemented:** Added `POST /api/evaluations/retrieve` with operationId `retrieveEvaluationForCopilot`, accepting `{"evaluation_id": "..."}` as a JSON body while preserving `GET /api/evaluations/{evaluation_id}` and `getEvaluation`.
- **Rationale:** During E6 manual implementation, Copilot Studio repeatedly removed or broke the explicit topic-variable binding for the path-parameter input. A normal JSON body field is the smallest source-controlled adapter that keeps identifier handoff explicit and avoids AI-filled identifier inference.
- **Impact on current-state docs:** Stage 12 should update API/current-state and Copilot integration docs to include the additive body-based retrieve action. Current-state docs are intentionally not updated in this implementation pass.
- **Lesson flag:** Yes - Copilot Studio topic-variable bindings may be more reliable for body fields than for OpenAPI path parameters, so future connector-facing state handoff actions should prefer body-bindable identifiers when the UI cannot persist path bindings.
- **GitHub Issue recommendation:** No new issue. The change directly addresses the active E6 blocker; if body binding also fails after connector re-import, track that as a separate Copilot Studio platform limitation.
- **Compliance flag:** None. The wrapper does not change authorization, persistence, evidence, applicant-data scope, residency, or secret handling.

## 4. Current-State Documentation Impact Summary

| # | Current-State Doc Section | What Needs to Change | Related Deviation |
|---|---|---|---|
| 1 | `docs/product-current-state/candidate-evaluation-council.md` | Add the new body-based retrieve endpoint once Stage 12 reconciliation runs. | D-001 |
| 2 | `docs/architecture/actual-technical-architecture.md` | Update API route and OpenAPI contract summaries once Stage 12 reconciliation runs. | D-001 |
| 3 | `docs/integration/copilot-studio-tool-readiness.md` and Copilot registration docs | Note `retrieveEvaluationForCopilot` as the preferred E6 Copilot topic-variable retrieve action once Stage 12 reconciliation runs. | D-001 |

## 5. Lesson Flags

| # | Deviation | Lesson Candidate Summary | Why Durable? |
|---|---|---|---|
| 1 | D-001 | For Copilot Studio state handoff, prefer body-bindable identifier fields when path-parameter bindings cannot be persisted by the topic editor. | This affects future Power Platform/Copilot connector design and can prevent repeated manual-binding failures. |

## 6. Compliance Flags

No compliance concerns identified in the deviations for this slice.

## 7. Recommended GitHub Issues

No issues recommended for deviations in this slice.

## 8. Handoff Notes

**To `live-eval-runner` (Stage 10):** Use `retrieveEvaluationForCopilot` for the E6 retrieve happy path after connector re-import. The pass condition remains stored ID equals retrieved envelope ID, with no AI-filled identifier.

**To `current-state-reconciler` (Stage 12):** Update current-state API and Copilot integration docs for the additive endpoint and operation ID; do not remove the existing GET route.

**To `slice-retro-and-lessons` (Stage 18):** Consider promoting the body-bindable identifier lesson from Section 5.

**Summary for Closeout:** total deviations 1; high-severity 0; compliance flags 0; issue recommendations 0; lesson flags 1.
