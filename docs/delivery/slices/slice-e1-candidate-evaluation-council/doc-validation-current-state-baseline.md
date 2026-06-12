# Documentation Validation Report — Current-State Baseline (Stage 13)

| Field | Value |
|---|---|
| Slice | `slice-e1-candidate-evaluation-council` |
| Stage | 13 — Documentation consistency validation (`documentation-consistency-validator` skill) |
| Performed by | documentation-and-architecture-reconciliation-agent (validation mode) |
| Date | 2026-06-11 |
| Execution model | **Independent, isolated validation pass.** This validator did not author the documentation under review and shared **no session context** with the Stage 12 reconciler. All docs were read cold and checked against the uncommitted working tree, which is the implementation evidence (no feature branch / no useful diff exists — see Scope). |
| Overall result | **`non-blocking-gap`** (skill recommendation: **CONDITIONAL-PASS** — advance to Stage 14) |

---

## 1. Scope

### Documents validated (read cold)

| # | File | Class |
|---|---|---|
| 1 | `docs/product-current-state/README.md` | Durable current-state (slice-agnostic required) |
| 2 | `docs/product-current-state/candidate-evaluation-council.md` | Durable current-state (slice-agnostic required) |
| 3 | `docs/architecture/actual-technical-architecture.md` | Durable actual-architecture (slice-agnostic required) |
| 4 | `docs/architecture/candidate-evaluation-council-architecture.md` | Durable actual-architecture (slice-agnostic required) |
| 5 | `docs/architecture/provider-and-storage-seams.md` | Durable actual-architecture (slice-agnostic required) |
| 6 | `docs/integration/README.md` | Durable integration current-state (slice-agnostic required) |
| 7 | `docs/delivery/slices/slice-e1-candidate-evaluation-council/documentation-catchup-current-state.md` | Slice-scoped Stage 12 delivery artifact (slice language allowed here) |
| 8 | `README.md` ("Current Scope" section) | Repo top-level (updated section only) |

### Evidence reviewed

- **Code:** all modules under `src/hr_eval_lab/` actually inspected for the claims they back, including `api/` (app, auth, envelope, errors, routes), `cli.py`, `config.py`, `logging_setup.py`, `review_queue.py`, `council/` (composition, orchestrator, code_roles), `domain/` (ids; schemas: request, council, evaluation, provider, audit), `escalation/policy.py`, `evidence/packet_builder.py`, `gates/quality_gates.py`, `persistence/` (store, idempotency), `providers/` (base, mock, foundry_stub), `rigor/` (resolver, triggers), `sources/fixture_store.py`.
- **Tests:** `tests/test_dt001…dt018*.py` (structure/docstrings, plus targeted reads of DT-002, DT-007, DT-011), `tests/test_smoke.py`, `tests/sentinels.py`, `tests/live_evals/test_le_stubs.py` (LE-001…LE-007 skip stubs).
- **Config/contracts:** `config/lab-config.toml`, `openapi/evaluations-api.json` (info + paths), `pyproject.toml`, `.github/workflows/ci.yml`, `.gitignore` (incl. `git diff`), `fixtures/manifest.json`.
- **Slice artifacts (intent / cross-reference only, never documentation authority):** `slice-spec.md` not used as authority; `deviation-log.md` (DEV-001…DEV-006 verified present), `adr-deferred-foundry-wiring.md` (status header verified), `slice-state.yaml` (`current_stage: 9`, `eval_summary: null` verified), `architecture-check.md` (existence verified).

### Commands run (read-only, sandbox `/sessions/.../ai-hr-hiring-agent-lab`)

