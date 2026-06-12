# Eval Summary — Azure/Foundry Readiness Pack (slice-e1, follow-on coding batch)

## 1. Summary Metadata

| Field | Value |
|---|---|
| Slice ID / Name | `slice-e1-candidate-evaluation-council` / Single-Candidate Calibrated Evaluation Council — **Azure/Foundry readiness pack coding batch** |
| Summary Date / Produced By | 2026-06-11 / eval-execution-and-review-agent (Claude), `eval-result-summarizer` skill, Stage 11 |
| Eval Contract Reference | [`eval-contract.md`](./eval-contract.md) (`EC-slice-e1-candidate-evaluation-council-001`) §1 metadata + §7 deferral; RP test plan: [`implementation-plan-readiness-pack.md`](./implementation-plan-readiness-pack.md) §4 |
| Run Record Reference | N/A — no live eval run record exists (live evals deferred; see §6). Deterministic-run evidence: command transcript in §3a of this summary |
| Summary Status | **Complete** (deterministic scope); live-eval scope **Not Applicable this batch — documented deferral** |
| Live Eval Applicability | **Required — deferred to the Foundry-wiring slice** (eval contract §1/§7). This batch executes the deterministic suite only |
| Risk Tier | **High-Assurance** (binding, from `eval-risk-profile.md`; deterministic threshold = 100% pass on every run) |

> **Explicit statement (Process §18.1/§19, required by eval contract §1 and BQ-EC-003):**
> **Live Foundry evals (LE-001…LE-007) were NOT run, and NO live Azure tests were run, in this batch.**
> Why: this slice (including the readiness pack) ships the deterministic mock backend only
> (`ai_backend_type = none`, provider `deterministic_mock`) — there is no model, no prompt
> execution, no tool-orchestration behaviour against a live service, and no
> behaviour-affecting model dependency to evaluate; a live eval against the mock would
> measure nothing. The live-wiring ADR (`adr-deferred-foundry-wiring.md`) remains a
> **deferred, unapproved human gate**, and BQ-005 (Canadian-residency region/deployment
> approval) is a **pending mandatory human gate** before any live eval. LE-001…LE-007 are
> carried forward **unweakened** and gate the Foundry-wiring slice (eval contract §7/§10).

## 2. Version Block (Process §19.2)

Live-model version fields are marked `N/A — non-agentic carve-out` for this batch per the
summarizer skill §1: no model, prompt, tool-orchestration, agent behaviour, or
behaviour-affecting model dependency executed. Note the eval contract frames this slice as a
**documented deferral, not a permanent carve-out** — the capability is agentic and LE-001…007
remain binding on the wiring slice; the N/A markers below apply to this mock-only coding
batch only. Pinned values are from `slice-state.yaml` (`pinned_versions`, Stage 7).

| Field | Value |
|---|---|
| Model name / version | `N/A — non-agentic carve-out (this batch)`; pinned: **model = none** (`ai_backend_type=none`, deterministic mock; live model deferred to Foundry-wiring slice) |
| Prompt version | `N/A — non-agentic carve-out (this batch)`; prompt registry templates exist at v1 (`prompts/templates/<role_id>.v1.md`) but are **recorded, not executed** under the mock |
| Tool schema version | `src/hr_eval_lab/domain/schemas/` (pydantic v2 single schema source; **provider contract v1**) |
| Orchestration version | **council-composition-v1** (`src/hr_eval_lab/domain/schemas/provider.py` `ORCHESTRATION_VERSION`) |
| Workflow/state logic version | Deterministic council pipeline as implemented in `src/hr_eval_lab/` (no separate workflow version pinned; covered by orchestration version above) |
| Date run | 2026-06-11 |
| Scenario set | Deterministic suite DT-001…DT-018 + smoke baseline + readiness-pack RP suite (RP-001…RP-015 across `tests/test_rp001…rp005`); LE-001…LE-007 present as skipping stubs |
| Runs per scenario / Pass threshold | 1 CI-style run per test this execution (DT-002 internally runs the pipeline ≥2× for byte-identity) / **100% pass required** (High-Assurance deterministic rule, eval contract §10). Live thresholds (20+ runs, ≥90% / zero-critical) — `N/A this batch — deferred` |

