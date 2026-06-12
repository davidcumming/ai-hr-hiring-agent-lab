# Slice Sizing Assessment: slice-e1-candidate-evaluation-council

## 1. Candidate Metadata

| Field | Value |
|---|---|
| Candidate ID | `slice-e1-candidate-evaluation-council` |
| Candidate Name | Single-candidate Calibrated Evaluation Council (advisory, evidence-grounded) |
| Date Created | 2026-06-11 |
| Created By | slice-planning-agent (Claude), `slice-sizer` skill, Stage 1 |
| Source Planning Context | `docs/delivery/slices/slice-e1-candidate-evaluation-council/planning-context.md` (`pc-slice-e1-candidate-evaluation-council-2026-06-11`) |
| Status | Final |

## 2. Proposed Slice Summary

- **Primary Proposed Outcome** — A signed-in HR-role user submits or selects one synthetic candidate's resume and cover letter for one sample position with one pre-approved, versioned rubric; the service runs the Calibrated Evaluation Council and returns an advisory, evidence-grounded evaluation with a persisted audit/evidence record retrievable by `evaluation_id`. One primary outcome; the admin rigor-configuration requirement is treated as a server-side configuration input to this outcome, not a second outcome (see §6).
- **Proposed Scope** — API/service facade (`POST /api/evaluations`, `GET /api/evaluations/{evaluation_id}` — names to confirm at contract time), controlled evidence packet creation, orchestration of the 11 council roles, runtime rigor resolver (`standard | high_impact | escalated`, hiring defaults `high_impact`, server config wins), deterministic quality gates, local persistence/audit record, OpenAPI contract, local CLI/demo runner, and a Foundry Agents provider seam with a deterministic mock backend satisfying mock parity. No live Azure/Foundry/Copilot/Entra wiring.
- **Initial Concern Level** — `Moderate` (scope gravity of 11 roles + rigor config flagged in planning context §11; resolved below by bounding, not splitting).

## 3. Inputs Reviewed

| Input Type | Reference | Notes |
|---|---|---|
| Reconciled planning context | `planning-context.md` (Stage 0, 2026-06-11) | Status "Ready for Slice Planning"; findings RF-001…RF-013; open questions BQ-001…BQ-005 |
| Source document inventory | `source-document-inventory.md` | All 14 source docs present; source repo read-only; fixtures identified |
| Current-state doc | None exists | Greenfield repo (`main` @ `44dd219`); empty baseline is a recorded fact, not a gap to invent around |
| Architecture guideline | Canonical architecture + Foundry companion + API contracts + storage + identity docs (via planning context §2/§5) | Facade-owns-contract pattern; Foundry Agent Service / Agent Framework workflow is live target |
| ADR | None exist | Two-plus future ADRs flagged (planning context §11); none approved |
| Implementation/process lesson | None exist | First slice in repo |
| GitHub Issue | None exist | No unresolved blockers from prior work |
| Test/eval strategy | None exists | Eval-readiness note in planning context §8: behaviour unusually well defined for eval design |
| User instruction | Product Owner direction of 2026-06-11 (authoritative) | Maximize useful end-to-end coding progress pre-lab-wiring; Foundry Agents live target; rigor modes; hard boundaries |
| Process/standards | Process Doc §11, Orchestration Map §3 Stage 1, skills usage doc | Sizing rules and split triggers applied below |

## 4. Sizing Decision

**Decision** — `accept-as-one-slice`

**Decision Rationale** — The slice has exactly one primary outcome (one synthetic candidate evaluated against one approved rubric, advisory output persisted and retrievable) delivered through one user workflow on one contract surface, which keeps outcome coherence and workflow breadth within bounds despite high internal component count (Process Doc §11.2 triggers — multiple workflows, multiple process areas, unmanageable eval set — do not fire). Deterministic-mock execution with fixed JSON schemas, a fixed status vocabulary, and a written UAT statement makes the slice testable and evaluable as one focused unit, and live-model eval is explicitly deferred with the Foundry seam, so the eval set stays bounded. The two split candidates named in the planning context — the admin rigor-configuration surface and escalated Mode C runtime execution — are handled by bounding rather than splitting: rigor configuration enters this slice only as source-controlled server-side configuration (no admin API/UI workflow), and escalation triggers are always computed and recorded with Mode C execution semantics pinned by BQ-002 before spec acceptance criteria are written. Splitting further (e.g., council without persistence, or facade without council) would yield sub-slices that violate the Product Owner's requirement that the first slice be a useful end-to-end evaluation capability.

