# Traceability Matrix — Azure/Foundry Readiness Pack batch (slice-e1)

> **Partial Stage 14 artifact** (`traceability-and-closeout-agent`, `traceability-matrix-builder` skill), 2026-06-11.
> Scope is **only** this traceability matrix for the readiness-pack coding batch, on explicit
> orchestrator instruction. This artifact does **not** include a closeout package, does **not**
> run definition-of-done, creates **no** GitHub Issues, and makes **no** statement about merge.
> Nothing has been merged; **no human gate has been passed**. Full closeout (Stages 14–16)
> remains to be run.

## 1. Metadata and inputs

| Field | Value |
|---|---|
| Slice | `slice-e1-candidate-evaluation-council` — Azure/Foundry readiness pack coding batch (layered on the completed local deterministic baseline batch) |
| Spec of record | [`slice-spec.md`](./slice-spec.md) (post-deviation; deviations in [`deviation-log.md`](./deviation-log.md) DEV-001..006 and [`implementation-deviations.md`](./implementation-deviations.md) DEV-R01..R08) |
| Eval contract | [`eval-contract.md`](./eval-contract.md) (`EC-slice-e1-candidate-evaluation-council-001`, hardened: DT-001..DT-018, LE-001..LE-007 deferred) |
| Test evidence | [`eval-summary-readiness-pack.md`](./eval-summary-readiness-pack.md): pre-fix run 146 passed / 7 skipped / 0 failed; **post fix-loop addendum: 147 passed / 7 skipped / 0 failed**, OpenAPI drift clean. Independently reproduced by the Stage-13 delta re-validation ([`doc-validation-readiness-pack.md`](./doc-validation-readiness-pack.md), CONDITIONAL-PASS) |
| Implementation summary | [`implementation-notes.md`](./implementation-notes.md); plan: [`implementation-plan-readiness-pack.md`](./implementation-plan-readiness-pack.md) (T1–T9, RP test plan §4) |
| Architecture check | [`architecture-check-readiness-pack.md`](./architecture-check-readiness-pack.md) — verdict Clear; C-COND-1/C-COND-2 standing; G-001 unchanged (deferred ADR) |
| Open GitHub Issues | **None — verified.** Greenfield repo; no issue numbers are referenced anywhere in the docs tree (checked), and all open items are presented as *candidates*, consistent with the doc-validation finding. No issue numbers appear in this matrix; deferred/unresolved rows cite the artifact where the item is tracked instead. |
| Live eval applicability | Required for this capability, **deferred to the Foundry-wiring slice** with documented rationale (eval contract §1/§7; eval summary §6). Per the skill rule that agent-behaviour items need live evals: every agent-behaviour item below therefore carries the deferral reference — deterministic coverage alone is not treated as full behavioural proof. |

**Input caveats:** none — all eight required skill inputs were available (manual evidence: N/A,
nothing manual was configured; `source-control-config-capture.md` exists for the batch).
**NB-002-R verification (orchestrator request):** the residual wording overclaim in
`docs/architecture/provider-and-storage-seams.md` §3 is **fixed** — the prompt-registry bullet
now states the absence of real applicant data "is maintained by review convention … rather than
by a dedicated test pattern," consistent with `candidate-evaluation-council.md` §16. Verified by
direct read this pass.

---

## 2. Section A — Slice-spec acceptance criteria (AC-001..AC-020)

Statuses are **unchanged from the baseline batch**. The readiness pack touched some AC surfaces
(noted per row); no coverage was weakened — the full DT suite re-ran green after every change
(147/7/0). Evidence citations are the covering test IDs/files plus the eval-summary run record.

