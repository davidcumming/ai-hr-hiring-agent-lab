# Reconciled Planning Context: slice-e6-copilot-evaluation-id-state

## 1. Context Metadata

| Field | Value |
|---|---|
| Context ID | `pc-slice-e6-copilot-evaluation-id-state-2026-06-13` |
| Topic / Capability Area | Explicit Copilot topic/workflow variable storage for `evaluation_id` |
| Date Created | 2026-06-13 |
| Created By | Codex using `slice-planning-agent` with `planning-context-reconciler` |
| Documentation Repo Reference | E5 closeout package, post-E5 lessons, open GitHub issues #1 and #4 |
| Code Repo Baseline | `slice-e6-copilot-evaluation-id-state` branched from `main` at `13b20fa6e3c393e462020ebf26b90e20caf34add` |
| Status | Ready for Slice Sizing |

This artifact is planning context only. It prepares the E6 candidate for sizing and specification; it does not update current-state documentation, create issues, change application code, change OpenAPI, or configure Copilot Studio.

## 2. Planning Question or Target Area

Can the next slice safely focus on one reliable two-step Copilot Studio workflow: submit one synthetic sample candidate evaluation, store the returned `evaluation_id` explicitly in a Copilot topic/workflow variable, then retrieve the same evaluation by mapping that stored variable into `getEvaluation`?

## 3. Inputs Reviewed

| Input Type | Reference | Notes |
|---|---|---|
| Documentation / historical evidence | `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/manual-config-evidence.md` | E5 manual/note evidence for Copilot Studio setup, tool/action mappings, and the E6 limitation. |
| Traceability | `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/traceability.md` | E5 covered submit and explicit-ID retrieve; deferred reliable dynamic chaining to E6. |
| Closeout | `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/closeout.md` | E5 scope, caveats, residual risks, and follow-up issue context. |
| DoD validation | `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/dod.md` | E5 done for limited scope, with `evaluation_id` state handoff deferred. |
| Manual-config debt | `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/manual-config-debt.md` | Debt ceiling status is `no-block`; issue #1 counted as non-critical manual-config/source-control-adjacent debt. |
| Next-slice recommendation | `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/next-slice-recommendation.md` | Recommends E6 as top next slice if kept narrow. |
| Implementation lessons | `docs/delivery/implementation-lessons.md` | Relevant lessons: separate connector/connection/action/topic layers; map idempotency header/body separately; store workflow identifiers explicitly. |
| Process lessons | `docs/delivery/process-lessons.md` | Relevant lessons: manual configuration needs repo evidence; caveated note evidence can be acceptable for narrow lab smoke; track but do not silently solve doc drift. |
| OpenAPI / Swagger | `openapi/copilot-studio/evaluations-tool.swagger.json` | Existing Swagger 2.0 artifact exposes `submitEvaluation`, `getEvaluation`, path parameter `evaluation_id`, and response envelope field `evaluation_id`. |
| GitHub Issue | #1, `E6: Add explicit Copilot topic/workflow variable storage for evaluation_id` | Direct E6 scope: store `evaluation_id` explicitly and pass it into `getEvaluation`; synthetic fixture only; avoid secrets. |
| GitHub Issue | #4, `Reconcile current-state docs after E5 Copilot Studio registration smoke` | Documentation drift context only for E6; do not solve #4 in this slice unless needed to avoid misleading E6 artifacts. |
| Architecture guideline | `standards/azure-development-standards/Initial_Documentation/40.2-technical-architecture-guidelines.md` | Copilot owns conversation/orchestration; facade owns controls; Copilot variables may hold transient active-turn values, not trusted durable state. |
| Process standard | `standards/azure-development-standards/gentech_slice_based_development_process_revised.md` | Planning, manual evidence, eval, and definition-of-done rules. |

## 4. Source Authority Summary

| Claim Type | Authority Used |
|---|---|
| Current product behaviour | E5 manual evidence, traceability, closeout, DoD, and current Swagger artifact. |
| Strategic intent | User-selected E6 goal and post-E5 next-slice recommendation. |
| Architecture rules | Vendored technical architecture guidelines and process standard. |
| Unresolved work | GitHub issues #1 and #4. |
| Verified behaviour | E5 note-based manual smoke; existing Swagger structure; no automated E6 evidence yet. |
| Known limitations | E5 caveats, manual-config debt report, implementation/process lessons. |

## 5. Current-State Baseline

E5 proved a narrow Copilot Studio registration smoke under manual/note-evidenced lab conditions:

