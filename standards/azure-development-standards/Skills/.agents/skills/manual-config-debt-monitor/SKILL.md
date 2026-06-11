---
name: manual-config-debt-monitor
description: Tracks accumulated manual-config and source-control debt against the project ceiling policy and recommends whether it blocks the next slice. Use at Stage 19 or before a new planning cycle.
---
# Skill: Manual Config Debt Monitor

**Used at:** Stage 19 — Strategic doc update & debt monitor (Orchestration Map §3 stage table)
**Execution model:** `inline`
**Supports:** Process Doc §17 Manual Portal and Configuration Evidence, §30 Definition of Done

---

## 1. Purpose

Track accumulated manual-configuration and source-control debt, compare it against the project's debt ceiling policy, and recommend whether that debt blocks the next slice from beginning. Debt arises when Azure Portal, Power Platform, Copilot Studio, Azure AI Foundry UI, or other web config surfaces are changed without representation in source control; each such item must be tracked as an open GitHub Issue. The skill counts, classifies, and ages that debt and produces a block / conditional / no-block recommendation — it applies the ceiling policy and recommends; it does not set the policy or approve carry-over, and the human confirms (AGENTS.md "Authority and human gates").

---

## 2. When to Use This Skill

Runs at every Stage 19 invocation, regardless of whether `strategic-doc-update-recommender` fired. Also run before a new planning cycle (Stage 0) if Stage 19 was skipped or debt status is uncertain, or when the user asks whether a new slice can begin.

---

## 3. Do Not Use This Skill For

- Creating or closing GitHub Issues — `github-issue-drafter` drafts; issues close only with approved evidence.
- Performing manual-config evidence capture — that is `manual-config-evidence-capture` (Stage 7) and `manual-evidence-normalizer` (Stage 12).
- Setting the debt ceiling policy — the project defines it before feature delivery (Process Doc §17.3); this skill applies it.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Open GitHub Issues tagged manual-config / source-control debt | Required | Source of truth for unresolved work |
| 2 | Debt ceiling policy | Required | Cannot recommend block/no-block without it |
| 3 | Manual-config evidence summaries this slice (Stage 12) | If debt incurred | From `manual-evidence-normalizer` |
| 4 | Source-control capture reports this slice (Stage 7) | If config changes occurred | From `source-control-config-capture` |
| 5 | Closeout packages, recent slices (Stage 14) | Required | Current slice; prior slices if debt ages matter |
| 6 | Slice history (slices each open issue survived) | Required | For age-based ceiling checks |

If the ceiling policy is unavailable, stop and ask the user — do not produce a recommendation without a ceiling. If the GitHub Issues list is unavailable, raise a structural blocker, not a no-block recommendation.

---

## 6. Source Authority Rules

Open debt items and resolution status come from GitHub Issues (source of truth for unresolved work, Process Doc §3): an item counts as resolved only if its Issue is **closed with evidence**, never if "probably fixed." The ceiling is the stated project policy. Whether debt blocks the next slice is this skill's recommendation; the human confirms, and any carry-over or issue closure is a human decision.

---

## 7. Process Steps

**Step 1 — Load ceiling policy.** Retrieve the project's debt ceiling and confirm the three dimensions (Process Doc §17.3 or custom): unresolved **critical** items (default zero → always blocks); unresolved **non-critical** items (default ceiling three); **age limit** — any non-critical item surviving more than one subsequent slice without explicit re-approval triggers a block review. Note any custom override.

**Step 2 — Inventory open debt.** Load all open manual-config / source-control debt Issues. Per issue record: ID and title, severity (critical / non-critical), date opened, completed slices survived, prior re-approval status, and config surface (Azure Portal / Power Platform / Copilot Studio / Foundry UI / other). Note issues closed this slice.

**Step 3 — Load debt incurred this slice.** Review this slice's evidence summaries and source-control capture reports. Identify new debt items that should have Issues. If new debt exists with no Issue, flag a gap requiring issue creation before any recommendation.

**Step 4 — Apply the ceiling check.** Compare inventory to each dimension:

| Dimension | Threshold | Current | Status |
|---|---|---|---|
| Unresolved critical | 0 | `<count>` | `Pass / BLOCK` |
| Unresolved non-critical | 3 (or custom) | `<count>` | `Pass / BLOCK` |
| Age-limit violations | 0 (over limit w/o re-approval) | `<count>` | `Pass / BLOCK / Review required` |

Any `BLOCK` → "block next slice." Any "Review required" → "conditional — human must re-approve aged items first." All pass → "no block."

**Step 5 — Burn-down actions.** For each breach or near-breach: which issues must resolve before the next slice, which require explicit carry-over re-approval, and priority order.

**Step 6 — Output.** Write to `docs/delivery/slices/<slice-id>/manual-config-debt-report.md`; append a debt status summary to the Stage 19 governance log if one exists.

---

## 10. Quality Bar

Before handoff, confirm:

- The debt ceiling policy is cited (with source), not assumed; if unavailable, a structural blocker is raised and no recommendation given.
- The three ceiling dimensions are identified, with any custom thresholds recorded and sourced.
- Every open debt issue carries a GitHub Issue ID, severity, config surface, age (slices survived), and re-approval status.
- New debt incurred this slice is identified, and missing GitHub Issues are flagged as gaps.
- Debt resolved this slice is listed with resolution evidence; no issue is marked closed without evidence.
- The ceiling check table shows all three dimensions with current counts and pass/block/review status, sourced from GitHub Issues.
- The recommendation is exactly one of `block-next-slice`, `conditional-re-approval-required`, `no-block` — never a "maybe" — with a rationale naming the breached dimension(s).
- Burn-down actions are concrete and ordered; aged items needing re-approval are listed explicitly.
- The report recommends blocking rather than approving new debt beyond the ceiling, and marks carry-over as requiring human confirmation.

---

## 9. Output Format

Use `templates/manual-config-debt-report-template.md`. Recommendation value is exactly one of `block-next-slice` / `conditional-re-approval-required` / `no-block`. Conditional recommendations must name the specific approval decision required.

---

## 13. Handoff to Next Skill

**Stage 20 — Next-slice recommendation (`next-slice-recommender`).** Hand off: path to `manual-config-debt-report.md`; block / no-block status; list of items requiring human action before Stage 20.

- `no-block`: clean debt status passes to `next-slice-recommender`.
- `block-next-slice`: orchestrator stops at Stage 19 for human-directed burn-down.
- `conditional-re-approval-required`: orchestrator surfaces aged items, waits for re-approval, then proceeds.

State the ceiling policy in use, the recommendation, each dimension's pass/fail, new and resolved debt this slice, burn-down actions, aged items needing re-approval, and the referenced Issue IDs.
