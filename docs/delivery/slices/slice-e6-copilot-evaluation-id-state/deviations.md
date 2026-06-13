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
| `platform-forced` | 2 | Medium |
| `architecture-driven` | 0 | N/A |
| `eval-gap` | 0 | N/A |
| **Total** | 2 | Medium |

**Compliance flags:** None. **Lesson flags:** 2. **GitHub Issue recommendations:** 0.

## 3. Deviation Entries

| # | Classification | Severity | Spec Section Affected | Brief Description | Doc Impact | Lesson Flag | Issue Recommended |
|---|---|---|---|---|---|---|---|
| D-001 | `platform-forced` | Medium | Slice spec sections 4, 5, 9, 11, 22; eval contract sections 6, 16, 17 | Added a body-based retrieve wrapper after Copilot Studio stripped path-parameter variable bindings. | Yes | Yes | No |
| D-002 | `platform-forced` | Medium | Slice spec sections 4, 6, 8, 9, 17, 22; eval contract sections 6, 16, 17 | Narrowed Copilot Studio tool availability after standalone connector tools pre-empted topic routing. | Yes | Yes | No |

### D-001 - Body-Based Retrieve Wrapper Added For Copilot Studio Binding

- **Classification / Severity:** `platform-forced` / Medium
- **Spec section / requirement:** E6 intended explicit variable mapping into `getEvaluation.evaluation_id` and expected no app code or Swagger change unless implementation discovered a blocker.
- **What the spec intended:** Configure Copilot Studio to store `submitEvaluation.response.evaluation_id` in a topic/workflow variable and bind that variable into the existing `getEvaluation` path-parameter input.
- **What was implemented:** Added `POST /api/evaluations/retrieve` with operationId `retrieveEvaluationForCopilot`, accepting `{"evaluation_id": "..."}` as a JSON body while preserving `GET /api/evaluations/{evaluation_id}` and `getEvaluation`. The body-based wrapper worked in deployed backend, connector, and final Copilot Studio topic testing.
- **Rationale:** During E6 manual implementation, Copilot Studio repeatedly removed or broke the explicit topic-variable binding for the path-parameter input. A normal JSON body field is the smallest source-controlled adapter that keeps identifier handoff explicit and avoids AI-filled identifier inference.
- **Impact on current-state docs:** Stage 12 should update API/current-state and Copilot integration docs to include the additive body-based retrieve action. Current-state docs are intentionally not updated in this implementation pass.
- **Lesson flag:** Yes - Copilot Studio topic-variable bindings may be more reliable for body fields than for OpenAPI path parameters, so future connector-facing state handoff actions should prefer body-bindable identifiers when the UI cannot persist path bindings.
- **GitHub Issue recommendation:** No new issue. The change directly addresses the active E6 blocker; if body binding also fails after connector re-import, track that as a separate Copilot Studio platform limitation.
- **Compliance flag:** None. The wrapper does not change authorization, persistence, evidence, applicant-data scope, residency, or secret handling.

### D-002 - Tool Availability Narrowed To Preserve Topic Routing

- **Classification / Severity:** `platform-forced` / Medium
- **Spec section / requirement:** E6 intended the Copilot Studio topic/workflow to own the sample-candidate submit -> store -> retrieve path, with tool calls referenced from that workflow.
- **What the spec intended:** A user prompt such as `Evaluate the sample candidate.` should route to the `E6 Evaluate Sample Candidate` topic, which then calls `submitEvaluation`, stores `evaluation_id` in `submitted_evaluation_id`, and calls `retrieveEvaluationForCopilot`.
- **What was implemented:** `submitEvaluation` and `retrieveEvaluationForCopilot` were set to `Only when referenced by topics or agents` so the topic-driven workflow could route and complete. The final Copilot Studio test completed the `E6 Evaluate Sample Candidate` topic and displayed `eval-a427db3ad61c4e8eac20`.
- **Rationale:** The standalone `submitEvaluation` connector tool initially pre-empted topic routing. Copilot Studio tool availability needed to be narrowed so the topic could control the stateful workflow rather than letting broad direct tool use intercept the prompt.
- **Impact on current-state docs:** Stage 12 should note that topic-driven Copilot Studio workflows rely on topic/agent referenced tool availability for these actions. Current-state docs are intentionally not updated in this requested evidence-capture pass.
- **Lesson flag:** Yes - for Copilot Studio, standalone connector tools can pre-empt topic routing unless their availability is set to `Only when referenced by topics or agents`.
- **GitHub Issue recommendation:** No new issue. The requested evidence capture records the manual configuration lesson and does not create or close GitHub issues.
- **Compliance flag:** None. The setting affects routing behavior only and does not change secrets, applicant-data scope, production identity, residency, or authorization semantics.

## 4. Current-State Documentation Impact Summary

| # | Current-State Doc Section | What Needs to Change | Related Deviation |
|---|---|---|---|
| 1 | `docs/product-current-state/candidate-evaluation-council.md` | Add the new body-based retrieve endpoint once Stage 12 reconciliation runs. | D-001 |
| 2 | `docs/architecture/actual-technical-architecture.md` | Update API route and OpenAPI contract summaries once Stage 12 reconciliation runs. | D-001 |
| 3 | `docs/integration/copilot-studio-tool-readiness.md` and Copilot registration docs | Note `retrieveEvaluationForCopilot` as the preferred E6 Copilot topic-variable retrieve action once Stage 12 reconciliation runs. | D-001 |
| 4 | Copilot Studio topic/tool configuration docs, if reconciled later | Note that topic-driven workflows should keep `submitEvaluation` and `retrieveEvaluationForCopilot` at `Only when referenced by topics or agents` to avoid standalone tool pre-emption. | D-002 |

Current-state docs are intentionally not updated in this requested evidence-capture pass.

## 5. Lesson Flags

| # | Deviation | Lesson Candidate Summary | Why Durable? |
|---|---|---|---|
| 1 | D-001 | For Copilot Studio state handoff, prefer body-bindable identifier fields when path-parameter bindings cannot be persisted by the topic editor. | This affects future Power Platform/Copilot connector design and can prevent repeated manual-binding failures. |
| 2 | D-002 | For Copilot Studio topic-driven workflows, set connector actions to `Only when referenced by topics or agents` when broad standalone tool availability can pre-empt topic routing. | This affects future Copilot Studio workflow design and can prevent topic bypass during stateful workflows. |

## 6. Compliance Flags

No compliance concerns identified in the deviations for this slice.

## 7. Recommended GitHub Issues

No issues recommended for deviations in this slice.

## 8. Handoff Notes

**To `live-eval-runner` (Stage 10):** Use `retrieveEvaluationForCopilot` for the E6 retrieve happy path after connector re-import. The pass condition remains stored ID equals retrieved envelope ID, with no AI-filled identifier.

**To `current-state-reconciler` (Stage 12):** Update current-state API and Copilot integration docs for the additive endpoint and operation ID; do not remove the existing GET route. Also capture the topic-routing tool availability constraint if Copilot Studio topic/tool configuration docs are reconciled later. Current-state docs were explicitly out of scope for the requested evidence-capture pass.

**To `slice-retro-and-lessons` (Stage 18):** Consider promoting the body-bindable identifier lesson and the tool availability / topic-routing lesson from Section 5.

**Summary for Closeout:** total deviations 2; high-severity 0; compliance flags 0; issue recommendations 0; lesson flags 2.
