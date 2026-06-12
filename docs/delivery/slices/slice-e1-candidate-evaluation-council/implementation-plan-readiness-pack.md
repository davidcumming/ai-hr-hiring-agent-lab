# Implementation Plan — Azure/Foundry Readiness Pack (slice-e1, follow-on coding batch)

> Stage 5 artifact (`implementation-plan-builder`, coding-agent role), 2026-06-11.
> Scope: the **Azure/Foundry readiness pack** layered on the completed local deterministic
> E1 implementation (88 passed / 7 skipped at batch start; baseline verified healthy —
> submit→retrieve, persistence, mandatory flags all confirmed before planning).
> This plan is intent. It changes no requirement of the approved slice spec; everything
> here stays **local/deterministic by default**. No Azure resources, no live Foundry or
> model calls, no secrets, synthetic data only, advisory-only invariants unchanged.

## 1. Objective

Make the next slice (live Azure/Foundry wiring) a **configuration exercise, not a
restructuring exercise**, by hardening the seams that already exist and adding the
missing readiness surfaces: a formal storage backend boundary with an Azure-Blob-shaped
scaffold, a provider registry compatible with the future Foundry runtime options, a
versioned source-controlled prompt registry, per-role council transcripts as discrete
artifacts, Copilot-ready OpenAPI, local demo + future smoke scripts, and a no-deploy
infra skeleton.

## 2. Inputs honoured

- Approved slice spec (revised 2026-06-11) §15 constraints; hardened eval contract
  (DT-001..DT-018, LE deferral rationale); architecture-check.md verdict CLEAR +
  C-COND-1/C-COND-2; adr-deferred-foundry-wiring.md (draft, NOT approved).
- Current-state docs (product-current-state/, architecture/) and the live code under
  `src/hr_eval_lab/` as implementation truth.
- hr-hiring read-only reference (storage/evidence design, Foundry companion,
  quality-controls, API contracts, security rules) — requirements extracted, nothing
  copied wholesale.

## 3. Work breakdown (coding targets → repo changes)

### T1 — Domain data model (harden, don't fork)

Most target models already exist; the plan is a mapping plus additive gaps. Existing →
target mapping (no rename churn; serialization stays canonical JSON via
`store.canonical_json`):

| Target model | Status | Where |
|---|---|---|
| EvaluationRequest / EvaluationContext | exists | `domain/schemas/request.py` (context = actor + correlation in record) |
| EvaluationRecord | exists | `domain/schemas/audit.py` |
| SourceDocument / SourceDocumentVersion | exists | `SourceRef` (id + version + sha256 + provenance) |
| Rubric / RubricCriterion | exists | `RubricView` / `RubricCriterionView` |
| EvidencePacket / EvidenceItem / MissingEvidenceItem / PolicySensitiveEvidenceItem | exists (packet + segments; item shapes enforced by council role schemas) | `audit.py`, `council.py` |
| CouncilRole / CouncilRoleInvocation / CouncilRoleOutput | exists as composition + `RoleExecution`; **add** `CouncilRoleInvocation` transcript view (T5) | `council/composition.py`, new `domain/schemas/transcript.py` |
| RigorMode / RigorResolution / EscalationPolicy / EscalationTrigger | exists | `config.py`, `audit.py`, `rigor/`, `escalation/` |
| QualityGateResult | exists (gate result entries) | `gates/quality_gates.py`, record `gate_results` |
| FinalSynthesis | exists (synthesis role output in record) | `council.py` |
| HumanReviewState | exists | `HumanReviewBlock` |
| ProviderMetadata | exists; **extend** (T3 contract fields) | `domain/schemas/provider.py` |
| StorageArtifactRef | **new** | new `domain/schemas/storage.py` |
| Record summary row (metadata, never-log) | **new** `RecordSummaryRow` | new `domain/schemas/storage.py` |

Rules: deterministic JSON; IDs/hashes/versions first-class (already true); every record
reconstructs the evaluation from exact source versions (already true — keep invariant
tested).

