# Slice Spec: <Slice ID> — <Slice Name>

## 1. Slice Metadata

| Field | Value |
|---|---|
| Slice ID | `<slice-id>` |
| Slice Name | `<slice-name>` |
| Date Created | `<yyyy-mm-dd>` |
| Created By | `<agent/user>` |
| Source Documentation Repo Reference | `<path/link/description>` |
| Code Repo Baseline | `<branch/commit/current-state-doc-reference>` |
| Status | `Draft / Ready for Readiness Review / Blocked` |
| Risk Tier (draft estimate) | `Low / Standard / High-Assurance / Unknown` |

## 2. Planning Inputs Used

| Input Type | Reference | Used For |
|---|---|---|
| Documentation repo source | `<reference>` | `<purpose>` |
| Reconciled planning context | `<reference>` | `<purpose>` |
| Current-state doc | `<reference>` | `<purpose>` |
| Architecture guideline | `<reference>` | `<purpose>` |
| ADR | `<reference>` | `<purpose>` |
| Implementation lesson | `<reference>` | `<purpose>` |
| GitHub Issue | `<reference>` | `<purpose>` |
| Sizing assessment | `<reference>` | `<purpose>` |

## 3. Business Outcome

The primary business/process outcome (one main outcome, two to four sentences).

## 4. User and Process Scope

- **In Scope** — users, roles, workflows, or process steps included.
- **Out of Scope** — what is explicitly excluded.

## 5. Current-State Context

Relevant current product state from current-state docs. Not historical slice specs, not aspirational documentation-repo content.

## 6. Functional Requirements

| ID | Requirement | Rationale | Priority |
|---|---|---|---|
| FR-001 | `<requirement>` | `<why this matters>` | `Must / Should / Could` |

## 7. Business Rules

| ID | Rule | Trigger/Condition | Expected Behaviour |
|---|---|---|---|
| BR-001 | `<rule>` | `<condition>` | `<behaviour>` |

## 8. Agent Behaviour Requirements

How the agent behaves, especially under ambiguity or risk.

| ID | Behaviour | Expected Agent Action | Unacceptable Behaviour |
|---|---|---|---|
| AB-001 | `<behaviour>` | `<expected>` | `<unacceptable>` |

## 9. Acceptance Criteria

| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-001 | `<criterion>` | `Deterministic test / Live eval / Human review / Manual evidence` |

## 10. Eval Contract (Draft)

### 10.1 Behavioural Contract

Behaviours the live-model evals must verify.

### 10.2 Unsafe Failure Modes

| ID | Unsafe Failure Mode | Blocking? | Notes |
|---|---|---|---|
| UFM-001 | `<failure mode>` | `Yes / No` | `<notes>` |

### 10.3 Expected Outputs

Acceptable outputs or decisions.

### 10.4 Unacceptable Outputs

Outputs or decisions that should fail eval.

### 10.5 Ambiguity Handling

How the agent should respond when input, evidence, or workflow state is ambiguous.

### 10.6 Human Review Requirements

Behaviours requiring human review.

### 10.7 Eval Data Governance Constraints

PHI, PII, residency, or retention constraints on eval data for this slice.

## 11. Deterministic Test Expectations

| ID | Test Expectation | Related Requirement/Rule | Notes |
|---|---|---|---|
| DT-001 | `<test expectation>` | `<FR/BR/AC>` | `<notes>` |

## 12. Live-Model Eval Expectations (Draft)

Draft only; `eval-contract-designer` hardens at Stage 4.

| ID | Eval Scenario | Expected Behaviour | Pass Criteria | Runs/Threshold | Risk |
|---|---|---|---|---|---|
| LE-001 | `<scenario>` | `<expected>` | `<rubric>` | `<Process §19.1 tier threshold>` | `Low / Standard / High` |

## 13. Cost and Latency Considerations

Expected response-time, token-cost, or operational-cost expectations for the eval contract.

## 14. Privacy, Data Residency, and Auditability

| Concern | Applies? | Requirement / Open Question |
|---|---|---|
| PHI | `Yes / No / Unknown` | `<requirement or question>` |
| PII | `Yes / No / Unknown` | `<requirement or question>` |
| Canadian data residency | `Yes / No / Unknown` | `<requirement or question>` |
| Audit trail | `Yes / No / Unknown` | `<requirement or question>` |
| Sensitive eval data | `Yes / No / Unknown` | `<requirement or question>` |
| External sharing | `Yes / No / Unknown` | `<requirement or question>` |
| Evidence retention | `Yes / No / Unknown` | `<requirement or question>` |

## 15. Architecture Constraints

Only approved constraints; reference the guideline or ADR for each.

| Constraint | Source (Guideline / ADR) | Impact on Implementation |
|---|---|---|
| `<constraint>` | `<source>` | `<impact>` |

## 16. Architecture Guideline Gaps

| Gap | Impact | Recommended Action |
|---|---|---|
| `<gap>` | `<impact>` | `Draft ADR via adr-gap-detector / Update guideline / None` |

## 17. Manual Configuration Expectations

| Surface | Expected Configuration | Evidence Required | Source-Control Follow-Up Needed? |
|---|---|---|---|
| `<Azure/Power Platform/Copilot Studio/Foundry/Entra/etc.>` | `<configuration>` | `<screenshot/export/notes>` | `Yes / No / Unknown` |

## 18. Dependencies and Blockers

| Type | Description | Status |
|---|---|---|
| Dependency | `<dependency>` | `<status>` |
| Blocker | `<blocker>` | `<status>` |

## 19. Slice Sizing Assessment Summary

- One primary outcome? `Yes / No`
- Modifies more than one independent workflow? `Yes / No`
- Testable/evaluable without excessive scenarios? `Yes / No`
- Requires multiple unrelated architecture decisions? `Yes / No`
- Sizing decision: `Accept as one slice / Split recommended / Blocked`

## 20. Traceability Seed

Initial rows for the traceability skill to expand at Stage 14.

| Requirement/Rule/Behaviour | Acceptance Criterion | Deterministic Test | Live Eval | Expected Evidence |
|---|---|---|---|---|
| `<FR/BR/AB>` | `<AC>` | `<DT>` | `<LE>` | `<expected evidence>` |

## 21. Open Questions

| ID | Question | Must Resolve Before Coding? |
|---|---|---|
| OQ-001 | `<question>` | `Yes / No` |

## 22. Handoff Notes for Coding Agent

- Primary user/process outcome (one sentence).
- Must-follow architecture constraints (list).
- Required tests and evals.
- Known blockers.
- What not to build in this slice.
