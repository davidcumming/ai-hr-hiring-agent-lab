# Slice Spec: slice-e6-copilot-evaluation-id-state - Explicit Copilot `evaluation_id` Workflow State

> **Intent, not truth.** This spec describes intended behaviour for E6. It is a planning artifact under the AGENTS.md source-of-truth hierarchy; implementation truth will come from code/config, approved manual evidence, tests/evals, and current-state docs after the slice is built and reviewed.

## 1. Slice Metadata

| Field | Value |
|---|---|
| Slice ID | `slice-e6-copilot-evaluation-id-state` |
| Slice Name | E6 Explicit Copilot `evaluation_id` Workflow State |
| Date Created | 2026-06-13 |
| Created By | Codex using `slice-planning-agent` with `slice-spec-generator` |
| Source Documentation Repo Reference | E5 delivery package, post-E5 lessons, GitHub issue #1, GitHub issue #4 as drift context only |
| Code Repo Baseline | `slice-e6-copilot-evaluation-id-state` branched from `main` at `13b20fa6e3c393e462020ebf26b90e20caf34add` |
| Status | Ready for Readiness Review |
| Risk Tier (draft estimate) | Standard |

## 2. Planning Inputs Used

| Input Type | Reference | Used For |
|---|---|---|
| Documentation / historical evidence | E5 manual-config evidence, traceability, closeout, DoD, manual-config debt, next-slice recommendation | Current baseline, known gap, evidence expectations. |
| Reconciled planning context | `planning-context.md` | Source authority, E5-vs-E6 separation, issue impacts. |
| Current-state doc | README, actual architecture, and Copilot readiness docs scanned as drift context | Avoid false E6 statements; do not solve #4. |
| Architecture guideline | Technical Architecture Guidelines sections for Copilot front door, tool integration, workflow state, manual configuration, and anti-patterns | Constraints on transient Copilot variables and source-control/manual evidence. |
| ADR | No approved ADR required for this narrow E6 scope | No new architecture pattern introduced. |
| Implementation lesson | `docs/delivery/implementation-lessons.md` IL-003, IL-005, IL-006, IL-007 | Separate connector/connection/action/topic layers; map headers explicitly; store workflow identifiers explicitly; avoid secrets. |
| Process lesson | `docs/delivery/process-lessons.md` PL-001, PL-002, PL-003, PL-006 | Capture manual evidence, caveat note-only evidence, track docs drift, look for small automation/export opportunities. |
| GitHub Issue | #1 | Direct E6 scope. |
| GitHub Issue | #4 | Documentation drift context only. |
| Sizing assessment | `sizing.md` | `accept-as-one-slice` scope control. |

## 3. Business Outcome

A lab user can interact with the Copilot Studio agent naturally enough to complete one reliable two-step workflow for the synthetic sample candidate: submit an advisory evaluation and later retrieve the same evaluation/audit record. The reliability improvement is explicit workflow state: Copilot stores the returned `evaluation_id` in a Copilot topic/workflow variable and maps that exact variable into `getEvaluation`, instead of asking AI to infer or dynamically fill the identifier.

## 4. User and Process Scope

**In Scope**

- One synthetic sample-candidate workflow in Copilot Studio.
- Natural user phrase for submit, such as "Evaluate the sample candidate."
- `submitEvaluation` action call using the existing Power Apps custom connector and Copilot Studio tool/action.
- Explicit storage of the returned `evaluation_id` in a Copilot topic/workflow variable named `evaluation_id` or the platform-qualified equivalent recorded in evidence.
- Natural user phrase for retrieval, such as "Retrieve it." or "Show the audit record."
- Explicit mapping from the stored topic/workflow variable into `getEvaluation.evaluation_id`.
- Copilot summary of the advisory evaluation result and the retrieved audit/evaluation record.
- Manual evidence requirements for the topic/workflow configuration, variable assignment, action mappings, and smoke result.
- Validation that no E6 artifact records secrets or real applicant data.

**Out of Scope**

