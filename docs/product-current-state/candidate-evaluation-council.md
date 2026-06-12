# Candidate Evaluation Council — Current Behavior

Present-tense reference for what the system does today. Sources: the modules
under `src/hr_eval_lab/`, `config/lab-config.toml`, `fixtures/`,
`openapi/evaluations-api.json`, and the deterministic test suite under
`tests/` (DT-001…DT-018; 88 passed / 7 deferred-live-eval skips, verified
2026-06-11). Claims that rest on code inspection alone (no dedicated test)
are flagged inline.

## 1. What the system does

The system evaluates **one synthetic candidate against one position rubric**
and returns an **advisory, evidence-grounded** evaluation for a human
reviewer. It never makes a hiring decision, never ranks candidates, never
contacts anyone — the result schema has no field capable of expressing any of
those (`src/hr_eval_lab/domain/schemas/evaluation.py`; DT-010, DT-017).

Everything runs locally and deterministically:

- AI council roles execute against a **deterministic mock provider**
  (`providers/mock.py`); identical inputs produce byte-identical records after
  normalizing run identity (evaluation id, derived correlation id, two
  timestamps) — DT-002.
- There is **no live model**, no Azure resource, no Entra identity, no
  Copilot Studio surface, and no network dependency in the runtime path. A
  non-functional Foundry seam stub exists and raises on any use (see §13 and
  `../architecture/provider-and-storage-seams.md`).

## 2. HTTP API

The FastAPI app is built by `create_app()` in `src/hr_eval_lab/api/app.py`.
The OpenAPI 3 contract is committed at `openapi/evaluations-api.json` and is
generated from the live app factory; `scripts/export_openapi.py --check`
fails on any drift (DT-014, CI step).

### Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/evaluations` | Submit one candidate evaluation to the council. |
| `GET` | `/api/evaluations/{evaluation_id}` | Retrieve the persisted full audit record. |

### Request body (POST)

`EvaluationRequest` (`domain/schemas/request.py`, `extra="forbid"`):

| Field | Required | Notes |
|---|---|---|
| `position_id` | yes | Must be a known fixture position (`pos-sample-001`). |
| `candidate_ref` | one of | Fixture candidate (`cand-sample-001`), **or** |
| `resume_text` + `cover_letter_text` | one of | Inline synthetic documents (both required together; mutually exclusive with `candidate_ref`). |
| `idempotency_key` | yes | See §9. |
| `evaluation_question` | no | Free-text focus question; scanned for instruction-like content (§7). |
| `requested_rigor` | no | **Advisory only**; can never lower the server-resolved rigor (§5). |

### Response envelope

Every response body is the standard envelope (`api/envelope.py`):
`status`, `evaluation_id`, `case_id` (**always null** — there is no case
entity), `correlation_id`, `user_message`, `safe_details`, `result`,
`errors`, `warnings`.

Emitted status vocabulary: `completed | blocked | validation_failed |
unauthorized`. `needs_input` and `error` are **declared but reserved — never
emitted** (DT-007).

### HTTP status mapping (`api/errors.py`; DT-007/DT-009/DT-014)

| Condition | HTTP | Envelope status |
|---|---|---|
| Business outcome (success, gate-blocked, semantic validation failure) | 200 | `completed` / `blocked` / `validation_failed` |
| Malformed body (invalid JSON, non-object, schema-invalid shape) | 400 | none — body is `{"error": "malformed_request_body", "detail": …}`; detail carries field locations/types only, never values |
| Missing/empty identity header | 401 | `unauthorized` |
| Authenticated caller without the `hr` role | 403 | `unauthorized` |
| 409 / 422 | never used | — |

### Order of operations (POST handler, `api/routes_evaluations.py`)

1. Authentication + role authorization (short-circuits everything; DT-009).
2. Malformed-body rejection → HTTP 400.
3. Semantic validation (unknown `position_id` / `candidate_ref` →
   `validation_failed`).
4. Idempotency check (replay → stored result, **zero** council execution).
5. Source resolution + sha256 verification (mismatch → `blocked`, zero
   council execution).
6. Evidence packet build → council orchestration → gates → persistence →
   envelope.

`GET` returns the full persisted audit record inside `result` (status
`completed`), or `validation_failed` for an unknown id.

## 3. Authentication and authorization (simulated)

