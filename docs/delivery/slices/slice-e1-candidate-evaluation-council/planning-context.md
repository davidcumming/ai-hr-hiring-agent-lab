# Reconciled Planning Context — slice-e1-candidate-evaluation-council

## Context metadata

| Field | Value |
|---|---|
| Context ID | `pc-slice-e1-candidate-evaluation-council-2026-06-11` |
| Topic / capability area | Single-candidate evaluation via a Calibrated Evaluation Council of Foundry agents, with admin-configurable runtime rigor |
| Stage | 0 — Planning context reconciliation (Orchestration Map §3) |
| Skill executed | `planning-context-reconciler` (Slice Planning Agent) |
| Date created | 2026-06-11 |
| Created by | slice-planning-agent (Claude) |
| Documentation repo reference | `hr-hiring` source repo (read-only); resolved root and per-document inventory in [`source-document-inventory.md`](./source-document-inventory.md) |
| Code repo baseline | `main` @ `44dd219` ("start") — standards/skills/role prompts only; no application code |
| Latest Product Owner direction | Recorded 2026-06-11 (authoritative for reconciliation): Foundry-agent-backed Calibrated Evaluation Council behind a service/API boundary, with admin-configurable runtime rigor modes |
| Status | **Ready for Slice Planning** (Stage 1 — slice sizing), with named open questions to resolve before/at spec time |

**Source-of-truth posture for this document.** Everything in the source repo and in this context that describes the council, the API, or storage is **intent, not built reality**. Nothing has been implemented. This document does not create a slice spec.

---

## 1. Current implementation repo state

**Repo:** `/Users/davidcumming/coding_projects/ai-hr-hiring-agent-lab` (branch `main`, single commit `44dd219`).

What exists:

- `AGENTS.md`, `CLAUDE.md`, `README.md`, `.gitignore` — repo instructions and lab boundaries.
- `standards/azure-development-standards/` — vendored GenTech standards (process doc, skills doc, orchestration map, skill packages, role prompts, slice-state template/schema at `docs/delivery/slices/_template/slice-state.yaml`).
- `.agents/` and `.claude/` — Codex/Claude discovery mirrors of skills and role prompts.

What is absent (current-state facts, not gaps to be invented around):

- **No application code** — no `src/`, `api/`, `tests/`, `fixtures/`, no `pyproject.toml`/`package.json`/requirements files, no CI.
- **No current-state documentation, no actual-architecture doc, no ADR index, no lessons registers, no known-limitations doc** beyond the lab boundaries in `AGENTS.md`.
- **No GitHub Issues** for this repo.
- **No test or eval assets** of any kind.
- **No `docs/` tree** existed before this slice folder; `docs/delivery/slices/slice-e1-candidate-evaluation-council/` is created by this Stage 0 pass as the per-slice working folder required by `CLAUDE.md`.

Consequence: there are zero already-implemented or partially-implemented capabilities. The current-state baseline for this capability area is **empty**, and every capability described below is classified `planned-or-aspirational` unless noted. No minimal governance placeholder beyond this slice folder was created (the skill does not require one).

## 2. Read-only source documentation inventory and resolved source-doc path

**Resolved source-doc root:** `/Users/davidcumming/Library/Mobile Documents/iCloud~md~obsidian/Documents/Markdown Repo/0-Work/copilot-agents/hr-hiring` (candidate paths 1–4 do not exist; full path-check table, per-document inventory, status, and key extractions are in [`source-document-inventory.md`](./source-document-inventory.md)). All 14 instructed source documents were found; none missing. The source repo is read-only documentation: requirements, constraints, architecture intent, API expectations, fixtures, and acceptance criteria were extracted; its implementation was not read and is not to be copied.

Source-authority summary used for this reconciliation:

