# AI HR Hiring Agent Lab

This repo is a self-contained Copilot Studio / Azure AI Foundry HR hiring agent lab. It vendors the GenTech Azure Development Standards and exposes the same active skill packages to Codex and Claude.

## Layout

- `AGENTS.md` - repo instructions shared by Codex and Claude.
- `CLAUDE.md` - Claude Code entrypoint that points back to `AGENTS.md`.
- `standards/azure-development-standards/` - vendored standards snapshot.
- `.agents/skills/` - Codex skill discovery mirror.
- `.agents/agents/` - Codex-readable role prompt mirror.
- `.claude/skills/` - Claude Code skill discovery mirror.
- `.claude/agents/` - Claude Code role prompt mirror.

## Start Here

Read these standards together before planning implementation work:

- `standards/azure-development-standards/gentech_slice_based_development_process_revised.md`
- `standards/azure-development-standards/gentech_agent_skills_usage_and_requirements.md`
- `standards/azure-development-standards/gentech_slice_lifecycle_orchestration_map.md`

The first-project policy and architecture documents are in `standards/azure-development-standards/Initial_Documentation/`.

## Current Scope

This checkout contains a working, fully local Candidate Evaluation Council application alongside the vendored standards:

- `src/hr_eval_lab/` - FastAPI facade, 11-role council orchestration (Modes A/B/C), rigor/escalation/quality-gate logic, deterministic mock AI provider behind a provider seam, local audit-record persistence, explicit Azure Blob evaluation-record persistence for the Function App path, the canonical explicit-ID read plus a Copilot-friendly body-based retrieve wrapper, and a thin CLI.
- `tests/` - deterministic suite DT-001..DT-018 plus RP, Copilot Swagger, and smoke coverage (200 passing); `tests/live_evals/` holds deferred live-eval stubs that skip.
- `openapi/evaluations-api.json` - the committed source API contract, drift-checked against the app factory by `scripts/export_openapi.py --check`.
- `openapi/copilot-studio/evaluations-tool.swagger.json` - the curated Copilot Studio / Power Platform Swagger 2.0 artifact, drift-checked by `scripts/export_copilot_openapi.py --check`; it exposes `submitEvaluation`, `getEvaluation`, and `retrieveEvaluationForCopilot`.
- `config/lab-config.toml`, `fixtures/` (synthetic, hash-pinned), `scripts/`, and `.github/workflows/ci.yml`.
- `docs/product-current-state/` and `docs/architecture/` - what the system does and what is physically built; `docs/delivery/slices/` - per-slice planning and delivery artifacts.

This repo still **does not create Azure resources and has no live AI backend, no production Copilot Studio surface, and no Entra integration**. The narrow Azure Blob storage path is for already-created lab resources and keeps the deterministic mock provider. A manual Copilot Studio lab configuration exists for one synthetic topic workflow: `submitEvaluation` stores `submitted_evaluation_id`, then `retrieveEvaluationForCopilot` retrieves the same advisory/audit record by body field `evaluation_id`. That portal state is partial note-based evidence only; there is no source-controlled Copilot ALM export, durable screenshot/export/transcript, production identity, or live Foundry execution.

Use the vendored process to plan further Copilot Studio, Azure AI Foundry, Azure Functions, storage, search, identity, and evaluation work as slices.