- A Copilot Studio agent named `HR Hiring Agent Lab` exists in environment `CHI-LAB-SANDBOX`.
- The Power Apps custom connector API definition was imported from `openapi/copilot-studio/evaluations-tool.swagger.json`.
- The imported API definition exposes the two existing operations E6 needs: `submitEvaluation` and `getEvaluation`.
- `submitEvaluation` succeeded from Copilot Studio for the synthetic sample candidate and position.
- `getEvaluation` succeeded from Copilot Studio when supplied an explicit `evaluation_id`.
- E5 corrected the distinction between `idempotency_key` in the body and `Idempotency-Key` in the header.

E5 did not prove reliable stateful orchestration:

- `getEvaluation` was reported as using `Dynamically fill with AI` for `evaluation_id`, but E5 evidence says this does not reliably chain `submitEvaluation.evaluation_id` into `getEvaluation.evaluation_id`.
- E5 classified this as a Copilot topic/workflow orchestration and state-management limitation, not an API failure.
- Robust natural-language orchestration, multi-candidate workflow, live Foundry execution, Entra delegated identity, and production readiness remain out of scope.

Current-state docs still contain E4/no-Copilot-registration statements. That drift is tracked by issue #4 and should not be repeated as fact in E6 artifacts.

## 6. Strategic Intent Summary

Intent for E6 is the smallest workflow demonstration that proves stateful orchestration beyond E5:

1. User asks naturally, for example: "Evaluate the sample candidate."
2. Copilot Studio topic/workflow calls `submitEvaluation`.
3. The returned `evaluation_id` is stored explicitly in a Copilot topic/workflow variable.
4. Copilot summarizes the advisory evaluation result.
5. User later asks: "Retrieve it." or "Show the audit record."
6. Copilot passes the stored variable into `getEvaluation`.
7. Copilot summarizes the retrieved evaluation or audit record.

The core architectural rule is that workflow identifiers such as `evaluation_id` must not rely on `Dynamically fill with AI`; they must be stored and mapped explicitly.

## 7. Reconciliation Findings

| ID | Finding | Category | Source(s) | Planning Impact |
|---|---|---|---|---|
| RF-E6-001 | E5 proved `submitEvaluation` can be called from Copilot Studio for the synthetic fixture. | already-implemented | E5 manual evidence, traceability, closeout | Do not re-plan API or action registration; extend into stateful workflow. |
| RF-E6-002 | E5 proved `getEvaluation` can retrieve when an explicit `evaluation_id` is supplied. | already-implemented | E5 manual evidence, traceability, closeout | E6 should reuse the existing action and path input. |
| RF-E6-003 | E5 did not prove reliable chaining of `submitEvaluation.evaluation_id` into `getEvaluation.evaluation_id`. | partially-implemented | E5 traceability AB-E5-03, closeout RR-E5-02, issue #1 | This is the E6 primary gap. |
| RF-E6-004 | `Dynamically fill with AI` is not reliable enough for workflow identifiers. | aligned | E5 evidence, implementation lesson IL-006, issue #1 | E6 must explicitly forbid AI-filled identifier handoff. |
| RF-E6-005 | The Swagger already exposes `Envelope.evaluation_id` and `getEvaluation` path parameter `evaluation_id`. | already-implemented | Swagger artifact | No OpenAPI/Swagger change is required for E6. |
| RF-E6-006 | Topic/workflow configuration will likely remain low-code/manual state unless exported or captured as evidence. | manual-config-risk | E5 manual evidence, process lessons, architecture guidelines | E6 must require structured manual evidence and source-control follow-up where feasible. |
| RF-E6-007 | Current-state docs are stale after E5. | stale-or-contradicted | E5 closeout, issue #4 | Mention only as drift context; do not solve #4 in E6. |
| RF-E6-008 | E6 can proceed without production identity if it keeps lab-only auth caveats explicit. | aligned | E5 closeout, issue #3 context, architecture guidelines | Do not claim Entra, production auth, or least-privilege completion. |
| RF-E6-009 | E6 has enough behavioural definition for eval design. | requires-eval-design | User E6 goal, issue #1, E5 evidence | Stage 4 should harden live/manual eval expectations before implementation. |
| RF-E6-010 | E6 is a candidate next slice if kept to one synthetic two-step workflow. | candidate-for-next-slice | Post-E5 next-slice recommendation | Handoff to `slice-sizer`. |

## 8. Already Implemented Capabilities

