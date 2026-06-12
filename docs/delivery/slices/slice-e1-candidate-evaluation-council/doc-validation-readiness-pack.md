# Documentation Validation Report: slice-e1-candidate-evaluation-council (Azure/Foundry Readiness Pack batch)

| Field | Value |
|---|---|
| Slice ID / Branch | `slice-e1-candidate-evaluation-council` / working tree (readiness-pack batch, uncommitted) |
| Validation Date | 2026-06-11 |
| Produced By | `documentation-consistency-validator` (isolated-verification; fresh pass, did not author the docs) |
| Stage 12 Artifacts Reviewed | `implementation-notes.md` (§2 branch-diff analysis), `cloud-readiness-notes.md`, the eight durable docs listed below |
| Status | Final |

---

## Validation Scope

**Files validated:**

| File | Type | Sections reviewed |
|---|---|---|
| `docs/product-current-state/README.md` | current-state doc | all |
| `docs/product-current-state/candidate-evaluation-council.md` | current-state doc | all (§1–§21) |
| `docs/architecture/actual-technical-architecture.md` | actual architecture | all (§1–§12) |
| `docs/architecture/candidate-evaluation-council-architecture.md` | actual architecture | all (§1–§6) |
| `docs/architecture/provider-and-storage-seams.md` | actual architecture | all (§1–§5) |
| `docs/integration/README.md` | current-state (integration) | all |
| `docs/integration/copilot-studio-tool-readiness.md` | current-state (readiness, documentation-only) | all |
| `docs/integration/azure-lab-wiring-tomorrow.md` | durable integration checklist (forward-looking, placeholder-only) | all |
| `docs/delivery/slices/slice-e1-candidate-evaluation-council/cloud-readiness-notes.md` | slice-scoped (slice language allowed) | all |
| `docs/delivery/slices/slice-e1-candidate-evaluation-council/implementation-notes.md` | slice-scoped (slice language allowed) | all |

**Evidence reviewed:** working-tree `git status --short` + `git diff` (18 modified files, 25+ new paths); direct cold reads of `src/hr_eval_lab/persistence/backend.py`, `azure_blob_backend.py`, `store.py`, `providers/registry.py`, `providers/base.py`, `providers/foundry/` (all four modules), `providers/foundry_stub.py`, `providers/mock.py` (diff + docstring), `prompts/registry.py` + `prompts/templates/` (10 files verified on disk), `domain/schemas/storage.py`, `transcript.py`, `provider.py`, `request.py` (diff), `config.py`, `api/routes_evaluations.py`, `api/app.py`, `api/envelope.py`, `scripts/run_council_local.py`, `scripts/smoke_storage_config.py`, `scripts/smoke_foundry_config.py`, `infra/` (README, `bicep/main.bicep`, `env.sample`), `config/lab-config.toml` (diff), `config/azure.env.sample`, `config/role-agent-mapping.sample.json`, `openapi/evaluations-api.json`, `.github/workflows/ci.yml`, `pyproject.toml`, `.gitignore`; tests `test_rp001`–`test_rp005`, updated `test_dt002_determinism.py` / `test_dt010_mandatory_flags.py` (diffs); eval summary `eval-summary-readiness-pack.md`; deviation log `implementation-deviations.md` (DEV-R01…R07); deferred ADR `adr-deferred-foundry-wiring.md` (status header). Manual evidence: N/A. Approved ADRs: none exist (consistent with doc claims). Architecture guidelines: none exist in this repo's `docs/architecture/` tree (consistent with doc claims). GitHub Issues: none created yet (docs correctly present open items as Stage-14 issue *candidates*, not tracked issues).