| Command | Result |
|---|---|
| `python3 -m pytest` | **88 passed, 7 skipped, 0 failed** (skips = LE-001…LE-007 deferral stubs) — matches the count claimed in docs 1, 2, 7, and 8 |
| `python3 scripts/export_openapi.py --check` | "OpenAPI document matches the committed file (no drift)" — matches docs 2, 3, 7 |
| `git status` / `git log --oneline` / `git diff .gitignore` | Branch `main`, single commit `44dd219 "start"`; entire implementation uncommitted/untracked; `.gitignore` diff adds `var/` + `*.egg-info/` — matches catch-up artifact §1 (see Observation O-1 re README.md) |

---

## 2. Findings

### 2.1 Blocking mismatches

**None found.**

Spot-checks performed (all claims verified against code/tests; none failed):

| Claim area | Doc(s) | Evidence verified |
|---|---|---|
| Endpoints: only `POST /api/evaluations`, `GET /api/evaluations/{evaluation_id}` | 1, 2, 3, 8 | `api/routes_evaluations.py`; `openapi/evaluations-api.json` paths list exactly these two |
| Envelope status vocabulary `completed\|blocked\|validation_failed\|unauthorized` emitted; `needs_input`/`error` reserved | 2, 7 | `api/envelope.py` `EnvelopeStatus` literal + reserved comments; `tests/test_dt007_status_vocabulary.py::test_no_reserved_status_emitted` |
| HTTP mapping 200/400/401/403; 409/422 never used; 400 body `{"error": "malformed_request_body", ...}` field-locations-only | 2 | `api/errors.py` (`ApiError`, `MalformedBodyError`, handlers); handlers take raw `Request` so framework 422 is bypassed; DT-007 |
| Order of operations: auth → malformed body → semantic validation → idempotency → source integrity → orchestration | 2, 3 | `api/routes_evaluations.py` steps 1–6 exactly as documented |
| Role vocabulary (7 roles), only `hr` authorizes; `admin_lab` rejected; headers `X-Lab-Actor-Id`/`X-Lab-Roles`/`X-Lab-Actor-Display` | 2 | `api/auth.py` `LAB_ROLES` (7 entries), `REQUIRED_ROLE = "hr"`, header constants; DT-009 exists |
| 11-role registry; Mode A/B/C compositions; 2 Mode C extension roles; `mode_letter()` derivation | 2, 3, 4 | `council/composition.py` `ROLE_REGISTRY` (11 entries, kinds match doc table), `MODE_C_EXTENSION_ROLES`, judgment tables, `mode_letter()` — role ids in doc 4 §1 match `domain/schemas/council.py` constants exactly |
| Exactly one bounded corrective retry, `corrective_hint`, no coercion; `provider_invocation_count`; `packet_sequence_index` | 2, 3, 4 | `council/orchestrator.py` `_invoke_model_role` (retry_count ≤ 1), `domain/schemas/audit.py` fields |
| Rigor: server-controlled, `standard\|high_impact\|escalated`, hiring classification floors at `high_impact`, downgrade recorded+ignored | 2 | `rigor/resolver.py` (pure function, `_ORDER`, `downgrade_attempted`/`downgrade_detail`) |
| Six triggers with exact ids and thresholds (spread ≥ 3; confidence < 40; severity high; score exactly at anchor-3) | 2, 4 | `rigor/triggers.py` `TRIGGER_IDS` (6), `SCORE_VARIANCE_THRESHOLD = 3`, `SYNTHESIS_CONFIDENCE_THRESHOLD = 40`, `THRESHOLD_PROXIMITY_MARGIN = 1` (⇒ exactly 3), `not_computed_inputs` |
| Escalation provenance `none\|configured_escalated\|policy_triggered`; `record_only` default; `auto_escalate` implemented behind config | 2, 4 | `escalation/policy.py` `decide_escalation` (all three branches); `config/lab-config.toml` `policy = "record_only"` |
| Six gates with exact ids; gate-3 missing-evidence-note interpretation; gate-4 prohibited-term scan incl. `employment gap`; any failure ⇒ `blocked` + record persisted + review entry | 2, 7 | `gates/quality_gates.py` `GATE_IDS` (6), module docstring (DEV-004 recorded decision), `PROHIBITED_RATIONALE_TERMS` |
| Idempotency: sha256 fingerprint of canonical request JSON; replay = zero council execution + "(Idempotent replay…)" message; key conflict ⇒ `validation_failed` `idempotency_key_conflict` | 2 | `persistence/idempotency.py`, `routes_evaluations.py` step 4 |
| Fixture sha256 re-verified per evaluation; mismatch ⇒ `blocked`, truncated hashes only | 2 | `sources/fixture_store.py` `resolve()`/`safe_detail()` (12-char truncation); DT-007 `test_tampered_source_hash_blocked_with_zero_council_execution` |
| Inline source `origin="inline"`, `synthetic=true` unconditional — labeled "inferred from code, no test" | 2 | `fixture_store.py` `inline_source()` line `synthetic=True` + code comment; labeling present in doc §10 |
| Persistence: canonical JSON blob `evaluations/{id}.json`; JSONL tables `EvaluationEvidence`/`IdempotencyRecords`/`ReviewQueue`; PartitionKey/RowKey shapes; evidence row has no text-bearing field | 2, 3, 5 | `persistence/store.py`, `domain/schemas/audit.py` `EvidenceRow` (refs/hashes/sizes/counters/flags/actor props only) |
| Audit record contents and `RECORD_SCHEMA_VERSION = "1.0"` | 2, 3 | `domain/schemas/audit.py` `EvaluationRecord` — every listed field present |
| `Literal[True]` advisory flags; closed recommendation enum (4 values); extraction schema has no score/recommendation field | 1, 2, 4 | `domain/schemas/evaluation.py` (lines 100–104, enum values), `domain/schemas/council.py` `EvidenceExtractionOutput`; DT-010/DT-017 exist |
| `PROVIDER_CONTRACT_VERSION = "1.0"`, `ORCHESTRATION_VERSION = "council-composition-v1"`, nullable trace/eval/agent/deployment/prompt placeholders, token_usage, latency_ms | 3, 4, 5, 6 | `domain/schemas/provider.py` — all fields exactly as documented |
| Mock provider: deterministic, content-derived, sha256-seeded, all 8 model-role schemas, scenario scripting constructor-only | 5 | `providers/mock.py` (script param in `__init__` only); `MODEL_ROLE_SCHEMAS` map has exactly 8 entries |
| Foundry stub: no Azure SDK imports, no network code, raises `ProviderNotConfiguredError`; lazy `select_provider` never imports stub on default path | 2, 3, 5, 6, 8 | `providers/foundry_stub.py` (imports: stdlib + app schemas only), `providers/base.py` `select_provider` (stub import inside non-default branch) |
| Config surface: exactly 4 keys with documented values; `extra="forbid"`; closed literals; `tomli` fallback | 2, 3, 7 | `config/lab-config.toml`, `config.py` (`RigorMode`/`EscalationPolicy`/`AiBackendType` literals, all models `extra="forbid"`) |
| CLI: stdlib + httpx imports only; `submit`/`get` subcommands with the documented flags | 2, 3 | `cli.py` import list (`argparse`, `json`, `sys`, `httpx`); argparse definitions; DT-018 exists |
| Never-log: DT-011 runs with sentinel registry deliberately empty | 2 | `tests/test_dt011_never_log.py` (`clear_sentinels()` + comment "redaction must NOT be what saves us"); `logging_setup.py` `RedactionFilter` |
| Fixtures: one position + one candidate, sha256-pinned, `synthetic: true`, "no real applicant data" notice | 2 | `fixtures/manifest.json` (4 artifacts, `synthetic_notice`) |
| CI: PR + push to main, Python 3.10, `pip install -e ".[dev]"`, `pytest -q`, OpenAPI drift check; no cloud credentials | 2, 3, 7 | `.github/workflows/ci.yml` — exact match |
| Runtime requirements: Python ≥ 3.10, FastAPI, uvicorn, pydantic ≥ 2, `tomli` on < 3.11; dev extras pytest/httpx/openapi-spec-validator | 2, 3 | `pyproject.toml` — exact match |
| Test counts: 88 passed / 7 skipped / 0 failed; DT-001…DT-018 + smoke; LE-001…LE-007 skip with deferral rationale | 1, 2, 7, 8 | Re-run by this validator (see Commands); `tests/live_evals/test_le_stubs.py` `_DEFERRAL` string |
| "No architecture guidelines and no approved ADRs in `docs/architecture/`" | 1, 3 | `find docs -type f`: `docs/architecture/` contains only the three durable docs; no `adr/` directory exists |
| Deferred Foundry ADR referenced only as deferred/unapproved | 3, 5, 6, 8 | `adr-deferred-foundry-wiring.md` status header: "Deferred — Draft. NOT APPROVED…"; every durable-doc reference carries draft/not-approved/human-gate language |
| Slice-language absence in docs 1–6 and 8 | 1–6, 8 | Grep for slice/branch/future-promise phrasing: all matches are path references to `docs/delivery/slices/...` or descriptions of the delivery-artifact folder and process — both explicitly acceptable. No "Slice E1 added…", no "this branch implemented…", no future-slice promises stated as product behavior. |
| Aspirational text labeled | 3 §8, 5, 6 | "Not built" list in doc 3; swap analyses in doc 5 headed "(planned, not implemented)"; doc 6 frames everything as "planned integration seams only". Nothing not-built is described as current. |
| Catch-up artifact (doc 7) git/evidence accuracy | 7 | Branch/commit/untracked-path claims, `.gitignore` diff content, test+drift evidence, `slice-state.yaml` stage 9 / null eval_summary, fixture `vendored_date: 2026-06-12` anomaly, DEV-001…DEV-006 — all verified true (see O-1, G-1 below for two minor imprecisions) |