The accepted slice definition is: **one synthetic candidate, one sample position, one approved versioned rubric, local deterministic council execution with a Foundry Agents provider seam, API/OpenAPI contract, local persistence/audit record, server-side runtime rigor modes, and audit-ready advisory output; no live Azure/Foundry/Copilot/Entra wiring.**

### Explicit in-scope / deferred evaluation (per Product Owner instruction)

| Capability | Verdict | Rationale |
|---|---|---|
| API/service facade (submit + retrieve) | **In scope** | The facade is the slice's contract surface (no chat UI); without it nothing is user-visible or UAT-able |
| Controlled evidence packet creation | **In scope** | Council sequencing constraint (evidence before any evaluative reasoning) is core to the outcome's integrity; cannot be deferred without changing the architecture later |
| Council role orchestration (11 roles) | **In scope** | The council *is* the outcome; model-role reasoning is mock-backed, code roles are real. Orchestration shape must match the Foundry-agent target so wiring later is config, not restructuring |
| Runtime rigor resolver | **In scope** | Computes effective rigor from server config + request classification, records rigor-resolution explanation and all escalation triggers every run; request body can never downgrade rigor |
| Deterministic quality gates | **In scope** | Code-only, cheap, and required for the advisory output to be trustworthy enough to demo; part of the same closeout |
| Local persistence/audit record | **In scope** | Retrieval by `evaluation_id` with full intermediate outputs is half the UAT statement; local emulator/filesystem equivalents of the Blob + Table shapes |
| OpenAPI contract | **In scope** | One contract artifact for the two endpoints, using the adopted envelope/status vocabulary; small, and prevents contract drift |
| Local CLI/demo runner | **In scope (thin)** | Demo/UAT vehicle only; must call the facade exactly as an HTTP client would — no privileged side door |
| Foundry provider interface/scaffold | **In scope (seam only)** | Provider interface + deterministic mock with mock parity (`ai_backend_type = none`), incl. trace/eval metadata placeholders; no live client code paths exercised |
| Admin rigor-configuration **surface** (API/UI) | **Deferred — bounded in-slice substitute** | In-slice: source-controlled server-side config read at runtime, change-audited via source control. An admin endpoint/UI is a second persona workflow and new surface (RF-004, likely ADR) — natural follow-up slice |
| Escalated Mode C **execution** | **Conditional — BQ-002** | Triggers always computed/recorded in-slice. Whether Mode C executes at runtime is a PO decision (BQ-002) needed before Stage 2 acceptance criteria; either answer fits this slice's size since escalation adds council passes, not new architecture |
| GitHub Actions CI | **In scope (minimal only)** | One source-controlled workflow running the deterministic test suite on PR — directly supports the Stage 16 merge gate at low risk. Anything beyond (deployment, live evals in CI, environments) deferred |
| Live Foundry call execution | **Deferred** | Blocked behind backend ADR (BQ-001) and Canadian region/deployment approval (BQ-005); PO boundary for this phase |
| Azure resource provisioning | **Deferred** | Hard lab boundary; nothing in this slice requires it |
| Copilot Studio integration | **Deferred** | Out of scope per functional spec and planning context §10; facade API is the contract |
| Entra live delegated auth | **Deferred** | Lab roles (`hr`, `admin_lab`) simulated/stubbed consistent with the identity design's trusted-boundary rules; no Entra configuration created |

## 5. Sizing Scorecard