Identity is a **simulated lab stand-in**, not a real identity system
(`api/auth.py`): headers `X-Lab-Actor-Id` (required), `X-Lab-Roles`
(comma-separated), optional `X-Lab-Actor-Display`. The known role vocabulary
is `hr, hiring_manager, reviewer, auditor, admin_lab, admin_prod, support`,
but **only `hr` authorizes either endpoint** — all other roles, including
`admin_lab`, are rejected (DT-009). Authorization is case-less (global role
group only; no per-case ACL exists). The authenticated actor id, roles, and
resolving role are persisted on every audit record. This mechanism is never
an Entra substitute; no Entra integration exists.

## 4. Council orchestration

`council/orchestrator.py` runs a single synchronous pipeline over an 11-role
registry (`council/composition.py`). Code roles are deterministic and
facade-owned; model-backed roles execute only through the provider seam.

Roles in pipeline order: Request Normalizer (code) → Source
Ingestion/Versioning (code, builds the evidence packet) → Evidence Extraction
(model; **the first provider call, only after packet completion** — DT-016) →
Deterministic Rules Validator (code, before any judgment role) → judgment
roles for the mode → Quality Gate Evaluators (code) → Persistence/Review
Queue (code).

**Modes** (recorded as `effective_mode` A/B/C on every record):

| Mode | Composition |
|---|---|
| A (`standard` rigor) | Extraction + Merit Advocate, Risk/Gaps Advocate, Synthesis Judge |
| B (`high_impact` rigor — the default) | Mode A + Neutral Scoring Judge + Policy/Fairness Auditor |
| C (escalated) | Mode B + Second Synthesis Judge + Rubric Calibration Judge (extension roles run only via the escalation decision) |

Every model-backed output is validated against its declared pydantic schema
immediately, with **exactly one bounded corrective retry** on schema failure;
a still-invalid output fails quality gate 1 — no coercion, no further retries
(DT-006). Every role execution (code and model) is recorded with sequence
index, schema version, output, provider metadata, retry count, and schema
validity. Role discipline is structural: the Evidence Extraction schema has
no score/recommendation field of any kind (DT-017).

## 5. Rigor modes and resolution

Rigor is server-controlled (`rigor/resolver.py`, DT-003):

- Modes: `standard | high_impact | escalated`. Server default comes from
  `config/lab-config.toml` (`rigor.default_mode`, currently `high_impact`).
- The hiring risk classification (`hiring_candidate_evaluation`) defaults the
  run to `high_impact`; an explicit server `standard` or `escalated` wins.
- The request's `requested_rigor` is advisory and **can never lower** the
  resolved rigor; a downgrade attempt is recorded
  (`downgrade_attempted`/`downgrade_detail` on the record) and ignored.

## 6. Escalation triggers and policy

Six escalation triggers are **computed and recorded on every run**
(`rigor/triggers.py`, DT-005), regardless of policy:
`score_variance_above_threshold` (spread ≥ 3),
`evidence_packet_missing_required_criteria`, `synthesis_confidence_low`
(confidence_score < 40), `policy_fairness_severity_high`,
`recommendation_near_decision_threshold` (required-criterion score exactly at
the anchor-3 boundary), `criterion_scored_with_no_direct_evidence`.
Thresholds are source-controlled constants in that module (first-cut values;
tuning is not yet implemented). Roles absent from the current mode are listed
in `not_computed_inputs` — no silent omission.

The escalation decision (`escalation/policy.py`, DT-004) records
**`escalation_provenance`** on every record — `none |
configured_escalated | policy_triggered`:

- `effective_rigor = escalated` → Mode C extension roles run
  unconditionally; provenance `configured_escalated`; human review reason
  recorded.
- Triggers fired + `escalation.policy = "auto_escalate"` → Mode C runs;
  provenance `policy_triggered`.
- Triggers fired + `escalation.policy = "record_only"` (the default) →
  triggers, rationale, and review flags are recorded; **no** Mode C roles
  run; provenance `none`.

## 7. Untrusted-content handling (injection resistance)

Candidate document text and the free-text `evaluation_question` are treated
as **data, never instructions**. The Deterministic Rules Validator
(`council/code_roles.py`) scans candidate segments and the evaluation
question against a source-controlled marker list (`ignore previous`,
`system prompt`, `you must score`, …); matches set
`anomalous_content_detected`, flag the segments on the record and in the
fairness block, and add a human-review reason — **scores are unchanged**
versus a clean baseline (DT-012). It also checks required-document presence
and notes disqualifier-D1 (work eligibility) evidence presence/absence —
absence is recorded as **missing evidence, never a disqualification**.

