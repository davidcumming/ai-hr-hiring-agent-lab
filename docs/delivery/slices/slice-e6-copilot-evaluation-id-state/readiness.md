# Slice Readiness Report: slice-e6-copilot-evaluation-id-state - Explicit Copilot `evaluation_id` Workflow State

## 1. Review Metadata

| Field | Value |
|---|---|
| Report ID | `RR-slice-e6-copilot-evaluation-id-state-001` |
| Slice ID | `slice-e6-copilot-evaluation-id-state` |
| Slice Name | E6 Explicit Copilot `evaluation_id` Workflow State |
| Date Reviewed | 2026-06-13 |
| Reviewed By | Codex using `slice-planning-agent` with `slice-readiness-reviewer` as a fresh reviewer |
| Draft Spec Reference | `docs/delivery/slices/slice-e6-copilot-evaluation-id-state/slice-spec.md` |
| Execution Model | `isolated-verification` |
| Status | Complete |

This report approves readiness for eval design only. It does not approve implementation, residual risk, merge readiness, current-state documentation truth, or any cloud/manual configuration change.

## 2. Inputs Reviewed

| Input | Reference | Notes |
|---|---|---|
| Draft slice spec | `slice-spec.md` | Primary artifact under review. |
| Reconciled planning context | `planning-context.md` | Baseline for E5 reality, E6 intent, issue impact, and known drift. |
| Sizing assessment | `sizing.md` | Confirms `accept-as-one-slice`. |
| E5 manual evidence | `../slice-e5-copilot-studio-registration-smoke/manual-config-evidence.md` | Establishes the `Dynamically fill with AI` limitation and E6 follow-up. |
| E5 closeout | `../slice-e5-copilot-studio-registration-smoke/closeout.md` | Confirms E5 deferred reliable `evaluation_id` chaining to E6. |
| Implementation lessons | `docs/delivery/implementation-lessons.md` | IL-006 requires explicit workflow identifier storage. |
| Process lessons | `docs/delivery/process-lessons.md` | Manual evidence and current-state drift lessons. |
| OpenAPI / Swagger | `openapi/copilot-studio/evaluations-tool.swagger.json` | Existing `submitEvaluation`, `getEvaluation`, path `evaluation_id`, and envelope `evaluation_id`. |
| GitHub Issues | #1 and #4 | #1 is direct E6 scope; #4 is non-blocking current-state doc drift context. |
| Architecture / process standards | Vendored GenTech standards | Source-of-truth, eval, manual evidence, and architecture guardrails. |

Findings below use `Type` = `Required fix / Recommended improvement / Note`.

## 3. Scope Review

| Finding ID | Finding | Type | Recommended Fix |
|---|---|---|---|
| SCO-001 | The spec has one coherent outcome: a single synthetic Copilot Studio submit-store-retrieve workflow for one `evaluation_id`. | Note | None. |
| SCO-002 | The out-of-scope list excludes app code, Swagger/OpenAPI changes, current-state doc reconciliation, Entra identity, live Foundry execution, multi-candidate workflow, production readiness, issue mutation, and real applicant data. | Note | None. |
| SCO-003 | E6 remains one slice and is not a milestone in disguise. | Note | None. |

**Scope summary:** Pass.

## 4. Functional Requirements Review

| Finding ID | Finding | Type | Recommended Fix |
|---|---|---|---|
| FR-001 | Requirements are behaviourally testable: call `submitEvaluation`, capture response `evaluation_id`, store it in a Copilot topic/workflow variable, map it into `getEvaluation.evaluation_id`, and prove the retrieved ID matches. | Note | None. |
| FR-002 | Missing-state behaviour is explicit: retrieve must not run when no stored `evaluation_id` exists. | Note | None. |
| FR-003 | Non-completed facade envelope handling is explicit for `validation_failed`, `blocked`, `unauthorized`, and `error`. | Note | None. |

**Requirements summary:** Pass.

## 5. Agent Behaviour Review

| Finding ID | Finding | Type | Recommended Fix |
|---|---|---|---|
| AB-001 | Expected agent actions and unacceptable behaviours are specific enough for eval design. | Note | None. |
| AB-002 | The spec explicitly rejects `Dynamically fill with AI`, model inference, guessed IDs, stale IDs, and final hiring-decision language. | Note | None. |
| AB-003 | Ambiguity handling is covered for a user asking to retrieve before an ID exists. | Note | None. |

**Behaviour summary:** Pass.

## 6. Eval Contract Draft Review

| Finding ID | Finding | Type | Recommended Fix |
|---|---|---|---|
| EC-001 | The draft eval contract covers the submit/store happy path, retrieve happy path, missing stored ID, non-completed envelopes, unsafe failure modes, human review, and synthetic-only eval data. | Note | None. |
| EC-002 | Stage 4 must harden manual evidence requirements, repeated-run thresholds, UFM-to-scenario mapping, regression selection, and cost/latency criteria. | Recommended improvement | Carry into `eval-risk-profiler` and `eval-contract-designer`. |

