---
name: closeout-package-builder
description: "Assembles the full slice closeout package from Stage 2-13 artifacts for Release Authority review. Use at Stage 14 to build the merge-readiness evidence set."
---

# Skill: Closeout Package Builder

**Used at:** Stage 14 — Traceability & closeout (Orchestration Map §3 stage table)
**Execution model:** `inline`
**Supports:** Process Doc §29 Slice Closeout Package, §30 Definition of Done

---

## 1. Purpose

Assemble the full slice closeout package from artifacts produced across Stages 2–13 — the complete evidence set the Release Authority reviews before approving merge. The package carries a merge-readiness recommendation and a human approval checklist, but does not itself approve anything; that authority belongs to the Release Authority at Stage 16. Every gap in the provided inputs must be visible; missing evidence is named, never hidden, so the Release Authority can decide with full information.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Implementation summary | Yes | What was built; key coding decisions |
| 2 | Deviation log | Conditional | From `implementation-deviation-capture`; "no deviations" if clean |
| 3 | Traceability matrix | Yes | Backbone of the package; gaps become residual-risk items |
| 4 | Deterministic test summary | Yes | Coverage map + pass/fail counts |
| 5 | Live eval summary | Yes | Threshold table, version metadata, artifact references |
| 6 | Cost and latency summary | Conditional | Required when cost/latency was an eval criterion; else "not measured" + reason |
| 7 | Manual evidence summary | Conditional | Required if portal/low-code config captured; else N/A + reason |
| 8 | ADRs created or updated | Yes | All ADRs raised or changed this slice; "none" if none |
| 9 | Architecture guideline updates | Conditional | Summarize; "none" if no changes |
| 10 | Master documentation updates | Yes | Current-state and actual-architecture changes |
| 11 | GitHub follow-up issue summary | Yes | Created issue refs or safe drafts from `github-issue-drafter` |
| 12 | Known residual risks | Yes | From eval failure classification, traceability gaps, deviation log |
| 13 | Human approval records | Conditional | Stage 11 high-risk review, ADR approvals; "none yet" if Stage 16 pending |

---

## 7. Process Steps

### Step 1 — Collect and verify inputs
Confirm each input is available. Record any missing input in the "Evidence gaps" section. Do not proceed without the traceability matrix — it links everything else.

### Step 2 — Implementation summary section
Summarize what was built: features, key technical decisions, config changes, Azure / Power Platform / Copilot Studio / Azure AI Foundry components modified. Use implemented-reality language (not "the spec said X"). If a deviation log exists, give a brief deviation summary here (detail stays in its own section).

### Step 3 — Compile evidence sections
Reference artifacts, do not reproduce them. Cover: deterministic tests (pass/fail/skipped + reasons); live evals (threshold table, overall result, accepted non-blocking items); cost and latency (P90 / budget compliance if measured); manual evidence (config register summary; source-control debt status).

### Step 4 — Record architecture and ADR changes
List ADRs raised/updated (title, decision question, outcome, link). List guideline changes with effective date.

### Step 5 — Summarize documentation updates
State which current-state and actual-architecture sections were updated. Confirm the Stage 13 documentation validation gate passed (or passed with named non-blocking conditions).

### Step 6 — Record residual risks
For each residual risk (non-blocking eval failures, traceability gaps, known limitations, accepted deviations, manual-config debt): Risk ID, description, source stage/artifact, severity, disposition (accepted/deferred/mitigated), required action before/after merge, issue reference. The Release Authority explicitly accepts each at Stage 16.

### Step 7 — Summarize follow-up issues
List all GitHub follow-up issues and relevant existing open issues: number/URL or draft reason, type, severity, title, disposition (created / safe draft / existing open).

### Step 8 — Produce merge-readiness recommendation

| State | Criteria |
|---|---|
| **Ready for Release Authority review** | All blocking items resolved; matrix complete; no evidence gaps; required safe issues created or intentionally drafted; approval checklist complete |
| **Conditionally ready** | Minor non-blocking gaps, tracked as issues; human judgement required on residual risks |
| **Not ready** | One or more blocking gaps, missing evidence, or unresolved blocking items |

State which items must be resolved before merge and which are accepted as post-merge follow-up.

### Step 9 — Complete the human approval checklist
Populate the template's approval checklist (Process Doc §29 items), marking each complete / conditionally complete (issue tracked) / incomplete. The Release Authority signs at Stage 16.

---

## 9. Output Format

Use `templates/slice-closeout-package-template.md`; every section is present even if "N/A — reason: `<reason>`". Reference artifacts by location; keep raw eval data and any PHI/PII/Canadian-residency-restricted data out of the package body (reference secure storage instead).

---

## 10. Quality Bar

Before handoff, confirm:

- [ ] All mandatory Process Doc §29 sections are present, each "N/A — reason" rather than omitted where not applicable.
- [ ] The implementation summary uses current-state language, not spec-planning or slice-history language.
- [ ] All artifact references (eval runs, test runs, manual evidence) are specific IDs or paths, not generic.
- [ ] Model, prompt, tool schema, and orchestration versions are recorded in the eval summary section.
- [ ] No evidence gap is hidden — all are named in the evidence-gaps section.
- [ ] Every residual risk has a severity and a disposition; none is implicitly accepted; each non-blocking one has an issue reference.
- [ ] The deviation log is present (or explicitly "No deviations recorded") and entries reference the original spec item and implemented alternative.
- [ ] Manual-config debt is not marked resolved without source-control evidence.
- [ ] The traceability coverage summary in the package matches the matrix artifact.
- [ ] The merge-readiness recommendation is explicit (Ready / Conditionally ready / Not ready) and stated as a recommendation, not a decision.
- [ ] The human approval checklist is present, pre-populated, and marked "Pending Stage 16 review".
- [ ] Created GitHub Issues include number/URL; drafts include an explicit draft reason; no issue implies ADR approval, risk acceptance, release approval, merge approval, or committed scope.

---

## 11. Failure Modes to Avoid

| Failure mode | Why it matters |
|---|---|
| Omitting sections because evidence is missing | The Release Authority must see what is missing to decide |
| Presenting non-blocking failures as fully resolved | Residual risks must be explicit; Stage 16 accepts them, not this skill |
| Including raw eval artifact data rather than references | Keeps sensitive data out of the code repo |
| Omitting the deviation log when deviations exist | Hides intent-vs-reality gaps from the Release Authority |
| Marking manual-config debt resolved without source-control evidence | Manual evidence is not a permanent substitute; debt remains until source-controlled |

---

## 13. Handoff to Next Skill

Pass the package to `definition-of-done-validator` (Stage 15) for independent validation. The Release Authority reviews the package, the DoD report, and the issue summary at Stage 16. After merge, pass the package to `archive-package-preparer` (Stage 17); implementation and process lessons flow to `slice-retro-and-lessons` (Stage 18). The skill response must include the complete package, an evidence-gap section (or "No evidence gaps"), a residual-risk register (or "No residual risks identified"), a follow-up issue summary, the merge-readiness recommendation with reasoning, the human approval checklist, and a clear statement that the Release Authority must approve at Stage 16 before merge. Obeys the recommend-never-approve and source-of-truth rules in AGENTS.md.