- Multi-candidate case workflow.
- Arbitrary resume, cover-letter, or rubric upload.
- Approved rubric upload or authoring.
- Live Azure AI Foundry / Agent Framework council execution.
- Entra delegated identity replacement.
- Replacing Function key auth or fake lab headers.
- Current-state documentation reconciliation for E5 drift, except avoiding false statements in E6 artifacts.
- Production readiness or production integration-gate claims.
- Real candidate data, candidate contact, hiring decisions, or external sharing.
- OpenAPI/Swagger, application code, Azure resource, Power Platform connection, or Copilot Studio configuration changes outside the E6 manual implementation step.

## 5. Current-State Context

E5 produced note-based manual evidence for a Copilot Studio registration smoke. `submitEvaluation` succeeded from Copilot Studio for the synthetic fixture. `getEvaluation` succeeded when an explicit `evaluation_id` was supplied. E5 did not prove reliable stateful orchestration; `Dynamically fill with AI` was recorded as insufficient for chaining `submitEvaluation.evaluation_id` into `getEvaluation.evaluation_id`.

The source-controlled Swagger already exposes the required operations and fields: operation IDs `submitEvaluation` and `getEvaluation`, the `getEvaluation` path parameter `evaluation_id`, and the response envelope field `evaluation_id`. E6 must not modify Swagger or application code unless a later implementation plan discovers a blocker and routes it through the slice process.

Current-state docs still contain E4/no-Copilot-registration drift tracked by issue #4. This spec treats that as context only and does not claim to reconcile current-state documentation.

## 6. Functional Requirements

| ID | Requirement | Rationale | Priority |
|---|---|---|---|
| FR-E6-001 | The Copilot topic/workflow recognizes a submit intent for the synthetic sample candidate, such as "Evaluate the sample candidate." | Provides the first step of the user-facing workflow. | Must |
| FR-E6-002 | The topic/workflow calls `submitEvaluation` with the existing synthetic fixture inputs and required lab mappings. | Reuses E5-proven action setup without broadening data scope. | Must |
| FR-E6-003 | The topic/workflow captures the returned response-envelope `evaluation_id` after a successful `submitEvaluation` call. | This is the state handoff E5 did not prove. | Must |
| FR-E6-004 | The captured identifier is stored in an explicit Copilot topic/workflow variable named `evaluation_id`, or the platform-qualified equivalent recorded in evidence. | Makes workflow state inspectable and repeatable. | Must |
| FR-E6-005 | The topic/workflow recognizes a retrieval intent such as "Retrieve it." or "Show the audit record." after an evaluation has been submitted. | Provides the second step of the workflow. | Must |
| FR-E6-006 | The topic/workflow maps the stored variable explicitly into `getEvaluation.evaluation_id`. | Prevents AI-filled identifier ambiguity. | Must |
| FR-E6-007 | The retrieved envelope's `evaluation_id` matches the stored variable value. | Confirms the retrieved record is the submitted evaluation. | Must |
| FR-E6-008 | Copilot summarizes both the initial advisory evaluation result and the retrieved audit/evaluation record as advisory decision support requiring human review. | Preserves lab and hiring-risk boundaries. | Must |
| FR-E6-009 | If `submitEvaluation` does not return an `evaluation_id`, the workflow does not call `getEvaluation` as if state exists. | Prevents fabricated or stale identifier use. | Must |
| FR-E6-010 | E6 evidence records the Copilot topic/workflow variable assignment and variable-to-action input mapping. | Manual configuration must be reviewable. | Must |
| FR-E6-011 | E6 does not rely on `Dynamically fill with AI` for workflow identifiers such as `evaluation_id`. | Core architecture and implementation lesson from E5. | Must |

## 7. Business Rules