| AC | Status | Evidence (specific) | Readiness-pack touch (no weakening) |
|---|---|---|---|
| AC-001 | **Covered** | DT-001 `tests/test_dt001_happy_path.py`; eval summary §3b (100% pass) | — |
| AC-002 | **Covered** | DT-001/DT-009 (`test_actor_identity_and_role_context_persisted` in `tests/test_dt009_authorization.py`) | Record is now also projected to per-artifact files (`council/{role}.json` etc.) — additive; record stays single source of truth (T5; `test_rp014_council_transcripts_validate`) |
| AC-003 | **Covered** | DT-002 `tests/test_dt002_determinism.py::test_two_identical_runs_byte_identical_after_normalization` | Record path moved to `evaluations/{id}/record.json` (DEV-R01); DT-002 updated to the new path, assertion semantics unchanged, re-run green |
| AC-004 | **Covered** | DT-003 `tests/test_dt003_rigor_resolver.py` | — |
| AC-005 | **Covered** | DT-003, DT-004 `tests/test_dt004_escalation_matrix.py` | — |
| AC-006 | **Covered** | DT-004 (escalated/Mode C role-set assertions) | — |
| AC-007 | **Covered** | DT-004, DT-005 `tests/test_dt005_triggers.py` | — |
| AC-008 | **Covered** | DT-004 (both BR-005 branches asserted; implemented choice explicit) | — |
| AC-009 | **Covered** | DT-005 (one crafted scenario per trigger, 6/6) | — |
| AC-010 | **Covered** | DT-006 `tests/test_dt006_gates.py` (per-gate pass+fail fixtures, bounded-retry path) | — |
| AC-011 | **Covered** | DT-007 `tests/test_dt007_status_vocabulary.py`; DT-009 (`unauthorized` on POST and GET) | — |
| AC-012 | **Covered** | DT-008 `tests/test_dt008_idempotency.py` (unchanged) | `Idempotency-Key` header added as **additive** equivalent (DEV-R02); body field stays canonical; pinned by `test_rp011_*` (4 tests in `tests/test_rp004_openapi_and_headers.py`) |
| AC-013 | **Covered** | DT-010 `tests/test_dt010_mandatory_flags.py` (both tests) | Path-updated for DEV-R01 (semantics unchanged); invariant extended to new surfaces by `test_rp015_mandatory_flags_in_new_surfaces` |
| AC-014 | **Covered** | DT-011 `tests/test_dt011_never_log.py` | Never-log extended to the new metadata summary rows (`test_rp004_metadata_summary_is_text_free`) and CLI stdout (`test_rp012_cli_local_run_writes_artifacts_and_safe_stdout`) |
| AC-015 | **Partial** | Deterministic half: DT-012 `tests/test_dt012_injection.py` (pass). **Human review of the flagged output not yet recorded** — mandatory, unsatisfied (eval summary §10; eval contract §11). Tracked there as a closeout human-gate item; no issue number exists (greenfield) | — |
| AC-016 | **Covered** | DT-013 `tests/test_dt013_mock_parity.py` | `ProviderMetadata` extended (template id/version, `model_or_agent_ref`, `warnings`, `safe_error`); mock conformance pinned by `test_rp008_mock_conforms_to_extended_provider_contract`; DT-013 still green |
| AC-017 | **Covered** | DT-014 `tests/test_dt014_openapi.py`; drift check clean (`scripts/export_openapi.py --check`, eval summary addendum) | OpenAPI regenerated with operation IDs + headers; formal spec validation added (`test_rp010_openapi_parses_and_validates`, openapi-spec-validator) — coverage strengthened |
| AC-018 | **Covered** | DT-018 `tests/test_dt018_cli_facade_only.py` | New demo script `scripts/run_council_local.py` follows the same facade-only discipline, pinned by `test_rp012_cli_local_run_writes_artifacts_and_safe_stdout`; CLI demo run recorded in eval summary §3d |
| AC-019 | **Untested — pending human evidence** | PO plausibility review by design (eval contract §15: "human-judgment criterion by design"). Not yet performed (eval summary §9/§10). Tracked in eval contract §11/§15 as a closeout human item; no issue number exists | — |
| AC-020 | **Untested — pending manual evidence** | CI workflow exists (`.github/workflows/ci.yml`) but the required evidence (green run link + failure-fails demonstration) is not yet captured (eval contract §15: "CI cannot test itself"; eval summary §9). Tracked in eval contract §15 as a closeout manual-evidence item | — |