## 8. Quality gates and bounded retry

Six deterministic gates run on every evaluation (`gates/quality_gates.py`,
DT-006), each recorded as `{gate_id, result, reason, details_safe}`:

1. `schema_validity` — every role output schema-valid with retry_count ≤ 1.
2. `all_criteria_scored` — every rubric criterion carries an integer score 1–5.
3. `evidence_per_score` — every score cites mechanically resolvable evidence
   **or** carries an explicit missing-evidence note with the conservative
   floor posture (recorded design decision in the module docstring:
   missing evidence is surfaced, never fabricated; unresolvable/fabricated
   citations still fail).
4. `no_prohibited_factors` — deterministic scan of scoring rationale for
   prohibited-factor/proxy terms (age, gender, race, …, employment gap);
   also fails if auditor findings were dropped.
5. `human_review_flag_present` — belt-and-braces; the `Literal[True]` schema
   makes the failing state nearly unconstructible.
6. `groundedness_heuristic` — every quoted evidence span must appear verbatim
   in its referenced segment; missing-evidence notes present where required.

Any gate failure maps to envelope status `blocked`; the full record is still
persisted and a review-queue entry is still written.

## 9. Idempotency

`persistence/idempotency.py` (DT-008): the request fingerprint is a sha256 of
the canonical request JSON (never content-derived beyond the request body
itself). Replay with the same `idempotency_key` and same fingerprint returns
the original result with **zero council execution** and an explicit
"(Idempotent replay…)" note in `user_message`. The same key with a different
fingerprint returns `validation_failed` (`idempotency_key_conflict`).

## 10. Evidence packet and source integrity

- `sources/fixture_store.py`: `fixtures/manifest.json` is the hash authority;
  every fixture file is sha256-re-verified **on every evaluation**. A
  mismatch raises a source-integrity error that the facade maps to `blocked`
  with zero council execution; details carry artifact id and truncated
  expected/actual hashes only — never content (DT-007). Inline request text
  is wrapped as a versioned, hashed source (`origin="inline"`,
  `synthetic=true` — the synthetic flag for inline text is set
  unconditionally by code; callers are trusted to supply synthetic text;
  inferred from code, no test enforces caller behavior).
- `evidence/packet_builder.py`: source text is split into stable,
  whitespace-normalized paragraph segments with addressable ids
  (`resume:s01`, …) so every later citation mechanically resolves to a packet
  segment or extraction evidence id (gates 3/6). The packet also carries a
  typed rubric view (scale, anchors, criteria with required/preferred kind,
  disqualifier and prohibited-factors notes). Packet completion **precedes**
  any provider call, proven by recorded sequence indices (DT-016).

## 11. Persistence and the audit record

`persistence/store.py` writes append-only under the configured local root
(default `var/lab-data/`, gitignored):

- **Blob-equivalent** `evaluations/{evaluation_id}.json` — the full audit
  record (`EvaluationRecord`, `domain/schemas/audit.py`) in canonical JSON
  (sorted keys, fixed separators, UTF-8). It contains: record schema version
  (1.0), evaluation/correlation ids, timestamps, status
  (`completed`/`blocked`), the authenticated actor context, the request as
  received, hash-pinned source refs, the entire evidence packet, **every**
  role execution with provider metadata, rigor resolution, all six triggers,
  the escalation block, gate results, provider invocation count, effective
  mode A/B/C, the advisory result, and the human-review block. This is the
  **only** artifact allowed to carry document/model text.
- **Table-equivalent JSONL** under `tables/`:
  `EvaluationEvidence.jsonl` (one metadata-first row per role execution — the
  row schema has **no text-bearing field** by construction: references,
  hashes, sizes, counters, flags, actor/role/correlation properties),
  `IdempotencyRecords.jsonl`, and `ReviewQueue.jsonl`.

## 12. Review queue

Every evaluation gets a `ReviewQueue.jsonl` entry (`review_queue.py`) —
review is always required. `mandatory_reasons` always includes the
advisory-only policy reason and is enriched for configured-escalated runs,
policy-triggered escalation, quality-gate failure, and anomalous-content
flags. Rows are metadata-only.

## 13. Advisory result shape

