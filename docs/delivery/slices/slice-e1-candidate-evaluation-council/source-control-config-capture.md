# Source-Control Config Capture Report — Azure/Foundry Readiness Pack

> Stage 9 artifact (`source-control-config-capture`, coding-agent role), 2026-06-11.
> Scope: configuration surfaces added or changed by the readiness-pack batch.
> Verdict basis: code/config committed to the working tree is implementation truth;
> no portal state exists (no Azure/Power Platform/Copilot/Foundry resource exists).

## Capture table

| Config surface | Where (source-controlled) | State |
|---|---|---|
| Local storage backend selection | `config/lab-config.toml` `[storage] backend = "local_filesystem"` | **Committed** |
| Azure Blob backend placeholders | `config/lab-config.toml` `[storage.azure]` (empty placeholders); `infra/env.sample`; `config/azure.env.sample` | **Committed (placeholders only)** — scaffold fails closed while empty |
| Foundry provider selection + placeholders | `config/lab-config.toml` `[provider] provider_id` (+ legacy `ai_backend_type`); `config/azure.env.sample` Foundry placeholder vars | **Committed (placeholders only)** |
| Provider kill switch | Env var `HRHA_PROVIDER_KILL_SWITCH` (documented in `config/azure.env.sample`, `infra/env.sample`; enforced in `providers/registry.py`) | **Committed (mechanism + sample)** — env values are runtime state, not repo state, by design |
| Live Azure enable flag | Env var `HRHA_ENABLE_LIVE_AZURE` (same locations; enforced in `config.py`, `providers/registry.py`, `persistence/azure_blob_backend.py`, smoke scripts) | **Committed (mechanism + sample)** |
| Versioned prompt registry | `src/hr_eval_lab/prompts/templates/*.v1.md` + `prompts/registry.py` (10 roles, mandatory constraints, no secrets — test-pinned RP-009) | **Committed** (config-by-construction in source control) |
| Role-to-template mapping | Implicit by filename convention (`<role_id>.v<N>.md`) + `config/role-agent-mapping.sample.json` | **Committed** |
| Role-to-future-agent mapping sample | `config/role-agent-mapping.sample.json` (placeholder refs only) | **Committed (placeholders only)** |
| Local artifact path / layout | `config/lab-config.toml` `[persistence] root`; layout owned by `persistence/backend.py` (documented in module docstring) | **Committed** |
| IaC skeleton | `infra/README.md`, `infra/bicep/main.bicep`, `infra/parameters.sample.json`, `infra/env.sample` | **Committed (placeholders only; never deployed)** |
| OpenAPI contract | `openapi/evaluations-api.json` regenerated from the app factory; drift-checked in CI | **Committed** |
| CI workflow | `.github/workflows/ci.yml` (unchanged this batch; runs full suite incl. RP tests + OpenAPI drift) | **Committed** |

## Gaps / debt

- **No manual-config evidence needed**: no portal surface was touched (none exists).
- **Real Azure values** (subscription, resource group, account URL, container,
  Function App name, Foundry endpoint/agent IDs, managed-identity client ID,
  Entra group object IDs) are intentionally NOT in source control and never will
  be as secrets/tenant details; non-secret names will be committed at the wiring
  slice as config values. Until then they are placeholders — not debt, a gate.
- **Secrets**: none exist, none committed, none needed (identity-based auth is
  the documented live path).

## Verdict

All readiness-pack configuration is source-controlled or an explicit, fail-closed
placeholder. No manual-config debt created. No GitHub Issue recommendation needed
from this report.