## 3. Scenario Results

### 3a. Commands run and outcomes (2026-06-11, local, Python 3.10.12)

| # | Command | Result | Exit code |
|---|---|---|---|
| 1 | `python3 -m pytest` | **146 passed, 7 skipped, 0 failed** (1 unrelated starlette deprecation warning), 2.48 s | 0 |
| 2 | `python3 scripts/export_openapi.py --check` | "OpenAPI document matches the committed file (no drift)." | 0 |
| 3 | `python3 scripts/run_council_local.py --data-root /tmp/eval-summary-demo` | Completed; safe summary only (see §3d) | 0 |
| 4 | `python3 scripts/smoke_foundry_config.py` | Config echo + **SKIPPED** (live disabled by default; requires `HRHA_ENABLE_LIVE_AZURE=true` AND `--live` AND human-approved ADR) | 0 |
| 5 | `python3 scripts/smoke_storage_config.py` | `local_filesystem backend: OK` + **SKIPPED** live Azure checks (same double guard) | 0 |

Count reconciliation: 146 passed = 88 (pre-existing DT-001…DT-018 suite + smoke baseline,
matching the batch-start baseline of 88 passed) + 58 (readiness-pack RP test files, verified
by running the five RP files in isolation: 58 passed). 7 skipped = exactly the LE-001…LE-007
stubs, each skipping with the contract's rationale string:
`"live eval not applicable until Foundry wiring — deferred per eval contract"`
(`tests/live_evals/test_le_stubs.py`).

### 3b. Deterministic scenarios (executed — all pass)

| Scenario set | Test file(s) | What it covers (from module docstrings / eval contract §6) | Status |
|---|---|---|---|
| DT-001…DT-018 | `tests/test_dt001_happy_path.py` … `test_dt018_cli_facade_only.py` (+ `tests/test_smoke.py` baseline) | Full eval-contract §6 deterministic suite: happy path, byte-identical determinism, rigor resolver, escalation matrix, 6 triggers, 6 gates + bounded retry, status vocabulary, idempotency, authorization/actor provenance, mandatory advisory flags, never-log, injection resistance, mock parity, OpenAPI conformance, missing evidence, sequencing, per-role discipline, CLI-via-facade | **Pass (100%)** |
| RP-001…RP-004, RP-014 | `tests/test_rp001_storage_backend.py` | Storage backend boundary, artifact layout, summary rows, per-role transcripts; "all local/deterministic; no network, no Azure SDK, synthetic data only" | **Pass** |
| RP-005…RP-008 | `tests/test_rp002_scaffolds_and_registry.py` | Azure Blob scaffold, provider registry, kill switch, mock contract conformance; "pins the disabled-by-default posture: no Azure/Foundry import on the default path, fail-closed configuration errors, guards enforced server-side" | **Pass** |
| RP-009 | `tests/test_rp003_prompt_registry.py` | Versioned prompt registry — all 10 role templates present, mandatory safety constraints embedded, no secrets / no real-looking tenant/subscription/endpoint/GUID values | **Pass** |
| RP-010, RP-011 | `tests/test_rp004_openapi_and_headers.py` | OpenAPI readiness (operation IDs, headers documented, no provider/model/deployment/endpoint/agent field in the request schema) and Idempotency-Key header behaviour. **Includes formal spec validation**: `test_rp010_openapi_parses_and_validates` runs `openapi_spec_validator.validate()` on `openapi/evaluations-api.json` | **Pass** |
| RP-012, RP-013 | `tests/test_rp005_cli_and_smoke.py` | Local CLI demo writes the artifact tree with a safe stdout (no resume/prompt text); smoke scripts disabled by default and perform no live work | **Pass** |

