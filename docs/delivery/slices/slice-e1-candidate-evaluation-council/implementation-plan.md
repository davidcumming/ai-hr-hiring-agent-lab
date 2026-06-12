# Implementation Plan: Single-Candidate Calibrated Evaluation Council

## 1. Plan Metadata

| Field | Value |
|---|---|
| Slice ID | `slice-e1-candidate-evaluation-council` |
| Slice Name | Single-Candidate Calibrated Evaluation Council (advisory, evidence-grounded, mock-backed with Foundry seam) |
| Plan Date | 2026-06-11 |
| Plan Author | coding-agent (Claude), `implementation-plan-builder` skill, Stage 5 |
| Linked Slice Spec | [`slice-spec.md`](./slice-spec.md) (REVISED — readiness passed 2026-06-11; PO decision records §2.1/§2.2) |
| Linked Eval Contract | [`eval-contract.md`](./eval-contract.md) (`EC-slice-e1-candidate-evaluation-council-001`, hardened, Ready for Implementation Planning) |
| Linked Risk Profile | [`eval-risk-profile.md`](./eval-risk-profile.md) (High-Assurance, binding) |
| Status | **Ready for Architecture Check** (Stage 6) |
| Template deviation note | This plan uses the `implementation-plan-builder` template skeleton with one addition: a "Design Specification" section (§3) inserted before the File and Change Plan, because the repo is greenfield and the plan must define module responsibilities, not just changed files. Subsequent template sections are renumbered (+1). Recorded here per skill §8/§9. |

### 1.1 Input confirmation (skill §7 step 1)

- Slice spec: approved revision (readiness review passed 2026-06-11, delta re-review §15) — confirmed, not a draft.
- Eval contract: hardened at Stage 4 (DT-001…DT-018, LE-001…LE-007 deferred with rationale, UFM-001…013) — confirmed.
- No blocker exists for implementation planning (eval contract §16: BQ-EC-001…005 all non-blocking).

### 1.2 Decisions recorded in this plan (required at Stage 5)

| Decision | Outcome | Where specified |
|---|---|---|
| Stack | **Python 3.12 (≥3.11), FastAPI + uvicorn, pydantic v2, pytest + httpx** | §3.1 |
| OQ-002 / BQ-EC-002 (`auto_escalate`) | **INCLUDE — implement `auto_escalate` execution behind server-side config** (default remains `record_only`). Rationale in §3.9: the Mode C extension executor must exist anyway for BR-003 explicit-escalated mode, and triggers are computed on every run anyway (FR-011), so auto-escalate is one conditional branch plus a provenance enum — "cheap and clean" per PO §2.1.3. DT-004(c) asserts the implemented branch: escalated path executes with `policy_triggered` provenance. | §3.9 |
| Endpoint names / envelope subset (OQ-005/BQ-EC-004) | `POST /api/evaluations`, `GET /api/evaluations/{evaluation_id}` as proposed by the source functional spec; envelope field subset in §3.4, finalized when the OpenAPI document is written (DT-014 asserts whatever is declared) | §3.4, §3.13 |

---

## 2. Slice Intent Summary

> Copied verbatim from slice spec §3 (Business Outcome):

A signed-in HR-role user submits or selects one synthetic candidate's resume and cover letter for one sample position with one pre-approved, versioned rubric, and receives an advisory, evidence-grounded evaluation from the Calibrated Evaluation Council in a single response envelope. The full audit/evidence record — including every intermediate council output, rigor resolution, escalation triggers, and quality-gate results — is persisted and retrievable by `evaluation_id`. The council runs locally against a deterministic mock backend behind the same provider seam intended for Foundry Agents, so useful coding progress happens now without live Azure/Foundry wiring, and the output is always decision support for a human, never a hiring decision.

---

## 3. Design Specification

This section defines repo layout, module responsibilities, and runtime behaviour at the intent level. It contains no code. Where a detail is provisional, it says so and names the gate that confirms it.

### 3.1 Stack decision

**Python 3.12 (compatible ≥3.11), FastAPI + uvicorn, pydantic v2, pytest + httpx, openapi-spec-validator.** Rationale:

- The read-only source repo's implementation conventions are Python/`pyproject.toml`; staying aligned eases the future Foundry-wiring slice (Azure Functions Python / Agent Framework are Python-first).
- FastAPI + pydantic v2 gives a **single schema source** for role-output contracts, the response envelope, and the OpenAPI document — directly servicing DT-013 (mock parity, "no mock-only schema fork") and DT-014 (contract-vs-implementation conformance).
- `tomllib` (stdlib) reads the server-side config file; no YAML dependency needed.
- Zero cloud SDKs anywhere in the dependency set (hard boundary; eval contract §9 blocking-fail row).

Runtime dependencies: `fastapi`, `uvicorn`, `pydantic` (v2). Dev/test dependencies: `pytest`, `httpx`, `openapi-spec-validator`. Nothing else without a deviation note.

### 3.2 Repo layout