| Dimension | Assessment | Notes |
|---|---|---|
| Outcome coherence | `Good` | One primary outcome statable in two sentences; rigor config bounded as configuration input, not a second outcome |
| Workflow breadth | `Moderate` | One user workflow (submit → evaluate → retrieve), one persona at the API. Admin persona deliberately kept out of the workflow surface (config-file only) to avoid a second-workflow split trigger |
| Architecture impact | `Medium` | Greenfield, so no existing architecture is disturbed; fits canonical facade-owns-contract pattern. Two ADRs flagged (backend seam RF-002/BQ-001; rigor config RF-004/BQ-003) but both are sequenced at Stage 6 / before live wiring — neither requires resolution to size or spec the mock-backed slice. Watch item, not a split trigger |
| Data/state impact | `Medium` | One new, well-defined persistence area (evaluation record + evidence metadata), local only, metadata-first rows, no resume text in tables/logs. No memory, no permissions store, no cross-case state |
| Deterministic testability | `Clear` | Deterministic mock mandated; JSON schemas per council role; fixed status vocabulary; anchored 6-criterion rubric; written UAT statement; idempotency rules defined |
| Live-eval tractability | `Clear` | Live-model eval explicitly deferred to the Foundry-wiring/calibration follow-up (RF-008); this slice's eval contract is deterministic/structural plus fairness/never-log/rigor-downgrade cases. The Stage 10 carve-out rationale must be documented in the eval contract |
| Documentation impact | `Medium` | First current-state docs, actual-architecture doc, and ADR index will be created — all in one new coherent area, no cross-cutting rewrites |
| Privacy/data/audit risk | `Medium` | Synthetic-only, nothing leaves the lab; but hiring-domain fairness constraints and the audit record are high-assurance behaviours. They are the slice's purpose, not buried in it — the §7.5 isolate-by-splitting concern does not apply |
| Manual-config/source-control risk | `Low` | No portal/low-code config in this slice (no Azure/Foundry/Copilot/Entra). Rigor config and CI workflow are repo files. No prior manual-config debt exists |
| Closeout complexity | `Medium` | Sizable but single coherent branch delta: one service area, one contract, one fixtures set, one test/eval package, one new docs area. Passes the §11.3 heuristic: one agent can implement, one reviewer can understand, one eval package can verify, one doc pass can reconcile, one closeout review can approve |

Rough risk tier (sizing-only estimate, per skill §7.3): **High-Assurance** — hiring-domain evaluative output, fairness-sensitive, audit-bearing. The slice is bounded around exactly this behaviour rather than mixing it with unrelated lower-risk changes, so the §7.3 "split to isolate" rule is satisfied without splitting. Binding tier is assigned by `eval-risk-profiler` at Stage 4; high-assurance implies the full un-collapsed lifecycle path.

## 6. Scope Concerns

| Concern | Impact | Recommended Treatment |
|---|---|---|
| Scope gravity: 11 council roles + facade + persistence + rigor + gates is a large first branch | Larger-than-ideal PR; reviewer load | Accept (PO explicitly wants a meaningful end-to-end first slice); mitigate at Stage 5 with an implementation plan ordered by pipeline position; keep CLI and CI minimal |
| Admin rigor-configuration surface could balloon into an admin API/UI + config audit subsystem | Second workflow/persona; RF-004 ADR territory | Bound in-slice to source-controlled server-side config read at runtime; defer the admin surface to a follow-up slice; spec must state this boundary explicitly |
| Escalated Mode C execution semantics unresolved (BQ-002) | Acceptance criteria cannot be finalized | PO answer required before Stage 2 sign-off; both answers fit this slice's size — recorded-only narrows scope slightly, runtime-executable adds council passes under the same orchestration |
| Mock-centric drift: deterministic mock becomes de-facto architecture | Violates PO center-of-gravity rule; restructuring cost later | Spec must name the Foundry-agent live target as a binding architecture constraint; mock parity enforced against the agent-backed output contract incl. trace metadata placeholders |
| Fixture vendoring (job description, rubric v1, Jordan Rivera docs) lacks hashes (RF-012) | Hash-mismatch → `blocked` behaviour untestable without them | Compute and record `sha256` when vendoring fixtures into this repo; small in-slice task |
| Temptation to add second candidate / comparison output | Crosses no-ranking hard boundary | Out of scope; restate hard boundary in spec |

## 7. Architecture Concerns