### T2 — Storage abstraction

- New `persistence/backend.py`: `StorageBackend` ABC with
  `write_evaluation_record(record)`, `read_evaluation_record(evaluation_id)`,
  `write_artifact(evaluation_id, artifact_type, role_or_name, payload)`,
  `list_artifacts(evaluation_id)`, `write_metadata_row(record_summary)`,
  `read_metadata_row(evaluation_id)`. Idempotency stays a thin layer over the store
  (existing pattern preserved).
- `LocalFilesystemBackend` (default): artifact layout
  `evaluations/{evaluation_id}/record.json | request.json | source-documents.json |
  evidence-packet.json | council/{role}.json | synthesis.json | quality-gates.json |
  provider-metadata.json | human-review.json` plus `metadata/evaluations.jsonl`
  (summary rows; **no resume/cover-letter text** — enforced by `RecordSummaryRow`
  schema having no text-bearing field).
- `LocalStore` keeps its public API (`save_record` / `load_record` / `read_table`) so
  the facade and DT-001..018 are untouched; internally it delegates to the backend and
  continues writing the existing table-equivalents (`EvaluationEvidence.jsonl`,
  `IdempotencyRecords.jsonl`, `ReviewQueue.jsonl`). The blob path moves from
  `evaluations/{id}.json` to `evaluations/{id}/record.json` (tests do not reference raw
  paths; verified).
- `AzureBlobBackend` scaffold (`persistence/azure_blob_backend.py`): same ABC;
  **disabled by default**; no import-time or test-time network; azure SDK imported
  lazily inside methods only; selecting it without complete config (or with
  `HRHA_ENABLE_LIVE_AZURE` unset/false) raises `StorageNotConfiguredError` (safe,
  fail-closed). Auth path documented as managed-identity-first; app settings are
  placeholders only. Config: `[storage] backend = "local_filesystem"` default;
  `azure_*` keys empty placeholders.

### T3 — Foundry provider seam (registry + scaffolds)

- Provider IDs: `deterministic_mock` (default) | `foundry_project_responses` |
  `foundry_prompt_agent` | `foundry_hosted_agent`. New `providers/registry.py` resolves
  lazily by ID; default path never imports any Foundry module.
- Config `[provider]` gains `provider_id = "deterministic_mock"`. Legacy
  `ai_backend_type` (`none|foundry_agents`) retained for record compatibility and must
  be consistent with `provider_id` (validated; mismatch = config error). The legacy
  `foundry_stub.py` remains the `foundry_agents` family stub; the three new scaffold
  modules live under `providers/foundry/` and raise `ProviderNotConfiguredError` on use.
- Guards: `HRHA_ENABLE_LIVE_AZURE` (default false) disables all live paths;
  `HRHA_PROVIDER_KILL_SWITCH=true` blocks resolution of any Foundry provider even if
  otherwise configured. Request bodies cannot select provider/model/deployment/
  endpoint/agent (already true — request schema unchanged and test-pinned).
- Provider output contract: `ProviderMetadata` extended with nullable
  `prompt_template_id`, `prompt_template_version`, `model_or_agent_ref`,
  `provider_trace_id` (alias of existing `trace_id` kept — no field rename),
  `warnings: list[str]`, `safe_error: Optional[str]`. `role`, `input_artifact_refs`,
  `output_json`, `validation_status` are carried by the `CouncilRoleInvocation`
  transcript (T5) since validation is facade-owned. Mock populates everything
  deterministically; Foundry scaffolds never run.

### T4 — Versioned prompt registry

- New `src/hr_eval_lab/prompts/`: `registry.py` + `templates/<role_id>.v1.md` for the 10
  required roles (`request_normalizer`, `evidence_extraction`, `merit_advocate`,
  `risk_gaps_advocate`, `neutral_scoring_judge`, `policy_fairness_auditor`,
  `synthesis_judge`, `quality_gate_evaluator`, `second_synthesis_judge`,
  `rubric_calibration_judge`).
