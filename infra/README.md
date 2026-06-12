# Infra Skeleton — PLACEHOLDERS ONLY, NO DEPLOYMENT

This folder is a **documentation-grade infrastructure-as-code skeleton** for the
future Azure/Foundry wiring slice. Nothing here has been deployed, validated
against a subscription, or approved. **Do not deploy**: live wiring is gated on
the human-approved Foundry-wiring ADR
(`docs/delivery/slices/slice-e1-candidate-evaluation-council/adr-deferred-foundry-wiring.md`)
and the Canadian region/deployment approval (BQ-005).

Rules embedded in every file here:

- No real tenant IDs, subscription IDs, endpoints, object IDs, or secrets —
  placeholders only (`<...>` or `TODO-...` markers).
- Identity-based access (managed identity + RBAC), never account keys,
  connection strings, or SAS tokens.
- Synthetic/sample data only; the lab never processes real applicant data.

## Files

| File | Purpose |
|---|---|
| `bicep/main.bicep` | Placeholder Bicep for the lab resource set (storage, Function App, App Insights, Key Vault, Foundry placeholders, managed identity, RBAC) |
| `parameters.sample.json` | Sample parameter file — placeholder values only |
| `env.sample` | Placeholder app settings / environment variables (mirrors `config/azure.env.sample`) |

## Intended (not provisioned) resource set

- Resource group: parameter `resourceGroupName`, default suggestion `rg-hrha-lab-cac`
  (Canada Central placeholder — region adoption requires the BQ-005 human approval).
- Storage account + blob container (full evaluation records and artifact tree)
  + table endpoints (summary/evidence/idempotency/review-queue rows).
- Azure Function App (the facade API host candidate).
- Application Insights (safe-metadata telemetry only; never-log rules apply).
- Key Vault (future secrets that cannot be eliminated by managed identity; none known today).
- Azure AI Foundry resource/project placeholders (runtime shape is the deferred ADR's decision).
- User-assigned managed identity + RBAC role-assignment placeholders
  (Storage Blob Data Contributor / Table Data Contributor scoped to the lab data resources).

## What must happen before any deployment

1. Human approval of the deferred Foundry-wiring ADR (runtime shape, backend enumeration, trace/eval metadata contract).
2. Human approval of region/data-residency (BQ-005).
3. Real parameter values supplied through an approved channel (never committed).
4. A scoped implementation slice with its own human gates.