Agent-behaviour note (skill quality bar): AB-001..AB-008 deterministic coverage is per eval
contract §15 (DT-006/012/015/016/017 etc., all green); their live-eval dimension is **deferred
with documented rationale** to LE-001..LE-007 (Section C) — deterministic tests are not claimed
as sufficient behavioural proof.

---

## 3. Section B — Readiness-pack targets T1..T9

All RP tests cited below passed in the 147/7/0 run (eval summary §3a/§3b + fix-loop addendum;
independently reproduced by doc validation, including 58 RP tests in isolation pre-fix).

| Target | Implemented code/module paths | Covering RP tests (exact names) | Docs updated | Status |
|---|---|---|---|---|
| **T1 — Domain data model** (harden, additive) | `src/hr_eval_lab/domain/schemas/storage.py` (new: `StorageArtifactRef`, `RecordSummaryRow`), `transcript.py` (new: `CouncilRoleInvocation`), `provider.py` (extended `ProviderMetadata`), `request.py` (`idempotency_key` now Optional, DEV-R02) | `test_rp001_domain_roundtrip_is_deterministic`, `test_rp001_backend_roundtrip_and_artifact_layout`, `test_rp002_source_hash_provenance_in_record_and_summary` (all in `tests/test_rp001_storage_backend.py`) | `docs/architecture/actual-technical-architecture.md`, `docs/architecture/candidate-evaluation-council-architecture.md` | **Covered** |
| **T2 — Storage boundary + Azure scaffold** | `src/hr_eval_lab/persistence/backend.py` (`StorageBackend` ABC + `LocalFilesystemBackend` + `select_backend`), `azure_blob_backend.py` (fail-closed scaffold), `store.py` (delegation, artifact tree, summary rows); app-level wiring `src/hr_eval_lab/api/app.py` (`select_backend(config)` — DEV-R08/BM-001 fix) | `test_rp001_backend_roundtrip_and_artifact_layout`, `test_rp004_metadata_summary_is_text_free` (`tests/test_rp001_storage_backend.py`); `test_rp005_no_azure_import_on_default_path`, `test_rp005_azure_blob_selected_without_config_fails_closed`, `test_rp005_azure_blob_configured_but_live_disabled_fails_closed`, `test_rp005_app_factory_fails_closed_when_azure_blob_selected` (`tests/test_rp002_scaffolds_and_registry.py`) | `docs/architecture/provider-and-storage-seams.md`, `docs/product-current-state/candidate-evaluation-council.md` §11/§15 | **Covered** |
| **T3 — Provider registry + guards** | `src/hr_eval_lab/providers/registry.py` (4 provider IDs, mock default), `providers/foundry/{project_responses,prompt_agent,hosted_agent}.py` (fail-closed scaffolds), `providers/base.py`, `config.py` (guards `HRHA_ENABLE_LIVE_AZURE`, `HRHA_PROVIDER_KILL_SWITCH`; `provider_id`/`ai_backend_type` consistency validation); legacy `providers/foundry_stub.py` retained-unreachable (DEV-R05) | `test_rp006_default_provider_is_mock_without_foundry_imports`, `test_rp006_unknown_provider_fails_safely`, `test_rp006_inconsistent_backend_family_rejected`, `test_rp006_foundry_ids_blocked_while_live_disabled`, `test_rp007_kill_switch_blocks_foundry_even_with_live_enabled`, `test_rp007_scaffolds_fail_closed_on_use` (`tests/test_rp002_scaffolds_and_registry.py`) | `docs/architecture/provider-and-storage-seams.md` (two-value enum claim removed), current-state §15; enumeration recorded option-neutrally as input to the deferred ADR (architecture check finding 4) | **Covered** |
| **T4 — Versioned prompt registry** | `src/hr_eval_lab/prompts/registry.py` + `prompts/templates/<role_id>.v1.md` (10 roles, verified on disk); templates **recorded, not executed** (DEV-R06) — mock stamps template id/version into `ProviderMetadata` | `test_rp009_all_required_roles_registered`, `test_rp009_every_template_contains_every_mandatory_constraint`, `test_rp009_no_secrets_or_live_identifiers_in_templates`, `test_rp009_unknown_role_and_version_fail_safely` (`tests/test_rp003_prompt_registry.py`); provenance stamping: `test_rp008_mock_conforms_to_extended_provider_contract` | Seams doc §3 ("no prompt seam exists" stale claim removed; NB-002-R wording fix verified); current-state §16 | **Covered** |
| **T5 — Council transcripts** | `src/hr_eval_lab/domain/schemas/transcript.py`; projection at persistence time in `persistence/store.py` (artifact tree `council/{role}.json` + 8 other projections; record = single source of truth) | `test_rp014_council_transcripts_validate`, `test_rp015_mandatory_flags_in_new_surfaces` (`tests/test_rp001_storage_backend.py`); CLI demo evidence: 19 artifacts incl. per-role transcripts (eval summary §3d) | Current-state §11; architecture docs | **Covered** |
| **T6 — OpenAPI/Copilot readiness** | `src/hr_eval_lab/api/routes_evaluations.py`, `api/app.py` (correlation middleware), `api/envelope.py`; regenerated `openapi/evaluations-api.json` (operation IDs `submitEvaluation`/`getEvaluation`, `X-Correlation-Id`, `Idempotency-Key`) | `test_rp010_openapi_parses_and_validates`, `test_rp010_stable_operation_ids_present`, `test_rp010_headers_documented`, `test_rp010_request_schema_exposes_no_backend_selection`, `test_rp010_correlation_header_on_responses`, `test_rp011_header_only_idempotency_key`, `test_rp011_header_body_mismatch_is_http_400`, `test_rp011_missing_both_keys_is_http_400`, `test_rp011_matching_header_and_body_accepted` (`tests/test_rp004_openapi_and_headers.py`); drift check clean | New `docs/integration/copilot-studio-tool-readiness.md` (registration-readiness only, BM-002 wording corrected); `docs/integration/README.md` | **Covered** |
| **T7 — CLI demo + smoke scripts** | `scripts/run_council_local.py` (facade-only, safe stdout); `scripts/smoke_foundry_config.py`, `scripts/smoke_storage_config.py` (disabled by default, double-guarded `HRHA_ENABLE_LIVE_AZURE=true` + `--live`, no SDK import/no network when disabled) | `test_rp012_cli_local_run_writes_artifacts_and_safe_stdout`, `test_rp013_smoke_foundry_disabled_by_default`, `test_rp013_smoke_foundry_live_flag_alone_is_still_skipped`, `test_rp013_smoke_foundry_live_fails_safely_without_config`, `test_rp013_smoke_foundry_respects_kill_switch`, `test_rp013_smoke_storage_disabled_by_default`, `test_rp013_smoke_storage_live_fails_safely_without_config` (`tests/test_rp005_cli_and_smoke.py`); live runs of all three scripts recorded in eval summary §3a (exit 0, SKIPPED live paths) | Current-state §15; `docs/integration/azure-lab-wiring-tomorrow.md` (placeholder checklist, DEV-R07) | **Covered** |
| **T8 — Infra skeleton (placeholders only, NO deploy)** | `infra/README.md`, `infra/bicep/main.bicep`, `infra/parameters.sample.json`, `infra/env.sample` | **No executable behaviour by design** — documentation-grade placeholders; nothing to test. Verification evidence: independent doc-validation scan OB-003 (no GUIDs, no real endpoints, no key/SAS material, `allowSharedKeyAccess: false`) and architecture check finding 11 (Compliant) | `infra/README.md` itself; current-state README (corrected per NB-003: infra "executes nothing") | **Untestable (by design)** — non-blocking; see gap list |
| **T9 — Config samples** | `config/lab-config.toml` (`[provider] provider_id`, `[storage]`/`[storage.azure]`), `config/azure.env.sample`, `config/role-agent-mapping.sample.json`; validation in `src/hr_eval_lab/config.py` | `test_rp006_inconsistent_backend_family_rejected` (config family validation); `test_rp005_azure_blob_selected_without_config_fails_closed` (placeholder keys insufficient by design); no-secrets posture: doc-validation OB-003 scan; capture record: [`source-control-config-capture.md`](./source-control-config-capture.md) | Current-state §15; seams doc §2 (guard semantics, NB-001 wording fixed) | **Covered** |

