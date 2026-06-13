# Next Slice Recommendation: 2026-06-13 - Post-Slice E5

## 1. Recommendation Metadata

| Field | Value |
|---|---|
| Recommendation ID | `post-e5-next-slice-recommendation` |
| Date Created | 2026-06-13 |
| Created By | `governance-and-process-improvement-agent` / `next-slice-recommender` |
| Prior Slice Closed | `slice-e5-copilot-studio-registration-smoke` |
| Planning Context Reference | E5 closeout, traceability, DoD, manual-config evidence, implementation lessons, process lessons, and open issues #1-#4 |
| Status | Complete recommendation; human chooses the next slice |

## 2. Debt Ceiling Check

Performed first using `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/manual-config-debt.md`.

| Status | Details |
|---|---|
| Manual-config debt ceiling | Clear |
| Open high-priority GitHub Issues | 1 high-severity related issue (#3), not marked critical and not blocking E6's lab workflow-state scope |
| Notes | #1, #2, and #3 are counted as the non-critical manual-config/source-control-adjacent debt set. #4 is current-state documentation drift and is tracked but not counted toward the manual-config ceiling. |

## 3. Inputs Reviewed

| Input | Reference | Notes |
|---|---|---|
| Manual evidence | `manual-config-evidence.md` | E5 smoke succeeded for `submitEvaluation` and explicit-ID `getEvaluation`; workflow handoff remains deferred. |
| Traceability | `traceability.md` | One deferred agent-behavior item remains, tracked by #1. |
| Closeout | `closeout.md` | E5 scope was narrow tool-registration smoke with no application code changes. |
| Definition of Done | `dod.md` | Done for limited E5 scope, with caveats. |
| Implementation lessons | `docs/delivery/implementation-lessons.md` | E5 promoted Copilot/Power Platform technical lessons. |
| Process lessons | `docs/delivery/process-lessons.md` | E5 promoted evidence, issue-tracking, and gate-boundary lessons. |
| GitHub Issues | #1, #2, #3, #4 | All are open follow-up tracking records. |
| Manual-config debt status | `manual-config-debt.md` | Recommendation is `no-block`. |

## 4. Blocked Candidates

| Candidate | Blocking Reason | Required Resolution |
|---|---|---|
| Production-like Entra delegated identity as a broad identity slice | Too broad and higher risk for the immediate next slice; #3 may require architecture and security review before implementation. | Run ADR or architecture-gap review before starting a production-like identity slice. |
| Live Foundry / Agent Framework council execution through Copilot Studio | Outside E5 evidence and still dependent on identity, orchestration, and live-model scope decisions. | Plan as a later slice after workflow-state and identity foundations are clearer. |

## 5. Assessed Candidates

### Candidate: E6: Explicit Copilot topic/workflow variable storage for evaluation_id

**Summary:** Store the `submitEvaluation` result identifier in a Copilot topic/workflow variable and pass it explicitly into `getEvaluation`.

| Dimension | Standing | Rationale |
|---|---|---|
| Business value | Strong | Turns E5's tool smoke into a reliable workflow interaction. |
| Dependency order | Strong | Directly resolves the only deferred E5 agent-behavior item. |
| Testability | Strong | Acceptance can be expressed as submit, store ID, retrieve by stored ID. |
| Eval readiness | Strong | The behavior is deterministic workflow state, not broad natural-language orchestration. |
| Technical risk | Moderate | Still portal/low-code state, but narrow and informed by E5 evidence. |
| Demo/stakeholder value | Strong | Demonstrates a meaningful end-to-end Copilot action sequence. |
| Unresolved issue impact | Strong | Directly addresses issue #1. |
| Architecture readiness | Moderate | No new ADR expected for explicit workflow variable storage in the lab scope. |
| Manual-config/source-control risk | Moderate | Adds low-code state, but stays within the current debt ceiling and can produce better evidence. |
| Implementation complexity | Moderate | Requires Copilot topic/workflow configuration and evidence, not application code. |

**Ready for `slice-spec-generator`?** Yes.

**Main risk:** The topic/workflow remains manual or low-code state unless E6 also captures export/import or stronger evidence.

### Candidate: Current-state documentation reconciliation (#4)

**Summary:** Update current-state docs so they distinguish E4 source-controlled readiness from E5 note-evidenced Copilot Studio registration smoke.

| Dimension | Standing | Rationale |
|---|---|---|
| Business value | Moderate | Improves planning truth and reduces confusion. |
| Dependency order | Moderate | Useful before broader Copilot planning, but not required before E6 if E6 remains narrow. |
| Testability | Strong | Can be validated with doc grep and consistency checks. |
| Eval readiness | Strong | No live eval needed for documentation-only cleanup. |
| Technical risk | Weak | Low technical risk. |
| Demo/stakeholder value | Moderate | Improves reviewer confidence but does not advance workflow behavior. |
| Unresolved issue impact | Strong | Directly addresses issue #4. |
| Architecture readiness | Strong | No ADR expected. |
| Manual-config/source-control risk | Strong | Reduces documentation drift without adding portal state. |
| Implementation complexity | Weak | Small documentation pass. |

**Ready for `slice-spec-generator`?** Yes, if chosen as a documentation slice.

**Main risk:** It does not resolve the deferred E5 agent-behavior item.

### Candidate: Power Platform connection staleness runbook (#2)

**Summary:** Document how to refresh or recreate Power Platform/Copilot connections after custom connector host or security changes.

| Dimension | Standing | Rationale |
|---|---|---|
| Business value | Moderate | Reduces repeated operator confusion during connector changes. |
| Dependency order | Moderate | Helpful before more connector changes, but not the central behavior gap from E5. |
| Testability | Moderate | Can be validated as documentation plus a manual checklist. |
| Eval readiness | Strong | No live-model eval needed. |
| Technical risk | Weak | Documentation/runbook work only unless validation expands scope. |
| Demo/stakeholder value | Weak | Operationally useful but less visible than E6. |
| Unresolved issue impact | Strong | Directly addresses issue #2. |
| Architecture readiness | Strong | No ADR expected. |
| Manual-config/source-control risk | Strong | Reduces manual-config operating risk. |
| Implementation complexity | Weak | Narrow runbook artifact. |

**Ready for `slice-spec-generator`?** Yes, if chosen as an operations-documentation slice.

**Main risk:** It does not improve the actual Copilot workflow handoff.

### Candidate: Entra delegated identity replacement (#3)

**Summary:** Replace lab-only Function key auth and fake `X-Lab-*` headers with Entra delegated identity and role mapping.

| Dimension | Standing | Rationale |
|---|---|---|
| Business value | Strong | Required before production-like identity, authorization, and audit claims. |
| Dependency order | Moderate | Important, but E6 can proceed without claiming production identity. |
| Testability | Moderate | Requires identity and role-mapping validation design. |
| Eval readiness | Moderate | Mostly deterministic security behavior, but higher assurance review may be needed. |
| Technical risk | Strong | Higher risk than E6 because it touches auth and identity boundaries. |
| Demo/stakeholder value | Moderate | Important for governance, less visible than workflow chaining. |
| Unresolved issue impact | Strong | Directly addresses issue #3. |
| Architecture readiness | Moderate | May require ADR or architecture-guideline review before implementation. |
| Manual-config/source-control risk | Moderate | Could reduce secret-bound manual config if scoped well, but setup may involve portal/admin dependencies. |
| Implementation complexity | Strong | Broader and more cross-system than E6. |

**Ready for `slice-spec-generator`?** Conditional: run architecture and identity readiness review first.

**Main risk:** Too broad for the immediate post-E5 slice unless the human prioritizes identity over workflow reliability.

## 6. Dependency Map

| Candidate | Depends On | Enables |
|---|---|---|
| E6 explicit `evaluation_id` variable storage | E5 manual tool-registration smoke | Reliable Copilot workflow interaction, better future topic/workflow evidence |
| Current-state documentation reconciliation (#4) | E5 closeout facts | Cleaner planning context for later Copilot and identity slices |
| Connection staleness runbook (#2) | E5 connection refresh evidence | Safer future custom connector changes |
| Entra delegated identity replacement (#3) | Architecture and security readiness | Production-like identity, authorization, and audit claims |

## 7. Ranked Recommendation

| Rank | Candidate | Overall Standing | Key Reason | Ready for Spec? |
|---:|---|---|---|---|
| 1 | E6: Explicit Copilot topic/workflow variable storage for evaluation_id | Strong | Resolves the only deferred E5 agent-behavior item and turns tool smoke into reliable workflow interaction. | Yes |
| 2 | Current-state documentation reconciliation (#4) | Moderate | Repairs planning truth without adding manual config. | Yes |
| 3 | Power Platform connection staleness runbook (#2) | Moderate | Reduces repeated operator risk around connector changes. | Yes |
| 4 | Entra delegated identity replacement (#3) | Conditional | Important but broader and likely needs architecture/security readiness first. | Conditional |

## 8. Recommended Default Next Action

**Top recommendation:** E6: Explicit Copilot topic/workflow variable storage for evaluation_id

**Rationale:** E6 is the best next slice because it resolves E5's only deferred agent-behavior item (#1), preserves the narrow lab boundary, and converts a manual two-action smoke into a reliable workflow interaction. It can be specified with clear acceptance criteria around explicit variable storage and retrieval without widening into identity replacement, current-state doc reconciliation, multi-candidate workflow, or live Foundry council execution.

**Required first step if selected:** Run Stage 0 planning-context reconciliation, then `slice-spec-generator` for E6.

**This is a recommendation. The human chooses the next slice.**

## 9. Notes From Implementation And Process Lessons

Implementation and process lessons are kept distinct.

**Implementation lessons relevant to next planning:**

- E6 should treat Copilot topic/workflow as the state-management layer and explicitly store `evaluation_id`.
- E6 should verify body fields and headers separately where tool/action mapping controls request correctness.
- E6 should not expand into production-like identity; issue #3 remains a separate path.

**Process lessons relevant to next planning:**

- Capture repo evidence for any manual Copilot Studio or Power Platform configuration.
- Treat ordinary issue creation as backlog tracking, while keeping issue closure/deletion, committed priority or milestone changes, residual-risk acceptance, ADR approval, merge, and release human-governed.
- Ask whether E6 can generate, pre-fill, validate, export, import, or replay any part of the low-code configuration to reduce manual operator work.