| Concern | Impact | Requires ADR? |
|---|---|---|
| AI-backend seam: Foundry Agent Service vs Agent Framework workflow vs interim model-endpoint rung; seam enumeration; trace/eval metadata contract (RF-002/BQ-001) | Blocks Stage 6/7 implementation start, not sizing or spec drafting; functional spec §4 is the outlier vs PO + canonical docs | `Yes` (before implementation; `adr-gap-detector` at Stage 6 or earlier; human approves) |
| Runtime rigor-mode configuration: location, admin surface, change audit, source-control capture (RF-004/BQ-003) | In-slice bounded version (repo config) needs only a spec statement; the full mechanism needs a decision | `Yes` (full mechanism — likely deferred-slice ADR; in-slice bounded version documented in spec) |
| Evaluation persistence layout: Blob + Table shapes vs local-emulator/filesystem equivalents; system-of-record boundary | Wrong local shapes would force migration when Azure wiring lands | `Unknown` (decide at spec/Stage 6; adopt source storage-doc shapes as default; ADR only if deviating) |
| Identity simulation for `hr`/`admin_lab` pre-Entra; case-less authorization = global role only (RF-006/BQ-004) | Authorization rule must be a stated decision, not an accident | `No` (explicit spec statement + PO sign-off at readiness review suffices for the lab) |
| Canadian region / approved Foundry deployments (RF-011/BQ-005) | Blocks any live Foundry call; irrelevant to mock-backed build | `Yes` (deferred — before live wiring slice, not this slice) |

## 8. Test and Eval Concerns

| Concern | Impact | Recommended Treatment |
|---|---|---|
| Live-model eval not executable in this slice (mock backend only) | Stage 10 needs an explicit, documented "live eval not applicable" rationale | Eval contract (Stage 4) records the deferral and ties council *trustworthiness* claims to the calibration follow-up slice (RF-008); slice output remains advisory-only |
| Rigor-downgrade hole is the named governance failure mode | Fairness/governance regression if untested | Mandatory eval/test cases: request-body rigor attempts are advisory-only, server config wins, attempted downgrade is recorded in the audit record |
| Prompt-injection via candidate documents (untrusted content) | Instruction-following from resume text would be a serious failure | Deterministic gate + test fixtures containing instruction-like resume content; flagged-never-followed assertion |
| Quality-gate coverage breadth (schema validity, all-criteria-scored, evidence-per-score, no-prohibited-factors, human-review flag, groundedness heuristic) | Each gate needs deterministic cases; manageable but must be enumerated | Eval contract enumerates per-gate pass/fail fixtures; deterministic mock makes the full pipeline repeatable |
| Escalation-trigger computation (6 trigger types) | Triggers must be unit-testable independent of BQ-002's answer | Test triggers as pure recorded computations; Mode C execution tests added per BQ-002 outcome |
| Cost/latency dimensions (6–7 model calls live; RF-013) | Not measurable against mock; must not be silently dropped | Record as deferred eval dimensions in the eval contract for the live-wiring slice |

## 9. Privacy, Data Residency, and Auditability Concerns

| Concern | Applies? | Impact | Recommended Treatment |
|---|---|---|---|
| PHI | `No` | Sample position is health-sector themed but fully fictional | Keep fixtures `SYNTHETIC`-labelled; no real health data ever |
| PII | `No` (real) / handled *as if* yes | Synthetic resumes only; discipline must match real-PII handling so habits survive contact with reality | Metadata-first evidence rows; no resume text in Table rows, logs, or telemetry; never-log rule enforced by tests |
| Canadian data residency | `No` (this slice) / `Yes` (when live) | No live calls in this slice; residency decision gates the wiring slice | Carry RF-011/BQ-005 forward as a live-wiring blocker; never adopt an unapproved region silently |
| Audit trail | `Yes` — core requirement | Full record (request, doc hashes, evidence packet, every council output, synthesis, gate results, agent metadata, rigor resolution, human-review block, timestamps) retrievable by `evaluation_id` | In scope as a primary acceptance area; eval cases verify reconstruction of every intermediate step |
| Sensitive eval data | `Yes` | Fairness-trap cases are sensitive-by-design | Synthetic-only fixtures; calibration gold set (60 cases) deferred to follow-up slice per RF-008 |
| External sharing | `No` | Nothing leaves the lab | Restate in spec out-of-scope |

## 10. Manual Configuration and Source-Control Concerns

| Surface / Area | Risk | Evidence Needed | Follow-Up Needed |
|---|---|---|---|
| Azure / Foundry / Copilot Studio / Entra portals | None this slice — no portal work occurs | None | `No` (re-assess at live-wiring slice; RF-004 admin-config mechanism is the known future debt source) |
| Runtime rigor configuration | Low if repo-file config; becomes manual-config debt if it drifts to portal app settings later | Config file in source control; changes visible in git history | `Yes` — follow-up slice + ADR for the admin surface and config audit (BQ-003) |
| GitHub Actions (minimal CI) | Low — single source-controlled workflow file | Workflow file in repo | `No` |
| Local persistence (emulator/filesystem) | Low — no cloud resources; shapes should mirror storage-doc design to avoid migration debt | Persistence layout documented in current-state docs at Stage 12 | `No` |

