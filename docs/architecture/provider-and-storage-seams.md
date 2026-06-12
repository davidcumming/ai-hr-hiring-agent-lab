# Provider and Storage Seams

Describes the replacement seams that exist **in code today**, and what
swapping each for an Azure-backed implementation would touch. Nothing here is
wired to any cloud service; every Azure/Foundry-shaped component is a
fail-closed, non-functional scaffold, and the swap analysis is forward-looking
and labeled as such. Live wiring is human-gated (deferred ADR + BQ-005 region
approval — see §5).

## 1. Provider seam (AI backend)

### Contract (`src/hr_eval_lab/providers/base.py`)

`CouncilProvider` is an abstract base class with a single method:

```python
def invoke_role(role_id: str, packet: EvidencePacket,
                role_context: dict) -> ProviderResult
```

- One model-backed council role in, one schema-bearing result out.
- `role_context` carries prior validated role outputs, effective rigor,
  anomaly flags from the Deterministic Rules Validator, and (on a bounded
  corrective retry) a `corrective_hint`.
- `ProviderResult` (`domain/schemas/provider.py`) = `role_id` + `payload`
  (validated by the orchestrator against the role's declared schema) +
  `ProviderMetadata`: `ai_backend_type`, nullable `trace_id` / `eval_run_id`
  / `agent_run_id` / `model_deployment` / `prompt_version` /
  `prompt_template_id` / `prompt_template_version` / `model_or_agent_ref` /
  `safe_error`, a `warnings` list, `orchestration_version`
  (`council-composition-v1`), `role_schema_version` (`1.0`), `token_usage`,
  `latency_ms`. `safe_error` carries a safe error category only — never a raw
  provider error.
- The orchestrator, gates, and persistence depend only on this protocol plus
  the schema source — never on a concrete backend.

### Provider registry and selection (`src/hr_eval_lab/providers/registry.py`)

`select_provider()` (`providers/base.py`) delegates to
`resolve_provider()` in the provider registry, which resolves the configured
`provider.provider_id` lazily. The `provider_id` enumeration
(`config.py`, closed config literal):

| `provider_id` | Implementation | Status |
|---|---|---|
| `deterministic_mock` (default) | `DeterministicMockProvider` (`providers/mock.py`) | **Active — the only functional provider.** Fully deterministic, content-derived (criterion-keyword matching against rubric anchors; sha256-seeded identifiers; integer arithmetic). Schema-valid for all 8 model-backed role types; cites real packet segment / evidence ids so gates 3 and 6 are genuinely exercised. Stamps the role's prompt-registry template id/version into `ProviderMetadata` (templates are recorded, never executed — see §3). Test-only scenario scripting exists via constructor injection only — no API or config path reaches it. |
| `foundry_project_responses` | `providers/foundry/project_responses.py` | **Non-functional scaffold.** Fail-closed: any invocation raises `ProviderNotConfiguredError`. |
| `foundry_prompt_agent` | `providers/foundry/prompt_agent.py` | **Non-functional scaffold.** Same fail-closed behavior. |
| `foundry_hosted_agent` | `providers/foundry/hosted_agent.py` | **Non-functional scaffold.** Same fail-closed behavior. |

The three `foundry_*` IDs exist only so future wiring is a configuration
exercise; **none of them is chosen** — the live runtime shape
is an open question of the deferred, unapproved ADR. No module under
`providers/foundry/` imports any Azure/Foundry SDK at import time or performs
network I/O.

Resolution rules (all server-side; no request field can reach them):

- The default path imports only the mock — no Foundry module is imported.
- `HRHA_PROVIDER_KILL_SWITCH=true` blocks every Foundry provider
  (`ProviderBlockedError`, a `ProviderNotConfiguredError` subclass),
  regardless of any other configuration.
- `HRHA_ENABLE_LIVE_AZURE` unset or not `"true"` (case-insensitive,
  whitespace-trimmed; unset is the default) also blocks Foundry provider
  resolution. Even with both guards open, only the
  fail-closed scaffolds exist — no live call is possible.
- An unknown `provider_id` fails config validation (closed literal).

The legacy config key `provider.ai_backend_type` (`none | foundry_agents`)
is retained for audit-record compatibility. It is validated for consistency
with `provider_id` (`none` ↔ `deterministic_mock`; `foundry_agents` ↔ any
`foundry_*` id) — a mismatch is a configuration error. The legacy
`providers/foundry_stub.py` (`FoundryAgentProvider`) still exists in the tree
but is **no longer reachable** through `select_provider()`; the registry
routes exclusively on `provider_id`.

### What a live Azure AI Foundry swap would touch (planned, not implemented)

Sourced from the seam design and the deferred ADR draft
(`docs/delivery/slices/slice-e1-candidate-evaluation-council/adr-deferred-foundry-wiring.md`
— **draft, NOT approved; human approval is required before any live
wiring**). By design, wiring is intended to be configuration plus one real
provider implementation behind an existing scaffold, not restructuring:

- Implement `invoke_role` in one (or more) of the `providers/foundry/`
  scaffolds, filling the metadata fields the contract already carries
  (`trace_id`, `eval_run_id`, `agent_run_id`, `model_deployment`,
  `model_or_agent_ref`, `prompt_template_id/version`, real token/latency
  values, `warnings`, `safe_error`).
- Confirm or revise the provider-ID enumeration — the final enumeration is an
  open ADR question; the current IDs decide nothing.
- Add endpoint/identity configuration (placeholders exist in
  `config/azure.env.sample` and `infra/env.sample`; no live value or secret
  exists anywhere in the repo) plus region/data-residency approval (BQ-005).
- Un-defer the live evals (LE-001…LE-007 stubs in
  `tests/live_evals/test_le_stubs.py`).
- The orchestrator, gates, schemas, persistence, and facade are designed to
  remain untouched; any contract drift would surface through the pinned
  `role_schema_version` / `orchestration_version` values. (Design intent —
  only the seam discipline itself is test-verified today, via DT-013.)

## 2. Storage seam (persistence)

### Backend contract (`src/hr_eval_lab/persistence/backend.py`)

`StorageBackend` is a formal abstract base class — the seam between the
facade's persistence layer and a physical store:

```python
write_evaluation_record(evaluation_id, record_payload)
read_evaluation_record(evaluation_id) -> Optional[dict]
write_artifact(evaluation_id, artifact_type, role_or_name, payload) -> StorageArtifactRef
list_artifacts(evaluation_id) -> list[StorageArtifactRef]
write_metadata_row(record_summary)
read_metadata_row(evaluation_id) -> Optional[dict]
```

Two implementations exist, resolved by `select_backend()` from
`[storage] backend` in config (closed literal `local_filesystem |
azure_blob`; the Azure module is imported only when explicitly selected):

| Backend | Status |
|---|---|
| `LocalFilesystemBackend` (default) | **Active — the only functional backend.** Writes the artifact-per-evaluation layout below under the local persistence root. |
| `AzureBlobBackend` (`persistence/azure_blob_backend.py`) | **Non-functional scaffold, fail-closed.** No Azure SDK import at module import time (or in default tests), no network code, no credentials. Construction raises `StorageNotConfiguredError` unless every `[storage.azure]` value is populated **and** `HRHA_ENABLE_LIVE_AZURE=true`; even fully configured, every operation raises — live storage wiring is deferred and human-gated. Intended live auth is identity-based (managed identity / `DefaultAzureCredential`); never account keys, connection strings, or SAS tokens. |

Local artifact layout (mirrors the intended future blob layout so wiring is
configuration, not restructuring):

```
evaluations/{evaluation_id}/record.json            full audit record (canonical JSON)
evaluations/{evaluation_id}/request.json
evaluations/{evaluation_id}/source-documents.json
evaluations/{evaluation_id}/evidence-packet.json
evaluations/{evaluation_id}/council/{role}.json    per-role transcript (CouncilRoleInvocation)
evaluations/{evaluation_id}/synthesis.json
evaluations/{evaluation_id}/quality-gates.json
evaluations/{evaluation_id}/provider-metadata.json
evaluations/{evaluation_id}/human-review.json
metadata/evaluations.jsonl                          one text-free summary row per evaluation
```

Every artifact below `record.json` is a **projection of the audit record**,
emitted at persistence time — the record is the single source of truth; no
second truth exists. `StorageArtifactRef` and `RecordSummaryRow`
(`domain/schemas/storage.py`) are the boundary schemas; `RecordSummaryRow`
deliberately mirrors an Azure Table shape (`PartitionKey`/`RowKey` + typed
properties) and has **no text-bearing field** by construction.

### Store facade (`src/hr_eval_lab/persistence/store.py`)

`LocalStore` keeps the facade-facing API (`save_record` / `load_record` /
`read_table`), constructed once in `create_app` from `persistence.root`. It
delegates record and artifact I/O to the `StorageBackend` and additionally
writes the established append-only JSONL table-equivalents:
`tables/EvaluationEvidence.jsonl` (metadata-first rows, no text-bearing
field), `tables/IdempotencyRecords.jsonl`, `tables/ReviewQueue.jsonl`.
Idempotency logic (`persistence/idempotency.py`) remains a thin layer over
`LocalStore`'s table-equivalents — deliberately **not** part of the
`StorageBackend` ABC, to avoid a second source of truth (a future Azure
implementation would map the idempotency table to Azure Table directly).

### What an Azure storage swap would touch (planned, not implemented)

- Implement the `AzureBlobBackend` methods: artifacts become block blobs
  under `{container}/evaluations/{evaluation_id}/...` (same names as the
  local layout); the metadata summary becomes an Azure Table row
  (`PartitionKey` = evaluation id, `RowKey` = `"summary"`) — the row schema
  is already Table-shaped and text-free.
- Map the three JSONL table-equivalents to Table Storage; idempotency lookup
  becomes a point query on PartitionKey — same semantics.
- Byte-identity determinism (DT-002) depends on the canonical-JSON
  serialization (`backend.canonical_json`); a swap must preserve it.
- No retention, concurrency-control, or cleanup behavior exists today; a
  cloud-backed store would need those decisions (not specified anywhere in
  code).

## 3. Prompt seam (versioned prompt registry)

A source-controlled prompt registry exists at `src/hr_eval_lab/prompts/`:

- `registry.py` — `get_template(role_id, version=None) -> PromptTemplate`
  (latest version by default) and `list_roles()`. Template files live at
  `prompts/templates/<role_id>.v<N>.md`; the stable template id is
  `prompt-<role_id>` and the version is `v<N>`.
- Ten roles have a `v1` template (the eight model-backed roles plus
  `request_normalizer` and `quality_gate_evaluator`).
- Every template embeds the mandatory safety-constraint block
  (`MANDATORY_CONSTRAINTS` in `registry.py`: evidence-packet-only reasoning,
  no unsupported inference, evidence-relation discipline, no protected
  characteristics or proxies, rubric-as-written, structured JSON only,
  advisory-only, human review required). Test-pinned (RP-009), which also
  pins the absence of secret-bearing patterns, GUID-like tenant/subscription
  identifiers, and non-example Azure/Microsoft endpoints; the absence of real
  applicant data is maintained by review convention (the templates contain
  none) rather than by a dedicated test pattern.

**Templates are recorded, never executed.** The deterministic mock derives
outputs from the evidence packet directly and stamps the role's
`prompt_template_id` / `prompt_template_version` into `ProviderMetadata`, so
the audit trail already carries prompt provenance. No prompt text is ever
sent anywhere; there is no model to send it to. A role-to-template /
role-to-future-agent mapping sample (placeholders only) is committed at
`config/role-agent-mapping.sample.json`.

## 4. Seams that do NOT exist

To prevent over-reading: there is no identity seam (auth is a single
header-parsing function in `api/auth.py`), no queue/messaging seam (the
review queue is a JSONL file), no eval-harness seam (live-eval stubs skip
unconditionally), and no configuration service seam (one TOML file read at
startup, plus the two server-side environment guards
`HRHA_ENABLE_LIVE_AZURE` / `HRHA_PROVIDER_KILL_SWITCH`).

## 5. Live-wiring gates (status, not architecture)

Live Foundry/Azure wiring is **deferred and human-gated**: the Foundry-wiring
ADR
(`docs/delivery/slices/slice-e1-candidate-evaluation-council/adr-deferred-foundry-wiring.md`)
is a draft and NOT approved, and BQ-005 (Canadian-residency region/deployment
approval) is pending. Until both human gates pass, every Azure/Foundry-shaped
component in this document remains a fail-closed scaffold and no live call,
resource creation, or token spend is possible from this codebase.
