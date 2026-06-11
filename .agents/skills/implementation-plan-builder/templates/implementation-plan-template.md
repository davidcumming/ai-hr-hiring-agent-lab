# Implementation Plan: <Slice Name>

## 1. Plan Metadata

| Field | Value |
|---|---|
| Slice ID | `<slice-id>` |
| Slice Name | `<slice-name>` |
| Plan Date | `<yyyy-mm-dd>` |
| Plan Author | `<agent/user>` |
| Linked Slice Spec | `<path or reference>` |
| Linked Eval Contract | `<path or reference>` |
| Status | `Draft / Ready for Architecture Check / Blocked` |

---

## 2. Slice Intent Summary

> Copy the one-paragraph intent summary from the approved slice spec verbatim.

---

## 3. File and Change Plan

Group by layer. For each entry: file path (or component name), change type, brief rationale.

### 3.1 Application Logic / Agent Orchestration / Prompt Files
### 3.2 Data Layer / State Management / Workflow-State
### 3.3 API Layer / Connectors / External Integrations
### 3.4 IaC / Resource Configuration

| File / Component | Change Type | Rationale |
|---|---|---|
| `<path>` | `New / Modify / Delete / Refactor` | `<why>` |

### 3.5 Microsoft-Stack Surfaces (Portal / Low-Code)

Copilot Studio topics/actions/agents, Power Platform flows/connectors, Foundry deployments, or other non-source-controlled config expected to change.

| Surface | Configuration Change | Source-Control Feasible? | Evidence Plan (Stage 7) |
|---|---|---|---|
| `<surface>` | `<change>` | `Yes / No / Partial` | `<how evidence is captured>` |

### 3.6 Tests

| Test File / Suite | Test Type | Change Type | Mapped Requirement / Criterion |
|---|---|---|---|
| `<path>` | `Unit / Integration / Workflow-state` | `New / Modify` | `<req-id or criterion>` |

### 3.7 Eval Scenario Files

| Scenario File | Maps to Eval Contract Section | Change Type |
|---|---|---|
| `<path>` | `<section>` | `New / Modify` |

---

## 4. Test Plan

### 4.1 Deterministic Test Coverage Map

| Acceptance Criterion / Requirement | Test File | Test Type | Framework | Status |
|---|---|---|---|---|
| `<criterion>` | `<path>` | `Unit / Integration / Workflow-state` | `<framework>` | `Covered / Gap — needs new test / Gap — deferred` |

### 4.2 Test Infrastructure Needs

| Need | Description | Effort |
|---|---|---|
| `<need>` | `<description>` | `Low / Medium / High` |

### 4.3 Test Gaps

| Requirement / Criterion | Gap Reason | Resolution Plan |
|---|---|---|
| `<criterion>` | `<reason>` | `<plan or deferral note>` |

---

## 5. Eval-Integration Plan

### 5.1 Trigger Mechanism

How live-model evals are triggered (CI/CD step, manual `live-eval-runner`, Foundry / Prompt Flow evaluation, etc.): `<description>`

### 5.2 Eval Scenario File References

| Scenario File | Eval Contract Reference | Data Fixture | Env Var / Config Needed |
|---|---|---|---|
| `<path>` | `<section>` | `<fixture or none>` | `<env var / config>` |

### 5.3 Model and Version Dependencies

| Dependency | Version / Reference | Notes |
|---|---|---|
| Model deployment | `<model name + version>` | `<notes>` |
| Prompt file | `<path>` | `<notes>` |
| Tool schema | `<path or version>` | `<notes>` |
| Orchestration version | `<reference>` | `<notes>` |

### 5.4 Eval-Data Governance Notes

Synthetic-data requirements, PII/PHI constraints, Canadian residency: `<notes or "No special constraints identified">`

---

## 6. Architecture and ADR Flags

Every potential guideline concern or ADR gap identified during planning; checked at Stage 6.

| # | Flag | Guideline Section / ADR | Severity | Recommended Action |
|---|---|---|---|---|
| AF-001 | `<description>` | `<reference>` | `Blocking / Non-blocking / Unknown` | `<action — do NOT resolve here>` |

> If none: "No architecture or ADR flags identified. Proceed to Stage 6 for standard compliance check."

---

## 7. Risks and Blockers

### 7.1 Implementation Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `<risk>` | `Low / Med / High` | `Low / Med / High` | `<mitigation>` |

### 7.2 Architecture Risks

| Risk | ADR Needed? | Notes |
|---|---|---|
| `<risk>` | `Yes / No / Unknown` | `<notes>` |

### 7.3 Test and Eval Risks

| Risk | Affects Deterministic Tests? | Affects Live Evals? | Notes |
|---|---|---|---|
| `<risk>` | `Yes / No` | `Yes / No` | `<notes>` |

### 7.4 Privacy, Data Residency, and Audit Risks

| Concern | Applies? | Notes |
|---|---|---|
| PHI / PII handling | `Yes / No / Unknown` | `<notes>` |
| Canadian data residency | `Yes / No / Unknown` | `<notes>` |
| Audit trail requirement | `Yes / No / Unknown` | `<notes>` |

### 7.5 Manual-Config and Source-Control Risks

| Surface | Risk | Follow-Up at Stage 7? |
|---|---|---|
| `<surface>` | `<risk>` | `Yes / No / N/A` |

### 7.6 Sequencing Dependencies

| Item | Depends On | Parallel OK? |
|---|---|---|
| `<item>` | `<dependency>` | `Yes / No` |

### 7.7 Open Blockers

| ID | Blocker | Blocks Plan? | Blocks Coding? | Recommended Action |
|---|---|---|---|---|
| BK-001 | `<description>` | `Yes / No` | `Yes / No` | `<action>` |

---

## 8. Recommended Next Step

```text
Stage 6 — Architecture compliance & ADR check
Skills: architecture-guideline-checker (always) + adr-gap-detector (if AF flags exist)
```

### Handoff Notes

What the architecture-guideline-checker and (if applicable) adr-gap-detector should focus on: `<handoff notes>`