### 2.2 Non-blocking gaps

| ID | Location | Finding | Recommended treatment |
|---|---|---|---|
| G-1 | Doc 7, `documentation-catchup-current-state.md` §2 ("all 27 modules") | The stated module count is off: `src/hr_eval_lab/` contains **29** non-`__init__` Python modules (41 `.py` files including 12 `__init__.py`). The inventory list itself in §3 is complete and correct; only the headline count is wrong. Slice-scoped artifact, no durable-doc impact, no behavioral claim affected. | Correct the count (or restate as "all modules, 41 files") next time this artifact is touched; no Stage 12 rework required. |

### 2.3 Observations

| ID | Location | Observation |
|---|---|---|
| O-1 | Doc 7 §1 (git status summary) | The snapshot lists modified-tracked files as `.gitignore` and `CLAUDE.md` only. Current `git status` also shows `README.md` modified — the modification the reconciliation pass itself made (documented in §4/§5 of the same artifact). The snapshot is internally consistent ("at reconciliation time" = pre-update) but a reader comparing it to live `git status` will see one more modified file. Informational only. |
| O-2 | Doc 7 §6 item 6 | "`.gitignore` does not exclude it [.DS_Store]" is effectively true for the listed paths but literally imprecise: `.gitignore` *does* contain `.DS_Store` / `**/.DS_Store` patterns; the files under `.agents/`, `.claude/`, `standards/` surface as untracked because the trailing negation rules (`!.agents/**`, `!.claude/**`, `!standards/**`) re-include them. The recommended hygiene fix (issue candidate 8) should account for the negation-pattern interaction, not just add an ignore line. |
| O-3 | Doc 4 §3 ("Code roles (`council/code_roles.py`)") | The section cites `CODE_ROLE_SCHEMA_VERSION` (value `"1.0"` — correct) under a heading naming `code_roles.py`; the constant is actually defined in `council/orchestrator.py:55`. The doc never explicitly claims a defining location, and the value and behavior are accurate, so this is wording-placement only. |
| O-4 | Docs 1, 2, 7 (test-evidence dating) | The "verified 2026-06-11" run claims were independently reproduced by this validator on the same date (88 passed / 7 skipped; OpenAPI no-drift). The fixture-manifest `vendored_date: "2026-06-12"` future-date anomaly flagged in doc 7 §6.5 was confirmed present; it is provenance metadata only — hashes verify. |
| O-5 | General quality note | Inferred-vs-tested labeling is present and used correctly where it matters (e.g., doc 2 §10 inline-synthetic flag "inferred from code, no test enforces caller behavior"; doc 5 §1 "Design intent — only the seam discipline itself is test-verified today, via DT-013"; doc 5 §2 `LocalStore` "observed from code"). This is the desired standard. |