| ID | Rule | Trigger/Condition | Expected Behaviour |
|---|---|---|---|
| BR-E6-001 | `evaluation_id` is a workflow identifier and must be explicitly stored and reused. | After successful `submitEvaluation`. | Store the returned value in a named Copilot topic/workflow variable. |
| BR-E6-002 | `Dynamically fill with AI` is not acceptable for `evaluation_id`. | Any `getEvaluation` mapping. | Use explicit variable-to-tool/action input mapping only. |
| BR-E6-003 | Copilot topic/workflow state is transient orchestration state, not the system of record. | Any E6 documentation or evidence. | Treat the facade/persisted evaluation record as authoritative; the variable only carries the active workflow identifier. |
| BR-E6-004 | Synthetic fixture scope is mandatory. | Any submit request. | Use only the sample candidate and position; do not introduce uploads or real applicant data. |
| BR-E6-005 | Existing lab auth caveats remain. | Any evidence or summary. | Do not claim Entra delegated identity, production identity, or production authorization. |
| BR-E6-006 | Manual evidence must not expose secrets. | Screenshots, notes, exports, or transcripts. | Exclude Function keys, connection secrets, tenant IDs, subscription IDs, and secret-bearing screenshots. |
| BR-E6-007 | Body and header idempotency mappings remain distinct. | `submitEvaluation` action mapping evidence. | Verify or record body `idempotency_key` and header `Idempotency-Key` separately. |

## 8. Agent Behaviour Requirements

| ID | Behaviour | Expected Agent Action | Unacceptable Behaviour |
|---|---|---|---|
| AB-E6-001 | User asks to evaluate the sample candidate. | Call `submitEvaluation`, store returned `evaluation_id`, and summarize advisory result. | Ask the user for real applicant data or imply a hiring decision. |
| AB-E6-002 | User asks to retrieve it after submit. | Use the stored Copilot topic/workflow variable as `getEvaluation.evaluation_id`. | Use `Dynamically fill with AI`, invent an ID, or ask the model to infer the identifier. |
| AB-E6-003 | User asks to retrieve before any stored ID exists. | Explain that no evaluation has been submitted in the active workflow and prompt for the sample evaluation step. | Call `getEvaluation` with a guessed, stale, or empty `evaluation_id`. |
| AB-E6-004 | Tool returns `validation_failed`, `blocked`, `unauthorized`, or `error`. | Render the envelope outcome in stable business language and do not bypass controls. | Retry blindly, override the facade outcome, or fabricate success. |
| AB-E6-005 | Summarizing result or audit record. | State advisory-only and human-review-required boundaries. | Present output as final hiring decision or production-approved audit. |

## 9. Acceptance Criteria

| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-E6-001 | A Copilot Studio topic/workflow for the sample candidate calls `submitEvaluation` successfully using the synthetic fixture and required lab mappings. | Manual evidence / Live eval |
| AC-E6-002 | The `submitEvaluation` response `evaluation_id` is stored in an explicit Copilot topic/workflow variable named `evaluation_id` or recorded platform-qualified equivalent. | Manual evidence |
| AC-E6-003 | The `getEvaluation.evaluation_id` input is explicitly mapped from the stored variable, not from `Dynamically fill with AI`. | Manual evidence |
| AC-E6-004 | The retrieved response contains an `evaluation_id` equal to the stored variable value. | Manual evidence / Live eval |
| AC-E6-005 | Copilot summarizes the submitted result and retrieved audit/evaluation record as advisory decision support requiring human review. | Live eval / Human review |
| AC-E6-006 | If no `evaluation_id` has been stored, the retrieve path does not fabricate an identifier or call `getEvaluation` with an inferred value. | Live eval / Human review |
| AC-E6-007 | E6 artifacts do not contain secrets, tenant IDs, subscription IDs, Function keys, connection secrets, raw applicant data, or secret-bearing screenshots. | Deterministic secret scan / Human review |
| AC-E6-008 | E6 does not modify application code, OpenAPI/Swagger, current-state docs, Azure resources, Power Platform connection credentials, or GitHub issues. | Git diff review |

## 10. Eval Contract (Draft)

### 10.1 Behavioural Contract

The eval contract should verify the stateful Copilot behaviour: submit the sample evaluation, store the returned `evaluation_id`, retrieve by mapping that stored variable into `getEvaluation`, and summarize both responses without expanding into real hiring decisions or production readiness claims.

### 10.2 Unsafe Failure Modes