- Every template embeds the mandatory constraint block (evidence-packet-only reasoning;
  no unsupported inference; direct/indirect/contrary/missing evidence distinction; no
  protected characteristics or proxies; rubric-as-written; structured JSON only;
  advisory decision support only; human review required for high-impact hiring). No
  secrets/endpoints/deployments/tenant/subscription IDs/real applicant data — test-enforced.
- Registry API: `get_template(role_id) -> PromptTemplate(template_id, version, body)` +
  `list_roles()`. The deterministic mock stamps `prompt_template_id/version` into
  `ProviderMetadata` (templates are **recorded, not executed** under the mock — stated
  explicitly in docs). Role→template and role→future-agent mapping samples are
  source-controlled config (T9).

### T5 — Council interaction transcripts

- The full audit record already persists normalized request, source versions+hashes,
  evidence packet, validator output, per-role executions, synthesis, gates, rigor,
  escalation, provider metadata, human-review block, timestamps. Readiness additions:
  per-role transcript artifacts `council/{role}.json` (a `CouncilRoleInvocation` view:
  role, prompt template id/version, input artifact refs, output JSON, validation
  status, provider metadata, retries, latency) plus the other artifact files in T2,
  emitted at persistence time from the record (single source, no second truth).
- Safe user response unchanged: envelope already excludes prompts, hidden instructions,
  raw provider errors, secrets, stack traces; metadata rows stay text-free (DT-011).

### T6 — Copilot/API contract readiness

- Stable operation IDs `submitEvaluation` / `getEvaluation`; Copilot-suitable tool
  summaries/descriptions; correlation ID header `X-Correlation-Id` (accepted on
  request, echoed on response, documented); optional `Idempotency-Key` header on POST
  (body field remains canonical; if both present they must match → else HTTP 400; body
  may omit the field when the header is supplied). Envelope `result` exposes
  `effective_rigor` and escalation policy outcome (add to result projection if absent).
- No request field selects provider/model/deployment/endpoint/agent (pinned by test).
  Synthetic examples only. Regenerate `openapi/evaluations-api.json` via
  `scripts/export_openapi.py`; OpenAPI parse + operation + schema-exclusion tests.
- New `docs/integration/copilot-studio-tool-readiness.md` (registration-readiness doc;
  no portal instructions executed now).

### T7 — Local CLI demo + future smoke scaffolds

- `scripts/run_council_local.py`: runs one synthetic candidate (cand-sample-001 /
  pos-sample-001) strictly through the HTTP facade in-process (ASGI transport — no
  privileged side door, consistent with DT-018), writes the local artifact tree, prints
  a **safe summary only** (status, evaluation_id, effective rigor, gates passed,
  artifact count; no resume text, no prompts).
- `scripts/smoke_foundry_config.py` and `scripts/smoke_storage_config.py`: disabled by
  default; refuse to do anything live unless `HRHA_ENABLE_LIVE_AZURE=true` **and**
  `--live` is passed; no SDK import and no network in the disabled path; safe failures
  (config-check messages) only.

### T8 — Infra-as-code skeleton (placeholders only; NO deploy)

`infra/README.md`, `infra/bicep/main.bicep`, `infra/parameters.sample.json`,
`infra/env.sample`. Placeholder resources: resource group param (default
`rg-hrha-lab-cac`), storage account + blob container, Function App, Application
Insights, Key Vault, Foundry resource/project placeholders, managed identity + RBAC
placeholders. No real tenant/subscription IDs, endpoints, or secrets; no deployment
commands executed.

### T9 — Source-controlled config samples (Stage 9 input)

`config/lab-config.toml` extended (`[provider] provider_id`, `[storage]` block);
`config/azure.env.sample` (HRHA_ENABLE_LIVE_AZURE, HRHA_PROVIDER_KILL_SWITCH, Azure
placeholder settings); `config/role-agent-mapping.sample.json` (role → future Foundry
agent/deployment placeholder mapping); prompt registry is config-by-construction in
source control.