---

## 4. Section C — Deferred live Azure/Foundry items

Per the skill rules, deferred rows carry the **deferral reference**, never an invented issue
number. All of these gate the future live-wiring work only; none blocks the local deterministic
batch.

| Item | Status | Deferral rationale / where tracked |
|---|---|---|
| LE-001 grounded advisory output (live) | **Deferred** | Eval contract §7 ("live eval not applicable until Foundry wiring"); visible-in-every-run stub `tests/live_evals/test_le_stubs.py::test_le_001_grounded_advisory_output` (skips with the contract rationale); eval summary §6 |
| LE-002 confidence calibration / decision language | **Deferred** | Same; stub `test_le_002_confidence_calibration_and_decision_language` |
| LE-003 fairness trap (safety-critical) | **Deferred** | Same; stub `test_le_003_fairness_trap_resistance`; stricter zero-critical threshold carried unweakened (eval contract §10) |
| LE-004 injection trap (safety-critical) | **Deferred** | Same; stub `test_le_004_prompt_injection_resistance_live` |
| LE-005 missing-document discipline | **Deferred** | Same; stub `test_le_005_missing_evidence_discipline_live` |
| LE-006 disagreement/role adherence | **Deferred** | Same; stub `test_le_006_council_role_adherence_live` |
| LE-007 adversarial request-surface injection (added Stage 4) | **Deferred** | Same; stub `test_le_007_adversarial_rigor_downgrade_live` |
| Foundry-wiring ADR (live runtime choice, final provider-ID enumeration, live trace/eval metadata semantics) | **Deferred — draft, NOT approved** | [`adr-deferred-foundry-wiring.md`](./adr-deferred-foundry-wiring.md) (status header: "Deferred — Draft. NOT APPROVED. Requires human approval before any live Foundry wiring begins"); PO decision slice spec §2.2.2; architecture check G-001 |
| BQ-005 Canadian-region/residency approval | **Deferred — pending mandatory human gate** | Slice spec §2.2.3 / §14; eval summary §6; [`cloud-readiness-notes.md`](./cloud-readiness-notes.md) §3 |
| Live Azure storage wiring (`AzureBlobBackend` operations; JSONL table-equivalents incl. idempotency → Azure Tables, per DEV-R04) | **Deferred** | `cloud-readiness-notes.md` §2/§4; `docs/integration/azure-lab-wiring-tomorrow.md`; fail-closed posture pinned today by `test_rp005_*` |
| Live Foundry provider wiring (any live call, token spend, Entra identity, Copilot Studio registration, hosted endpoint) | **Deferred** | `cloud-readiness-notes.md` §3; gated on the deferred ADR + BQ-005; guards pinned by `test_rp006_*`/`test_rp007_*`/`test_rp013_*`; zero live calls verified (eval summary §7: live token spend 0) |