### 3c. Live / future scenarios (NOT executed — deferred)

| Scenario | Vehicle | Status this batch |
|---|---|---|
| LE-001…LE-007 (grounding, calibration, fairness trap, injection trap, missing document, disagreement, request-surface injection) | `tests/live_evals/test_le_stubs.py` stubs | **Skipped (7/7)** with the documented deferral rationale; binding, unweakened obligations of the Foundry-wiring slice (eval contract §7) |
| Live Foundry config smoke | `scripts/smoke_foundry_config.py` | Scaffold only; **disabled by default** (double guard: env flag + `--live`); ran in disabled state → SKIPPED, exit 0, no SDK import, no network |
| Live Azure storage smoke | `scripts/smoke_storage_config.py` | Scaffold only; **disabled by default**; ran in disabled state → local backend OK, live checks SKIPPED, exit 0, no network |

### 3d. Local CLI demo — safe summary lines (RP-012 evidence; no resume text, no prompts)

`run_council_local.py --data-root /tmp/eval-summary-demo` printed (abridged to safe fields):
status `completed`; effective_rigor `high_impact`; effective_mode `B`; escalation_policy
`record_only`; triggers_fired `2/6`; gates `6 pass / 0 fail`; recommendation
`advance_to_interview`; `decision_support_only: True`; `human_review_required: True`;
19 artifacts written under `/tmp/eval-summary-demo/evaluations/<evaluation_id>/` (record,
request, source-documents, evidence-packet, synthesis, quality-gates, provider-metadata,
human-review, and per-role `council/*.json` transcripts, each with size + sha256); closing
line: "This output is decision support for a human reviewer — never a hiring decision."

### 3e. Static checks

**No lint or type checkers are configured in this repo** — verified: no ruff/mypy/flake8/
black/pylint configuration exists (`pyproject.toml` contains only `[tool.setuptools]` and
`[tool.pytest.ini_options]`; no `setup.cfg`, `tox.ini`, `mypy.ini`, `.flake8`, or
`ruff.toml`). This matches the RP implementation plan §4: "No lint/type config exists in
the repo (recorded; not added in this batch)."

## 4. Threshold Summary

| Risk Tier | Required Threshold (§19.1) | Actual | Zero Critical Failures? | Threshold Met? |
|---|---|---|---|---|
| High-Assurance — deterministic tests | **100% pass on every run** | 146/146 executed tests passed (100%); 7 skips are the documented LE deferral stubs, not test failures | Yes — zero failures of any kind | **Pass** |
| High-Assurance — live high-risk (LE-001/002/005/006) | 20+ runs, ≥90%, zero critical + human review | Not run | — | **N/A this batch — deferred (see §6)** |
| High-Assurance — safety/privacy/evidence-critical + adversarial (LE-003/004/007) | 20+ runs, zero critical failures, stricter rubric threshold + human review | Not run | — | **N/A this batch — deferred (see §6)** |

**Overall threshold result:** **Met** for everything executable in this batch (deterministic
scope). Live thresholds are intentionally unevaluated and carry forward unweakened.

## 5. Failure Summary

**No failures.** 0 failed / 0 errored across the full suite, OpenAPI drift check, CLI demo,
and both smoke scaffolds. There is nothing to classify — `eval-failure-classifier` is not
required for this batch. No deterministic failure blocks local deterministic readiness.

N/A — no live eval failures; the eval contract documents the live-eval deferral (§7), and
the version-field carve-out marking is per the summarizer skill §1 (see §6 nuance).

## 6. Deferral / Carve-Out Rationale (live evals not run)

