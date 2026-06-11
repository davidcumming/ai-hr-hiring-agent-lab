---
name: manual-evidence-normalizer
description: Normalizes screenshots, portal notes, and raw manual config evidence into a structured, closeout-ready record. Use at Stage 12 when manual evidence captured at Stage 7 must enter the closeout package.
---
# Skill: Manual Evidence Normalizer

**Used at:** Stage 12 — Current-state reconciliation (Orchestration Map §3 stage table), conditional — fires only when manual evidence exists and must enter closeout
**Execution model:** `inline`
**Supports:** Process Doc §17 Manual Portal and Configuration Evidence, §29 Slice Closeout Package

---

## 1. Purpose

Normalize screenshots, portal notes, and raw manual configuration evidence (captured during coding at Stage 7 by `manual-config-evidence-capture`) into a structured, closeout-ready evidence record that satisfies the merge-readiness requirements in Process Doc §17.2, can be consumed by `current-state-reconciler`, and clearly identifies source-control debt for `manual-config-debt-monitor`. Record only what the evidence demonstrably shows — never infer settings not visible or explicitly described.

---

## 3. Do Not Use This Skill For

- Capturing new manual evidence — that is `manual-config-evidence-capture` at Stage 7.
- Updating current-state documentation or actual architecture — that is `current-state-reconciler`.
- Making configuration changes or creating GitHub Issues — this is a documentation/evidence skill; produce issue candidates only.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Raw manual evidence files | Yes | Screenshots, portal notes, exported configs, free-text descriptions |
| 2 | Configuration descriptions | Yes | What was configured, where, by whom, why |
| 3 | Resource names | Yes | Azure resources, Power Platform environments, Copilot Studio bots, Foundry projects |
| 4 | Environment details | Yes | Dev / test / prod per manual change |
| 5 | Source-control capture report | Yes | From `source-control-config-capture` — what is and is not in source control |
| 6 | Related implementation branch | Yes | Links evidence to the correct slice/branch |
| 7 | Related GitHub Issues | If exists | Issues already created for this manual config |

Review only what is visible in screenshots. Do not infer or guess. If evidence is insufficient, list the gap and request clarification — do not leave fields blank or fabricate.

---

## 6. Source Authority Rules

Manual evidence is an exception path (Process Doc §17), never equivalent to source control for compliance. The repository and `source-control-config-capture` output define what is source-controlled; the raw evidence defines what was manually configured. Do not infer settings not visible or explicitly described in the provided evidence.

---

## 7. Process Steps

1. **Inventory raw evidence.** For each item, identify what it is (screenshot, export, note, CLI output), which Microsoft surface it relates to, the configuration area it covers, and whether it provides enough information for a complete record. Flag incomplete items immediately — note gaps rather than guessing.
2. **Normalize each evidence item** into a structured record (template fields): what changed; where (resource, environment, surface); who changed it (if known); why (linked to slice intent/implementation reason); evidence reference by file path; whether it is in source control; risk if not source-controlled; follow-up issue reference or candidate.
3. **Classify source-control debt risk** per item:

   | Risk | Criteria |
   |---|---|
   | Critical | Production-affecting; no fallback if lost; security/compliance relevant |
   | High | Feature-affecting, not yet in source control; recovery requires manual rework |
   | Medium | Non-critical but affects reproducibility; source-control representation is feasible |
   | Low | Cosmetic or transient; loss impact minor |

   Flag Critical and High as source-control debt candidates requiring GitHub Issues.
4. **Produce source-control debt recommendations** for each Critical/High item: recommended representation (IaC, solution export, script, version-controlled config), whether feasible now or future work, and whether a GitHub Issue candidate should be raised (candidate only).
5. **Write the normalized summary** combining all records. It must cover every manual-config item from this branch, contain no inferred settings, include risk classification and source-control debt recommendations per item, and reference all screenshots/exports by path (never embed sensitive content).

---

## 9. Output Format

Use `templates/manual-evidence-summary-template.md`. Write the summary to `docs/delivery/slices/<slice-id>/manual-evidence-summary.md`; reference evidence files at their captured locations (do not move or rename them). The final response includes: count of items normalized; items by surface; risk classification counts (Critical/High/Medium/Low); source-control debt recommendations; follow-up issue candidates; gaps; the summary file path; and confirmation it is ready for `current-state-reconciler` and `closeout-package-builder`.

---

## 10. Quality Bar

Before handoff, confirm:

- Every manual-config item from the source-control capture report is represented; no item silently omitted.
- Every raw evidence item has a normalized record or a documented gap.
- No settings were inferred or guessed — every value is traceable to provided evidence.
- No sensitive credentials, PHI, or PII are present (replaced with placeholders or excluded, with a note).
- All screenshot/export references are valid file paths, not embedded content.
- Every record carries a Critical/High/Medium/Low risk classification; Critical and High items have a rationale.
- Every Critical/High item has a concrete source-control recommendation with feasibility assessed.
- No manual config is approved as permanent without a debt classification and follow-up issue candidate.
- Gaps are listed explicitly; no configuration change was made and no evidence was fabricated.
- Risk counts and debt recommendations are available for downstream skills; handoff confirmed.

---

## 11. Failure Modes to Avoid

- **Inferring settings not visible in evidence** — record only what is demonstrably present.
- **Omitting high-risk items** — cross-check against the source-control capture report so hidden operational risk does not accumulate.
- **Including credentials or PHI** — replace with placeholder text and note what was captured without including the value.

---

## 13. Handoff to Next Skill

Output is consumed by `current-state-reconciler` (Stage 12, same stage — uses normalized evidence to document manual-config components) and `closeout-package-builder` (Stage 14 — includes the summary in the closeout package).

Pass forward: the normalized summary file path; the risk classification counts (for the closeout risk summary); the source-control debt recommendation list; the follow-up issue candidates; any gaps requiring clarification.
