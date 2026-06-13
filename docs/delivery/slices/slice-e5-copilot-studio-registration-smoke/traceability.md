# Traceability Matrix

**Slice ID:** `slice-e5-copilot-studio-registration-smoke` | **Slice name:** E5 Copilot Studio Registration Smoke | **Matrix date:** 2026-06-12 | **By:** `traceability-and-closeout-agent`

## Inputs Used

| Input | Version / reference | Available? |
|---|---|---|
| Slice scope | User-approved revised E5 closeout scope: Copilot Studio tool registration smoke, manual evidence capture, follow-up issue creation | Yes |
| Manual evidence summary | `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/manual-config-evidence.md` | Yes |
| Connector API definition | `openapi/copilot-studio/evaluations-tool.swagger.json` | Yes |
| Deterministic test summary | E4 Swagger contract tests exist; no new E5 runtime tests required for this manual-registration smoke | N/A for E5 scope |
| Live eval summary | Not applicable; E5 is not a live-model or robust natural-language orchestration slice | N/A for E5 scope |
| Implementation summary / deviation log | Branch adds E5 manual evidence only; no application code change and no separate deviation log | Yes |
| Open GitHub Issues at construction time | `#1`, `#2`, `#3`, `#4` verified open on branch `slice-e5-copilot-studio-registration-smoke` | Yes |

---

## 1. Full Coverage Table

Status values: Covered / Partial / Untested / Deferred / Untestable. Evidence type: Test / Eval / Manual / Config / Issue.

### 1.1 Functional Requirements

| ID | Requirement summary | Status | Evidence type | Evidence reference | Issue ref |
|---|---|---|---|---|---|
| FR-E5-01 | Copilot Studio agent exists as `HR Hiring Agent Lab` in `CHI-LAB-SANDBOX`. | Covered | Manual | `manual-config-evidence.md` sections 2 and 3.1 | - |
| FR-E5-02 | Dataverse was added after initially being missing, and maker/author privileges were resolved using available roles. | Covered | Manual | `manual-config-evidence.md` sections 2 and 3.2 | - |
| FR-E5-03 | Web search was disabled and GPT-4.1 was selected for the agent. | Covered | Manual | `manual-config-evidence.md` sections 2 and 3.3 | - |
| FR-E5-04 | Power Apps custom connector API definition was imported from `openapi/copilot-studio/evaluations-tool.swagger.json`. | Covered | Manual + Config | `manual-config-evidence.md` section 3.4; `openapi/copilot-studio/evaluations-tool.swagger.json` | - |
| FR-E5-05 | Connector host was corrected manually to `func-hrha-lab-cac001-a4fpachkcgcug9cb.canadacentral-01.azurewebsites.net`. | Covered | Manual | `manual-config-evidence.md` section 3.5 | - |
| FR-E5-06 | Azure Function direct auth with the `x-functions-key` header was confirmed, with no key value recorded. | Covered | Manual + Config | `manual-config-evidence.md` sections 3.5 and 8; Swagger `securityDefinitions.function_key` | #3 |
| FR-E5-07 | Power Platform/Copilot connection was refreshed or recreated after connector host/security changes. | Covered | Manual | `manual-config-evidence.md` section 3.6 | #2 |

### 1.2 Business Rules

| ID | Rule summary | Status | Evidence type | Evidence reference | Issue ref |
|---|---|---|---|---|---|
| BR-E5-01 | Note-based manual evidence is accepted as sufficient for this lab smoke; missing screenshots and exports are non-blocking. | Covered | Manual | `manual-config-evidence.md` sections 4 and 9; revised closeout scope | - |
| BR-E5-02 | E5 proves Copilot Studio tool registration smoke only. | Covered | Manual | `manual-config-evidence.md` section 5 | - |
| BR-E5-03 | E5 does not prove robust natural-language orchestration, multi-candidate case workflow, or live Azure AI Foundry / Agent Framework council execution. | Covered | Manual | `manual-config-evidence.md` section 5 | #1 |
| BR-E5-04 | E5 does not replace lab-only Function key/header auth. | Covered | Manual | `manual-config-evidence.md` sections 3.5, 3.7, 3.8, and 5 | #3 |
| BR-E5-05 | No Function key value, connection secret, tenant identifier, subscription identifier, raw applicant data, or secret-bearing screenshot is recorded in the E5 manual evidence. | Covered | Manual | `manual-config-evidence.md` section 8 | - |
| BR-E5-06 | Missing source-control-capture is non-blocking because E5 adds manual evidence only and relies on the E4 source-controlled Swagger artifact. | Covered | Manual + Git | `manual-config-evidence.md` sections 1 and 3.4; branch diff adds the E5 evidence file only | - |

### 1.3 Acceptance Criteria

| ID | Criterion summary | Status | Evidence type | Evidence reference | Issue ref |
|---|---|---|---|---|---|
| AC-E5-01 | `submitEvaluation` succeeded from Copilot Studio using synthetic fixture values and the corrected idempotency mapping. | Covered | Manual + Config | `manual-config-evidence.md` sections 3.7 and 3.9; Swagger operation `submitEvaluation` | - |
| AC-E5-02 | `getEvaluation` succeeded from Copilot Studio when given an explicit `evaluation_id`. | Covered | Manual + Config | `manual-config-evidence.md` section 3.8; Swagger operation `getEvaluation` | - |
| AC-E5-03 | The limitation with `Dynamically fill with AI` is recorded as an E6 orchestration/state-management follow-up, not an API failure. | Covered | Manual + Issue | `manual-config-evidence.md` section 3.9; issue `#1` | #1 |
| AC-E5-04 | Follow-up issues were created for explicit `evaluation_id` state, connection staleness/runbook work, replacing lab-only auth, and current-state documentation drift. | Covered | Issue | `manual-config-evidence.md` section 7; GitHub issues `#1`, `#2`, `#3`, `#4` | #1, #2, #3, #4 |

