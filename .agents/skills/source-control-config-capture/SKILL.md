---
name: source-control-config-capture
description: Verifies every config change in a slice is committed to source control or registered as manual-config debt. Use during implementation to check what can and should be source-controlled.
---
# Skill: Source Control Config Capture

**Used at:** Stage 7 — Implementation & config capture (Orchestration Map §3 stage table)
**Execution model:** `inline`
**Supports:** Process Doc §17 Manual Portal and Configuration Evidence, §30 Definition of Done

---

## 1. Purpose

Ensure that every configuration change introduced during a slice — across Azure services, Power Platform solutions, Copilot Studio agents, Azure AI Foundry projects, and any other Microsoft-stack surface — is either committed to source control or explicitly registered as manual-config debt. This is the proactive complement to `manual-config-evidence-capture`: that skill captures evidence for what *cannot yet* be source-controlled; this one verifies what *can and should* be, and checks that it is. The gap between the two is the debt register, which flows into `manual-config-debt-monitor` at Stage 19. This skill answers "is it in source control?", not "is the config correct?". It recommends; it does not approve debt or merge readiness — the human release authority decides whether remaining debt is acceptable for merge.

---

## 3. Do Not Use This Skill For

- Capturing portal screenshots/notes for config that cannot be source-controlled (`manual-config-evidence-capture`), normalizing evidence for closeout (`manual-evidence-normalizer`), or tracking cross-slice debt (`manual-config-debt-monitor`).
- Writing production IaC from scratch without review, modifying live infrastructure, or certifying production correctness.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Slice spec | Required | What configuration changes are expected. |
| 2 | Implementation plan | Required | Which Azure/Power Platform/Copilot/Foundry resources are added or changed. |
| 3 | Implementation branch changes | Required | PR diff or file list showing what was committed. |
| 4 | Repo IaC conventions | Required | Where IaC lives (`/infra/`, `/bicep/`) and expected toolchain (Bicep, Terraform, CLI). |
| 5 | Architecture guidelines | Required | Which services require IaC, which are allowed manual-only, the debt-ceiling policy. |
| 6 | Prior source-control capture reports | Recommended | Accumulated debt from earlier slices. |
| 7 | Known unsupported-export notes | Recommended | Copilot Studio features not exportable, connector configs not in solution, etc. |

If required inputs are incomplete, produce a partial report and list the gaps explicitly.

---

## 6. Source Authority Rules

Code/config/IaC committed to the branch is implementation truth; portal state alone is not. What remains manual is established by the absence of committed config plus explicit evidence from `manual-config-evidence-capture`. Whether remaining debt is acceptable for merge is decided by the human release authority at Stage 16.

---

## 7. Process Steps

1. **Identify the expected config surface.** From the spec and plan, list every resource/service/config area added or changed, grouped by surface: Azure services (App Service, Functions, Logic Apps, Service Bus, API Management, AI Search, AI Services, Key Vault, managed identity, role assignments, networking); Power Platform (solutions, environment variables, connection references, canvas apps, cloud flows, Dataverse tables/columns); Copilot Studio (agent definition, topics, environment settings, channels); Azure AI Foundry (project config, deployments, models, indexes, evaluators, SDK-defined steps); GitHub Actions/pipelines (workflow files, secret references); other (registry settings, feature flags). Run this proactively at the start of Stage 7 so gaps are clear before they become debt.
2. **Check what is source-controlled.** For each item, determine the capture state:

   | State | Meaning |
   |---|---|
   | Committed | IaC, solution file, or SDK-defined config exists and is committed. |
   | Partially committed | Some properties in IaC, some portal-only. |
   | Not committed — export unsupported | Platform does not support export of this config. |
   | Not committed — debt | Export is feasible but not yet done. |

3. **Identify gaps.** For each not-fully-committed item, assess source-control feasibility (Yes / No / Partially / Unknown). If feasible-but-omitted, it is a debt item needing a GitHub Issue recommendation. If not feasible, flag for `manual-config-evidence-capture` with the platform limitation noted. If partial, record which properties are captured and which are not.
4. **Produce the capture report** using `templates/source-control-config-capture-report-template.md`.
5. **Recommend follow-up actions.** Debt items with feasible source control → recommend a GitHub Issue (type `manual-config-debt`). Items needing manual evidence → explicit handoff to `manual-config-evidence-capture`. Unsupported-export scenarios → note the platform limitation and flag for the closeout package.

Never include secrets, credentials, connection strings, or SAS tokens in the report (Key Vault names and managed-identity resource IDs are fine; their values are not). This skill recommends GitHub Issues; it does not create them or approve debt. See AGENTS.md cross-cutting rules (Authority and human gates; Source of truth; Evidence, privacy, context).

---

## 8. Output Location

`docs/delivery/slices/<slice-id>/source-control-config-capture-report.md` — follow the project's convention if different. Reference the report in the implementation summary and closeout package.

---

## 9. Output Format

Use `templates/source-control-config-capture-report-template.md`. No secrets or sensitive values anywhere in the report.

---

## 10. Quality Bar

Before handoff, confirm:

- Every config area from the slice spec and implementation plan is in the surface summary; no area silently omitted.
- All Microsoft-stack surfaces are considered (Azure, Power Platform, Copilot Studio, Foundry, GitHub Actions/pipelines).
- Every committed IaC/solution/SDK-defined file is listed with its actual branch file path, naming the resource it represents.
- Every gap is classified (Debt / Export Unsupported / Partially Captured / Under Investigation) with source-control feasibility assessed; partial items specify which properties are committed.
- Every feasible-but-omitted debt item has a `manual-config-debt` GitHub Issue recommendation (not a duplicate of an open one) — recommended, not created.
- Every manual-evidence item is listed for `manual-config-evidence-capture` with enough detail to identify the resource; the handoff is explicit.
- Known platform export gaps are documented as limitations, not treated as debt.
- No credentials, secrets, keys, connection strings, SAS tokens, or sensitive personal/health data appear anywhere.
- The report is honest about what is not source-controlled, does not approve debt, and does not claim production config is correct.
- Prior debt from earlier slices is referenced where it affects the current picture.

---

## 11. Failure Modes to Avoid

- Treating portal state as source-controlled, or assuming Foundry/low-code config is automatically captured.
- Overlooking Copilot Studio and Power Platform — the most common sources of manual-config debt — or silently passing over "not yet implemented" IaC without flagging it as debt.
- Conflating source-control capture with correctness, or failing to hand off manual-config candidates explicitly.
- Including sensitive values (keys, passwords, SAS tokens) in the report.

---

## 13. Handoff to Next Skill

- **Primary:** `deterministic-test-author` (Stage 8) — pass the committed IaC and config asset list so test authors know which resources are expected to exist.
- **Conditional:** `manual-config-evidence-capture` (Stage 7) — if manual-config gaps exist, pass the debt candidates and known platform limitations.

Downstream consumers: `closeout-package-builder` (Stage 14, evidence of config coverage), `manual-config-debt-monitor` (Stage 19, debt counts and issue references), `definition-of-done-validator` (Stage 15, confirms capture evidence is present). Recommend proceeding to Stage 8, or pausing to complete `manual-config-evidence-capture` first if manual-config gaps are significant. The agent must not approve manual-config debt as permanent, nor approve merge readiness.