| Required statement | Evidence |
|---|---|
| No model behaviour in this batch | Eval contract §1/§7; `slice-state.yaml` `pinned_versions.model: none`; provider metadata records `ai_backend_type = "none"` truthfully (DT-013, RP-008) |
| No prompt execution in this batch | Prompt registry templates are recorded (template id/version stamped into provider metadata), **not executed** under the mock — RP implementation plan §3 T4; RP-008/RP-009 |
| No live tool-orchestration behaviour | Orchestration is the deterministic local council pipeline (council-composition-v1); no Foundry module imported on the default path (RP-005/006), kill switch + `HRHA_ENABLE_LIVE_AZURE=false` pinned by RP-007/RP-013 |
| No live agent behaviour | All Foundry provider scaffolds raise `ProviderNotConfiguredError`; smoke scripts SKIP in default state (verified this run, exit 0) |
| No behaviour-affecting model dependency | Eval contract §7: "the deterministic local provider replaces every model-backed role … live evals on a mock would measure nothing" |

**Live eval not applicable rationale (verbatim posture from the eval contract):** "live eval
not applicable until Foundry wiring." This is recorded in the contract as a **documented
deferral — explicitly not the permanent non-agentic carve-out** (the capability is agentic);
version/threshold fields in this summary are marked `N/A — non-agentic carve-out` only in the
mechanical sense required by the summarizer skill for a batch with zero model dependency.
Before any live eval may run, three human gates remain: (1) approval of the deferred
Foundry-wiring ADR (`adr-deferred-foundry-wiring.md`, draft, NOT approved); (2) BQ-005
Canadian-residency region/deployment approval; (3) the wiring slice's eval contract importing
LE-001…LE-007 unweakened with eval-infra/storage residency confirmed (eval contract §12/§16).

## 7. Cost and Latency Summary

Contract §13 thresholds are provisional (pending human ratification, BQ-EC-001). Actuals
recorded at the granularity available this run:

| Metric | Provisional target / threshold | Actual this run | Pass? |
|---|---|---|---|
| Deterministic suite duration | < 5 min target / 15 min fail | **2.48 s** | Pass |
| `POST`/`GET` end-to-end (mock) | < 2 s / 30 s ceiling; < 1 s / 5 s | CLI submit→retrieve demo completed within the suite/script run times; no per-request instrumentation captured (not contract-required for this summary) | Pass (no run approached any ceiling) |
| **Live token spend** | **0 — any live call = blocking fail (hard boundary)** | **0 — no live call occurred anywhere** (no network, scaffolds disabled, kill-switch posture test-pinned) | **Pass** |
| Live cost/latency dimensions (per-role token budgets, timeout, degraded mode, per-run eval cost) | To be set in the wiring slice's risk profile | Not tracked — deferred with the live evals | N/A — deferred |

**Cost/latency overall:** Met for in-slice metrics; live dimensions deferred by contract.

## 8. External Artifact References

| Item | Artifact Type | Location | Notes |
|---|---|---|---|
| Full pytest output | Test run transcript | Reproducible: `python3 -m pytest` at repo root (deterministic suite; result pinned: 146 passed / 7 skipped / 0 failed) | Synthetic data only |
| OpenAPI document | API contract | `openapi/evaluations-api.json` (drift check clean; validated by `openapi_spec_validator` in RP-010) | In-repo |
| CLI demo artifact tree | Audit record + per-role transcripts | `/tmp/eval-summary-demo/evaluations/<evaluation_id>/` (local, ephemeral; 19 files incl. `council/*.json`, each sha256-stamped in CLI output) | Contains synthetic fixture content only; not committed |
| LE deferral stubs | Skipping test stubs | `tests/live_evals/test_le_stubs.py` | Pins LE-001…007 visibility in every run |
| Smoke scaffolds | Disabled-by-default scripts | `scripts/smoke_foundry_config.py`, `scripts/smoke_storage_config.py` | SKIPPED state verified this run |
| Pinned versions | Run metadata | `slice-state.yaml` `pinned_versions` block | model=none; council-composition-v1; provider contract v1 |

No sensitive transcripts exist for this batch (no model I/O occurred). No resume/cover-letter
text, prompts, or secrets appear in this summary or in any captured output (never-log
verified by DT-011 and RP-012 in the same run).