**Independent re-verification performed:** `python3 -m pytest` → **146 passed, 7 skipped, 0 failed** (matches every doc citing these counts); `python3 scripts/export_openapi.py --check` → no drift; RP files in isolation → **58 passed** (matches the eval summary's count reconciliation); live behavioral probes of `create_app()` and the HTTP API (see BM-001/BM-002 evidence).

The slice spec was **not** used as a documentation authority.

---

## Blocking Mismatches

Must be resolved before Stage 14. Return to Stage 12 (`current-state-reconciler`).

| ID | File | Section | Mismatch (doc claim vs. evidence) | Evidence Gap | Required Action |
|---|---|---|---|---|---|
| BM-001 | `docs/product-current-state/candidate-evaluation-council.md` (primary); `docs/architecture/provider-and-storage-seams.md` (secondary) | §15 Configuration surface; seams doc §2 | Claim: "Selecting any `foundry_*` provider **or the `azure_blob` backend** yields only a fail-closed scaffold: … every scaffold raises (`ProviderNotConfiguredError` / `StorageNotConfiguredError`)." Seams doc §2: "Two implementations exist, **resolved by `select_backend()` from `[storage] backend` in config**." Evidence: the running application never consults `storage.backend`. `create_app()` (`src/hr_eval_lab/api/app.py:64`) constructs `LocalStore(config.persistence.root)`, and `LocalStore.__init__` defaults to `LocalFilesystemBackend`; `select_backend()` (`persistence/backend.py:195`) is referenced **only by tests** (grep: `tests/test_rp002_scaffolds_and_registry.py`). Empirically verified: `create_app(config with storage.backend="azure_blob")` starts cleanly and uses `LocalFilesystemBackend` — no `StorageNotConfiguredError` is raised. The fail-closed behavior is real and test-pinned at the *function* level (RP-005), but the documented app-level behavior ("selecting azure_blob yields a fail-closed scaffold") does not occur; the selection is silently ignored at runtime. The provider half of the sentence is accurate (`create_app` → `select_provider` → registry). | No evidence supports app-level fail-closed behavior for `storage.backend = "azure_blob"`; RP-005 tests call `select_backend()` directly, not through the app. | Correct both docs to state that `storage.backend` is a validated config key that the app factory does **not yet consult**: `create_app` always constructs the local backend; `select_backend()` exists, is fail-closed, and is test-verified, but is not wired into `create_app`. (Obvious local fix; alternatively Stage 12 may route a code-fix proposal to wire `select_backend()` into `create_app` — see follow-up candidates. Safety posture is unaffected either way: no live path exists under any configuration.) |
| BM-002 | `docs/product-current-state/candidate-evaluation-council.md` (primary); `docs/integration/copilot-studio-tool-readiness.md` (secondary) | §2 Request headers table; readiness table row "Correlation ID header" | Claim: "**Responses always carry an `X-Correlation-Id` header**: the server-assigned correlation id of the evaluation when an envelope correlation id exists, otherwise the caller-supplied value is echoed back." Evidence: the middleware (`api/app.py`) sets the header only when `request.state.correlation_id` was set by a handler **or** the caller supplied the request header. Empirically verified: a `validation_failed` (HTTP 200) response and an HTTP 400 malformed-body response, each without a caller-supplied header, carry **no** `X-Correlation-Id` header. RP-010 pins the header only on successful POST/GET. The copilot-studio doc's "returned on responses" carries the same overstatement in milder form. | Counterexamples exist; no test or code path supports "always". | Qualify the claim: the header is present when an envelope correlation id exists (completed/blocked/replayed POST, successful GET) or when the caller supplied one; early-failure responses (400/401/403, `validation_failed` envelopes without an assigned correlation id) carry it only if the caller sent one. (Obvious local wording fix in both files.) |

**Count:** 2

---

## Non-Blocking Gaps

Do not block Stage 14; should become follow-up issue candidates or wording fixes at the next reconciliation.

| ID | File | Section | Gap Description | Recommended Treatment |
|---|---|---|---|---|
| NB-001 | `docs/product-current-state/candidate-evaluation-council.md` | §15 (env guards) | "anything other than exactly `\"true\"`… disables every live Azure/Foundry path." Code (`config.py:79–86`) compares `.strip().lower() == "true"`, so `"TRUE"`, `" True "` etc. also enable. The doc understates the enabling set (impact nil — scaffolds fail closed regardless). Same wording appears in `config/azure.env.sample`'s comment. | Wording fix: "case-insensitive `true` (whitespace-trimmed)". |
| NB-002 | `docs/product-current-state/candidate-evaluation-council.md`; `docs/architecture/provider-and-storage-seams.md` | §16; §3 | Claim that the absence of "deployment names" and "real applicant data" in templates is **test-pinned**. RP-009's forbidden patterns pin GUIDs, Azure-family URLs, secret-assignment patterns, and tenant/subscription-id assignments — deployment names and applicant data are not directly pinned (both properties hold on inspection of all 10 templates). | Soften to match actual test coverage, or extend RP-009. |
| NB-003 | `docs/product-current-state/README.md` | "What the application is, at a glance" (para 2) | "All of them raise safe configuration errors on any use, are blocked by server-side environment guards" sweeps the **placeholder-only `infra/` skeleton** into a list of components that "raise" and are "blocked by guards" — `infra/` is documentation and raises nothing; and the blob scaffold's guard exposure is overstated given BM-001 (it is reachable only via direct construction, not via the app). | Tighten the collective claim once BM-001 is corrected. |
| NB-004 | `docs/integration/azure-lab-wiring-tomorrow.md` | Title context, §0, §7 | Future-slice phrasing in a durable integration doc ("the live Azure/Foundry wiring slice", "the wiring slice's risk profile"). The doc is explicitly forward-looking and placeholder-only, so this is not the blocking slice-history pattern ("Slice N added…"), but durable docs should stay slice-structure-agnostic. | Rephrase to "future live-wiring work" / "at wiring time". |

**Count:** 4

---

## Observations

| ID | File | Section | Observation |
|---|---|---|---|
| OB-001 | (evidence) | — | Eval evidence independently reproduced this validation run: 146 passed / 7 skipped / 0 failed; OpenAPI drift check clean; 58 RP tests pass in isolation. Every doc citing these numbers is accurate. |
| OB-002 | all validated docs | — | ADR cross-references are consistent everywhere: the Foundry-wiring ADR is presented as **draft, NOT approved** in all ten documents and in the ADR file itself; BQ-005 is consistently presented as a pending human gate. No doc presents any ADR as approved. |
| OB-003 | `infra/`, `config/*.sample*`, `prompts/templates/` | — | Independently scanned: no GUIDs, no real endpoints, no key/connection-string/SAS material anywhere; placeholders only (`<...>` / `TODO-...`); `allowSharedKeyAccess: false` in the Bicep placeholder. Matches the docs' no-secrets and identity-first claims. |
| OB-004 | `docs/product-current-state/candidate-evaluation-council.md` | §19 | "the **newer** surfaces" is mild temporal phrasing in a current-state doc (relative to an implied change history). Not the blocking slice-language pattern; suggest dropping "newer". |
| OB-005 | `docs/product-current-state/candidate-evaluation-council.md` | §11 | "Writes are append-only": the JSONL tables are append-mode; record/artifact writes are write-once-per-unique-evaluation-id (`write_text`), i.e. append-only by construction rather than by mechanism. Informational. |
| OB-006 | `implementation-deviations.md`, `implementation-notes.md`, `cloud-readiness-notes.md` | — | Slice-scoped artifacts verified accurate against code: DEV-R01 (record path move, DT-002/DT-010 diffs match), DEV-R02 (`idempotency_key` now `Optional`, header equivalence implemented exactly as described), DEV-R03 (`CouncilRoleInvocation` carries the contract fields), DEV-R04 (idempotency not on the ABC), DEV-R05 (`foundry_stub.py` retained, unreachable via `select_provider`), DEV-R06 (recorded-not-executed prompts, mock stamps template id/version), DEV-R07 (wiring doc produced at Stage 12). Cloud-readiness classification (ready / scaffold / deferred) matches code and tests. |
| OB-007 | `docs/product-current-state/candidate-evaluation-council.md` | §21 | The honest limitation that summary-row `provider_id` is derived (`deterministic_mock` vs `foundry_unresolved`) exactly matches `persistence/store.py:155` — a model example of limitation classification. |

---

## Architecture-Specific Findings

**Only-built-components:** every component listed in `actual-technical-architecture.md` was verified present in the working tree: provider registry + three `foundry/` scaffolds + legacy stub; `StorageBackend` ABC + `LocalFilesystemBackend` + `AzureBlobBackend` scaffold; prompt registry + 10 `v1` templates; `storage.py`/`transcript.py` schemas; correlation middleware; demo + smoke scripts; `infra/` skeleton; config samples. **No component is listed that was not built.** The §11 "What is NOT built" list is accurate and complete. **Pass**, with the caveat that the seams doc's description of *how* the storage backend is resolved at runtime is wrong (BM-001).

**Guideline consistency:** no architecture guideline documents and no approved ADRs exist in this repo's `docs/architecture/` tree — exactly as both architecture docs state. No guideline gap requiring an ADR was found. **Pass.**

**Manual-configuration components:** none exist (nothing deployed, no portal configuration); the docs say so and `source-control-config-capture.md` exists for the batch. Open items (foundry_stub retirement, run-time provider_id recording, retention decisions) are correctly presented as Stage-14 issue candidates, not as tracked/complete. **Pass.**

**ADR cross-reference accuracy:** see OB-002. **Pass.**

---

## Slice-Language Check

| File | Slice-Specific Language Found? | Finding |
|---|---|---|
| `docs/product-current-state/README.md` | No (slice folder referenced only as repository structure / source-of-truth hierarchy) | Pass |
| `docs/product-current-state/candidate-evaluation-council.md` | No ("newer surfaces" noted as OB-004; ADR referenced by path only) | Pass |
| `docs/architecture/actual-technical-architecture.md` | No (ADR path reference only) | Pass |
| `docs/architecture/candidate-evaluation-council-architecture.md` | No | Pass |
| `docs/architecture/provider-and-storage-seams.md` | No (ADR path references only) | Pass |
| `docs/integration/README.md` | No (ADR path reference only) | Pass |
| `docs/integration/copilot-studio-tool-readiness.md` | No | Pass |
| `docs/integration/azure-lab-wiring-tomorrow.md` | Future-slice phrasing (NB-004) | Non-blocking gap |
| slice-scoped docs (`cloud-readiness-notes.md`, `implementation-notes.md`) | Slice language allowed by charter | Pass |

No instance of the blocking patterns ("Slice N added…", "This branch implemented…", "The next slice will…") exists in any current-state or architecture doc.

---

## Suggested Follow-Up Issue Candidates

For `github-issue-drafter` at Stage 14 (creation is a human gate).

| Item | From Finding | Suggested Type | Priority |
|---|---|---|---|
| Wire `select_backend()` into `create_app` (or remove/justify the unused selector) so `storage.backend = "azure_blob"` actually fails closed at app start as intended, with an RP-level test through the app factory | BM-001 | source-control-debt / code-gap | High |
| Decide and pin (test) `X-Correlation-Id` behavior on early-failure responses (400/401/403, envelope-less `validation_failed`) | BM-002 | documentation-gap / code-gap | Medium |
| Extend RP-009 forbidden-pattern coverage or soften the doc claim (deployment names, applicant data) | NB-002 | documentation-gap | Low |
| Existing candidates already recorded by Stage 12 (retire `foundry_stub.py`; record concrete `provider_id` in summary rows at run time; cloud retention/concurrency/cleanup decisions) | OB-006 | as recorded | per Stage 14 |

---

## Validation Recommendation

**Recommendation:** **FAIL — return to Stage 12**

**Rationale:** Two blocking mismatches — both false claims about current behavior in current-state/architecture documentation: (BM-001) the docs state that selecting the `azure_blob` storage backend yields a fail-closed configuration error, but the running application never consults `storage.backend` and silently uses the local filesystem backend (empirically verified); (BM-002) the docs state responses *always* carry an `X-Correlation-Id` header, but early-failure responses without a caller-supplied header carry none (empirically verified). Both corrections are small and local; everything else validated cleanly — the documentation set is otherwise unusually accurate, evidence-grounded (146/7/0 reproduced, drift clean), free of slice language in durable docs, consistent on the unapproved-ADR/human-gate posture, and honest about scaffolds, limitations, and never-log guarantees. Neither blocking item affects the safety posture (no live call is possible under any configuration); they affect documentation accuracy only.

---

## Handoff

**FAIL path:** return to Stage 12 — `current-state-reconciler` must correct BM-001 (both files) and BM-002 (both files), optionally sweeping NB-001…NB-004 in the same pass, then re-run Stage 13. Do not advance to Stage 14 until Stage 13 passes on re-run. No documentation was rewritten by this validation; findings only.

---

## Delta re-validation (post fix loop) — 2026-06-11

Performed by a fresh, independent `documentation-consistency-validator` run (isolated-verification; did not author the docs or the fixes). Scope: only the artifacts touched by the Stage-13 fix loop — `src/hr_eval_lab/api/app.py`, `tests/test_rp002_scaffolds_and_registry.py`, `docs/product-current-state/candidate-evaluation-council.md`, `docs/product-current-state/README.md`, `docs/architecture/provider-and-storage-seams.md`, `docs/integration/copilot-studio-tool-readiness.md`, `docs/integration/azure-lab-wiring-tomorrow.md`, `config/azure.env.sample`, `implementation-deviations.md` (DEV-R08), `eval-summary-readiness-pack.md` (addendum). The original report body above is unchanged.

### Independent re-verification performed

- `python3 -m pytest tests/test_rp002_scaffolds_and_registry.py` → **15 passed, 0 failed** (includes the new `test_rp005_app_factory_fails_closed_when_azure_blob_selected`).
- `python3 -m pytest` (full suite) → **147 passed, 7 skipped, 0 failed** — matches DEV-R08 and the eval-summary addendum exactly (+1 vs. the original 146, the new BM-001 pin).
- `python3 scripts/export_openapi.py --check` → clean, no drift (exit 0).
- **Live behavioral probe (BM-001):** `create_app(config with storage.backend="azure_blob", no azure config)` now raises `StorageNotConfiguredError` at app construction ("azure_blob backend selected without configuration: missing storage.azure.account_url, …"). Default config still constructs `LocalFilesystemBackend` — the local path is undisturbed.
- Cold reads of every changed code/doc section listed above; re-read of RP-009's `FORBIDDEN_PATTERNS` (`tests/test_rp003_prompt_registry.py:19–25`) to re-check the NB-002 claim; slice-language regex sweep across `docs/product-current-state/`, `docs/architecture/`, `docs/integration/` → no blocking pattern anywhere.

### Fixes verified, per finding ID

| ID | Resolution route | Verified? | Evidence |
|---|---|---|---|
| BM-001 | **Code fix** (the report's noted alternative): `create_app` (`api/app.py:68`) now constructs `LocalStore(config.persistence.root, backend=select_backend(config))`, so `[storage] backend` is consulted at app construction and `azure_blob` fails closed. | **Yes** | New pinning test passes through the app factory; empirical probe raises `StorageNotConfiguredError`; lazy-Azure-import pin (`test_rp005_no_azure_imports_on_local_path`) still passes; the previously-overclaiming doc sentences (current-state §15, seams §2 "resolved by `select_backend()`") are now **true against code** as written — no doc edit was needed for the primary claim. |
| BM-002 | **Doc fix**: both files qualified. | **Yes** | `candidate-evaluation-council.md` §2 header table and `copilot-studio-tool-readiness.md` "Correlation ID header" row now state the header is present when an envelope correlation id exists or the caller supplied one, and that early-failure responses (400/401/403, envelope-less `validation_failed`) carry it only if the caller sent one — this matches the middleware (`api/app.py:89–97`) exactly. No "always" overclaim remains in any durable doc. |
| NB-001 | Doc fix in all three locations. | **Yes** | `candidate-evaluation-council.md` §15, `provider-and-storage-seams.md` §2 guard bullet, and `config/azure.env.sample` comment all now read case-insensitive / whitespace-trimmed `"true"` — matches `config.py` (`.strip().lower() == "true"`). |
| NB-002 | Doc fix (primary location). | **Partially** | `candidate-evaluation-council.md` §16 now correctly states deployment names / real applicant data are "maintained by review convention … rather than by a dedicated test pattern" — accurate against RP-009. **Residual:** `provider-and-storage-seams.md` §3 (lines 192–194) still lists "real applicant data" inside the test-pinned claim; RP-009's patterns pin GUIDs, non-example Azure/Microsoft URLs, secret-assignment keys, tenant/subscription-id assignments, and `AccountKey=` — none pins applicant data. See NB-002-R below. |
| NB-003 | Doc fix. | **Yes** | `docs/product-current-state/README.md` now separates the components: the four scaffolds "raise safe configuration errors on any use", while "the `infra/` skeleton is placeholder documentation only and executes nothing". The guard-blocked selection claim is now accurate for storage too, given the BM-001 code fix. |
| NB-004 | Doc fix. | **Yes** | `azure-lab-wiring-tomorrow.md` now uses "future live Azure/Foundry wiring" / "wiring day" / "at wiring time"; no "wiring slice" phrasing remains in any durable doc (the surviving instances are in slice-scoped artifacts, where slice language is allowed by charter). |
| DEV-R08 | Deviation record. | **Yes** | `implementation-deviations.md` Stage-13 fix-loop addendum accurately describes the code fix, the new test, and the 147/7/0 count; correctly notes BM-002/NB-001..NB-004 were wording-only. |
| Eval addendum | Append-only addendum. | **Yes** | `eval-summary-readiness-pack.md` "Fix-loop re-run addendum" leaves the original body intact, states the pre-fix body reflects the pre-fix run, and its re-run numbers (147/7/0; drift clean) were independently reproduced this pass. |

### Remaining / new findings

| ID | File | Section | Finding | Classification |
|---|---|---|---|---|
| NB-002-R | `docs/architecture/provider-and-storage-seams.md` | §3 (prompt registry bullet, lines 192–194) | Residual half of NB-002: "Test-pinned, along with the absence of secrets/endpoints/tenant or subscription identifiers/**real applicant data** in any template" — RP-009 has no applicant-data pattern; that absence holds on inspection but is review-convention, not test-pinned. ("Deployment names" was correctly removed.) Mirror the corrected §16 wording from `candidate-evaluation-council.md`, or extend RP-009. | **Non-blocking gap** |

No new inaccuracies, no new slice language, and no overclaims were introduced by the fix loop. Spot-checks of the untouched portions of the fix-loop files (correlation middleware behavior, AzureBlobBackend §11 description, request-header table's idempotency row, README source-of-truth hierarchy, copilot-readiness table's other rows) found the prior PASS-validated content undisturbed.

### Final recommendation

**CONDITIONAL-PASS**

Both blocking mismatches are resolved and empirically verified (BM-001 by code fix with an app-factory-level pinning test; BM-002 by accurate qualification in both files). One non-blocking gap remains (NB-002-R, a one-line wording overclaim in the seams doc's test-pinning list — improvable but not false in substance, and identical in character to the original non-blocking NB-002). Per the skill's recommendation rules, no blocking mismatches plus noted non-blocking gaps → CONDITIONAL-PASS: **advance to Stage 14**, carrying NB-002-R forward as a follow-up issue candidate (wording fix or RP-009 pattern extension) alongside the candidates already listed above.