---

## 3. Overall result and rationale

**Overall result: `non-blocking-gap`** (maps to the skill's **CONDITIONAL-PASS**).

Rationale:

- **Zero blocking mismatches.** Every capability claimed in the six durable docs and the README "Current Scope" section was traced to code, configuration, fixtures, or tests in the working tree; no unsupported or false claim was found across an extensive spot-check (endpoints, status vocabulary and HTTP mapping, role/gate/trigger counts and ids, enum values, config keys and values, version constants, module names, test counts, CI steps, runtime requirements).
- **No slice-specific language** appears in the durable docs; all slice references are path references or hierarchy explanations, which are permitted.
- **No aspirational text presented as built**: Azure/Foundry/Copilot/Entra are uniformly described as absent, with the Foundry seam stub correctly characterized as non-functional (raises `ProviderNotConfiguredError`) and the deferred ADR consistently labeled draft/NOT approved/human-gated.
- **Known limitations are correctly classified** (mock-only backend, simulated identity, single fixture pair, no admin surface, local-only persistence, first-cut thresholds, unreachable reserved statuses, deferred LE stubs) and match the code.
- **Completeness is good**: council modes, rigor, escalation provenance, all six triggers, all six gates, idempotency, persistence/audit record, review queue, auth, CLI, OpenAPI drift discipline, and CI are all documented.
- One **non-blocking gap** (G-1: a module-count typo in the slice-scoped catch-up artifact) and four observations exist; none affects correctness of the durable documentation, so the result is `non-blocking-gap` rather than `pass`, and advancement is warranted rather than a Stage 12 return.

---

## 4. Follow-up issue candidates

This validation endorses the catch-up artifact's eight issue candidates (§8 of doc 7) — especially candidate 1 (commit the uncommitted working tree to a reviewable branch; human-gated; prerequisite for evidence integrity at Stages 13–16). Additional candidates from this pass (suitable to fold into existing hygiene items rather than new issues):

1. Fix the "27 modules" count in `documentation-catchup-current-state.md` §2 (G-1) — fold into the next touch of that artifact or the closeout package.
2. When implementing the `.DS_Store` hygiene fix (doc 7 §8 item 8), handle the `.gitignore` negation-pattern interaction described in O-2.
3. Optionally relocate/clarify the `CODE_ROLE_SCHEMA_VERSION` mention in `candidate-evaluation-council-architecture.md` §3 (O-3) on the next documentation touch.

No GitHub issues were created by this pass.

---

## 5. Handoff

**Advance to Stage 14 (Traceability & closeout).** No return to Stage 12 is required: there are no blocking mismatches and the durable current-state and actual-architecture documentation accurately describes what was built. The non-blocking gap and observations above should travel with the closeout package as issue/cleanup candidates.

Reminder for the orchestrator (echoing doc 7 §7): the entire implementation remains uncommitted on `main`'s working tree; committing to a reviewable branch is human-gated and remains the highest-priority prerequisite before any further coding batch or the Stage 16 merge gate.

*This report was produced by a fresh, isolated validator with no shared context from the Stage 12 reconciler, against the uncommitted working tree as the implementation evidence baseline. No documentation, code, tests, or standards were modified by this pass — findings only.*