No prior manual-config debt exists (greenfield repo); the debt ceiling is not in play.

## 11. Closeout Complexity Assessment

One closeout package is achievable. The branch delta is one new service area plus fixtures, tests, one OpenAPI contract, one thin CLI, one CI workflow, and the first current-state/actual-architecture docs — all traceable to a single spec and a single eval contract. Traceability is unusually clean because the source docs already provide JSON schemas, a fixed status vocabulary, an anchored rubric, and a UAT statement to trace against. The main closeout burdens are (a) reviewing the council orchestration code as one coherent unit — mitigated by the pipeline's linear, role-per-component structure — and (b) producing the repo's first current-state documentation from scratch, which is bounded because nothing else exists to reconcile against. Re-running the deterministic eval package is cheap and repeatable by design. This does not exceed one practical human review.

## 12. Split Recommendation

Not applicable — decision is `accept-as-one-slice`. For the record, the natural seams identified (admin rigor-configuration surface; escalated Mode C execution if BQ-002 answers "recorded-only"; live Foundry wiring + calibration gold-set runs) are preserved as follow-up slice candidates rather than splits of this slice, because each depends on this slice's outputs and none can be a useful *first* end-to-end capability on its own.

## 13. Blockers and Open Questions

| ID | Blocker / Question | Blocks Sizing? | Blocks Slice Spec? | Recommended Action |
|---|---|---|---|---|
| BQ-002 | Escalated rigor semantics: when admin config sets `escalated` (or triggers fire under `high_impact`), does Mode C execute at runtime in this slice, or are escalations recorded-only with Mode C as follow-up? | `No` | `Yes` — acceptance criteria cannot be finalized without it | **Surface to Product Owner now**; cheap to answer; both answers fit the accepted slice size |
| BQ-001 | AI-backend ADR: Foundry Agent Service vs Agent Framework workflow; seam enumeration; trace/eval metadata contract (RF-002) | `No` | `No` (spec names the live target as constraint; ADR drafted by Stage 6) | `adr-gap-detector` at/before Stage 6; human approves ADR |
| BQ-003 | Rigor-config mechanism, admin surface, change audit, source-control capture (RF-004) | `No` | `No` (spec states the bounded in-slice version; full mechanism deferred) | Spec boundary statement now; ADR with the follow-up admin-surface slice |
| BQ-004 | Authorization rule for case-less evaluations (global `hr` role only; RF-006) | `No` | `No` (must be stated in spec) | Explicit spec statement; PO sign-off at Stage 3 readiness review |
| BQ-005 | Canadian region / Foundry deployment approval (RF-011) | `No` | `No` | Human decision before any live Foundry call; out of this slice |

No sizing blockers exist. The single spec-blocking item is BQ-002.

## 14. Recommended Next Skill

**Recommendation** — `slice-spec-generator`

**Handoff Notes** — Before or alongside spec drafting, obtain the Product Owner's answer to BQ-002 (escalated Mode C: runtime-executed vs recorded-only) — it is the only item blocking final acceptance criteria. The spec must: (1) define the slice exactly as bounded in §4, including the explicit in-scope/deferred table; (2) name the Foundry-agent-backed council as the binding live-target architecture constraint with the deterministic mock as scaffolding behind the same seam (mock parity incl. trace metadata placeholders); (3) state the rigor rules as acceptance criteria — server config wins, hiring defaults `high_impact`, request-body rigor advisory-only with attempted downgrades recorded, all six escalation triggers computed and recorded every run; (4) state the case-less authorization rule (global `hr` role; `admin_lab` for config) as a decision; (5) carry the hard boundaries (synthetic-only, advisory-only, `decision_support_only`/`human_review_required` always true, no ranking/contact/advance-reject, no Azure/live-Foundry/secrets/merge without human gates) into out-of-scope and unsafe-failure-mode sections; (6) seed the eval contract with the rigor-downgrade, prompt-injection, never-log, quality-gate, and audit-reconstruction cases from §8, plus the Stage 10 live-eval deferral rationale. Do not start implementation, create branches or issues, or treat this assessment or the spec as coding approval — Stage 3 readiness review and human gates govern.