```text
pyproject.toml                       # project metadata, deps, pytest config
.gitignore                           # excludes var/ (local persistence root)
config/
  lab-config.toml                    # server-side rigor/escalation/backend config (source-controlled)
openapi/
  evaluations-api.json               # committed OpenAPI document (FR-010, DT-014)
fixtures/
  manifest.json                      # id, version, sha256, SYNTHETIC label, provenance per artifact
  positions/pos-sample-001/
    job-description.md               # vendored from source repo (byte-identical)
    rubric.v1.json                   # rub-sample-001 v1, vendored byte-identical; hash lives in manifest
  candidates/cand-sample-001/
    resume.md                        # Jordan Rivera (synthetic)
    cover-letter.md
src/hr_eval_lab/
  __init__.py
  config.py                          # load + validate lab-config.toml; typed config object
  logging_setup.py                   # central logger config; never-log redaction filter
  api/
    app.py                           # FastAPI app factory; wiring; exception handlers
    auth.py                          # simulated lab identity (header stub); role check
    envelope.py                      # standard response envelope models + status enum
    errors.py                        # status mapping: 400 / validation_failed / unauthorized / blocked
    routes_evaluations.py            # POST /api/evaluations, GET /api/evaluations/{evaluation_id}
  domain/
    ids.py                           # evaluation_id generation; canonical timestamp source
    schemas/
      request.py                     # EvaluationRequest (candidate_ref | inline text, idempotency_key, evaluation_question, advisory rigor field)
      evaluation.py                  # advisory evaluation result: criterion scores, evidence, disagreements, fairness block, confidence, limitations, label enum, mandatory flags
      council.py                     # per-role output schemas (all 11 roles + Mode C extension roles)
      provider.py                    # provider-contract envelope: role I/O + trace/eval metadata (Foundry companion §8 shape, placeholders typed)
      audit.py                       # full audit record (blob-equivalent) + metadata row shapes (table-equivalent)
  sources/
    fixture_store.py                 # fixture resolution, version pinning, sha256 verification (mismatch -> blocked)
  evidence/
    packet_builder.py                # controlled evidence packet (code-built, pre-reasoning)
  rigor/
    resolver.py                      # effective_rigor pure function (server config wins; downgrade recorded)
    triggers.py                      # the 6 escalation-trigger computations (pure functions, every run)
  council/
    composition.py                   # Mode A/B/C role sets; code-role vs model-backed-role registry
    code_roles.py                    # Request Normalizer, Source Ingestion/Versioning, Deterministic Rules Validator
    orchestrator.py                  # pipeline: sequence, provider calls, bounded retry, escalation branch, gate hand-off
  escalation/
    policy.py                        # escalation_policy enum (record_only | auto_escalate); provenance enum; decision logic
  gates/
    quality_gates.py                 # the 6 deterministic gates + per-gate fail behaviour + retry accounting
  providers/
    base.py                          # CouncilProvider protocol: invoke_role(role, packet, context) -> ProviderResult
    mock.py                          # deterministic mock (default; ai_backend_type=none; scenario-scriptable in tests)
    foundry_stub.py                  # lazy seam stub; raises ProviderNotConfiguredError on any use
  persistence/
    store.py                         # blob-equivalent full record + table-equivalent metadata rows (append-only, canonical JSON)
    idempotency.py                   # IdempotencyRecords-equivalent: key -> evaluation_id + request fingerprint
  review_queue.py                    # human-review queue entries (Persistence/Review Queue role, code)
  cli.py                             # thin HTTP-only client (httpx + argparse only; no app imports)
scripts/
  vendor_fixtures.py                 # one-time/dev script: copy fixtures from source repo, compute sha256, write manifest
  export_openapi.py                  # regenerate openapi/evaluations-api.json from the app factory
tests/
  conftest.py                        # app/client fixtures, provider counter, log capture, temp persistence root
  sentinels.py                       # never-log sentinel substrings derived from fixture bodies
  fixtures/                          # test-only variants: injection resume, tampered-manifest dir, missing-evidence variant, trigger scripts
  unit/
    test_rigor_resolver.py           # DT-003
    test_escalation_triggers.py      # DT-005
    test_quality_gates.py            # DT-006
    test_fixture_store.py            # hash verification unit coverage (supports DT-007)
  integration/
    test_happy_path.py               # DT-001
    test_determinism.py              # DT-002
    test_escalation_matrix.py        # DT-004
    test_status_vocabulary.py        # DT-007
    test_idempotency.py              # DT-008
    test_authorization.py            # DT-009
    test_mandatory_flags_invariant.py# DT-010
    test_never_log_scrub.py          # DT-011
    test_injection_resistance.py     # DT-012
    test_missing_evidence.py         # DT-015
    test_sequencing.py               # DT-016
    test_role_discipline.py          # DT-017
    test_cli_runner.py               # DT-018
  contract/
    test_mock_parity.py              # DT-013
    test_openapi_conformance.py      # DT-014
.github/workflows/
  ci.yml                             # deterministic suite on PR (FR-014)
docs/delivery/slices/slice-e1-candidate-evaluation-council/
  evals/live/                        # pre-drafted LE-001..LE-007 scenario stubs carried forward (no runner; see §6)
var/                                 # local persistence root (gitignored; created at runtime)
```

### 3.3 Configuration (`config/lab-config.toml`)

Source-controlled server-side config, read once at app start (`config.py`), validated against a typed model. Keys:

| Key | Type / enum | Default | Governs |
|---|---|---|---|
| `rigor.default_mode` | `standard \| high_impact \| escalated` | `high_impact` | BR-001/BR-003; the server-resolved rigor input |
| `escalation.policy` | `record_only \| auto_escalate` | `record_only` | BR-004/BR-005/BR-006 |
| `provider.ai_backend_type` | `none \| foundry_agents` | `none` | provider selection; `foundry_agents` is the seam stub only |
| `persistence.root` | path | `var/lab-data` | local store location (overridable in tests via env for temp dirs) |

Git history is the change record (spec §17). No secrets exist in this file or anywhere in the repo. Tests exercise non-default states by constructing the app with an explicit config object (not by editing the committed file).

### 3.4 Facade API, envelope, and status vocabulary

**Endpoints** (`api/routes_evaluations.py`):

- `POST /api/evaluations` — body: `position_id`, `candidate_ref` **or** inline `resume_text` + `cover_letter_text`, required `idempotency_key`, optional `evaluation_question`, optional advisory `requested_rigor` (never authoritative — BR-002).
- `GET /api/evaluations/{evaluation_id}` — returns the full audit record wrapped in the envelope.

**Order of operations on every request (DT-009, DT-016 depend on this exact order):**
1. Authentication + role authorization (`auth.py`) — failure short-circuits before any validation, fixture access, or persistence side effect.
2. Malformed-body rejection (HTTP 400 via a custom request-validation handler — no envelope status consumed).
3. Semantic validation (unknown `position_id`/`candidate_ref` → `validation_failed`).
4. Idempotency check (replay → return stored result; zero council execution).
5. Source resolution + sha256 verification (mismatch → `blocked`, zero council execution).
6. Evidence packet build → council orchestration → gates → persistence → envelope.

**Simulated lab identity (auth stub).** Header-based, consistent with the identity-design trusted-boundary rule (facade validates identity/authorization before anything else; simulated identities are a lab stand-in, never an Entra substitute — documented in the module docstring and current-state docs):

- `X-Lab-Actor-Id` (string, required), `X-Lab-Actor-Display` (optional), `X-Lab-Roles` (comma-separated role names from the lab role vocabulary: `hr`, `hiring_manager`, `reviewer`, `auditor`, `admin_lab`, `admin_prod`, `support`).
- Authorization rule (PO §2.2.1, case-less): global role group only — `hr` required for both `POST` and `GET`. All other roles (including `admin_lab`) and unauthenticated callers → `unauthorized` on both verbs.
- The authenticated actor identity + role context is attached to the request context and **persisted in every audit record** (UFM-012).

**Envelope** (`api/envelope.py`) — adopted contract style (API-contracts doc), field subset for this slice (finalized at OpenAPI authoring, BQ-EC-004): `status`, `evaluation_id`, `case_id` (always `null` this slice — case-less rule), `correlation_id`, `user_message`, `safe_details`, `result` (the advisory evaluation, POST/GET success only), `errors`, `warnings`. `safe_details`/`user_message` obey never-log discipline (no document text).

**Status vocabulary emitted this slice** (fixed enum; remainder of the adopted vocabulary — `needs_input`, `error` — declared reserved in the OpenAPI doc, never emitted here):

| Condition | Envelope status | HTTP (provisional — confirmed against API-contracts doc when OpenAPI is written) |
|---|---|---|
| Success | `completed` | 200 |
| Unknown position/candidate; idempotency-key reuse with different payload | `validation_failed` | 422 |
| Malformed body | *(no envelope status — HTTP-level rejection)* | 400 |
| Missing/insufficient role; unauthenticated | `unauthorized` | 403 |
| Source/rubric hash mismatch; quality-gate failure (see §3.10) | `blocked` | 409 |