| Capability | Evidence | Planning Impact |
|---|---|---|
| Source-controlled Copilot Swagger artifact | `openapi/copilot-studio/evaluations-tool.swagger.json` exposes exactly two actions. | Reuse; do not edit Swagger for E6. |
| `submitEvaluation` Copilot action smoke | E5 manual evidence sections 3.7 and 3.9. | Use as prerequisite for topic/workflow orchestration. |
| `getEvaluation` Copilot action smoke with explicit ID | E5 manual evidence section 3.8. | Use as prerequisite for variable-to-input mapping. |
| Follow-up tracking | GitHub issue #1 exists and is open. | E6 should reference, not recreate, the issue. |

## 9. Partially Implemented Capabilities

| Capability | Implemented Portion | Remaining Gap | Candidate for Slice? |
|---|---|---|---|
| Copilot Studio evaluation workflow | Individual actions can be called manually/note-evidenced. | Store and reuse `evaluation_id` explicitly between turns/actions. | Yes, E6. |
| Manual evidence for Copilot configuration | E5 note evidence exists. | E6 should capture topic/workflow variable, storage step, mapping step, and smoke transcript/evidence. | Yes, as E6 evidence. |
| Current-state documentation | E4/E5 drift is identified. | Current-state docs still need reconciliation. | No for E6; tracked by #4. |

## 10. Planned or Aspirational Capabilities

| Capability | Strategic Source | Current-State Status | Notes |
|---|---|---|---|
| Explicit `evaluation_id` topic/workflow variable storage | User E6 goal, issue #1, IL-006 | Not implemented | E6 primary scope. |
| Copilot topic/workflow export or replayable ALM | Architecture guideline and process lessons | Unknown / not implemented | Evidence improvement only if feasible; do not make broad ALM automation required for E6. |
| Entra delegated identity | Architecture guideline, issue #3 | Not implemented | Out of scope. |
| Multi-candidate case workflow | Strategic future intent | Not implemented | Out of scope. |
| Live Foundry / Agent Framework council execution | Architecture guideline and deferred live-model path | Not implemented | Out of scope. |

## 11. Stale or Contradicted Assumptions

| Assumption | Contradicting Source | Recommended Treatment |
|---|---|---|
| "There is no Copilot Studio surface." | E5 manual evidence and closeout say a manual Copilot Studio registration smoke occurred. | Avoid repeating this in E6 artifacts; leave correction to issue #4. |
| `Dynamically fill with AI` can safely supply `evaluation_id`. | E5 evidence, issue #1, implementation lesson IL-006. | Treat as explicitly rejected for workflow identifiers. |
| Power Platform/Copilot connection metadata automatically reflects connector changes. | E5 connection refresh lesson and issue #2. | E6 evidence should record that connection state was verified or refreshed if relevant. |

## 12. Architecture and ADR Implications

| Item | Impact | Action |
|---|---|---|
| Copilot variables may hold transient active-turn values. | Supports E6 if the variable is framed as orchestration state, not trusted durable system-of-record state. | No ADR expected for narrow lab slice. |
| Durable workflow state remains facade/storage responsibility. | E6 must not claim the Copilot topic variable is authoritative audit or business state. | State as architecture constraint in spec. |
| Target architecture prefers source-controlled Copilot ALM and Entra auth. | E6 lab manual evidence does not satisfy the production integration-validation gate. | Caveat explicitly; do not expand scope. |
| `Dynamically fill with AI` rejected for identifiers. | Behavioural constraint for E6. | Include in requirements and acceptance criteria. |

## 13. Known Limitations and GitHub Issue Impacts

| Issue / Limitation | Impact on Planning | Required Action |
|---|---|---|
| Issue #1 | Direct E6 scope. | Reference and plan E6 against it. |
| Issue #2 | Connection staleness could make smoke results misleading. | Include evidence requirement to verify or refresh connection metadata if touched. |
| Issue #3 | Lab-only Function key and fake `X-Lab-*` headers remain. | Keep identity replacement out of E6; preserve caveat. |
| Issue #4 | Current-state docs still drift from E5 reality. | Mention as context only; do not update current-state docs in E6 planning. |
| Note-based E5 evidence | E5 proof is less reproducible than screenshots/exports. | E6 should seek stronger evidence if available and caveat notes if not. |

## 14. Testing and Eval Implications