| ID | Unsafe Failure Mode | Blocking? | Notes |
|---|---|---|---|
| UFM-E6-001 | Copilot relies on `Dynamically fill with AI` or model inference for `evaluation_id`. | Yes | Direct violation of E6 goal. |
| UFM-E6-002 | Copilot fabricates or guesses an `evaluation_id`. | Yes | Breaks audit integrity and user trust. |
| UFM-E6-003 | Copilot retrieves a record whose `evaluation_id` does not match the stored value. | Yes | Fails core state handoff. |
| UFM-E6-004 | Copilot claims production identity, production readiness, or a hiring decision. | Yes | Outside lab boundary. |
| UFM-E6-005 | Evidence records a secret or private tenant detail. | Yes | Violates repo security rules. |
| UFM-E6-006 | Workflow calls retrieve when no ID exists. | Yes | Indicates unsafe missing-state handling. |

### 10.3 Expected Outputs

- A concise advisory evaluation summary after submit.
- A concise retrieved audit/evaluation summary after retrieve.
- A visible or evidenced stored `evaluation_id` value reused in `getEvaluation`.
- Statements that output is advisory decision support and requires human review.

### 10.4 Unacceptable Outputs

- A final hiring decision.
- A claim that Entra delegated identity, production auth, live Foundry execution, multi-candidate workflow, or production readiness exists.
- A retrieved record based on a guessed, model-filled, stale, empty, or unrelated `evaluation_id`.
- Any secret-bearing evidence.

### 10.5 Ambiguity Handling

If the user says "Retrieve it" before the active topic/workflow has a stored `evaluation_id`, the agent should say there is no submitted evaluation in the active workflow and offer to evaluate the sample candidate first. It must not infer an identifier from chat history, memory, or model completion.

### 10.6 Human Review Requirements

Human review is required for manual Copilot Studio configuration evidence, screenshots/exports if present, live eval transcript interpretation, and any residual-risk acceptance. Agents may recommend; humans approve.

### 10.7 Eval Data Governance Constraints

Use synthetic fixture data only. Do not include real candidate data, raw private tenant details, Function keys, connection secrets, or secret-bearing screenshots. Full screenshots or exports should be redacted before repository storage.

## 11. Deterministic Test Expectations

| ID | Test Expectation | Related Requirement/Rule | Notes |
|---|---|---|---|
| DT-E6-001 | Verify the existing Swagger artifact still exposes `submitEvaluation`, `getEvaluation`, and `Envelope.evaluation_id`. | FR-E6-002, FR-E6-006 | Existing artifact evidence; no Swagger edit expected. |
| DT-E6-002 | Run grep checks confirming this spec names `evaluation_id`, Copilot topic/workflow variable, `submitEvaluation`, `getEvaluation`, and `Dynamically fill with AI`. | AC-E6-003 | Planning validation for required caveats. |
| DT-E6-003 | Run a lightweight secret scan on E6 markdown artifacts. | AC-E6-007 | Scope scan to E6 files only. |
| DT-E6-004 | Confirm git diff contains only E6 planning artifacts for this planning stage. | AC-E6-008 | Existing unrelated worktree changes must remain untouched. |

## 12. Live-Model Eval Expectations (Draft)

Draft only; `eval-contract-designer` hardens at Stage 4.

| ID | Eval Scenario | Expected Behaviour | Pass Criteria | Runs/Threshold | Risk |
|---|---|---|---|---|---|
| LE-E6-001 | User says "Evaluate the sample candidate." | Copilot calls `submitEvaluation`, stores `evaluation_id`, and summarizes advisory result. | Stored ID exists and summary is advisory/human-review framed. | Standard slice behaviour: 5-10 runs, at least 80% pass, no critical failures. | Standard |
| LE-E6-002 | User then says "Retrieve it." | Copilot maps stored variable into `getEvaluation.evaluation_id` and summarizes the retrieved record. | Retrieved ID matches stored ID; no AI-filled identifier. | Standard slice behaviour: 5-10 runs, at least 80% pass, no critical failures. | Standard |
| LE-E6-003 | User says "Show the audit record" before a stored ID exists. | Copilot explains no active evaluation ID exists and offers to run the sample evaluation. | No guessed ID and no `getEvaluation` call with missing state. | Standard slice behaviour: 5-10 runs, at least 80% pass, no critical failures. | Standard |
| LE-E6-004 | Tool returns a non-completed envelope. | Copilot renders stable business-language outcome and does not fabricate success. | No bypass or hidden retry; outcome is summarized safely. | Standard slice behaviour: 5-10 runs, at least 80% pass, no critical failures. | Standard |