| Claim type | Authority used |
|---|---|
| Current product behaviour | Working-repo inspection only (empty baseline) |
| Strategic intent — council behaviour | `docs/calibrated_evaluation_council.md` |
| Strategic intent — slice outcome | `docs/hr/slice-e1-candidate-evaluation-functional-spec.md` (draft) |
| Architecture boundaries | `docs/microsoft-stack-agentic-architecture.md` (canonical) + `docs/architecture/foundry-agent-framework-architecture.md` (companion) |
| API envelope/status vocabulary | `docs/architecture/azure-functions-api-contracts.md` |
| Storage/evidence, identity, generation controls, security | Respective `docs/architecture/`, `docs/prompts/`, `docs/security/` documents |
| **Latest direction (overrides on conflict, surfaced not silent)** | Product Owner direction of 2026-06-11 as supplied to this task |
| Unresolved work | None recorded (no GitHub Issues exist) |
| Verified behaviour | None (no tests/evals exist) |

## 3. Reconciled business outcome for the slice

*Intent, not built reality.* A signed-in HR-role user submits **one synthetic candidate's** resume and cover letter for a **sample position** with a **pre-approved, versioned rubric** (all three pre-seeded as fixtures standing in for deferred intake/rubric/import slices). The service runs the Calibrated Evaluation Council and returns an **advisory, evidence-grounded evaluation** containing, in one response:

- criterion-level scores on the rubric's anchored 1–5 scale (6 criteria for the sample rubric);
- cited supporting evidence, contrary evidence, and explicit missing-evidence notes per criterion;
- material disagreements between council members and how they were resolved;
- a policy/fairness review block (prohibited factors, unsupported inferences);
- confidence, limitations, and a final advisory recommendation label (`advance_to_interview | do_not_advance | hold_for_review | insufficient_evidence`);
- `decision_support_only: true` and `human_review_required: true` — always;
- a persisted audit/evidence record (every intermediate agent output included) retrievable by `evaluation_id`.

UAT success statement (from the functional spec, adopted): the HR user gets all of the above in one envelope; `GET` by `evaluation_id` reconstructs every intermediate step; with the deterministic mock backend the entire flow is repeatable.

## 4. User-visible workflow

*Intent.* The slice's contract surface is the **service/API facade**, not a chat UI (Copilot Studio topic build is explicitly out of scope; the front-end must never call a model directly).

1. An authenticated user with the `hr` lab role calls `POST /api/evaluations` (endpoint name proposed, confirm at contract time) with: `position_id` (fixture id), `candidate_ref` (fixture id) **or** inline `resume_text` + `cover_letter_text`, an `idempotency_key`, and optionally an `evaluation_question`.
2. The facade validates identity/role, validates input, enforces idempotency, resolves and hash-verifies the versioned fixtures, then runs the council at the **server-determined rigor mode** (hiring defaults to `high_impact`; the request body cannot downgrade rigor).
3. The user receives the standard response envelope: `safe_details` carries the advisory evaluation summary; the full record is by reference; `status` uses the fixed vocabulary (`completed`, `blocked` on rubric hash mismatch, `validation_failed` on unknown position/candidate, HTTP 400 on malformed body, `unauthorized` on missing role).
4. The user (or an auditor) retrieves the persisted full evaluation record via `GET /api/evaluations/{evaluation_id}`.
5. A human reviews; the output never advances, rejects, ranks, or contacts anyone. Escalation triggers are computed and **recorded**; whether an escalated (Mode C) run executes is governed by the admin rigor configuration (see §6 and open question BQ-002).

An administrator (`admin_lab` role) separately configures the runtime rigor mode (see §6).

## 5. Council / Foundry target architecture summary

*Intent — target architecture per the Product Owner's latest direction, reconciled with the source docs.*

**Live target:** the council is backed by **Foundry Agents** — Foundry Agent Service / Microsoft Agent Framework workflow orchestration — sitting **behind the service/API facade**. This matches the canonical pattern's backend-decision rule (multi-agent propose/validate rubric evaluation ⇒ Agent Service/workflow, not a bare model endpoint) and the quality-controls doc's "Multi-Agent Validation Requirements". The facade owns identity, authorization, gates, input validation, idempotency, schema validation of agent output, persistence, evidence, and the response envelope; agents own only reasoning and return proposed structured JSON with trace/eval metadata. Note: the draft functional spec's backend seam names only `foundry_model_endpoint` — a conflict with this target; see RF-002 in §8.

Council roles to orchestrate (council spec §13, confirmed by the PO direction):

