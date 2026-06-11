# Eval Risk Profile: <Slice ID> — <Slice Name>

## Metadata

| Field | Value |
|---|---|
| Slice ID / Name | `<slice-id>` / `<slice-name>` |
| Profile ID | `<ERP-<slice-id>-001>` |
| Date / Created By | `<yyyy-mm-dd>` / `<agent/user>` |
| Source Slice Spec | `<path or reference>` |
| Status | `Draft / Final / Blocked` |
| Live Eval Applicability | `Required / Not Applicable — Non-Agentic Carve-Out` |

**Inputs reviewed** (Present? + notes each): slice spec · draft eval contract · reconciled planning context · architecture guidelines · relevant ADRs · privacy/data-governance policy · current-state docs · known limitations + GitHub Issues · model/tool usage assumptions · cost/latency budgets · test/eval strategy.

---

## Section A — Risk Tier

### A.1 Risk Indicator Scorecard

For each indicator record Applies? (Yes/No/Unknown), Severity (Low/Medium/High/Unknown), Notes.

| Indicator | Applies? | Severity | Notes |
|---|---|---|---|
| PHI | | | |
| PII | | | |
| Sensitive business data | | | |
| Canadian data residency obligation | | | |
| Auditability obligation | | | |
| Approval/rejection/consequential decision | | | |
| Evidence claims or grounded assertions | | | |
| External sharing, export, or notification | | | |
| Memory behaviour affecting future decisions | | | |
| Permissions, identity, or authorization | | | |
| Irreversible or hard-to-reverse state change | | | |
| Authoritative user-facing output | | | |
| Healthcare workflow implication | | | |
| Safety, compliance, legal, or trust risk | | | |
| Cost/latency operational risk | | | |
| Manual-config/source-control debt | | | |

### A.2 Recommended Tier

`Low / Standard / High-Assurance / Standard with unresolved risk / High-Assurance pending clarification / Blocked pending clarification`

### A.3 Rationale

Why this tier — reference the most material indicators. For any `Unknown`, state what would change the classification.

### A.4 Required Test/Eval Package

Yes/No/Conditional + notes for each: relevant deterministic tests · slice-specific live evals · core regression evals · adversarial scenarios · human review (high-risk) · unsafe failure-mode analysis (exhaustive) · privacy/data governance review · auditability review · cost/latency evals · residual-risk human approval · GitHub Issues for accepted non-blocking failures. Repeated-run thresholds: specify per Process §19.1 (e.g., Standard 5-10 at ≥80%; high-risk 20+ at ≥90% + zero critical failures). If live evals are not applicable, record the carve-out statement: no model, prompt, tool-orchestration, agent behaviour, or behaviour-affecting model dependency.

### A.5 Split Recommendation

If a high-assurance element is separable, recommend the split; else `Not applicable.`

| Proposed sub-slice | Risk tier | Reason to separate | Suggested order |
|---|---|---|---|
| | | | |

---

## Section B — Unsafe Failure-Mode Register

| ID | Category | Description (unacceptable behaviour) | Why it matters (safety/privacy/trust/workflow/evidence/compliance) | Blocking? | Required eval scenarios (LE IDs — by eval-contract-designer) | Human review? |
|---|---|---|---|---|---|---|
| UFM-001 | | | | Yes/No | | Yes/No/Conditional |

**Completeness:** confirm minimum entries for the tier (≥3 Standard, ≥6 High-Assurance; Low may have fewer), or list gaps.

---

## Section C — Eval-Data Governance Assessment

### C.1 Data Type Inventory

Type = User input / System state / External artifact / Retrieved document / Log.

| Data element | Type | PHI? | PII? | Sensitive business? | Residency rule? | Retention rule? |
|---|---|---|---|---|---|---|
| | | Yes/No/Unk | Yes/No/Unk | Yes/No/Unk | Yes/No/Unk | Yes/No/Unk |

### C.2 Synthetic Data Summary

Per category (PHI, PII, sensitive business, external artifacts, audit evidence): Fully synthetic? · Partial substitute? · Real data required? · Governance approval needed?

| Data category | Fully synthetic? | Partial? | Real required? | Approval needed? |
|---|---|---|---|---|
| PHI | | | | |
| PII | | | | |
| Sensitive business data | | | | |
| External artifacts | | | | |
| Audit evidence | | | | |

### C.3 Canadian Residency Status

| Infrastructure component | In Canadian region? | Confirmed? | Notes |
|---|---|---|---|
| Model endpoint (Foundry / Copilot Studio / other) | Yes/No/Unknown | Confirmed/Unconfirmed | |
| Eval data storage | Yes/No/Unknown | Confirmed/Unconfirmed | |
| Eval orchestration environment | Yes/No/Unknown | Confirmed/Unconfirmed | |

### C.4 Auditability Requirements

What must be logged, retained, and accessible for audit review (include retention period if known), or `N/A`.

### C.5 Governance Blockers

| ID | Description | Data type | Eval scenarios affected | Required action | Who resolves |
|---|---|---|---|---|---|
| GB-001 | | | | | |

---

## Section D — Cost/Latency Criteria

### D.1 Latency Targets

| Scenario type | Target response time | Maximum acceptable | Ratification |
|---|---|---|---|
| Standard interactive response | | | Ratified/Proposed/Blocked |
| Multi-step orchestration | | | |
| Background/async (if applicable) | | | |

### D.2 Token and Cost Budget

| Interaction type | Expected input tokens | Expected output tokens | Total budget | Notes |
|---|---|---|---|---|
| Standard interaction | | | | |
| Complex retrieval | | | | |
| Adversarial/edge-case eval | | | | |

### D.3 Model and Tool-Call Count

| Scenario type | Expected model calls | Maximum acceptable | Notes |
|---|---|---|---|
| Standard path | | | |
| Multi-step / complex path | | | |
| Error-recovery path | | | |

| Tool | Expected calls per interaction | Maximum acceptable | Notes |
|---|---|---|---|
| `<tool name>` | | | |

### D.4 Measurement Plan

Per concern (end-to-end latency, per-call latency, token usage, tool-call count, cost estimate): approach + tool/service.

| Measurement concern | Approach | Tool/service |
|---|---|---|
| End-to-end latency | | |
| Per-call latency | | |
| Token usage | | |
| Tool-call count | | |
| Cost estimate | | |

### D.5 Ratification Status

List thresholds requiring human ratification before the contract is finalized, or `All thresholds ratified.`

---

## Blockers and Open Questions

| ID | Blocker/Question | Section | Blocks eval-contract design? | Recommended action |
|---|---|---|---|---|
| BQ-001 | | A/B/C/D | Yes/No | |

---

## Handoff Notes for eval-contract-designer

**Ready for handoff?** `Yes / No / Conditionally (list conditions)`

Key constraints to carry into the eval contract: (1) risk tier `<tier>` — sets thresholds and human-review requirements; (2) blocking failure modes `<UFM IDs>` — each needs ≥1 eval scenario; (3) governance constraints `<what scenarios are permitted / blocked>`; (4) cost/latency thresholds `<ratified thresholds>` — enforce in contract; (5) unresolved blockers `<BQ IDs to resolve first>`.