---

## 5. Coverage summary

Counts across Sections A (20 ACs), B (9 targets), C (11 deferred items). Percentage is
informational, not a gate (Process §24).

| Status | Count | Items |
|---|---|---|
| Covered | **25** | AC-001..AC-014, AC-016..AC-018 (17); T1..T7, T9 (8) |
| Partial | **1** | AC-015 (deterministic pass; mandatory human review of flagged output pending) |
| Untested (pending human/manual evidence) | **2** | AC-019 (PO plausibility review), AC-020 (CI evidence capture) |
| Untestable (by design, non-blocking) | **1** | T8 infra skeleton (placeholder documentation; independently scanned) |
| Deferred (documented, human-gated) | **11** | LE-001..LE-007, deferred Foundry-wiring ADR, BQ-005, live storage wiring, live provider wiring |

Deterministic evidence basis: 147 passed / 7 skipped / 0 failed (the 7 skips are exactly the
LE deferral stubs); 100% pass on every executed test, meeting the High-Assurance deterministic
threshold (eval summary §4 + addendum).

## 6. Gap list

Every non-Covered item, with blocking assessment for this batch's scope:

| Item | Why not Covered | Blocking for this batch? | Treatment |
|---|---|---|---|
| AC-015 human-review half | Flagged-injection output review is a mandatory human action not yet performed | No (deterministic half green) — **must be closed at full Stage 14–16 closeout** | Tracked in eval contract §11; closeout human-gate item |
| AC-019 | Human-judgment criterion by design; PO review not yet performed | No — closeout human-gate item | Eval contract §15 documented reason; PO review at closeout |
| AC-020 | CI evidence (green-run link + failure-fails demonstration) not yet captured | No — closeout manual-evidence item | Eval contract §15 documented reason |
| T8 infra skeleton | No executable behaviour to test (placeholders by design) | No | Independent scan evidence recorded (doc-validation OB-003); human review occurs at the wiring gate |
| LE-001..LE-007 + ADR + BQ-005 + live wiring | Documented deferral; human gates unpassed | No (gate the wiring work only) | Section C references; carried forward unweakened |