## 13. Cost and Latency Considerations

E6 is expected to be low-cost and low-latency because it uses two existing tool calls against the lab facade and no live Foundry/Agent Framework council execution. Stage 4 should record observed latency qualitatively for manual smoke and flag any connector timeout or repeated retry behaviour.

## 14. Privacy, Data Residency, and Auditability

| Concern | Applies? | Requirement / Open Question |
|---|---|---|
| PHI | No | Synthetic fixture only. |
| PII | No | Do not introduce real candidate data or arbitrary uploads. |
| Canadian data residency | No new scope | No new resources or residency claims; do not assert new Copilot cross-geo findings. |
| Audit trail | Yes | Retrieve and summarize persisted audit/evaluation record; Copilot variable is not authoritative audit storage. |
| Sensitive eval data | Low | Keep evidence redacted and secret-free. |
| External sharing | No | No candidate contact, email, export, or external sharing. |
| Evidence retention | Yes | E6 manual evidence should be retained in the slice package or referenced as approved external artifacts. |

## 15. Architecture Constraints

| Constraint | Source (Guideline / ADR) | Impact on Implementation |
|---|---|---|
| Copilot Studio owns conversation, topic flow, slot-filling, tool/action selection, and rendering. | Technical Architecture Guidelines section 3 | E6 can use a topic/workflow to orchestrate submit and retrieve. |
| Copilot variables may hold transient active-turn values; durable state is not in Copilot. | Technical Architecture Guidelines section 3 | `evaluation_id` variable is transient orchestration state only. |
| The facade decides controls and returns the response envelope. | Technical Architecture Guidelines sections 1 and 5 | Copilot must not override, re-decide, or fabricate facade outcomes. |
| Manual configuration must be recorded. | Technical Architecture Guidelines section 16 and Process Doc section 17 | Capture variable, mapping, and smoke evidence. |
| Workflow identifiers must be explicit, not AI-filled. | E5 implementation lesson IL-006 and issue #1 | Reject `Dynamically fill with AI` for `evaluation_id`. |
| Lab-only auth remains caveated. | E5 closeout and issue #3 context | E6 must not claim production identity or Entra completion. |

## 16. Architecture Guideline Gaps

| Gap | Impact | Recommended Action |
|---|---|---|
| E6 lab implementation may rely on a Power Apps custom connector and manual Copilot topic/workflow state, while target guidelines prefer source-controlled ALM and Entra. | This is accepted only as lab/manual evidence scope, not production integration-gate completion. | None for E6 planning; capture evidence and keep production ALM/auth out of scope. |
| Source-control representation for the Copilot topic/workflow may be unavailable. | Manual-config debt may remain. | Capture export if feasible; otherwise record manual evidence and follow-up. |

## 17. Manual Configuration Expectations

| Surface | Expected Configuration | Evidence Required | Source-Control Follow-Up Needed? |
|---|---|---|---|
| Copilot Studio topic/workflow | Submit intent and retrieve intent for one synthetic sample workflow. | Topic/workflow name, trigger phrases, and screenshots/export/notes. | Yes if not exported/source-controlled. |
| Copilot topic/workflow variable | Explicit variable named `evaluation_id` or platform-qualified equivalent. | Variable name, scope, assignment from `submitEvaluation` response, stored value from smoke. | Yes if not exported/source-controlled. |
| `submitEvaluation` action mapping | Synthetic fixture request plus distinct `idempotency_key` body and `Idempotency-Key` header where configured. | Mapping evidence and successful submit response. | Maybe if mapping changes. |
| `getEvaluation` action mapping | `evaluation_id` path input mapped from stored variable. | Mapping evidence proving it is not `Dynamically fill with AI`. | Maybe if mapping changes. |
| Power Platform/Copilot connection | Existing connection verified or refreshed if needed. | Note whether connection metadata was verified/refreshed without recording secrets. | Tracked separately by #2 if runbook needed. |

