# Slice Sizing Assessment: <Candidate Slice Name>

## 1. Candidate Metadata

| Field | Value |
|---|---|
| Candidate ID | `<candidate-id>` |
| Candidate Name | `<candidate-name>` |
| Date Created | `<yyyy-mm-dd>` |
| Created By | `<agent/user>` |
| Source Planning Context | `<path/link/description>` |
| Status | `Draft / Final / Blocked` |

## 2. Proposed Slice Summary

- **Primary Proposed Outcome** — business/process/user outcome in one or two sentences.
- **Proposed Scope** — what the slice appears to include.
- **Initial Concern Level** — `Low / Moderate / High`

## 3. Inputs Reviewed

| Input Type | Reference | Notes |
|---|---|---|
| Reconciled planning context | `<reference>` | `<notes>` |
| Current-state doc | `<reference>` | `<notes>` |
| Architecture guideline | `<reference>` | `<notes>` |
| ADR | `<reference>` | `<notes>` |
| Implementation/process lesson | `<reference>` | `<notes>` |
| GitHub Issue | `<reference>` | `<notes>` |
| Test/eval strategy | `<reference>` | `<notes>` |
| User instruction | `<reference>` | `<notes>` |

## 4. Sizing Decision

**Decision** — one of: `accept-as-one-slice / split-recommended / blocked-pending-clarification / blocked-pending-adr / blocked-pending-debt-burndown`

**Decision Rationale** — main reason, two to four sentences.

## 5. Sizing Scorecard

| Dimension | Assessment | Notes |
|---|---|---|
| Outcome coherence | `Good / Mixed / Poor / Unknown` | `<notes>` |
| Workflow breadth | `Narrow / Moderate / Broad / Unknown` | `<notes>` |
| Architecture impact | `Low / Medium / High / Unknown` | `<notes>` |
| Data/state impact | `Low / Medium / High / Unknown` | `<notes>` |
| Deterministic testability | `Clear / Mixed / Unclear` | `<notes>` |
| Live-eval tractability | `Clear / Mixed / Unclear` | `<notes>` |
| Documentation impact | `Low / Medium / High / Unknown` | `<notes>` |
| Privacy/data/audit risk | `Low / Medium / High / Unknown` | `<notes>` |
| Manual-config/source-control risk | `Low / Medium / High / Unknown` | `<notes>` |
| Closeout complexity | `Low / Medium / High / Unknown` | `<notes>` |

## 6. Scope Concerns

| Concern | Impact | Recommended Treatment |
|---|---|---|
| `<concern>` | `<impact>` | `<treatment>` |

## 7. Architecture Concerns

| Concern | Impact | Requires ADR? |
|---|---|---|
| `<concern>` | `<impact>` | `Yes / No / Unknown` |

## 8. Test and Eval Concerns

| Concern | Impact | Recommended Treatment |
|---|---|---|
| `<concern>` | `<impact>` | `<treatment>` |

## 9. Privacy, Data Residency, and Auditability Concerns

| Concern | Applies? | Impact | Recommended Treatment |
|---|---|---|---|
| PHI | `Yes / No / Unknown` | `<impact>` | `<treatment>` |
| PII | `Yes / No / Unknown` | `<impact>` | `<treatment>` |
| Canadian data residency | `Yes / No / Unknown` | `<impact>` | `<treatment>` |
| Audit trail | `Yes / No / Unknown` | `<impact>` | `<treatment>` |
| Sensitive eval data | `Yes / No / Unknown` | `<impact>` | `<treatment>` |
| External sharing | `Yes / No / Unknown` | `<impact>` | `<treatment>` |

## 10. Manual Configuration and Source-Control Concerns

| Surface / Area | Risk | Evidence Needed | Follow-Up Needed |
|---|---|---|---|
| `<Azure/Power Platform/Copilot Studio/Foundry/Entra/etc.>` | `<risk>` | `<evidence>` | `Yes / No / Unknown` |

## 11. Closeout Complexity Assessment

Whether implementation, tests, evals, doc reconciliation, traceability, evidence, Issues, and approval fit in one closeout package.

## 12. Split Recommendation

Complete only if decision is `split-recommended`.

| Proposed Sub-Slice | Primary Outcome | Why Separate | Dependencies | Estimated Risk Tier | Suggested Order | Ready for Slice Spec? |
|---|---|---|---|---|---|---|
| `<sub-slice>` | `<outcome>` | `<rationale>` | `<dependencies>` | `Low / Standard / High-Assurance / Unknown` | `<order>` | `Yes / No / Maybe` |

## 13. Blockers and Open Questions

| ID | Blocker / Question | Blocks Sizing? | Blocks Slice Spec? | Recommended Action |
|---|---|---|---|---|
| BQ-001 | `<question>` | `Yes / No` | `Yes / No` | `<action>` |

## 14. Recommended Next Skill

**Recommendation** — one of: `slice-spec-generator / planning-context-reconciler / adr-gap-detector / manual-config-debt-monitor / human clarification required`

**Handoff Notes** — what the next agent/skill needs to know.