### 3.5 Fixture vendoring with sha256 verification

`scripts/vendor_fixtures.py` (run once during implementation; output committed):

- Copies the four fixture files **byte-identical** from the read-only source repo (`fixtures/sample-position/job-description.md`, `fixtures/sample-position/rubric.v1.json`, `fixtures/candidates/jordan-rivera/{resume.md,cover-letter.md}`) into `fixtures/` as laid out in §3.2. The source repo is never edited; only content is extracted (vendoring fixtures is permitted and intended — they are requirements, not implementation).
- Writes `fixtures/manifest.json`: for each artifact — `artifact_id` (`pos-sample-001`, `rub-sample-001`, `cand-sample-001:resume`, `cand-sample-001:cover_letter`), `version` (`v1` for the rubric; `v1` assigned at vendoring for unversioned docs), `path`, `sha256` (computed over file bytes), `synthetic: true` label, and `provenance` (source-repo relative path + vendoring date). The manifest is the hash authority — the rubric file itself stays byte-identical to the source (the source fixture carries no hash field; inventory doc #12).
- `sources/fixture_store.py` verifies the sha256 of every resolved file against the manifest on each evaluation (cheap at this scale; guarantees BR-009 per-run). Any mismatch → status `blocked`, **zero council execution**, mismatch detail (artifact id + expected/actual hash — no content) recorded. DT-007's tampered-hash case runs against a test-only fixture directory whose manifest hash deliberately mismatches.

### 3.6 Evidence packet builder (before any evaluative reasoning)

`evidence/packet_builder.py`, invoked by the code role *Source Ingestion/Versioning* after validation and before any provider call (FR-005, DT-016):

- Inputs: resolved, hash-verified sources (resume, cover letter, job description, rubric) + the normalized request.
- Output: the **controlled evidence packet** — source references (`artifact_id`, `version`, `sha256`), the rubric (criteria C1–C6 with anchors, disqualifier D1, prohibited-factors note), and source content segmented into stably addressed segments (e.g., `resume:s04`) so citations are mechanically resolvable.
- Packet completion is written to the audit record with a **sequence index** before the first provider invocation; every later citation must resolve to a packet segment or evidence-item id (gate 3/6 in §3.10; DT-001/DT-017 citation-resolvability).
- The Evidence Extraction *agent* (model-backed, neutral per AB-002) then produces structured evidence items appended to the packet; judgment roles consume packet + evidence items only.

### 3.7 Council orchestration — 11 roles, code vs model-backed, Mode A/B/C

`council/composition.py` declares the role registry. **Code roles** (deterministic, facade-owned — no provider call, no token cost): 1 Request Normalizer, 2 Source Ingestion/Versioning, 4 Deterministic Rules Validator, 10 Quality Gate Evaluators (§3.10), 11 Persistence/Review Queue (§3.11). **Model-backed roles** (through the provider seam only): 3 Evidence Extraction, 5 Merit Advocate, 6 Risk/Gaps Advocate, 7 Neutral Scoring Judge, 8 Policy/Fairness Auditor, 9 Synthesis Judge; **Mode C extension roles**: Second Synthesis Judge, Rubric Calibration Judge.

Composition per effective rigor (council spec §10/§13; cost rows match eval contract §13):

| Mode | Effective rigor | Model-backed roles invoked | Approx. provider calls |
|---|---|---|---|
| A | `standard` | Evidence Extraction, Merit Advocate, Risk/Gaps Advocate, Synthesis Judge | ~4 |
| B | `high_impact` (default) | Mode A + Neutral Scoring Judge + Policy/Fairness Auditor | ~6 (7 with one retry) |
| C | `escalated` | Mode B + Second Synthesis Judge + Rubric Calibration Judge; human review mandatory | ~8 (9 with retry) |

`council/orchestrator.py` pipeline (single synchronous pass; sequence indices recorded for DT-016):

1. Code roles 1–2 (normalize; ingest/version/build packet).
2. Evidence Extraction (first provider call — only after packet completion).
3. Code role 4 (Deterministic Rules Validator — runs **before** judgment roles; deterministic checks: required-document presence, disqualifier D1 evidence presence/absence noted as missing evidence never disqualification, instruction-like-content scan that sets the anomalous-content flag for BR-012).
4. Judgment roles for the mode (advocates, then scoring/fairness where in mode, then Synthesis Judge).
5. Trigger computation (§3.8) — always, from the base-mode outputs.
6. Escalation decision (§3.9) — may invoke the Mode C extension roles.
7. Quality gates (§3.10).
8. Persistence + review queue (§3.11), envelope assembly.

Every model-backed invocation goes through `providers/base.py::CouncilProvider` and is recorded with: role name, role-schema version, provider metadata (`ai_backend_type`, trace/eval placeholders), retry count (0 or 1), and an invocation counter persisted in the record (DT-008/DT-004 assert on it). Each role's output is validated against its declared schema immediately (one bounded corrective retry on schema failure — §3.10 gate 1; AB-008).

### 3.8 Rigor resolver and the six escalation triggers

`rigor/resolver.py` — pure function (DT-003): inputs are server config (`rigor.default_mode`), the request's risk classification (hiring → `high_impact` per BR-001, computed by Request Normalizer), and the request's advisory `requested_rigor`. Rules: server config wins, always; hiring classification floors at `high_impact` unless server config explicitly sets otherwise; the request body can **never** lower the result — any downgrade attempt is ignored and recorded in the audit record's rigor-resolution block with the requested value (BR-002, UFM-002). Output: `effective_rigor` + human-readable resolution explanation + downgrade-attempt entry when applicable.

`rigor/triggers.py` — six pure functions computed and recorded on **every** run regardless of policy (FR-011, DT-005), each returning `{trigger_id, fired, computed_value, threshold}`:

1. `score_variance_above_threshold` — variance across role-proposed criterion scores.
2. `evidence_packet_missing_required_criteria` — required criterion (C1–C4) lacking evidence items.
3. `synthesis_confidence_low` — Synthesis Judge confidence below threshold.
4. `policy_fairness_severity_high` — Policy/Fairness Auditor severity at/above threshold.
5. `recommendation_near_decision_threshold` — synthesized score proximity to the label boundary.
6. `criterion_scored_with_no_direct_evidence` — any scored criterion with zero direct evidence citations.

Thresholds are constants in `triggers.py` (source-controlled; documented in current-state docs). For `standard`-mode runs the not-in-mode role inputs are recorded as `not_computed_inputs` with the trigger still evaluated over available outputs — explicitly noted in the record (no silent omission).

### 3.9 Escalation policy — OQ-002 decided: include `auto_escalate`

`escalation/policy.py`. Enum `record_only | auto_escalate` (default `record_only`), source-controlled, read at runtime (BR-006). Decision logic after trigger computation, with a recorded `escalation_provenance` enum on every record (`none | configured_escalated | policy_triggered`):

| State | Behaviour |
|---|---|
| `effective_rigor = escalated` (server config) | Mode C extension roles execute unconditionally; `configured_escalated`; human review mandatory (BR-003) |
| `high_impact` + ≥1 trigger fired + `record_only` | Triggers, rationale, human-review flags persisted; **zero** Mode C roles execute (BR-004) |
| `high_impact` + ≥1 trigger fired + `auto_escalate` | Mode C extension roles execute; `policy_triggered` provenance recorded (BR-005, implemented branch) |
| `high_impact` + no trigger fired (either policy) | No escalation; provenance `none` |

**OQ-002 rationale (recorded per BQ-EC-002):** the orchestrator must already (a) compute all six triggers every run (FR-011) and (b) own a Mode C extension executor for explicit escalated mode (BR-003). `auto_escalate` execution is therefore one conditional branch reusing the same executor, plus the provenance field DT-004(c) asserts. That meets the PO's "cheap and clean behind server-side config" bar (§2.1.3), avoids the configured-but-not-active half-state, and gives AC-008's stronger branch. The record states the policy applied and provenance on every run; silence in either direction is structurally impossible (UFM-008).

The trigger block persisted is the pre-extension computation (computed once from base-mode outputs); post-extension synthesis output is recorded separately with its own sequence indices so reviewers can see exactly what fired escalation and what the escalated roles added.

### 3.10 Quality gates (6) — per-gate fail behaviour + bounded retry

`gates/quality_gates.py`. All gates are deterministic code (FR-008); each produces `{gate_id, result: pass|fail, reason, details_safe}` recorded on every run (DT-006). Any gate failure → envelope status `blocked`, the full record (including gate results and all role outputs) is still persisted for audit, and a human-review queue entry is written. *(Gate-failure→`blocked` is a design decision within the adopted vocabulary — recorded for current-state docs; see §7 flag AF-003.)*

| # | Gate | Pass condition | Fail behaviour |
|---|---|---|---|
| 1 | Schema validity | Every role output validates against its declared schema; on first failure the orchestrator issues **exactly one** corrective retry to that role (AB-008), re-validates, records `retry_count ≤ 1` | After retry: gate `fail`, run → `blocked`; no coercion, no further retries |
| 2 | All-criteria-scored | All 6 rubric criteria carry an integer score 1–5 in the synthesis | `fail` → `blocked` |
| 3 | Evidence-per-score | Every score cites ≥1 supporting evidence reference that mechanically resolves to a packet segment/evidence-item id | `fail` → `blocked` (UFM-003 floor) |
| 4 | No-prohibited-factors | Deterministic scan: no prohibited factor/proxy term set (name, age, gender, race, nationality, disability, family status, school/address prestige, employment gaps, photographs) appears as a scoring rationale field; auditor-detected violations are present in the fairness block, never dropped | `fail` → `blocked` (UFM-001 floor) |
| 5 | Human-review-flag present | `human_review_required: true` and `decision_support_only: true` present and true on the assembled record | `fail` → `blocked` (UFM-005; structurally near-impossible per §3.12, gate is belt-and-braces) |
| 6 | Groundedness heuristic | Quoted evidence spans appear verbatim in the referenced source segment; missing-evidence notes present for any criterion with no direct evidence | `fail` → `blocked` (UFM-003/009 floor) |

### 3.11 Local persistence / audit store (storage-doc shapes)

`persistence/store.py`, root `var/lab-data/` (gitignored). Mirrors the storage-doc shapes so Azure wiring is config, not restructuring (spec §15):

- **Blob-equivalent:** `var/lab-data/evaluations/{evaluation_id}.json` — the full audit record: request (incl. advisory rigor field as received), **actor identity + role context**, source refs + hashes + versions, evidence packet, every council role's output with sequence index + provider metadata + retry count, synthesis, gate results, rigor resolution + downgrade attempts, trigger block, escalation policy + provenance, human-review block, timestamps. Serialized as **canonical JSON** (sorted keys, fixed separators, UTF-8) so DT-002 byte-identity holds.
- **Table-equivalent:** `var/lab-data/tables/EvaluationEvidence.jsonl` — one metadata-first row per evidence event/role output: `PartitionKey` (= `evaluation_id`), `RowKey` (sequence index), artifact/segment references, hashes, role name, schema version, sizes, flags. **No document text, prompt text, or model I/O fields exist in the row schema** (BR-010 enforced by shape, then verified by DT-011). `var/lab-data/tables/IdempotencyRecords.jsonl` — `idempotency_key` → `evaluation_id` + request fingerprint (hash, not content).
- Append-only writers; `GET` reads the blob-equivalent record and returns it in the envelope (AC-002 reconstruction).
- `review_queue.py` writes human-review queue entries (`var/lab-data/tables/ReviewQueue.jsonl`): every evaluation (review always required), with `mandatory_reason` enriched for escalated runs, gate failures, and anomalous-content flags.

**Idempotency semantics (`persistence/idempotency.py`):** replay with same key + same fingerprint → stored envelope returned, provider invocation counter unchanged, no new record (DT-008). Same key + different fingerprint → `validation_failed` with safe detail (no content).

### 3.12 Safe response contract (advisory-only invariants)

`domain/schemas/evaluation.py` enforces BR-007 structurally:

- `decision_support_only` and `human_review_required` are typed as **literal `True`** in the pydantic model — a record without them, or with `false`, cannot be constructed or serialized; there is no code path that emits an evaluation outside this model (DT-010's serializer-level assertion target).
- `recommendation_label` is a closed enum: `advance_to_interview | do_not_advance | hold_for_review | insufficient_evidence`. No field for hire/reject decision, cross-candidate rank, or candidate contact exists in any schema (UFM-006 — schema forbids, DT-001/DT-013 assert).
- The fairness block, contrary-evidence fields, missing-evidence notes, disagreement block, confidence, and limitations are required fields (present even when empty), per the behavioural contract §5.

### 3.13 OpenAPI document

`openapi/evaluations-api.json`, generated from the app factory by `scripts/export_openapi.py` and **committed**. Declares the two routes, the envelope (incl. the full adopted status vocabulary with reserved-status notes), the auth headers, and the advisory enum. DT-014 (a) validates the committed document (`openapi-spec-validator`) and (b) regenerates from the live app and asserts equality with the committed file — automated drift detection (RF-005), not eyeballing. Endpoint naming and envelope field subset are finalized here (BQ-EC-004).

### 3.14 Thin CLI runner

`src/hr_eval_lab/cli.py`: argparse + httpx **only** — it never imports application modules, storage, or fixtures (DT-018 asserts the import graph). Commands: `submit` (reads actor/role header values and request params from flags; posts to a `--base-url`), `get <evaluation_id>`. Output: the envelope JSON to stdout (subject to the same never-log expectation — it prints the API response only, which is the controlled channel, not telemetry). DT-018 runs it against a uvicorn instance on a local port and captures the session transcript as evidence.

### 3.15 Deterministic mock provider + Foundry seam stub

`providers/base.py` defines the seam: `CouncilProvider.invoke_role(role_id, packet_view, role_context) -> ProviderResult`, where `ProviderResult` = role-output payload + **provider metadata block** per the Foundry companion §8 trace/eval contract: `ai_backend_type`, `trace_id`, `agent_run_id`, `model_deployment`, `prompt_version`, `token_usage {prompt, completion}`, `latency_ms`. One schema source (`domain/schemas/provider.py`) serves both providers (DT-013 "no mock-only schema fork").

**Mock (`providers/mock.py`, default, `ai_backend_type = "none"`):**
- Fully deterministic and content-derived: outputs are computed from the evidence packet via stable rules (criterion-keyword matching against rubric anchors) plus a sha256-derived seed of the canonical packet serialization for any tie-breaking — identical inputs ⇒ identical outputs (DT-002). Integer/string arithmetic only (no floats in output values) to keep serialization stable.
- Emits schema-valid output for all 8 model-backed role types, citing **real packet segment/evidence-item ids** (so citation resolution genuinely exercises gates 3/6).
- Trace metadata placeholders populated and typed: `ai_backend_type: "none"`, `trace_id: "local-<deterministic>"`, `agent_run_id: placeholder`, `model_deployment: null`, `token_usage: {0,0}` (mock parity incl. metadata, DT-013).
- **Scenario scripting (test-only):** the constructor accepts an optional script table (role → output override/patch) so DT-005/DT-006/DT-015 can provoke each trigger and each gate failure individually. The default app path constructs the provider unscripted; scripts are injectable only through test composition, never via the API or config file.

**Foundry seam stub (`providers/foundry_stub.py`):**
- Selected only when config sets `ai_backend_type = "foundry_agents"`; the default path never instantiates it (lazy — provider selection resolves the class only on first use).
- Contains no Azure SDK imports and no network code. Any `invoke_role` call raises `ProviderNotConfiguredError("Foundry Agents backend is not configured in this slice; live wiring is deferred (PO §2.2.2)")`.
- Exists to pin the seam contract shape against the agent-backed target (spec §15: wiring later must be config, not restructuring). Real wiring details belong to the deferred ADR (OQ-001/BQ-001).

### 3.16 Logging and never-log enforcement

`logging_setup.py`: single logging configuration; log records carry only ids, hashes, statuses, role names, durations, and counters. A redaction filter rejects/flags any record whose message contains a registered sentinel (defense-in-depth; the primary control is that no call site passes content). HTTP access logs configured to omit bodies. DT-011 captures all log output (caplog + captured stdout/stderr) across full integration runs and asserts zero occurrences of fixture-derived sentinel substrings (maintained in `tests/sentinels.py`, derived from the vendored fixture bodies so they stay in sync).

### 3.17 Explicit no-live-cloud statement

This slice performs **no live cloud activity of any kind**: no Azure resource creation or configuration, no Foundry/model endpoint calls, no token spend (any live call = blocking fail, eval contract §9/§13), no Entra integration, no secrets (none exist in the repo; nothing requires one), no real applicant data, no deployment. All execution is local: FastAPI on uvicorn, filesystem persistence under `var/`, deterministic mock provider. The only network activity in the entire slice is localhost HTTP between the CLI/tests and the local facade, and GitHub Actions checking out the repo and running pytest. The Foundry provider is a non-functional seam stub that raises on use.

---

## 4. File and Change Plan

Greenfield: every entry is `New`. Paths are repo-relative; full layout in §3.2.

### 4.1 Application logic / agent orchestration

| File / Component | Change Type | Rationale |
|---|---|---|
| `src/hr_eval_lab/config.py`, `config/lab-config.toml` | New | Server-side source-controlled rigor/escalation/backend config (BR-006, spec §17) |
| `src/hr_eval_lab/logging_setup.py` | New | Never-log discipline (BR-010, DT-011) |
| `src/hr_eval_lab/domain/ids.py`, `domain/schemas/*` (5 modules) | New | Single schema source: request, evaluation result, 11+2 role outputs, provider contract, audit record (FR-007/012, DT-013) |
| `src/hr_eval_lab/sources/fixture_store.py` | New | Fixture resolution + sha256 verification → `blocked` on mismatch (BR-009, DT-007) |
| `src/hr_eval_lab/evidence/packet_builder.py` | New | Controlled evidence packet before any reasoning (FR-005, DT-016) |
| `src/hr_eval_lab/rigor/resolver.py`, `rigor/triggers.py` | New | Rigor governance + 6 triggers every run (FR-011, BR-001/002, DT-003/005) |
| `src/hr_eval_lab/council/composition.py`, `code_roles.py`, `orchestrator.py` | New | 11-role council, Mode A/B/C composition, sequencing, bounded retry (FR-006, DT-004/016/017) |
| `src/hr_eval_lab/escalation/policy.py` | New | record_only / auto_escalate (implemented) / configured-escalated semantics + provenance (BR-003…006, DT-004) |
| `src/hr_eval_lab/gates/quality_gates.py` | New | 6 deterministic gates + per-gate fail behaviour (FR-008, DT-006) |
| `src/hr_eval_lab/providers/base.py`, `mock.py`, `foundry_stub.py` | New | Provider seam; deterministic mock default; lazy not-configured Foundry stub (FR-012, DT-013) |
| `src/hr_eval_lab/cli.py` | New | HTTP-only demo runner (FR-013, DT-018) |
| `scripts/vendor_fixtures.py`, `scripts/export_openapi.py` | New | Fixture vendoring with hashes; OpenAPI regeneration (RF-012, DT-014) |

### 4.2 Data layer / state / workflow-state

| File / Component | Change Type | Rationale |
|---|---|---|
| `src/hr_eval_lab/persistence/store.py` | New | Blob-equivalent full record + table-equivalent metadata rows, canonical JSON, append-only (FR-009, spec §15 storage shapes) |
| `src/hr_eval_lab/persistence/idempotency.py` | New | IdempotencyRecords-equivalent (FR-004, DT-008) |
| `src/hr_eval_lab/review_queue.py` | New | Persistence/Review Queue role output (council role 11) |
| `fixtures/**` + `fixtures/manifest.json` | New (vendored) | Hashed SYNTHETIC fixtures — requirements artifacts (BR-011, RF-012) |
| `.gitignore` (`var/`) | New | Local persistence root never committed |

### 4.3 API layer / contracts

| File / Component | Change Type | Rationale |
|---|---|---|
| `src/hr_eval_lab/api/app.py`, `auth.py`, `envelope.py`, `errors.py`, `routes_evaluations.py` | New | Facade owns identity, authorization, validation, idempotency, envelope, status mapping (FR-001…004, spec §15) |
| `openapi/evaluations-api.json` | New (committed artifact) | Contract drift prevention (FR-010, DT-014) |

### 4.4 IaC / resource configuration

None — no cloud resources exist or are created this slice (§3.17). `pyproject.toml` and `config/lab-config.toml` are the only configuration artifacts; both source-controlled by construction.

### 4.5 Microsoft-stack surfaces (portal / low-code)

| Surface | Configuration Change | Source-Control Feasible? | Evidence Plan (Stage 7) |
|---|---|---|---|
| Azure / Foundry / Copilot Studio / Entra portals | **None this slice** (spec §17) | N/A | None required; re-assess at the live-wiring slice |
| GitHub Actions | One workflow file | Yes | Workflow file + first green run link (AC-020, manual evidence) |

### 4.6 Tests

Full mapping in §5.1. All test files under `tests/` per §3.2; framework pytest; `conftest.py` provides app factory with injectable config/provider, temp persistence root, provider invocation counter, and log capture.

### 4.7 Eval scenario files

| Scenario File | Maps to Eval Contract Section | Change Type |
|---|---|---|
| `docs/delivery/slices/slice-e1-candidate-evaluation-council/evals/live/LE-001…LE-007.md` (one stub each, carrying scenario, pass criteria, thresholds verbatim from eval contract §7) | §7 (deferred live scenarios) | New (stubs only — no runner; deferred to wiring slice) |
| `tests/fixtures/**` (injection resume variant, tampered-manifest dir, missing-evidence variant, per-trigger mock scripts, per-gate failure scripts) | §6 DT-005/006/007/012/015 | New |

### 4.8 Dependency-sorted build order

Each step compiles/tests green before the next; tests are written with (not after) their subject.

| # | Step | Builds | Depends on | Proves as it lands |
|---|---|---|---|---|
| 1 | Project skeleton | `pyproject.toml`, `.gitignore`, package layout, `config.py` + `lab-config.toml`, `logging_setup.py` | — | pytest runs; config loads |
| 2 | Fixture vendoring | `scripts/vendor_fixtures.py`, `fixtures/**`, `manifest.json` | 1 | Hashes recorded; SYNTHETIC labels present |
| 3 | Domain schemas | `domain/ids.py`, `domain/schemas/*` | 1 | Literal-True flags; advisory enum; provider contract shape (start of DT-010/013 surface) |
| 4 | Fixture store | `sources/fixture_store.py` + unit tests | 2,3 | Hash verify → blocked path (DT-007 precursor) |
| 5 | Persistence | `persistence/store.py`, `idempotency.py`, `review_queue.py` + unit tests | 3 | Canonical JSON; metadata-row shape has no text fields |
| 6 | Evidence packet | `evidence/packet_builder.py` + unit tests | 4 | Segment addressing; packet completeness |
| 7 | Provider seam + mock | `providers/base.py`, `mock.py`, `foundry_stub.py` + `tests/contract/test_mock_parity.py` | 3,6 | **DT-013**; stub raises not-configured |
| 8 | Rigor + triggers | `rigor/resolver.py`, `triggers.py` + `tests/unit/test_rigor_resolver.py`, `test_escalation_triggers.py` | 3 | **DT-003, DT-005** (unit level) |
| 9 | Gates | `gates/quality_gates.py` + `tests/unit/test_quality_gates.py` | 3,6 | **DT-006** incl. bounded-retry accounting |
| 10 | Council orchestration + escalation | `council/*`, `escalation/policy.py` | 6,7,8,9 | Mode composition; sequence indices; escalation branch (DT-004/016/017 surface) |
| 11 | Facade API | `api/*` (auth, envelope, errors, routes, app factory) | 5,10 | Order-of-operations §3.4; status mapping |
| 12 | Integration test wave | `tests/integration/*` except CLI: DT-001, 002, 004, 007, 008, 009, 010, 011, 012, 015, 016, 017 | 11 | The core suite, green |
| 13 | OpenAPI | `scripts/export_openapi.py`, `openapi/evaluations-api.json`, `tests/contract/test_openapi_conformance.py` | 11 | **DT-014**; BQ-EC-004 closed |
| 14 | CLI | `cli.py` + `tests/integration/test_cli_runner.py` | 11 | **DT-018** + transcript evidence |
| 15 | CI | `.github/workflows/ci.yml` | 12–14 | AC-020 evidence (first green run link captured at PR time) |
| 16 | LE stubs + doc notes | `evals/live/LE-00x.md` stubs; current-state doc stub notes (full docs are Stage 12) | any | Deferral carried forward (BQ-EC-003) |

---

## 5. Test Plan

### 5.1 Deterministic test coverage map (DT-001…DT-018 → concrete files)

Framework: pytest; HTTP via FastAPI TestClient/httpx (DT-018 uses a real uvicorn subprocess). Pass conditions are the **exact** conditions in eval contract §6 — never restated weaker here; 100% pass required in CI on every PR.

| DT | Test file | Type | Covers (req/AC) | Implementation notes |
|---|---|---|---|---|
| DT-001 | `tests/integration/test_happy_path.py` | Integration | FR-001/005/007/009, AC-001/002 | Asserts every FR-007 envelope field; mechanical citation-resolution against the persisted packet; GET reconstruction incl. actor/role |
| DT-002 | `tests/integration/test_determinism.py` | Integration | AC-003, BR-009 | Two full runs (fresh temp stores); normalize exactly `evaluation_id` + timestamps; byte-compare canonical JSON; regression-baseline anchor |
| DT-003 | `tests/unit/test_rigor_resolver.py` | Unit | FR-011, BR-001/002/003, AC-004/005/006 | Pure-function matrix over all config states; property-style "no input can lower server-resolved rigor" |
| DT-004 | `tests/integration/test_escalation_matrix.py` | Integration | BR-003…006, AC-006/007/008 | Asserts executed-roles list + provider invocation count per config state; auto_escalate **implemented branch**: extension roles ran, `policy_triggered` provenance present; enum-default/runtime-read config-state test |
| DT-005 | `tests/unit/test_escalation_triggers.py` | Unit | FR-011, AC-009 | One scripted mock scenario per trigger provoking exactly its target; all-runs invariant: all 6 computations present in every record (asserted again over integration-run records) |
| DT-006 | `tests/unit/test_quality_gates.py` | Unit | FR-008, AB-008, AC-010, BR-008 | Per gate: ≥1 failing fixture/script → documented fail behaviour, ≥1 passing path; schema gate: invalid → one retry → still invalid → fail, `retry_count ≤ 1` |
| DT-007 | `tests/integration/test_status_vocabulary.py` | Integration | FR-003, BR-009, AC-011 | Unknown position/candidate → `validation_failed`; malformed → HTTP 400; tampered manifest dir → `blocked` with **zero** role outputs persisted; valid → `completed` |
| DT-008 | `tests/integration/test_idempotency.py` | Integration | FR-004, AC-012 | Replay: same `evaluation_id`, identical payload, invocation counter unchanged, no duplicate record |
| DT-009 | `tests/integration/test_authorization.py` | Integration | FR-002/009, AC-011/002 | `hr` passes both verbs; `admin_lab`/unauthenticated/other → `unauthorized` both verbs, no side effects; persisted actor/role exactly matches caller headers |
| DT-010 | `tests/integration/test_mandatory_flags_invariant.py` | Integration (property-style) | BR-007, AC-013 | Sweeps **all** records persisted by the whole suite's shared store fixture + serializer-level test that the literal-True model cannot emit false/absent flags |
| DT-011 | `tests/integration/test_never_log_scrub.py` | Integration | BR-010, AC-014 | caplog + capfd across full runs; zero sentinel hits (`tests/sentinels.py` derives sentinels from fixture bodies); metadata-row schema scan: no text-bearing fields |
| DT-012 | `tests/integration/test_injection_resistance.py` | Integration | BR-012, AB-006, AC-015 | Injection resume variant vs clean baseline: identical criterion scores; anomalous-content flag in policy/fairness block; `evaluation_question` injection variant; flagged output saved as human-review evidence (eval contract §11) |
| DT-013 | `tests/contract/test_mock_parity.py` | Contract | FR-012, AC-016 | Every mock role output validated against the single provider-contract schema set; trace placeholder fields present + typed; `ai_backend_type = "none"`; foundry_stub raises `ProviderNotConfiguredError` on invoke |
| DT-014 | `tests/contract/test_openapi_conformance.py` | Contract | FR-010, AC-017 | `openapi-spec-validator` on committed doc; regenerate-and-diff vs committed file; status enum equals declared vocabulary |
| DT-015 | `tests/integration/test_missing_evidence.py` | Integration | BR-013, AB-005, UFM-009/011 | Missing-evidence variant: note present, trigger 6 fired, no fabricated citation, conservative posture + limitation recorded |
| DT-016 | `tests/integration/test_sequencing.py` | Integration | FR-005, AB-001/002 | Sequence indices prove packet completion < first model-backed call; Rules Validator < judgment roles; extraction output has no score/recommendation/evaluative fields |
| DT-017 | `tests/integration/test_role_discipline.py` | Integration | FR-006, AB-001/008 | Per rigor mode: executed role set == composition exactly (no missing/phantom roles); per-role schema validity; per-role retry metadata 0/1; per-role citations resolve to packet only |
| DT-018 | `tests/integration/test_cli_runner.py` | Integration | FR-013, AC-018 | uvicorn subprocess on free port; CLI submit→get over HTTP; import-graph assertion (cli imports limited to stdlib + httpx); transcript captured to evidence path |

No DT for FR-014/AC-020 (CI proves itself — manual evidence: first green run link) and AC-019 (PO human review by design) — documented reasons carried from eval contract §15.

### 5.2 Test infrastructure needs

| Need | Description | Effort |
|---|---|---|
| App factory with injectable config + provider | `create_app(config, provider_factory)` so tests set rigor/policy states and mock scripts without touching committed config | Low |
| Provider invocation counter | Counter on the provider wrapper, persisted into the record (DT-004/008 assertion surface) | Low |
| Temp persistence root | Per-test `var` override via env/config; shared-store fixture for DT-010's all-records sweep | Low |
| Sentinel registry | `tests/sentinels.py` deriving unique substrings from fixture bodies (stays in sync with vendored fixtures) | Low |
| Test fixture variants | Injection resume, tampered-manifest directory, missing-evidence variant, per-trigger and per-gate mock scripts under `tests/fixtures/` (all SYNTHETIC-labelled) | Medium |
| uvicorn subprocess harness | Free-port spawn/teardown for DT-018 | Low |

### 5.3 Test gaps

| Requirement / Criterion | Gap Reason | Resolution Plan |
|---|---|---|
| AC-019 (output plausibility) | Human-judgment criterion by design | PO review of the Jordan Rivera happy-path output before merge (eval contract §11) |
| AC-020 / FR-014 | CI cannot test itself | Manual evidence: first green run link + a demonstrated failing-check (eval contract §15) |
| AC-015 human-review half | DT-012 covers the deterministic half | Flagged output routed to human review before merge (eval contract §11) |
| Latency ceilings (eval contract §13) | Provisional pending human ratification (BQ-EC-001) | Record actuals in DT-001/DT-002 runs; ratification at Stage 6 touchpoint or merge gate |

No other gap: every DT-001…DT-018 expectation has a named file above; every AC maps per eval contract §15.

---

## 6. Eval-Integration Plan

### 6.1 Trigger mechanism

- **Deterministic suite:** GitHub Actions on every PR (`.github/workflows/ci.yml`): checkout → setup Python 3.12 → `pip install -e .[dev]` → `pytest -q`. 100% pass required; failure blocks merge pending human disposition (eval contract §10). No cloud credentials, no network beyond GitHub-hosted checkout.
- **Live-model evals:** **none run this slice — documented deferral** (eval contract §7: "live eval not applicable until Foundry wiring"; not the non-agentic carve-out). No live-eval runner is built. LE-001…LE-007 are carried forward as scenario stubs (§4.7) gating the wiring slice; the Stage 11 eval summary must restate the deferral.

### 6.2 Eval scenario file references

| Scenario File | Eval Contract Reference | Data Fixture | Env Var / Config Needed |
|---|---|---|---|
| `evals/live/LE-001…LE-007.md` (stubs, deferred) | §7 | Jordan Rivera + future synthetic variants (weak-fit, fairness-trap, etc. — authored at wiring slice) | None this slice; wiring slice needs model deployment, region approval (BQ-005), deferred ADR |
| `tests/fixtures/**` deterministic adversarial analogues | §6 DT-003/007/012 | Injection variant, tampered manifest, downgrade-attempt request | None (local only) |

### 6.3 Model and version dependencies

| Dependency | Version / Reference | Notes |
|---|---|---|
| Model deployment | **None** — `ai_backend_type = none` | Any live call = blocking fail |
| Prompt files | None exist this slice | Mock is rule-derived, not prompt-driven; prompts arrive with the wiring slice under the deferred ADR |
| Tool/role schemas | `domain/schemas/council.py` + `provider.py`, versioned via `role_schema_version` field | The seam-contract authority in-slice (PO §2.2.2); captured in the deferred ADR later |
| Orchestration version | `council/composition.py` mode tables (source-controlled) | Recorded in provider metadata block of every record |

### 6.4 Eval-data governance notes

Synthetic-only, absolutely (BR-011; no approval path for real data). Fixtures vendored with sha256 + SYNTHETIC labels and committed by design. Resume-like content handled with real-PII discipline: never-log (DT-011), metadata-first rows; eval/test artifacts reference fixtures rather than embedding text where a reference suffices. Fairness-trap and injection material synthetic-by-design. No Canadian-residency constraint activates locally; it is a mandatory human gate before any live eval at the wiring slice (BQ-005). No secrets exist anywhere in the repo.

---

## 7. Architecture and ADR Flags

| # | Flag | Guideline Section / ADR | Severity | Recommended Action (Stage 6 — not resolved here) |
|---|---|---|---|---|
| AF-001 | Live Foundry wiring ADR is **deferred by PO decision** (Agent Service vs Agent Framework, backend enumeration, full trace/eval contract). In-slice seam authority = Foundry companion §8 + this slice's provider schemas. | Spec §16 gap 1; PO §2.2.2; OQ-001/BQ-001 | Non-blocking (this slice) | `adr-gap-detector` records the **deferred ADR** at Stage 6; human approval gates the wiring slice. Verify the seam contract built here matches the Foundry companion's required metadata fields. |
| AF-002 | Persistence layout: plan **adopts** the storage-doc shapes via local filesystem equivalents (blob-JSON + JSONL table rows). No deviation intended ⇒ no ADR; record in current-state docs. | Spec §16 gap 3; storage/evidence design doc | Non-blocking | `architecture-guideline-checker` confirms the §3.11 shapes are a faithful local mirror (esp. metadata-first row schema). |
| AF-003 | Gate-failure → envelope status `blocked` (with record persisted + review-queue entry) is a design decision inside the adopted vocabulary; the API-contracts doc does not explicitly enumerate gate-failure mapping. | API-contracts doc (status vocabulary) | Unknown (expected non-blocking) | Stage 6 confirms this mapping is within the adopted contract style; if the checker reads it as a new pattern, escalate for ADR before coding the gates' envelope behaviour. |
| AF-004 | HTTP code mapping in §3.4 is provisional (422/403/409 choices) pending the OpenAPI authoring against the API-contracts doc's HTTP mapping section. | API-contracts doc; BQ-EC-004 | Non-blocking | Confirm at step 13 (OpenAPI); DT-014 then locks it. |
| AF-005 | `auto_escalate` **included** (OQ-002 decision §3.9) — PO pre-authorized either branch (§2.1.3), so no ADR; flagged for visibility only. | Spec §2.1.3, BR-005 | Non-blocking | Stage 6 notes the decision; current-state docs record it (BQ-EC-002). |
| AF-006 | In-slice rigor-config mechanism is the bounded repo-file version; the full admin surface/config-audit mechanism is a deferred follow-up slice. | Spec §16 gap 2; RF-004 | Non-blocking | No action this slice; `adr-gap-detector` when the admin-surface slice is planned. |

No new architecture pattern beyond the active guidelines is proposed; nothing here is silently assumed resolved.

---

## 8. Risks and Blockers

### 8.1 Implementation risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Mock determinism breaks across platforms/runs (dict ordering, float repr, locale) | Med | High (DT-002 anchors the regression baseline) | Canonical JSON serializer (sorted keys, fixed separators, UTF-8); integer-only score arithmetic in mock; pinned Python minor version in CI |
| Mock becomes the architecture center (anti-goal, spec §22) | Med | High | Orchestrator/gates/persistence depend only on `CouncilProvider` + provider-contract schemas; DT-013 single-schema-source check; foundry_stub kept compiling against the same protocol |
| Citation-resolution mechanics (segment addressing) underspecified → gates 3/6 brittle | Med | Med | Stable segment ids defined in packet builder first (build step 6) and treated as contract by mock + gates; unit-tested before orchestration lands |
| Trigger thresholds arbitrary at first cut | High | Low (record-only by default) | Constants source-controlled + documented; DT-005 scripts pin behaviour; tuning deferred to calibration slice (RF-008) |
| Never-log regressions from incidental `print`/exception traces | Med | High (UFM-007 blocking) | Central logging config; redaction filter; DT-011 sweeps stdout/stderr too; exception handlers return safe details only |
| FastAPI auto-422 body shape conflicts with envelope expectations | Med | Low | Custom request-validation handler (HTTP 400 per FR-003) installed in app factory; covered by DT-007 |

### 8.2 Architecture risks

| Risk | ADR Needed? | Notes |
|---|---|---|
| Seam contract drifts from what the deferred Foundry ADR later pins | No (deferred ADR exists as flag AF-001) | Wiring slice reconciles; provider schemas versioned to make drift visible |
| Gate-failure status mapping read as contract deviation | Unknown (AF-003) | Stage 6 call; cheap to adjust before step 9 |
| Local persistence shapes diverge from storage doc | No, if faithful (AF-002) | Deviation would need ADR per spec §16 |

### 8.3 Test and eval risks

| Risk | Affects Deterministic Tests? | Affects Live Evals? | Notes |
|---|---|---|---|
| Scenario-scripting backdoor leaks into runtime | Yes | No | Script injection only via test-side provider construction; no config/API path; DT-013 asserts default provider is unscripted |
| DT-010 sweep misses records from tests using isolated temp stores | Yes | No | Shared-store fixture pattern + serializer-level literal-True test as the structural guarantee |
| Live evals assumed runnable later without carry-forward | No | Yes | LE stubs committed (§4.7); Stage 11 summary restates deferral (BQ-EC-003) |

### 8.4 Privacy, data residency, and audit risks

| Concern | Applies? | Notes |
|---|---|---|
| PHI / PII handling | No real / handled as-if | Synthetic-only; never-log tested (DT-011); metadata-first rows by schema construction |
| Canadian data residency | No (this slice) | All-local; binds at wiring slice (BQ-005 human gate) |
| Audit trail requirement | Yes — core | Full reconstruction + actor/role provenance are implemented behaviours with dedicated tests (DT-001/009/016) |

### 8.5 Manual-config and source-control risks

| Surface | Risk | Follow-Up at Stage 7? |
|---|---|---|
| Portals (Azure/Foundry/Copilot/Entra) | None — no portal work | N/A |
| GitHub Actions | First-run evidence must be captured | Yes (AC-020 manual evidence) |
| Repo config file | None — source-controlled by construction | No |

### 8.6 Sequencing dependencies

| Item | Depends On | Parallel OK? |
|---|---|---|
| Build steps 1–16 | §4.8 order | Steps 4/5, 7/8/9 parallel within their tiers; orchestration (10) needs 6–9; API (11) needs 5+10 |
| Coding start | **Stage 6 architecture compliance check** (this plan is not approval to code) | No |
| Merge | Human gates: PO review AC-019, DT-012 flagged-output review, green CI, human merge approval | No |

### 8.7 Open blockers

| ID | Blocker | Blocks Plan? | Blocks Coding? | Recommended Action |
|---|---|---|---|---|
| BK-001 | None — no blocking ambiguity, governance blocker, or unresolved human decision exists (eval contract §16). BQ-EC-001 (latency ratification) and AF-003/AF-004 (contract-time confirmations) are non-blocking and scheduled above. | No | No | Proceed to Stage 6 |

---

## 9. Recommended Next Step

```text
Stage 6 — Architecture compliance & ADR check
Skills: architecture-guideline-checker (always) + adr-gap-detector (AF-001 deferred-ADR recording)
```

### Handoff notes

For `architecture-guideline-checker`: verify (a) facade-owns-contract split in §3.4/§3.7 — no business decision logic inside model-backed roles; (b) §3.11 persistence shapes are a faithful local mirror of the storage doc (metadata-first rows especially); (c) provider seam (§3.15) matches the Foundry companion's required trace/eval metadata fields; (d) AF-003 gate-failure→`blocked` mapping and AF-004 HTTP codes against the API-contracts doc. For `adr-gap-detector`: record the **deferred** live-wiring ADR (AF-001) exactly per PO §2.2.2 — it gates the wiring slice, not this one. This plan contains no code, changes no requirement, and does not authorize coding to start; coding begins only after Stage 6 clears.