**Eval contract summary:** Pass for Stage 4 handoff.

## 7. Architecture Review

| Finding ID | Finding | Type | Recommended Fix |
|---|---|---|---|
| ARC-001 | The spec aligns with the architecture rule that Copilot owns conversation and orchestration while the facade owns controls, durable state, and response envelopes. | Note | None. |
| ARC-002 | The Copilot topic/workflow variable is framed as transient orchestration state, not trusted durable state or audit storage. | Note | None. |
| ARC-003 | No ADR is required for the narrow lab/manual E6 pattern. | Note | None. |
| ARC-004 | Manual Copilot configuration remains manual-config risk and must be evidenced during implementation. | Recommended improvement | Capture structured manual evidence and source-control limitation notes during E6 implementation. |

**Architecture summary:** Pass.

## 8. Privacy and Governance Review

| Concern | Addressed in Spec? | Finding | Type |
|---|---|---|---|
| PHI | Yes | E6 uses synthetic fixtures only and introduces no health data. | Note |
| PII | Yes | No real applicant data, arbitrary uploads, or candidate contact are in scope. | Note |
| Canadian data residency | Yes | No new Azure, Foundry, storage, or cross-region claim is introduced. | Note |
| Audit trail | Yes | Retrieved record is advisory audit/evaluation evidence; the Copilot variable is not audit storage. | Note |
| Sensitive eval data | Yes | Evidence must exclude Function keys, connection secrets, tenant IDs, subscription IDs, real applicant data, and secret-bearing screenshots. | Note |
| External sharing | Yes | No candidate contact, email, export, or external delivery is in scope. | Note |
| Manual configuration | Yes | Topic/workflow configuration and mappings require structured manual evidence. | Note |

**Privacy/governance summary:** Pass.

## 9. Consistency Review

| Finding ID | Finding | Type | Recommended Fix |
|---|---|---|---|
| CON-001 | The spec is consistent with E5 evidence that `getEvaluation` succeeds with an explicit ID but not reliable AI-filled chaining. | Note | None. |
| CON-002 | GitHub issue #1 is reflected as E6 scope. | Note | None. |
| CON-003 | GitHub issue #4 remains non-blocking current-state documentation drift and is not pulled into E6 scope. | Note | None. |
| CON-004 | Existing Swagger already exposes the operations and fields E6 needs, so no OpenAPI change is planned. | Note | None. |

**Consistency summary:** Pass.

## 10. Open Questions Review

| Finding ID | Finding | Type | Recommended Fix |
|---|---|---|---|
| OQ-001 | The exact Copilot variable name/scope is not known before manual configuration. This does not block planning because evidence will record the platform-qualified equivalent if needed. | Note | None. |
| OQ-002 | Whether screenshots/export or note-based evidence will be available does not block planning. | Note | Record evidence depth and limitations during implementation. |
| OQ-003 | Whether the topic/workflow can be exported or represented in source control does not block E6. | Note | Capture export if feasible; otherwise record the manual-evidence limitation. |

**Open questions summary:** Pass. No must-resolve-before-coding blocker is hidden in the spec.

## 11. Required Fixes (Blocking)

Must be resolved before the spec can be approved for eval design.

| Fix ID | Finding Reference | Description | Required Action |
|---|---|---|---|
| None | N/A | No required fixes. | N/A |

**Total required fixes:** 0

## 12. Recommended Improvements (Non-Blocking)

| Improvement ID | Finding Reference | Description | Recommendation |
|---|---|---|---|
| IMP-001 | EC-002 | Stage 4 should harden the eval contract draft. | Define risk tier, manual/live scenarios, UFM coverage, evidence requirements, thresholds, and regression selection. |
| IMP-002 | ARC-004 | Manual configuration must be reviewable. | Capture topic/workflow name, variable name/scope, assignment, mapping, transcript/notes, ID comparison, and evidence limitations during implementation. |

## 13. Readiness Decision

**Decision:** `ready-for-eval-design`

**Decision Rationale:** E6 has one clear primary outcome, testable requirements, explicit unsafe failure modes, adequate ambiguity handling, architecture constraints grounded in existing standards, and privacy/governance boundaries for synthetic-only lab evidence. There are no required fixes or blockers. Issue #4 remains tracked current-state documentation drift and does not block this E6 eval-design handoff.

**If Blocked - Blocking Reason:** N/A.

## 14. Handoff Recommendation

| Decision | Recommended Next Action |
|---|---|
| `ready-for-eval-design` | Proceed to `eval-risk-profiler` and `eval-contract-designer` at Stage 4. |

**Recommendation:** Proceed to Stage 4 eval design. This report does not approve coding readiness; Stage 4 must produce the risk profile and hardened eval contract first.