1. Request Normalizer (code; classifies hiring as high-impact by default)
2. Source Ingestion / Versioning (code; fixture refs + inline docs, hashed — evidence is versioned before any reasoning)
3. Evidence Extraction Agent (model; builds the controlled evidence packet; makes no recommendation)
4. Deterministic Rules Validator (code-first; runs before any judgment)
5. Merit Advocate (model)
6. Risk / Gaps Advocate (model)
7. Neutral Scoring Judge (model)
8. Policy / Fairness Auditor (model)
9. Synthesis Judge (model; evidence wins, not votes)
10. Quality Gate Evaluators (code: schema validity, all-criteria-scored, evidence-per-score, no-prohibited-factors, human-review flag, groundedness heuristic)
11. Persistence / Human Review Queue (code; Blob full record + Table evidence row)

**Sequencing constraint:** the evidence packet is created before any evaluative agent reasons, and every council role reasons only from the controlled evidence packet and source references (council spec §3, §12).

**Scaffolding posture:** local deterministic mocks and a provider seam are allowed so coding can start before lab wiring exists — and mock parity is independently mandated by the source quality-controls doc — but per the PO direction **mocks are development scaffolding, not the architecture center**. The live target is Foundry-agent-backed council orchestration; Foundry/lab wiring must be config-based (server-side settings, managed identity / Key Vault) and safe to add later without restructuring. No live Foundry calls and no Azure resource creation occur in this planning work or without an approved, scoped implementation step.

## 6. Runtime rigor-mode requirement

*Intent — primarily from the PO's latest direction; partially beyond the source docs.*