| Behaviour / Capability | Test/Eval Implication | Readiness |
|---|---|---|
| Submit sample evaluation | Manual Copilot smoke plus existing API evidence should prove action call. | Ready for eval design. |
| Store returned `evaluation_id` | Evidence must show response field captured into an explicit topic/workflow variable. | Needs eval design. |
| Retrieve using stored variable | Evidence must show variable-to-`getEvaluation.evaluation_id` mapping and matching returned ID. | Needs eval design. |
| Ambiguous retrieve request before stored ID exists | Eval should require no fabricated ID and no blind `getEvaluation` call. | Needs eval design. |
| API contract | Existing Swagger provides field/operation evidence. | Ready; no code change expected. |

## 15. Privacy, Data Residency, and Auditability Implications

| Concern | Applies? | Planning Impact |
|---|---|---|
| PHI | No | Use synthetic fixtures only; no real applicant or health data. |
| PII | No | Synthetic sample candidate only; do not introduce arbitrary uploads. |
| Canadian data residency | Low / unchanged | No new Azure/Foundry resources or data movement planned; Copilot environment evidence remains manual. |
| Audit trail | Yes | Retrieved audit record is advisory evidence; Copilot variable is only transient orchestration state. |
| Sensitive eval data | Low | Evidence must avoid secrets, tenant IDs, subscription IDs, Function keys, connection secrets, and secret-bearing screenshots. |
| External sharing | No | No candidate contact or external delivery. |

## 16. Manual Configuration and Source-Control Risks

| Surface / Component | Risk | Planning Impact | Follow-Up Needed |
|---|---|---|---|
| Copilot Studio topic/workflow | Manual/low-code orchestration may not be source-controlled. | E6 must require evidence of variable name/scope, assignment, mapping, and result. | Yes, if no export/source-control representation is available. |
| Copilot Studio tool/action mappings | Header/body/path mappings can break silently. | E6 must verify body `idempotency_key`, header `Idempotency-Key`, and path `evaluation_id` mapping. | Maybe; only if mapping changes. |
| Power Platform/Copilot connection | Stale metadata can invalidate smoke evidence. | Evidence should record whether connection state was verified/refreshed. | Tracked by #2. |
| Entra / production identity | Not part of E6. | Preserve lab-only auth caveat. | Tracked by #3. |

## 17. Candidate Next-Slice Areas

| Candidate | Business/Process Outcome | Readiness | Main Risk | Recommended Next Action |
|---|---|---|---|---|
| E6 explicit `evaluation_id` topic/workflow variable storage | User can submit one sample evaluation and later retrieve it using stored workflow state. | Ready | Manual Copilot configuration evidence and possible connection staleness. | Use `slice-sizer`. |
| Current-state documentation reconciliation (#4) | Docs distinguish E4 source-controlled readiness from E5 note-evidenced registration smoke. | Ready if selected | Does not resolve E5's deferred agent-behaviour item. | Keep separate unless human widens scope. |
| Connection staleness runbook (#2) | Operators know when to refresh/recreate connections after connector changes. | Ready if selected | Operational docs only. | Keep separate. |
| Entra delegated identity (#3) | Replace lab-only auth with production-like identity. | Not ready for immediate E6 | Higher assurance and likely architecture/security review. | Plan later. |

## 18. Blockers and Open Questions

| ID | Blocker / Question | Blocking? | Owner / Next Action |
|---|---|---|---|
| BQ-E6-001 | Can the Copilot Studio UI bind `submitEvaluation` response `evaluation_id` into a named topic/workflow variable and map it into `getEvaluation.evaluation_id` without `Dynamically fill with AI`? | No for planning; yes for implementation closeout if unsupported. | Validate during E6 implementation/manual evidence. |
| BQ-E6-002 | Can the topic/workflow configuration be exported or otherwise represented in source control? | No for planning. | Capture export if feasible; otherwise record manual evidence and follow-up. |
| BQ-E6-003 | Was the Power Platform/Copilot connection refreshed or verified before E6 smoke? | No for planning. | Record in manual evidence if relevant. |

## 19. Recommended Handoff

**Recommendation:** `slice-sizer`

**Rationale:** The candidate has one clear outcome and no planning blocker, but the process requires an explicit sizing verdict before generating the E6 slice spec.

## 20. Strategic Documentation Update Recommendations

| Recommendation | Reason | Priority |
|---|---|---|
| After E6 proves the pattern, update current-state and integration docs to distinguish registration smoke from stateful topic/workflow orchestration. | Avoid confusing E4 readiness, E5 smoke, and E6 orchestration. | High |
| Keep issue #4 separate unless the human chooses a docs slice. | E6 is intended to prove behaviour, not complete current-state reconciliation. | Medium |
