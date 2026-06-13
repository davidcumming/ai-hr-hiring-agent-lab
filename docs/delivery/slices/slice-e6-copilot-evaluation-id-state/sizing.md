# Slice Sizing Assessment: slice-e6-copilot-evaluation-id-state

## 1. Candidate Metadata

| Field | Value |
|---|---|
| Candidate ID | `slice-e6-copilot-evaluation-id-state` |
| Candidate Name | E6 Explicit Copilot `evaluation_id` Workflow State |
| Date Created | 2026-06-13 |
| Created By | Codex using `slice-planning-agent` with `slice-sizer` |
| Source Planning Context | `docs/delivery/slices/slice-e6-copilot-evaluation-id-state/planning-context.md` |
| Status | Final |

## 2. Proposed Slice Summary

- **Primary Proposed Outcome** - A user can ask the Copilot Studio agent to evaluate the synthetic sample candidate, then later ask to retrieve it, and the agent uses an explicitly stored Copilot topic/workflow variable named `evaluation_id` to call `getEvaluation`.
- **Proposed Scope** - One synthetic candidate workflow: `submitEvaluation` -> capture returned `evaluation_id` -> store explicit topic/workflow variable -> summarize advisory result -> map stored variable into `getEvaluation.evaluation_id` -> summarize retrieved audit record.
- **Initial Concern Level** - Moderate, because the behaviour is narrow but depends on manual/low-code Copilot Studio topic/workflow configuration.

## 3. Inputs Reviewed

| Input Type | Reference | Notes |
|---|---|---|
| Reconciled planning context | `planning-context.md` | Establishes E5 baseline, E6 gap, architecture caveats, and issue context. |
| Current-state / actual behaviour evidence | E5 manual evidence, traceability, closeout, DoD | E5 proved action smoke, not reliable workflow state. |
| Architecture guideline | Technical Architecture Guidelines sections on Copilot front door, tool integration, workflow state, and manual configuration | Supports transient topic/workflow variables but not trusted durable state in Copilot. |
| ADR | None required for this narrow planning scope | No new service category or production identity pattern is introduced. |
| Implementation/process lesson | `docs/delivery/implementation-lessons.md`, `docs/delivery/process-lessons.md` | Store workflow identifiers explicitly; capture manual configuration evidence. |
| GitHub Issue | #1 direct scope; #4 context only | #1 drives E6; #4 must not be solved in this slice unless needed to avoid false E6 docs. |
| Test/eval strategy | Process Doc sections 18-19 and E5 evidence model | E6 is agentic/tool-orchestration behaviour; live/manual eval expectations must be hardened at Stage 4. |
| User instruction | Approved E6 planning request | Keeps scope to explicit variable storage and reuse for one synthetic sample candidate. |

## 4. Sizing Decision

**Decision** - `accept-as-one-slice`

**Decision Rationale** - E6 has one primary outcome, one workflow transition, one state element (`evaluation_id`), and two existing operations (`submitEvaluation` and `getEvaluation`). It is testable with a concise submit/store/retrieve scenario and closeout evidence can fit in one review package. The slice should split or stop if implementation expands into current-state documentation reconciliation, connection runbook work, Entra identity, Copilot ALM automation, arbitrary uploads, multi-candidate workflows, robust natural-language orchestration, or live Foundry execution.

## 5. Sizing Scorecard

| Dimension | Assessment | Notes |
|---|---|---|
| Outcome coherence | Good | One clear behaviour: explicit state handoff of `evaluation_id` between submit and retrieve. |
| Workflow breadth | Narrow | One two-step workflow for one synthetic sample candidate. |
| Architecture impact | Low / Medium | Uses existing API and lab Copilot setup; relies on manual Copilot configuration and must preserve caveats. |
| Data/state impact | Low | One transient workflow identifier; no new durable store, memory, case entity, permissions model, or audit schema. |
| Deterministic testability | Clear | Existing Swagger proves fields/actions; E6 evidence can verify exact variable storage and mapping. |
| Live-eval tractability | Clear | Focused Copilot Studio interaction with small run set and manual evidence; Stage 4 should harden thresholds. |
| Documentation impact | Low | Creates E6 delivery artifacts only; current-state docs stay unchanged. |
| Privacy/data/audit risk | Low / Medium | Synthetic fixture only; audit record is retrieved, but no real data or production decision is introduced. |
| Manual-config/source-control risk | Medium | Topic/workflow state may not be source-controlled; evidence must be captured. |
| Closeout complexity | Low / Medium | One manual evidence package, one traceability matrix, one focused closeout should be enough. |

## 6. Scope Concerns