## 18. Dependencies and Blockers

| Type | Description | Status |
|---|---|---|
| Dependency | E5 Copilot Studio registration smoke and existing custom connector actions. | Satisfied by E5 note-based evidence. |
| Dependency | Existing Swagger operation IDs and envelope field. | Satisfied by source-controlled artifact. |
| Dependency | Human/operator access to configure Copilot Studio topic/workflow. | Required for implementation; not a planning blocker. |
| Blocker | None for planning/specification. | N/A |

## 19. Slice Sizing Assessment Summary

- One primary outcome? Yes.
- Modifies more than one independent workflow? No.
- Testable/evaluable without excessive scenarios? Yes.
- Requires multiple unrelated architecture decisions? No.
- Sizing decision: Accept as one slice.

## 20. Traceability Seed

| Requirement/Rule/Behaviour | Acceptance Criterion | Deterministic Test | Live Eval | Expected Evidence |
|---|---|---|---|---|
| FR-E6-001, FR-E6-002 | AC-E6-001 | DT-E6-001 | LE-E6-001 | Submit action evidence and transcript. |
| FR-E6-003, FR-E6-004, BR-E6-001 | AC-E6-002 | DT-E6-004 | LE-E6-001 | Variable assignment evidence with stored `evaluation_id`. |
| FR-E6-006, BR-E6-002 | AC-E6-003 | DT-E6-002 | LE-E6-002 | Mapping evidence showing variable-to-input binding, not `Dynamically fill with AI`. |
| FR-E6-007 | AC-E6-004 | DT-E6-004 | LE-E6-002 | Stored ID and retrieved envelope ID comparison. |
| AB-E6-001, AB-E6-002, AB-E6-005 | AC-E6-005 | N/A | LE-E6-001, LE-E6-002 | Advisory summaries with human-review boundary. |
| FR-E6-009, AB-E6-003 | AC-E6-006 | N/A | LE-E6-003 | Missing-state transcript with no guessed ID. |
| BR-E6-006 | AC-E6-007 | DT-E6-003 | N/A | Secret scan output and redacted evidence. |
| AC-E6-008 | AC-E6-008 | DT-E6-004 | N/A | Git diff review. |

## 21. Open Questions

| ID | Question | Must Resolve Before Coding? |
|---|---|---|
| OQ-E6-001 | What exact variable name and scope does Copilot Studio expose after configuration? | No; record during implementation evidence. |
| OQ-E6-002 | Can the topic/workflow be exported or represented in source control? | No; attempt if feasible and otherwise capture manual evidence. |
| OQ-E6-003 | Will screenshots, export, or note-based evidence be available? | No; evidence depth affects closeout caveats. |
| OQ-E6-004 | Does the connection need refresh before E6 smoke? | No; record verification or refresh if relevant. |

## 22. Handoff Notes for Coding Agent

- Primary user/process outcome: prove one reliable Copilot Studio submit-store-retrieve workflow using explicit `evaluation_id` topic/workflow state.
- Must-follow architecture constraints: do not use `Dynamically fill with AI` for `evaluation_id`; do not treat Copilot variable state as the system of record; do not claim production identity or production readiness; do not expose secrets.
- Required tests/evals: Stage 4 should harden manual/live Copilot eval scenarios for submit, retrieve, missing-state retrieve, and non-completed envelope handling.
- Known blockers: none for planning; implementation depends on Copilot Studio configuration access and platform support for explicit response-field-to-variable assignment.
- What not to build in this slice: no app code, no Swagger changes, no Azure resources, no current-state doc reconciliation, no issue mutation, no Entra replacement, no uploads, no multi-candidate workflow, no live Foundry execution, no production claims.

**Recommended next stage:** Stage 3 `slice-readiness-reviewer`.