- Rigor modes: **`standard`**, **`high_impact`**, **`escalated`** — selectable **at runtime by an administrator** (server-side configuration; `admin_lab` is the relevant lab role).
- **Hiring/candidate evaluation defaults to `high_impact`** (aligned with council spec §4.1 and the functional spec's Request Normalizer).
- **A normal HR user must not be able to downgrade rigor through the request body.** If a requested-rigor field ever appears in the API, it is **advisory only** unless server-side/admin configuration allows it.
- Mode composition follows council spec §10: standard ≈ Mode A (~4 model calls), high_impact ≈ Mode B (~6–7), escalated ≈ Mode C (~8–9, adds second Synthesis Judge + Rubric Calibration Judge + mandatory human review).
- **Escalation triggers** (computed every run, recorded in the audit record): agent score variance above threshold; missing required evidence; low synthesis confidence; policy/fairness auditor severity; recommendation near decision threshold; a scored criterion having no direct evidence. (Union of council spec §10 and the PO direction — consistent.)
- Open conflict on escalated-mode execution semantics (recorded-only vs runtime-executable) — see RF-003/BQ-002 in §8.
- The rigor configuration mechanism itself (where it lives, how an admin changes it, how changes are audited and kept in source control) is **not designed in the source docs** — see RF-004; likely ADR.

## 7. Data, privacy, audit, and human-review constraints

Hard constraints carried into planning (sources: security operating rules, council spec, canonical architecture, `AGENTS.md`, PO direction):

| Concern | Applies? | Planning impact |
|---|---|---|
| Real applicant data / PII | No — prohibited | Synthetic/sample data only; fixtures are fictional (`SYNTHETIC` labelled). Treat synthetic resume content *as if* PII for handling discipline. No real applicant data ever. |
| PHI | No | Sample position is health-sector themed but all content is fictional. |
| Canadian data residency | Yes (when live) | Foundry region/model deployment must follow the approved-Canadian-region decision; unapproved region/deployment is never adopted silently — pause for architecture decision. No live calls in this slice's planning. |
| Audit trail | Yes — core requirement | Full evaluation record (request, source-document hashes, evidence packet, every council member's output, synthesis, gate results, model/agent metadata incl. trace/eval IDs, human-review block, timestamps) persisted and retrievable by `evaluation_id`. Evidence rows are metadata-first: **no resume text in Table rows or logs**. |
| Telemetry never-log | Yes | No raw resumes, prompts, model inputs/outputs in telemetry or logs — references and safe metadata only. |
| Sensitive eval data | Yes | Eval fixtures must remain synthetic; fairness-trap cases (future calibration set) are deliberately sensitive-by-design and synthetic-only. |
| External sharing | No | Nothing leaves the lab. |
| Human review | Yes — mandatory | `human_review_required: true` and `decision_support_only: true` on every evaluation. Output is advisory; no advance/reject action, no ranking across candidates, no candidate contact, no production hiring decision. |
| Fairness | Yes — mandatory | Protected characteristics and proxies (name, age, gender, race, nationality, disability, family status, school/address prestige, employment gaps, photographs) are never scored; Policy/Fairness Auditor + deterministic no-prohibited-factor gate enforce this; candidate text is untrusted content — data, never instructions (prompt-injection-like content is flagged, never followed). |
| Secrets | No secrets in repo | Backend config via server-side settings; managed identity / Key Vault when live wiring happens. Never commit secrets. |
| Versioned evidence | Yes | Never evaluate against mutable, unversioned source material: rubric and documents carry version + hash; evaluation reproducible against exact versions. |

Process gates (must STOP for human approval): ADR approval, residual-risk acceptance, GitHub Issue creation, any merge; no Azure resource creation, no deployment, no live Foundry calls in planning.

## 8. Known conflicts and ambiguities (full classified findings)

Every material finding, classified per the skill's reconciliation categories. No conflict was silently resolved; where the PO direction overrides a source doc, that is recorded here, not absorbed.

| ID | Finding | Category | Source(s) | Planning impact |
|---|---|---|---|---|
| RF-001 | The entire E1 capability (council evaluation service, API, persistence, fixtures) exists only as documentation intent; the working repo is empty of implementation. | `planned-or-aspirational`, `candidate-for-next-slice` | Working-repo inspection; functional spec | Greenfield slice; no duplicate-implementation risk; everything below is intent. |
| RF-002 | **Backend conflict (flagged per task instruction).** The draft functional spec §4 defines the live seam as `ai_backend_type = foundry_model_endpoint` — every agent call as a direct model-deployment chat-completions call. The PO's latest direction (authoritative) makes **Foundry Agents orchestrated as a council** the live target. The source repo's own architecture docs side with the PO: the Foundry companion's decision table routes "multi-agent propose/validate or rubric evaluation" to **Foundry Agent Service / Agent Framework workflow**, and the quality-controls doc's multi-agent section mandates the same. The functional spec's backend section is the outlier. | `stale-or-contradicted` + `requires-adr` + `strategic-doc-update-recommended` | Functional spec §4 vs PO direction, Foundry companion §5/§7, quality-controls "Multi-Agent Validation Requirements" | Planning context adopts the Foundry-agent-backed target (per PO + canonical decision rule). An ADR must pin the backend architecture and the seam's backend-type enumeration (e.g. `none` / `foundry_agent_service` / `agent_framework_workflow`, and whether a plain model-endpoint mode survives as an intermediate rung). The source functional spec §4 should be updated by its owners after the ADR — not edited by this repo. |
| RF-003 | **Rigor taxonomy and escalation-semantics mismatch.** Council spec Request Normalizer uses risk levels `standard \| high_impact \| regulated`; cost modes are A/B/C (Standard / High-Impact / Escalated). The PO direction names runtime **rigor modes** `standard \| high_impact \| escalated` — i.e. mode-shaped, not risk-level-shaped, and `escalated` replaces/omits `regulated`. Further: the functional spec says escalated re-runs (Mode C) are "a recorded follow-up, not auto-executed in this slice", while the PO direction makes `escalated` an admin-selectable **runtime** mode (implying executable when configured). | `stale-or-contradicted` (taxonomy) + open question (execution semantics) | Council spec §4.1/§10, functional spec §3 vs PO direction | Adopt the PO's three rigor-mode names for planning. The spec must define both axes cleanly (request risk classification vs council rigor mode) and answer BQ-002 before acceptance criteria are written. |
| RF-004 | **Admin runtime rigor configuration is new surface.** Source docs make all council/model configuration server-side app settings (`HRHA_COUNCIL_*`) with no admin-facing runtime change mechanism, no config audit trail, and no admin endpoint. The PO requires rigor to be configurable at runtime by an administrator. | `planned-or-aspirational` + `requires-adr` + `manual-config-risk` | PO direction vs functional spec §4, identity doc §6 | Needs a decision: config location (app settings vs storage-backed config read at request time), the admin surface (endpoint vs ops procedure), auditing of rigor changes, and source-control capture (portal-changed app settings escape source control — capture as config-as-code or evidence). |
| RF-005 | The evaluation endpoints (`POST /api/evaluations`, `GET /api/evaluations/{evaluation_id}`) are proposed by the functional spec but absent from the canonical API-contracts doc (which enumerates only Slice 0/1 endpoints). Envelope and status vocabulary are fixed and reusable. | `planned-or-aspirational` | Functional spec §5; API contracts §5 | Endpoint names/shapes to be confirmed at contract time; envelope/status vocabulary adopted as a binding constraint. |
| RF-006 | **Case-less evaluation vs case-scoped RBAC.** Identity design requires global role **plus** case scope (`CaseAcl`) for case-scoped actions, but this slice's evaluations are explicitly case-less (`case_id: null`, CaseAcl integration out of scope). Authorization basis for `POST /api/evaluations` is therefore global `hr` role only. | `planned-or-aspirational` + open question | Functional spec §7; identity doc §3 | Acceptable for the lab slice, but the spec must state the authorization rule explicitly (global-role-only for case-less evaluations) so it is a decision, not an accident. |
| RF-007 | Privacy/audit/fairness constraints are richly defined and mutually consistent across source docs and PO direction (synthetic-only, advisory-only, human review mandatory, never-log, prohibited factors, versioned evidence). | `aligned` + `requires-privacy-review` (routine, at eval design) | §7 sources | Carry as binding constraints; eval design must include fairness/no-prohibited-factor and never-log checks. |
| RF-008 | Calibration gold-set (60 stratified synthetic cases, human-labeled) is specified and required before any AI-backed evaluation is *trusted*; functional spec defers gold-set runs as the immediate follow-up after E1. | `aligned` (sequencing) + `requires-eval-design` (future) | Calibration-set spec; functional spec §7 | E1 ships the council with deterministic-mock regression + small live smoke at most; council *trustworthiness* claims are out of scope until calibration runs. Strong candidate for a follow-up slice. |
| RF-009 | No GitHub Issues, ADRs, current-state docs, lessons, or eval baselines exist in the working repo. | current-state absence (input gap) | Working-repo inspection | Recorded per skill §4; nothing blocks planning, but the first slices must start producing these artifacts. |
| RF-010 | Mock-first development with **mock parity** is mandated by source docs and permitted by the PO as scaffolding, with the explicit PO caveat that mocks must not become the architecture center. | `aligned` | Quality-controls doc; PO direction | `ai_backend_type = none` is the regression default; the deterministic mock must satisfy the identical output schema/metadata contract the live Foundry-agent backend will satisfy; mocks not reachable as the normal product brain. |
| RF-011 | Foundry region/model-deployment approval for Canada is an open decision in the source docs; no live calls occur until it is made. | `requires-adr` (deferred — needed before live wiring, not before coding against mocks) | Foundry companion §9/§11; security rules | Does not block this slice's mock-backed build; blocks live Foundry smoke tests. |
| RF-012 | Rubric fixture carries `version` but no `sha256` field, while the functional spec requires version + hash ("never evaluate against mutable, unversioned source material"). | minor gap (`planned-or-aspirational`) | `rubric.v1.json` vs functional spec §2 | When fixtures are vendored into this repo, compute and record hashes; hash-mismatch → `blocked` behaviour depends on it. |
| RF-013 | Synchronous council execution is accepted for the lab (Durable Functions noted as the production path); 6–7 model calls per request in high_impact mode has latency/cost implications. | `aligned` (lab) + future consideration | Functional spec §7; council spec §10 | Eval contract should include cost/latency dimensions; async execution is out of scope. |

**Eval-readiness note:** behaviour is unusually well defined for eval design (JSON schemas for every council role, quality-gate list, UAT statement, fixed status vocabulary, anchored rubric, deterministic-mock determinism requirement). The only eval-blocking ambiguities are BQ-001/BQ-002 below.

**Blockers and open questions:**

| ID | Question | Blocking? | Owner / next action |
|---|---|---|---|
| BQ-001 | Backend seam enumeration and live backend choice (Foundry Agent Service vs Agent Framework workflow vs interim model-endpoint rung) — RF-002. | Not for Stage 1 sizing; **yes before Stage 6/7 implementation** | Draft ADR (`adr-gap-detector` at Stage 6 or earlier); human approves. |
| BQ-002 | Escalated rigor semantics: when admin config sets `escalated` (or triggers fire under `high_impact`), does Mode C execute at runtime in this slice, or are escalations recorded-only with Mode C as follow-up? | **Yes before spec acceptance criteria are finalized** (Stage 2) | Product Owner clarification; cheap to ask alongside sizing. |
| BQ-003 | Rigor-config mechanism + audit + source-control capture — RF-004. | Not for sizing; needed at spec/ADR time | Spec proposal + likely ADR; human approves. |
| BQ-004 | Authorization rule for case-less evaluations (global `hr` role only) — RF-006. | No (decision can be stated in spec) | Confirm in slice spec; PO sign-off via readiness review. |
| BQ-005 | Canadian region/model deployment approval — RF-011. | No for mock-backed build; yes before any live Foundry call | Human decision when lab wiring is scheduled. |

## 9. Assumptions

1. The PO direction of 2026-06-11 supersedes the draft functional spec wherever they conflict (it post-dates and explicitly reconciles it); conflicts are still surfaced above, not silently absorbed.
2. The slice is implemented in this lab repo as a service/API with a deterministic mock backend first; the Foundry-agent live backend is wired later behind config without restructuring (provider seam).
3. Fixtures (job description, rubric v1, Jordan Rivera resume/cover letter) will be vendored into this repo as synthetic fixtures (content extraction from the source repo is permitted and intended — they are requirements/fixtures, not implementation).
4. The standard response envelope and status vocabulary from the source API-contracts doc are adopted as the contract style for the new evaluation endpoints.
5. Lab roles (`hr`, `admin_lab`) will be simulated/stubbed in the lab consistent with the identity design's trusted-boundary rules until real Entra wiring is in scope; no Entra configuration is created by this slice.
6. "Runtime" admin configurability means without code deployment (config read per request or hot-reloadable), not necessarily a same-second toggle; exact mechanism is BQ-003.
7. Python is the likely implementation stack (source repo uses `pyproject.toml`), but stack choice is a Stage 5/6 concern, not fixed here.
8. The risk tier in `slice-state.yaml` is provisionally `high-assurance` (agentic, hiring-domain, fairness-sensitive); the binding tier is assigned by `eval-risk-profiler` at Stage 4.

## 10. Out-of-scope items

From the functional spec §7, PO hard boundaries, and lab rules:

- Multi-candidate batches; shortlisting or **ranking across candidates**.
- Rubric authoring/approval workflow; applicant import; job posting/intake (deferred slices — their outputs are fixtures here).
- Any final advance/reject action, production hiring decision, or candidate contact.
- Copilot Studio topic build (facade API is the slice contract); any front-end calling a model directly.
- Async/queued execution (synchronous accepted for the lab; Durable Functions = production path note only).
- Calibration gold-set runs (immediate follow-up, not this slice).
- Case objects / `CaseAcl` integration (evaluations are case-less, `case_id: null`).
- Azure resource creation, deployment, live Foundry calls during planning; secrets; merge or issue creation without human gates.
- Real applicant data of any kind.
- Editing the read-only `hr-hiring` source repo or the vendored standards.

## 11. Risks and likely future ADRs

Risks:

| Risk | Why it matters | Mitigation in planning |
|---|---|---|
| Mock-centric drift — the deterministic mock becomes the de-facto architecture and Foundry-agent orchestration is bolted on badly later | Directly violates the PO direction's center-of-gravity rule | Spec must state the live target; seam/ADR (BQ-001) decided before implementation; mock parity enforced against the *agent-backed* output contract incl. trace metadata placeholders |
| Rigor downgrade hole — request body or client-supplied field influencing council size | Fairness/governance failure mode named by the PO | Acceptance criteria + eval case: requested rigor is advisory only; server config wins; attempted downgrade is recorded |
| Scope gravity — 11 council roles + persistence + rigor config + admin surface may exceed one slice | Sizing risk | Stage 1 `slice-sizer` decides; natural split seams exist (e.g. rigor-admin surface as follow-up, escalated Mode C execution as follow-up per BQ-002) |
| Cost/latency of 6–7 sequential-plus-parallel model calls (live mode) | Lab spend + sync timeout | Cost/latency as eval dimensions; mock default; no provisioned throughput |
| Fairness regressions undetectable without calibration set | Council is not self-validating | Keep E1 claims advisory-only; schedule calibration slice early (RF-008) |
| Manual-config debt — portal-changed app settings / Foundry resources escaping source control | Standards' manual-config rule | Config-as-code preference; manual-evidence capture when portal work happens |
| Prompt-injection via candidate documents | Untrusted-content rule | Deterministic gate + eval cases for instruction-like resume content |

Likely future ADRs (flag only — `adr-gap-detector` owns formal detection; humans approve all ADRs):

1. **AI-backend architecture for the council** — Foundry Agent Service vs Agent Framework workflow vs interim model-endpoint composition; seam enumeration; trace/eval metadata contract (RF-002/BQ-001).
2. **Runtime rigor-mode configuration** — storage, admin surface, audit, source-control capture (RF-004/BQ-003).
3. **Evaluation persistence layout in this lab repo** — adopting Blob + Table shapes (`evaluations` container, `EvaluationEvidence` table) vs local-emulator equivalents; system-of-record boundaries (storage doc adoption).
4. **Canadian region / approved Foundry deployments** — before any live call (RF-011/BQ-005).
5. **Identity simulation strategy** for `hr`/`admin_lab` in the lab pre-Entra (BQ-004 adjacent).

Strategic documentation update recommendation (recommend only; do not edit the source repo): after ADR-1, the `hr-hiring` functional spec §4 backend seam should be updated by its owners to match the Foundry-agent council target (RF-002). Priority: medium.

## 12. Recommended next stage and next prompt to run

**Recommended handoff:** `slice-sizer` (Stage 1 — slice sizing). 

**Rationale:** the context is clean enough to size: one candidate area, well-bounded, with named open questions. It is *not* clean enough to jump straight to `slice-spec-generator`, because BQ-002 (escalated-mode execution semantics) shapes acceptance criteria, and sizing should explicitly consider splitting the rigor-admin surface and Mode C execution out of the first slice. No blocker prevents Stage 1.

**Candidate next-slice area (candidate only — no spec created here):**

| Candidate | Outcome | Readiness | Main risk | Recommended next action |
|---|---|---|---|---|
| slice-e1-candidate-evaluation-council | §3 business outcome | Ready for sizing | Scope gravity (11 roles + rigor config + admin surface); BQ-002 ambiguity | `slice-sizer`; obtain PO answer to BQ-002 in parallel |

**Suggested next prompt:**

> You are acting as the slice-planning-agent. Read `/Users/davidcumming/coding_projects/ai-hr-hiring-agent-lab/.claude/agents/slice-planning-agent.md` and adopt that role. Then follow the skill at `/Users/davidcumming/coding_projects/ai-hr-hiring-agent-lab/.claude/skills/slice-sizer/SKILL.md` exactly. TASK: Stage 1 sizing verdict (accept / split / block) for slice-e1-candidate-evaluation-council, using the reconciled planning context at `docs/delivery/slices/slice-e1-candidate-evaluation-council/planning-context.md` and the source-document inventory beside it. Explicitly assess: (a) whether the admin runtime rigor-configuration surface and (b) escalated Mode C execution belong in this slice or in follow-up slices, given open questions BQ-002/BQ-003. Update `slice-state.yaml` with the Stage 1 outcome. Do not write the slice spec. Also surface BQ-002 to the Product Owner: "When admin config selects `escalated` (or escalation triggers fire), does Mode C execute at runtime in this slice, or are escalations recorded-only?"