| Concern | Impact | Recommended Treatment |
|---|---|---|
| Current-state doc drift (#4) | Could make E6 planning text misleading if it repeats stale docs. | Mention drift as context only; do not update current-state docs in E6. |
| Connection staleness (#2) | Could make Copilot smoke misleading if the connection uses old metadata. | Require evidence that connection state was verified or refreshed if touched. |
| Entra delegated identity (#3) | Higher-risk auth slice could overwhelm E6. | Explicitly out of scope; preserve lab-only auth caveat. |
| Robust natural-language orchestration | Would broaden eval scope beyond state handoff. | Keep prompts/examples to the smallest natural phrases needed for the workflow demo. |
| Copilot ALM/export automation | Useful but could turn E6 into source-control automation. | Capture export if already feasible; otherwise note manual evidence and follow-up. |

## 7. Architecture Concerns

| Concern | Impact | Requires ADR? |
|---|---|---|
| Copilot topic/workflow variable used for `evaluation_id` | Acceptable as transient orchestration state, not authoritative durable state. | No |
| `Dynamically fill with AI` rejected for workflow identifiers | Behavioural constraint, not a new architecture pattern. | No |
| Manual Copilot topic/workflow configuration | Manual-config debt and evidence requirement. | No |
| Production integration gate not satisfied | E6 cannot claim production readiness or source-controlled agent ALM. | No; keep caveated. |

## 8. Test and Eval Concerns

| Concern | Impact | Recommended Treatment |
|---|---|---|
| Manual UI evidence may be note-only | Lower reproducibility. | Prefer screenshots/export; if unavailable, use structured notes with explicit limitations. |
| Matching IDs across submit and retrieve | Core pass/fail condition. | Acceptance criteria must require stored ID equals retrieved envelope ID. |
| Missing ID after submit | Prevents valid retrieve. | Agent must not fabricate an ID or call retrieve blindly. |
| Live-model/tool orchestration behaviour | Agentic behaviour needs eval design. | Handoff to Stage 4 after readiness review. |

## 9. Privacy, Data Residency, and Auditability Concerns

| Concern | Applies? | Impact | Recommended Treatment |
|---|---|---|---|
| PHI | No | None. | Synthetic fixtures only. |
| PII | No | None for E6 scope. | Do not add real candidate data or arbitrary uploads. |
| Canadian data residency | No new scope | No new Azure/Foundry resources or data movement planned. | Do not claim new residency verification. |
| Audit trail | Yes | Retrieved record is audit/evidence output. | Summarize as advisory decision support; do not treat Copilot variable as audit storage. |
| Sensitive eval data | Low | Evidence could accidentally capture secrets. | Redact screenshots; do not record Function keys, connection secrets, tenant IDs, subscription IDs, or secret-bearing screenshots. |
| External sharing | No | None. | No candidate contact or external delivery. |

## 10. Manual Configuration and Source-Control Concerns

| Surface / Area | Risk | Evidence Needed | Follow-Up Needed |
|---|---|---|---|
| Copilot Studio topic/workflow | Variable storage and mapping may only exist in portal state. | Variable name/scope, response-field assignment, `getEvaluation` input mapping, transcript/smoke result. | Yes if no export or source-controlled representation. |
| Copilot Studio tool/action mappings | Required header/body/path mappings can drift. | Confirm `submitEvaluation` body/header mappings and `getEvaluation.evaluation_id` path mapping. | Maybe, if changed. |
| Power Platform/Copilot connection | Stored credentials and metadata may be stale. | Record verification or refresh if relevant. | Tracked by #2. |

## 11. Closeout Complexity Assessment

E6 fits one closeout package. The branch should contain planning, implementation/manual evidence, eval/test summaries, traceability, and closeout for the one submit-store-retrieve workflow. If the work grows to include identity, ALM/source-control automation, current-state doc reconciliation, or connection runbook content, that additional work should be split.

## 12. Split Recommendation

Not applicable. Decision is `accept-as-one-slice`.

| Proposed Sub-Slice | Primary Outcome | Why Separate | Dependencies | Estimated Risk Tier | Suggested Order | Ready for Slice Spec? |
|---|---|---|---|---|---|---|
| N/A | N/A | N/A | N/A | N/A | N/A | N/A |

## 13. Blockers and Open Questions

| ID | Blocker / Question | Blocks Sizing? | Blocks Slice Spec? | Recommended Action |
|---|---|---|---|---|
| BQ-E6-SZ-001 | Can the Copilot UI explicitly bind response `evaluation_id` to a topic/workflow variable and then to the path parameter? | No | No | Carry as implementation validation/evidence requirement. |
| BQ-E6-SZ-002 | Will E6 produce screenshots/export or note-only evidence? | No | No | Spec should allow either, with stronger evidence preferred and limitations recorded. |
| BQ-E6-SZ-003 | Can any topic/workflow configuration be source-controlled? | No | No | Capture export if feasible; otherwise record manual-config debt/follow-up. |

## 14. Recommended Next Skill

**Recommendation** - `slice-spec-generator`

**Handoff Notes** - Generate a slice spec for one explicit Copilot topic/workflow variable named `evaluation_id`, mapped from `submitEvaluation` response into `getEvaluation.evaluation_id`, with `Dynamically fill with AI` explicitly rejected for identifier handoff.
