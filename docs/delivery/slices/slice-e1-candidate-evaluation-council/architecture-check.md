# Architecture Guideline Compliance Report: Single-Candidate Calibrated Evaluation Council

> Stage 6 — Architecture compliance & ADR check. Produced with `architecture-guideline-checker`
> (compliance findings) and `adr-gap-detector` (AF-001 deferred-ADR recording only — conditional
> trigger satisfied by the plan's flagged ADR concern; not run speculatively).
>
> **Path note (skill §8):** the skill's default output name is
> `architecture-compliance-report.md`; this slice's orchestrator directed the report to
> `architecture-check.md`. This file is that report — no second report exists.

## 1. Report Metadata

| Field | Value |
|---|---|
| Slice ID | `slice-e1-candidate-evaluation-council` |
| Slice Name | Single-Candidate Calibrated Evaluation Council (advisory, evidence-grounded, mock-backed with Foundry seam) |
| Report Date | 2026-06-11 |
| Report Author | coding-agent (Claude), Stage 6 |
| Implementation Plan Reference | [`implementation-plan.md`](./implementation-plan.md) (Stage 5 final, 2026-06-11) |
| Architecture Guidelines Version | Slice spec §15 adopted constraints (2026-06-11), sourced from the read-only `hr-hiring` canonical docs: canonical architecture, Foundry companion (`foundry-agent-framework-architecture.md`), API contracts (`azure-functions-api-contracts.md`), storage/evidence design (`azure-storage-and-evidence-design.md`), identity/RBAC design, quality controls (`agentic-capability-implementation-guidelines.md`). Source docs were consulted read-only to verify specific claims. |
| ADR References Reviewed | **None exist** (greenfield repo; confirmed — no `docs/architecture/adr/` content) |
| Actual Architecture Document | **None exists** (greenfield, `main` @ `44dd219`); drift analysis is therefore vacuous by construction |
| Slice Spec Reference | [`slice-spec.md`](./slice-spec.md) (§15 constraints, §16 gaps, §2.2.2 PO decision) |
| Status | Final |

---

## 2. Compliance Surface Summary

Every planned item assessed (plan §3/§4 — greenfield, all `New`):

| Area | Description | Plan Section |
|---|---|---|
| Server-side config | `config/lab-config.toml`, `config.py`, defaults, test-override mechanism | §3.3 |
| Facade API | endpoints, order of operations, auth stub, envelope, status vocabulary, error mapping | §3.4 |
| Fixtures | vendoring, manifest, sha256, SYNTHETIC labels | §3.5 |
| Evidence packet | code-built pre-reasoning packet, segment addressing | §3.6 |
| Council orchestration | 11 roles, code vs model-backed split, Mode A/B/C, sequencing, bounded retry | §3.7 |
| Rigor + triggers | resolver pure function, six triggers every run | §3.8 |
| Escalation policy | `record_only`/`auto_escalate` (implemented), provenance enum | §3.9 |
| Quality gates | six deterministic gates, per-gate fail behaviour | §3.10 |
| Local persistence | blob-equivalent record, table-equivalent JSONL rows, idempotency, review queue | §3.11 |
| Safe response contract | literal-True flags, closed advisory enum | §3.12 |
| OpenAPI contract | committed document + regenerate-and-diff | §3.13 |
| CLI runner | HTTP-only client, import-graph constraint | §3.14 |
| Provider seam + mock + stub | `CouncilProvider`, deterministic mock, lazy Foundry stub | §3.15 |
| Logging | never-log discipline, redaction filter | §3.16 |
| Dependencies | fastapi, uvicorn, pydantic v2; dev: pytest, httpx, openapi-spec-validator — **zero cloud SDKs** | §3.1 |
| Microsoft-stack surfaces | **None live this slice** — no Azure/Foundry/Copilot Studio/Entra/portal/IaC activity (plan §3.17, §4.4, §4.5); only GitHub Actions (source-controlled workflow, no credentials) | §3.17, §4.5 |

---

## 3. Compliance Findings — per spec §15 constraint

Finding types per skill §7: Compliant / Violation / Not covered / Ambiguous / ADR extends guideline.

| # | §15 Constraint | Finding | Rationale |
|---|---|---|---|
| C-001 | **Facade owns the deterministic business contract** (identity, authorization, validation, idempotency, gates, schema validation of agent output, persistence, envelope); agents own reasoning only, return proposed structured JSON | **Compliant** | Plan §3.4 fixed order of operations puts auth first, before any validation/fixture/persistence side effect (DT-009/DT-016). Code roles (Normalizer, Ingestion/Versioning, Rules Validator, Gate Evaluators, Persistence/Review Queue) are facade-owned with no provider calls (§3.7). Model-backed roles return schema-validated proposed JSON; validation, gates, escalation decision, and persistence are all code (§3.7/§3.9/§3.10/§3.11). No business decision logic inside model-backed roles. CLI is HTTP-only with an import-graph test — no privileged side door (§3.14, DT-018). Matches the Foundry companion §9 rule that backends never mutate state and never bypass the facade. |
| C-002 | **Foundry Agents live target; seam designed against the agent-backed contract incl. trace/eval metadata placeholders; mock parity; wiring later = config, not restructuring** | **Compliant** — with condition **C-COND-2** (below) | Seam (`CouncilProvider`, §3.15) declares the Foundry companion §8 shape as its authority; one schema source serves mock and stub (DT-013, "no mock-only schema fork"); placeholders typed and populated by the mock; stub is lazy, SDK-free, raises `ProviderNotConfiguredError`; backend selection is config (`ai_backend_type`). Mock parity satisfies the quality-controls mandate ("every AI-powered operation has a deterministic mock equivalent", guidelines doc §2.8/§"Testing"). Companion §8 verification: AI backend type ✓; model/agent ID ✓ (`model_deployment`, `agent_run_id`); workflow version ✓ via orchestration version recorded in provider metadata (plan §6.3) plus `role_schema_version`/`prompt_version`; token + latency ✓; validated-output confirmation ✓ (immediate schema validation + recorded retry count + gate 1 results). **Gap within the placeholder list:** companion §8 requires "trace ID **and eval ID**"; plan §3.15 enumerates `trace_id` but no evaluation-run identifier → condition C-COND-2. The *exact* live metadata schema is an open decision in the companion itself (§11 item 2) and belongs to the deferred ADR (G-001). |
| C-003 | **Standard response envelope + fixed status vocabulary adopted as contract style** | **Compliant** — with condition **C-COND-1** on the provisional HTTP codes (see §5) | Envelope field subset (§3.4) is drawn from the adopted envelope; all emitted statuses (`completed`, `validation_failed`, `unauthorized`, `blocked`) are within the fixed vocabulary; reserved statuses (`needs_input`, `error`) declared, never emitted; DT-014 locks the declared vocabulary. **AF-003 verified compliant:** gate-failure → `blocked` is inside the adopted vocabulary with explicit documented precedent — API-contracts §5.6 returns `blocked` with reason `generation_quality_gate_failed` when model output fails schema validation after one bounded retry, and §3.2 defines `blocked` as a business workflow gate. No new pattern; no ADR. Record the mapping as a design note in current-state docs (Stage 12). The provisional **HTTP codes** in plan §3.4 do conflict with the API-contracts decided mapping — captured as ambiguity A-001/condition C-COND-1; it binds build steps 11/13, not coding start. |
| C-004 | **Local persistence mirrors the storage-doc shapes** (Blob-equivalent full record + Table-equivalent metadata-first rows); deviation needs ADR | **Compliant** (AF-002 confirmed — faithful local mirror; no deviation, no ADR) | Verified against storage doc §2–§4: blob-equivalent full record holds the content-bearing payload (`evaluations/{evaluation_id}.json`) — mirrors "Blob holds large content" (§2.1) and the evidence-payload pattern (§3.4). Table-equivalent JSONL rows are metadata-first: partitioned by the owning entity id (`PartitionKey = evaluation_id` — the case-less analogue of `PartitionKey = case_id`, consistent with PO §2.2.1 case-less rule), ordered `RowKey` (sequence index — deterministic analogue of the doc's timestamp-prefixed RowKey, preserving the ordered-partition-scan intent without breaking DT-002 byte-identity), references/hashes/flags only, **no text-bearing fields in the row schema** (§2.1 "Tables never store large bodies of text"; BR-010). `IdempotencyRecords`-equivalent replays the stored envelope without re-execution — exactly storage doc §4.2/§6. Append-only writers mirror §2.7 append-only-by-code evidence. Local table name `EvaluationEvidence` vs doc `EvidenceMetadata` is local-equivalent naming, to be recorded in current-state docs. Non-blocking parity recommendation in §8 (row-level `actor_id`/`resolved_role`/`correlation_id`). |
| C-005 | **Never-log rule; managed identity/Key Vault when live; no secrets in repo** | **Compliant** | Central logging config with ids/hashes/statuses/counters only; redaction filter as defense-in-depth; HTTP access logs omit bodies; metadata-row schema structurally excludes content; DT-011 sweeps caplog + stdout/stderr against fixture-derived sentinels; CLI prints only the API response (the controlled channel). No secrets exist anywhere in the repo and nothing requires one (§3.3, §3.17); managed identity/Key Vault obligations activate only at live wiring (deferred ADR scope notes this). Consistent with companion §9 telemetry constraints. |
| C-006 | **Synthetic-only, advisory-only, mandatory human review; no ranking/contact/decisions** | **Compliant** | Fixtures vendored with `synthetic: true` manifest labels + sha256 (BR-011); test fixtures SYNTHETIC-labelled; no approval path for real data (plan §6.4). `decision_support_only`/`human_review_required` typed as literal `True` — unconstructible otherwise (§3.12, DT-010); closed advisory enum; **no field for hire/reject, cross-candidate rank, or candidate contact exists in any schema** (UFM-006); review-queue entry written for every evaluation; gate 5 belt-and-braces. Matches the lab boundary and companion §9 (no candidate-affecting action driven by a model). |
| C-007 | **Rigor/escalation configuration is server-side and source-controlled; request body never authoritative** | **Compliant** | `config/lab-config.toml` source-controlled, read at start, validated; defaults match spec §17 exactly (`high_impact`, `record_only`, `none`); git history is the change record. Resolver is a pure function in which server config always wins and a request can never lower rigor — downgrade attempts recorded (BR-002, DT-003). Tests use explicit config objects, never edits to the committed file. `auto_escalate` inclusion (AF-005) is config-gated, defaults off, PO-pre-authorized (§2.1.3) — no ADR; the provenance enum makes the policy applied explicit on every record (UFM-008). The full admin-surface/config-audit mechanism is correctly deferred (AF-006, spec §16 gap 2). |

Supporting findings (surfaces beyond the seven constraints):

| # | Planned Item / Pattern | Finding | Rationale |
|---|---|---|---|
| C-008 | Live Foundry wiring details (Agent Service vs Agent Framework, backend enumeration, live trace/eval metadata schema, region/residency) | **Not covered** → **G-001**, dispositioned **Deferred** (§6) | No guideline or ADR pins these; the Foundry companion lists them as open decisions (§11 items 1–2). PO decision 2026-06-11 (spec §2.2.2) defers the ADR; nothing in this slice's plan implements live wiring (stub raises on use). |
| C-009 | Dependency set (fastapi, uvicorn, pydantic v2; pytest, httpx, openapi-spec-validator) | **Compliant** (no constraint contradicted) | Zero cloud SDKs honours the hard no-live-cloud boundary (eval contract §9 blocking-fail row). No §15 constraint prescribes an application stack; the Stage 5 stack decision is recorded with rationale (plan §1.2/§3.1) and aligns with source-repo conventions. Guideline-update note in §8 (record in current-state docs; facade hosting shape at wiring time is an adjacent, not-pinned decision). |
| C-010 | GitHub Actions CI (one workflow, deterministic suite on PR) | **Compliant** | Source-controlled, no cloud credentials, no network beyond checkout; matches spec §17 and FR-014. AC-020 manual evidence scheduled. |
| C-011 | Test scenario-scripting backdoor risk | **Compliant** | Scripts injectable only via test-side provider construction, never via API or config (plan §3.15); DT-013 asserts the default provider is unscripted. Facade enforcement is not bypassable in the runtime path. |

---

## 4. Violations (Blocking)

No violations found.

---

## 5. Ambiguities (Clarification Required)

| ID | Planned Item | Ambiguity Description | Guideline Section | Clarification Needed From |
|---|---|---|---|---|
| A-001 (= condition **C-COND-1**; plan flag AF-004) | Provisional HTTP codes in plan §3.4 (`validation_failed` → 422, `blocked` → 409, unauthenticated → 403) | The API-contracts doc's **decided** mapping differs: business outcomes `completed`/`blocked`/`validation_failed` return **HTTP 200** with the status in the envelope (§2 principle 1, §4 table); **400** only for a malformed body (the plan already matches this); **401** for missing/invalid identity vs **403** for an authenticated role denial (§2 principle 2, §4); **409 is reserved** for concurrency conflicts carrying `status: "error"` (§3.2/§4) — a use this slice never emits. The plan itself marks its codes provisional "pending the OpenAPI authoring against the API-contracts doc's HTTP mapping section", i.e. it binds itself to the doc; this check performed that confirmation early and the provisional values do not match. The §15 constraint binds the envelope + status *vocabulary* (both met), so this does **not** block coding start — but it must be resolved before build step 11 (`api/errors.py` status mapping) to avoid rework, and is locked at step 13 by DT-014. | API-contracts doc §2 (principles 1–3, 5), §3.2, §4 | **None required if the documented mapping is adopted** (the doc already decides it — adjust plan §3.4's provisional table accordingly). Only if the team wants REST-style codes for the direct lab facade instead of the doc's tool-call convention does this become a recorded deviation requiring a human decision before step 11. |

No other ambiguities found.

---

## 6. Not-Covered Areas (ADR Gap Candidates) and Deferred-ADR Record

### 6.1 Gap inventory (adr-gap-detector, executed in-stage per plan §9 handoff)

ADRs searched: none exist (greenfield — confirmed). The gap cannot be closed by an existing ADR.

| ID | Gap | Confirmed Real? | Blocking Severity | Disposition |
|---|---|---|---|---|
| G-001 (= AF-001; spec §16 gap 1; OQ-001/BQ-001) | Live Foundry Agents wiring is not pinned by any guideline or ADR: Agent Service vs Agent Framework workflow choice; `ai_backend_type` enumeration beyond `none \| foundry_agents`; the exact live trace/eval metadata schema and its storage split (telemetry vs evidence rows — Foundry companion §11 item 2); approved Canadian region / data residency and approved model deployments (BQ-005) | Yes — companion §11 names these as open decisions; no ADR exists | **Conditionally blocking**: blocks every live-wiring component; **no such component exists in this slice's plan** (the Foundry stub is non-functional by design and raises on use) | **ADR required — DEFERRED by Product Owner decision 2026-06-11 (spec §2.2.2)**; durably recorded in §6.2 below and in [`adr-deferred-foundry-wiring.md`](./adr-deferred-foundry-wiring.md) (Status: Deferred — Draft). **Human approval of the ADR is a mandatory gate before the live-wiring slice begins.** |

| ID | Gap | Disposition |
|---|---|---|
| (not a new gap) | Admin rigor-config surface / config-change audit (AF-006; spec §16 gap 2) | Out of this slice's scope by spec; the in-slice bounded repo-file config needs no ADR (spec §16). Run `adr-gap-detector` when the admin-surface follow-up slice is planned. Not folded into G-001. |

### 6.2 Deferred-ADR record for live Foundry wiring (G-001 / AF-001)

Recorded here so the deferral is durable and auditable; full stub at
[`adr-deferred-foundry-wiring.md`](./adr-deferred-foundry-wiring.md).

| Field | Value |
|---|---|
| Decision deferred | The ADR pinning **live Foundry Agents wiring details** for the Candidate Evaluation Council |
| Deferral authority | Product Owner decision, 2026-06-11, recorded in slice spec §2.2.2 (BQ-001) and §2.2.3 (BQ-005) |
| Scope the ADR must pin | (1) **Foundry Agent Service vs Agent Framework workflow** (companion §5 decision table; §11 item 1); (2) **backend-type enumeration** — the final set of supported `ai_backend_type` values; (3) **live trace/eval metadata contract** — exact field schema (trace id, evaluation-run id, agent/workflow id, workflow version, model deployment, token/latency metrics, validated-output confirmation) and where each field lives (safe telemetry vs evidence rows; companion §8 and §11 item 2); (4) **region/residency** — approved Canadian region and approved model deployments (BQ-005; companion §9: never adopt a region silently) |
| What is NOT blocked by the deferral | Local deterministic implementation: the mock provider, the Foundry seam stub, and everything else in this slice's plan (PO §2.2.2: "local deterministic implementation is not blocked on it") |
| What IS blocked until human ADR approval | Any live Foundry/Azure wiring, resource creation, model/agent calls, token spend, live evals LE-001…LE-007, region adoption, Entra integration |
| Interim seam-contract authority (in-slice) | Foundry companion §8 required trace/eval metadata + this slice's provider schemas (`domain/schemas/provider.py`), versioned via `role_schema_version` (PO §2.2.2) |
| Reconciliation duty | The wiring slice reconciles the seam contract built here against the approved ADR; schema versioning makes drift visible (plan §8.2) |
| Approval gate | **Human approval required before the live-wiring slice begins. The stub is not approved and must not be marked approved by any agent.** |

---

## 7. Actual-Architecture Drift Flags

No actual-architecture drift identified — no actual architecture document or prior implementation exists (greenfield, `main` @ `44dd219`). The actual-architecture input is vacuously satisfied; this slice will create the first current-state docs at Stage 12.

---

## 8. Recommended Guideline Update Notes / Conditions

Recommendations, not approvals. The two conditions are verifiable by already-planned tests and do not block coding start.

| ID | Area | Note | Suggested Next Step |
|---|---|---|---|
| **C-COND-1** | HTTP status mapping (A-001 / AF-004) | Align plan §3.4's provisional table with API-contracts §4 (`blocked`/`validation_failed` → 200 envelope; 401 unauthenticated vs 403 authenticated denial; do not use 409 — reserved for concurrency `error`), or escalate a recorded deviation for human decision | Resolve **before build step 11** (`api/errors.py`); DT-014 locks it at step 13 |
| **C-COND-2** | Provider metadata placeholders (§3.15) | Add a typed, nullable **evaluation-run identifier** placeholder (e.g. `eval_run_id: null` under the mock) so the seam covers the full companion §8 set ("trace ID **and eval ID**"); confirm the orchestration/workflow-version value (plan §6.3) lands in the provider metadata block | Add at **build step 3** (domain schemas); DT-013 asserts presence + typing; final live schema pinned by the deferred ADR |
| — | Persistence row parity | Consider carrying `actor_id`, `resolved_role`, `correlation_id` as properties on `EvaluationEvidence` rows for closer parity with storage doc §4.4 important-properties (actor identity is already guaranteed in the full record per UFM-012; these are safe metadata, not content) | Optional at build step 5; record either way in current-state docs |
| — | Stack + naming notes for current-state docs | Record at Stage 12: Python/FastAPI lab-facade stack decision (plan §3.1); local table naming `EvaluationEvidence` ≙ `EvidenceMetadata`; gate-failure → `blocked` mapping (AF-003) with its API-contracts §5.6 precedent; `auto_escalate` inclusion (AF-005) | Stage 12 documentation; no ADR |

---

## 9. AF-Flag Dispositions (plan §7)

Per the Stage 6 decision rule: (a) no ADR needed / (b) ADR needed for live wiring only → DEFERRED per PO §2.2.2 / (c) ADR needed BEFORE local deterministic implementation → stop condition.

| Flag | Disposition | Detail |
|---|---|---|
| AF-001 | **(b) — ADR for live wiring only → DEFERRED** | Recorded as G-001 (§6); deferred-ADR stub created (`adr-deferred-foundry-wiring.md`, Status: Deferred — Draft). Seam-vs-companion-§8 verification done (C-002): match confirmed, one placeholder addition required (C-COND-2). Conditionally blocking — blocks the wiring slice only; no in-slice component is blocked. |
| AF-002 | **(a) — no ADR** | §3.11 shapes verified as a faithful local mirror of the storage doc (C-004), including the metadata-first row schema. No deviation → no ADR per spec §16 gap 3 default. Record in current-state docs. |
| AF-003 | **(a) — no ADR** | Gate-failure → `blocked` confirmed **within** the adopted contract style: API-contracts §3.2 `blocked` semantics + the explicit §5.6 precedent (`generation_quality_gate_failed` → `blocked` after one bounded retry). Not a new pattern. Design note for current-state docs. |
| AF-004 | **(a) — no ADR**, with condition C-COND-1 | The documented HTTP mapping already exists (API-contracts §4) — no new architecture decision is required, only alignment of the plan's provisional codes before build step 11/13. Becomes a human-gated deviation only if the team chooses not to adopt the documented mapping. |
| AF-005 | **(a) — no ADR** | `auto_escalate` inclusion was pre-authorized by the PO (spec §2.1.3, "cheap and clean behind server-side config"); config-gated, defaults off, provenance recorded. Visibility note only; current-state docs record it (BQ-EC-002). |
| AF-006 | **(a) this slice — deferred follow-up** | In-slice bounded repo-file config needs no ADR (spec §16 gap 2). The admin-surface/config-audit ADR belongs to the follow-up slice; trigger `adr-gap-detector` when that slice is planned. Not part of the G-001 wiring ADR. |

No AF flag falls into category (c). **No stop condition exists.**

---

## 10. Compliance Verdict

### Verdict

**CLEAR-for-local-implementation.**

Skill-vocabulary mapping (skill §9 requires one of four): the strict in-stage sequence was
**"ADR check required" → `adr-gap-detector` executed → gap G-001 confirmed and dispositioned as
Deferred by explicit PO decision (spec §2.2.2) with severity *conditionally blocking* — affecting
only live-wiring components, none of which exist in this slice's plan.** With the deferral durably
recorded (§6.2 + the ADR stub), no violation, no blocking ambiguity, and no unresolved not-covered
area applies to any component this slice will build. Coding of the local deterministic
implementation (mock provider + Foundry seam) may begin.

### Verdict Rationale

- All seven spec §15 constraints: **Compliant** (C-001…C-007), verified against the canonical
  source docs, with two non-blocking, test-enforced conditions (C-COND-1 at build step 11/13;
  C-COND-2 at build step 3).
- No violations (§4). One ambiguity (A-001) whose resolution is already prescribed by the adopted
  API-contracts doc and binds a later build step, not coding start.
- One not-covered area (G-001), which is exactly the gap the Product Owner explicitly deferred on
  2026-06-11; it blocks the live-wiring slice, not this one. It is not silently passed — it is
  recorded with scope, interim authority, and a human approval gate.
- **Single exact decision needed: none.** No human decision is required to start local
  deterministic implementation. (The next human decisions on file are future-dated: approval of the
  deferred Foundry-wiring ADR before the wiring slice, and the standing merge-time gates — AC-019
  PO review, DT-012 flagged-output review, latency-ceiling ratification BQ-EC-001.)

---

## 11. Recommended Next Step

| Verdict | Next Step |
|---|---|
| CLEAR-for-local-implementation | **Stage 7 — Implementation & config capture**, following the plan §4.8 build order |

### Handoff Notes

For the Stage 7 coding agent:

1. Apply **C-COND-2** at build step 3 (add the nullable `eval_run_id` placeholder to the provider
   metadata schema; ensure orchestration/workflow version is in the metadata block) — DT-013
   asserts it.
2. Apply **C-COND-1** before build step 11: adopt the API-contracts §4 HTTP mapping
   (`blocked`/`validation_failed` → 200; 401/403 split; no 409) unless a human approves a recorded
   deviation first — DT-014 locks the result at step 13.
3. The Foundry stub must remain SDK-free and raise on use; nothing in this slice may perform live
   cloud activity (eval contract §9 blocking-fail row).
4. The deferred ADR stub (`adr-deferred-foundry-wiring.md`) is **not approved**; do not wire, do
   not mark approved, do not expand its scope. It gates the future wiring slice via human approval.
5. This report approves no deviation and updates no guideline; human gates (merge, residual risk,
   issue creation) remain in force per AGENTS.md.