## 4. Test plan (Stage 8)

Keep DT-001..DT-018 green (regression baseline). Add readiness-pack suite `tests/test_rp0xx_*.py`:

| ID | Covers |
|---|---|
| RP-001 | Domain JSON roundtrip incl. new schemas; deterministic serialization |
| RP-002 | Source hash/provenance invariant retained through new artifact layout |
| RP-003 | Local backend write/read: record + all artifact files + list_artifacts |
| RP-004 | `metadata/evaluations.jsonl` summary excludes resume/cover-letter text |
| RP-005 | Azure Blob backend: no azure import at module import; safe `StorageNotConfiguredError` when selected without config; no network in default tests |
| RP-006 | Provider registry: deterministic_mock default; unknown provider fails safely; foundry IDs resolve to scaffolds that raise `ProviderNotConfiguredError`; no Foundry import on default path |
| RP-007 | Kill switch blocks Foundry providers; `HRHA_ENABLE_LIVE_AZURE=false` blocks live paths |
| RP-008 | Mock conforms to extended provider contract (template id/version stamped; warnings/safe_error fields) |
| RP-009 | Prompt registry: all 10 roles present; every template contains each mandatory safety constraint; no secret/endpoint/tenant/subscription-like strings |
| RP-010 | OpenAPI parses; submitEvaluation/getEvaluation present; request schema exposes no provider/model/deployment/endpoint/agent field; headers documented |
| RP-011 | Idempotency-Key header behaviour (header-only, body-only, match, mismatch→400) |
| RP-012 | CLI local run writes artifact tree; stdout has no resume text/prompt text |
| RP-013 | Smoke scripts exit safely with live disabled; perform no network |
| RP-014 | Per-role transcript artifacts exist and validate as `CouncilRoleInvocation` |
| RP-015 | Mandatory flags invariant (`human_review_required`, `decision_support_only`) still true across new surfaces |

Checks run: full pytest, OpenAPI validation (openapi-spec-validator), import checks,
CLI run. No lint/type config exists in the repo (recorded; not added in this batch).

## 5. Architecture/ADR flags (input to Stage 6)

1. **Live Foundry runtime choice** (project responses vs prompt agent vs hosted agent
   vs agent framework workflow) — remains the **deferred, unapproved** ADR
   (`adr-deferred-foundry-wiring.md`). This batch only widens the seam enumeration to
   keep all options open; it chooses none. Non-blocking for local work.
2. **Azure Blob/Table as the live storage target** — already documented intent (storage
   doc shapes mirrored since the first batch); scaffold-only here. Non-blocking;
   no new pattern beyond the documented one.
3. **Prompt seam introduction** — current-state docs say "no prompt seam exists"; this
   batch adds a versioned registry as source-controlled configuration. Consistent with
   quality-controls doc (template id/version per invocation). Flag for Stage 6
   confirmation; expected verdict: covered by spec §15 (server-side source-controlled
   config) — no new ADR needed for the local registry.
4. Request-contract addition (headers) is additive and stays within the adopted
   envelope/status vocabulary — compliance check at Stage 6.

## 6. Risks / mitigations

- **Regression risk to byte-identity (DT-002)** from new metadata fields → new fields
  are deterministic constants/nullables under the mock; DT-002 re-run is the guard.
- **Scaffold drift into live behaviour** → fail-closed errors + RP-005/006/007/013
  pin disabled-by-default behaviour.
- **Contract churn on idempotency header** → body field stays canonical; header is
  additive with explicit mismatch rule; DT-008 unchanged.
- **Doc/current-state divergence** ("no prompt seam" statement becomes stale) →
  Stage 12 reconciliation is in this batch's scope and must update it.

## 7. Blockers

None for local deterministic implementation. Deferred ADR (live Foundry runtime) and
BQ-005 (region approval) gate the live-wiring slice only. → Proceed to Stage 6.