## 9. Gap and Discrepancy Flags

| ID | Description | Impact | Action Required |
|---|---|---|---|
| — | **None.** Every contract scenario is accounted for: DT-001…DT-018 executed and passed; LE-001…LE-007 skipped exactly per the contract's documented deferral; RP suite (plan §4) executed and passed; FR-014/AC-020 (CI proves itself) and AC-019 (PO plausibility review) remain manual/human evidence items per the contract's documented reasons, outside this summary's scope | — | — |

Open non-blocking items carried (unchanged from the contract): BQ-EC-001 latency-ceiling
ratification; AC-019 PO review and AC-020 CI-evidence capture remain human-gate items for
closeout; deferred ADR + BQ-005 gate the wiring slice.

## 10. Human-Review Notes

None provided for this run. Contract §11 human-review points (DT-012 flagged-output review,
AC-019 PO happy-path review, CI evidence, merge gate) remain mandatory and are **not**
satisfied or waived by this summary.

## 11. Reviewer Notes (Process Doc §19.2)

> Single-environment note: suite executed on Python 3.10.12 per the recorded plan deviation
> in `pyproject.toml` (plan targeted 3.12; behaviour unaffected, CI pins 3.10). The 7 skips
> are by-design deferral markers, not flaky or environmental skips.

## 12. Handoff Notes

**Summary status:** Complete (deterministic scope; live scope deferred per contract).

**Counts:** Total 153 collected · **Passed 146** · **Failed 0** · **Skipped 7** (LE-001…LE-007
deferral stubs) · Errors 0 · Threshold met **Yes** (deterministic 100%) · Applicability:
live evals **Required — deferred to the Foundry-wiring slice**.

**Failures present?** **No.**

**Recommended next skill:** no failures exist, so `eval-failure-classifier` is not dispatched.
Orchestrator proceeds to **Stage 12** (`current-state-reconciler`) — the RP plan §6 already
flags the "no prompt seam exists" current-state statement as stale and in this batch's
reconciliation scope. High-Assurance conditional packaging (`high-risk-human-review-packager`)
has no live results to package this batch; it applies at the wiring slice.

This summary records results only. It does **not** classify failures (none exist), does
**not** approve residual risk, does **not** accept any deferral as permanently closed, and
does **not** recommend or approve merge — merge, residual-risk acceptance, ADR approval, and
BQ-005 residency approval remain human gates.

---

## Fix-loop re-run addendum (Stage 13 BM-001) — 2026-06-11

This section is an append-only addendum; the original summary body above is unchanged and
reflects the pre-fix run.

**What was fixed:** Stage-13 documentation validation found one code gap (BM-001) —
`src/hr_eval_lab/api/app.py` now resolves the storage backend via `select_backend(config)`
instead of constructing the local backend directly, and a covering test
`test_rp005_app_factory_fails_closed_when_azure_blob_selected` was added in
`tests/test_rp002_scaffolds_and_registry.py`.

**Re-run commands (repo root, 2026-06-11):**

```
python3 -m pytest
python3 scripts/export_openapi.py --check
```

**Re-run results:**

- `python3 -m pytest`: **147 passed, 7 skipped, 0 failed** (154 collected; +1 passed vs.
  the original 146 due to the new BM-001 test; errors 0).
- `python3 scripts/export_openapi.py --check`: **clean** — "OpenAPI document matches the
  committed file (no drift)", exit code 0.

**Skip rationale (unchanged):** the 7 skips are the LE-001…LE-007 live-eval deferral stubs
in `tests/live_evals/test_le_stubs.py`, deferred to the Foundry-wiring slice exactly per
the contract's documented deferral. They are by-design markers, not flaky or environmental
skips.

**Status:** No failures exist. Nothing blocks local deterministic readiness. All human
gates noted in §12 (merge, residual-risk acceptance, ADR approval, BQ-005 residency
approval, AC-019/AC-020 evidence) remain open and are unaffected by this addendum.