The `result` payload on a completed evaluation (`AdvisoryEvaluation`)
carries: the two `Literal[True]` advisory flags; a closed
`recommendation_label` enum (`advance_to_interview | do_not_advance |
hold_for_review | insufficient_evidence`); per-criterion evaluations with
score 1–5, rationale, supporting/contrary evidence citations, and explicit
missing-evidence notes; disagreements with resolution rationale ("evidence
wins, not votes"); a fairness block (required even when empty); confidence
label + 0–100 score; limitations (always including a note that the output
came from the deterministic mock backend); rigor, escalation, trigger, and
gate blocks; and the truthful `ai_backend_type` (DT-001, DT-013).

## 14. CLI

`python3 -m hr_eval_lab.cli` (`cli.py`, DT-018) is a thin HTTP client of the
facade — its import graph is stdlib + httpx only; there is no privileged side
door. Subcommands: `submit` (POST) and `get <evaluation_id>` (GET), with
flags for base URL, identity headers, fixture/inline candidate sources,
idempotency key, evaluation question, and advisory requested rigor. It prints
the response envelope to stdout.

## 15. Configuration surface

`config/lab-config.toml` is the **only** runtime configuration surface
(source-controlled, read once at app start, validated by
`config.py` with `extra="forbid"`; no admin/config API exists):

| Key | Values | Current value |
|---|---|---|
| `rigor.default_mode` | `standard \| high_impact \| escalated` | `high_impact` |
| `escalation.policy` | `record_only \| auto_escalate` | `record_only` |
| `provider.ai_backend_type` | `none \| foundry_agents` | `none` |
| `persistence.root` | path | `var/lab-data` |

Setting `provider.ai_backend_type = "foundry_agents"` selects a
**non-functional seam stub** that raises `ProviderNotConfiguredError` on any
invocation — there is no configuration value that produces a live model call.
No secrets exist in the repository.

## 16. Fixtures

`fixtures/` contains one synthetic position (`pos-sample-001`: job
description + versioned rubric `rub-sample-001`) and one synthetic candidate
(`cand-sample-001`: resume + cover letter), pinned by
`fixtures/manifest.json` (artifact id, version, path, sha256, provenance,
`synthetic: true`). All fixtures are synthetic lab data; the manifest states
no real applicant data is permitted. `scripts/vendor_fixtures.py` is the
dev-time vendoring/hash-refresh tool.

## 17. Logging and never-log guarantees

`logging_setup.py`: log records carry only ids, hashes, statuses, role names,
durations, and counters. The primary control is that no call site passes
content; a defense-in-depth redaction filter additionally replaces any record
containing a registered sentinel substring. DT-011 verifies a full
integration run with the redaction registry deliberately **empty** — zero
fixture-document substrings appear in any log line or any JSONL table row.

## 18. Tests and CI

- `tests/` — deterministic suite DT-001…DT-018 plus `test_smoke.py`;
  `tests/live_evals/test_le_stubs.py` holds LE-001…LE-007 stubs that **skip**
  with a documented rationale (no live model behavior exists to evaluate).
  Verified result (2026-06-11): 88 passed, 7 skipped, 0 failed.
- `.github/workflows/ci.yml` — on PR and push to main: Python 3.10,
  `pip install -e ".[dev]"`, `pytest -q`, and the OpenAPI drift check. No
  cloud credentials, no deployment.
- Runtime requirements (`pyproject.toml`): Python ≥ 3.10, FastAPI, uvicorn,
  pydantic ≥ 2, `tomli` on Python < 3.11.

## 19. Known limitations

- **No live AI backend.** All judgment content is produced by the
  deterministic mock (keyword-matching against rubric anchors); recommendation
  labels and confidence values are mechanical, not model judgments. Every
  result's limitations list says so.
- **Single fixture pair.** Exactly one known position and one known candidate
  reference; any other id is `validation_failed`.
- **Simulated identity only.** Header-based identity with no verification of
  the caller; suitable for a local lab only.
- **No admin/config surface.** Rigor and escalation are changeable only by
  editing the source-controlled config file; no change-audit subsystem exists.
- **Local filesystem persistence only.** No Azure storage, no retention
  policy, no cleanup tooling for `var/lab-data`.
- **Trigger thresholds are first-cut constants**; no calibration mechanism
  exists.
- **Reserved envelope statuses** `needs_input`/`error` and HTTP 409 are
  declared but unreachable.
- **Live evals LE-001…LE-007 are deferred stubs** — they assert nothing yet.