No coverage gap requires returning to an earlier stage: the deterministic suite fully covers
every executable item, the deferrals are documented in the hardened eval contract, and the
remaining items are human/manual evidence actions that belong to the (not yet run) full
closeout.

---

## 7. Issue candidates — DRAFT ONLY (consolidated, deduplicated)

Consolidated from [`implementation-notes.md`](./implementation-notes.md) §5,
[`doc-validation-readiness-pack.md`](./doc-validation-readiness-pack.md) follow-up table +
NB-002-R, [`cloud-readiness-notes.md`](./cloud-readiness-notes.md) §4, and DEV-R05. The
doc-validation BM-001 candidate ("wire `select_backend()` into `create_app`") is **resolved**
— fixed in code during the Stage-13 fix loop (DEV-R08, pinning test
`test_rp005_app_factory_fails_closed_when_azure_blob_selected`) and is therefore *not* carried
as a candidate (no issue references for completed items).

| # | Draft candidate | Type | Source(s) | Priority |
|---|---|---|---|---|
| IC-1 | Retire/remove legacy `providers/foundry_stub.py` at the wiring slice (retained-unreachable today) | source-control-debt | DEV-R05; implementation-notes §5; cloud-readiness §4 | Low |
| IC-2 | Record the concrete `provider_id` in `RecordSummaryRow` from config at run time (today derived `deterministic_mock` vs `foundry_unresolved` in `persistence/store.py`) | technical-debt | implementation-notes §5; cloud-readiness §4; doc-validation OB-007 | Low |
| IC-3 | Decide and test-pin `X-Correlation-Id` behaviour on early-failure responses (400/401/403, envelope-less `validation_failed`) — docs now accurately describe the current conditional behaviour; the open item is whether to make the header unconditional | code-gap / decision | doc-validation BM-002 follow-up candidate (doc half already fixed) | Medium |
| IC-4 | Extend RP-009 forbidden-pattern coverage to applicant-data/deployment-name patterns, or formally keep the documented review-convention note (NB-002-R wording is now consistent in both docs; the candidate is the test-extension decision) | test-gap / documentation | doc-validation NB-002 + NB-002-R | Low |
| IC-5 | Cloud retention / concurrency / cleanup decisions for the blob storage backend (no behaviour exists today; needed before live storage wiring) | decision / technical-debt | implementation-notes §5; cloud-readiness §4; slice spec §14 (retention deferred, non-blocking) | Medium |

> **Awaiting human approval — no issues created.** The candidates above are drafts for
> `github-issue-drafter` and require explicit human approval before any GitHub Issue is
> created. No issue numbers exist or are referenced anywhere in this matrix (the repo has
> zero open issues — verified).

---

## 8. Closing statement

This matrix records traceability only. It does not approve closeout, does not waive any gap,
does not accept residual risk, and makes no merge recommendation. **Full closeout — Stage 14
(issue drafting + closeout package), Stage 15 (definition-of-done validation), and the Stage 16
human gate — remains to be run.** Open human gates at this point: deferred Foundry-wiring ADR
approval, BQ-005 residency approval, AC-015 flagged-output review, AC-019 PO review, AC-020 CI
evidence, issue-creation approval, residual-risk acceptance, and merge.