### 1.4 Agent Behavior Requirements

| ID | Behavior summary | Status | Eval scenario ID | Eval result | Issue ref |
|---|---|---|---|---|---|
| AB-E5-01 | Copilot Studio can call the registered `submitEvaluation` action successfully for the synthetic fixture. | Covered | E5 manual smoke | Pass, note-based | - |
| AB-E5-02 | Copilot Studio can call the registered `getEvaluation` action successfully when supplied an explicit `evaluation_id`. | Covered | E5 manual smoke | Pass, note-based | - |
| AB-E5-03 | Copilot Studio does not reliably chain `submitEvaluation.evaluation_id` into `getEvaluation.evaluation_id` using only "Dynamically fill with AI." | Deferred | E5 manual smoke | Limitation recorded; solve in E6 | #1 |

### 1.5 High-Risk Behaviors

| ID | Behavior summary | Risk tier | Status | Eval scenario ID | Human review record | Issue ref |
|---|---|---|---|---|---|---|
| HRB-E5-01 | No hiring decision, real applicant data processing, live council execution, or production identity behavior is claimed by E5. | Low for E5 smoke | Covered | N/A | Manual evidence boundary in `manual-config-evidence.md` section 5 | #1, #3 |

---

## 2. Coverage Summary

| Category | Total | Covered | Partial | Untested | Deferred | Untestable |
|---|---:|---:|---:|---:|---:|---:|
| Functional requirements | 7 | 7 | 0 | 0 | 0 | 0 |
| Business rules | 6 | 6 | 0 | 0 | 0 | 0 |
| Acceptance criteria | 4 | 4 | 0 | 0 | 0 | 0 |
| Agent behavior requirements | 3 | 2 | 0 | 0 | 1 | 0 |
| High-risk behaviors | 1 | 1 | 0 | 0 | 0 | 0 |
| **Totals** | **21** | **20** | **0** | **0** | **1** | **0** |

**Overall coverage rate (informational):** 95% covered, with the single deferred item tracked by issue `#1`.

---

## 3. Gap List

### 3.1 Untested

No untested items for E5's limited tool-registration-smoke scope.

### 3.2 Partial

No partial items for E5's limited closeout posture. The underlying evidence is note-based, but that evidence depth is accepted as sufficient for this lab smoke.

### 3.3 Deferred

| Item ID | Item summary | Deferral reason | Deviation log ref | Issue ref |
|---|---|---|---|---|
| AB-E5-03 | Reliable chaining of `submitEvaluation.evaluation_id` into `getEvaluation.evaluation_id`. | E5 proves explicit-action smoke only. E6 must solve explicit Copilot topic/workflow variable storage for `evaluation_id`. | N/A | #1 |

### 3.4 Untestable

No untestable items for E5's limited scope.

---

## 4. Issue Candidate List

No new issue candidates. Existing open issues cover the known follow-up work:

| Issue | Type | Severity | Summary sentence | Notes |
|---|---|---|---|---|
| #1 | enhancement / orchestration follow-up | Medium | Add explicit Copilot topic/workflow variable storage for `evaluation_id`. | Required for E6. |
| #2 | documentation-gap / runbook follow-up | Medium | Document Power Platform connection staleness and recreate-after-connector-change guidance. | Required because the E5 smoke needed a refreshed or recreated connection. |
| #3 | security / identity follow-up | High | Replace lab-only Function key plus fake `X-Lab-*` headers with Entra delegated identity and role mapping. | Required before production-like identity claims. |
| #4 | documentation-gap | Medium | Reconcile current-state docs after E5 Copilot Studio registration smoke. | Required so current-state/integration docs distinguish E4 source-controlled readiness from E5 note-evidenced manual registration smoke. |

---

## 5. Caveats and Limitations

- Note-based manual evidence is accepted as sufficient for this lab smoke.
- Missing screenshots and portal exports are non-blocking for E5.
- E5 does not prove robust natural-language orchestration.
- E5 does not prove multi-candidate case workflow.
- E5 does not prove live Azure AI Foundry / Agent Framework council execution.
- E5 does not replace lab-only Function key/header auth.
- E6 must solve explicit Copilot topic/workflow variable storage for `evaluation_id`.
- The source-controlled Swagger remains environment-neutral with placeholder host `function-app-host.example`; the actual connector host correction is manual evidence.
- Current-state docs still contain E4/no-Copilot-registration language; this is non-blocking documentation drift for E5, tracked in #4, and is not a not-done finding.

---

## 6. Matrix Status

| Check | Result |
|---|---|
| All traceable items present | Yes |
| All gaps explicitly listed | Yes |
| Issue references for unresolved items only | Yes |
| No untested agent behavior items without rationale | Yes |
| Ready to pass to `closeout-package-builder` | Yes |
