---
name: manual-config-evidence-capture
description: Captures structured evidence for portal and low-code config changes that cannot yet be source-controlled. Use during config capture (Stage 7) when portal/low-code changes are not source-controllable.
---
# Skill: Manual Config Evidence Capture

**Used at:** Stage 7 — Implementation & config capture (Orchestration Map §3 stage table), conditional — fires only when portal or low-code configuration is not yet source-controllable.
**Execution model:** `inline`
**Supports:** Process Doc §17 Manual Portal and Configuration Evidence, §29 Slice Closeout Package

---

## 1. Purpose

Capture structured evidence for portal-based, low-code, and other configuration changes that cannot currently be represented in source control, producing a raw evidence summary and configuration register that travel with the slice through closeout. This is the immediate companion to `source-control-config-capture`: that skill establishes what *is* in source control; this one records what is *not* — and ensures it is not lost. It captures and organizes raw evidence so that, at Stage 12, `manual-evidence-normalizer` can normalize it for the closeout package — this skill does not perform that normalization. It recommends; it does not approve manual-config debt or authorize merge without human sign-off.

---

## 2. When to Use This Skill

Conditional. Fires when `source-control-config-capture` hands off manual-config debt candidates, or when portal/low-code changes have been made (Azure portal, Power Platform admin center, Copilot Studio canvas, Foundry portal) that are not yet in source control — e.g. solution exports missing connection references or environment variables, portal-only Copilot Studio topics/channels, portal-only Foundry deployment or evaluation settings. Do not run if there are no manual-config candidates and no portal changes.

---

## 3. Do Not Use This Skill For

- Normalizing/restructuring evidence for closeout (`manual-evidence-normalizer`, Stage 12), tracking cross-slice debt (`manual-config-debt-monitor`, Stage 19), or IaC/source-control capture (`source-control-config-capture`).
- Modifying the configuration being evidenced, creating GitHub Issues (recommend only), or deciding which surfaces should remain portal-only.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | `source-control-config-capture` output | Required | Manual-config debt candidates list and platform limitations. |
| 2 | Portal screenshots | Required | Provided by whoever made the change, organized by resource. |
| 3 | Portal-exported files | Recommended | YAML/JSON where partial export is supported. |
| 4 | Human-written notes | Recommended | Settings/values/resource names for items that cannot be captured otherwise. |
| 5 | Non-secret resource identifiers | Required | Resource/environment/tenant names — never secrets, keys, or passwords. |
| 6 | Slice spec | Required | Which configurations are expected; whether anything is missing. |
| 7 | Related GitHub Issues | Recommended | Prior manual-config debt on the same resources. |

If screenshots or notes are not yet available, produce a partial register with placeholders, mark status `Evidence Pending`, and do not proceed to closeout in that state without human acknowledgment.

---

## 6. Source Authority Rules

Manual evidence never overrides committed code or IaC. Where committed config and manual evidence conflict, surface the conflict to the human — do not resolve it silently. Whether evidence is sufficient for closeout is the human release authority's call at Stage 16, after `manual-evidence-normalizer` normalization.

---

## 7. Process Steps

1. **Review the manual-config candidates list.** For each item from the `source-control-config-capture` report, confirm resource name and environment, why source control is not feasible (platform limitation vs. feasible-but-not-done), and what evidence is expected. Ask the team to clarify any missing or unclear candidates.
2. **Collect evidence for each item.** Request/receive screenshots of the relevant portal pages and any partial exports (Power Platform / Copilot Studio YAML where available); collect human-written notes for settings not visible in screenshots; record identifiers (names, GUIDs, environment names) sufficient to locate the resource. Mark status per item:

   | Status | Meaning |
   |---|---|
   | `Complete` | All expected evidence collected. |
   | `Partial` | Some evidence collected; specific gaps noted. |
   | `Evidence Pending` | No evidence yet; placeholder recorded. Human must acknowledge before closeout. |

3. **Check redaction requirements.** Review all screenshots/notes for visible credentials, keys, tokens, or passwords (request redacted replacements); PHI/PII beyond what is needed to identify the resource (request redaction); sensitive business data. Flag unresolved redaction concerns. Resource names and GUIDs are safe to record; secrets are not.
4. **Produce the evidence summary** using `templates/manual-config-evidence-template.md`: metadata, evidence register, file references, notes, risk summary, source-control follow-up recommendations, handoff notes for `manual-evidence-normalizer`.
5. **Recommend follow-up actions.** Items where source control is feasible now/soon → recommend a GitHub Issue (type `manual-config-debt`). Platform-limitation items → note expected resolution timeline if known. `Evidence Pending` high-risk items → flag as closeout blockers.

Never store credentials, raw secrets, or regulated personal data in any evidence file. This skill recommends GitHub Issues; it does not create them or approve debt as a permanent substitute for source control. See AGENTS.md cross-cutting rules (Authority and human gates; Source of truth; Evidence, privacy, context).

---

## 8. Output Location

Evidence summary: `docs/delivery/slices/<slice-id>/manual-config-evidence-summary.md`. Screenshots: `docs/delivery/slices/<slice-id>/evidence/screenshots/`. Exports: `docs/delivery/slices/<slice-id>/evidence/exports/`. Follow the project's convention if different; reference the summary location in the closeout package.

---

## 9. Output Format

Use `templates/manual-config-evidence-template.md`. No credential values, raw secrets, or sensitive personal data in any section.

---

## 10. Quality Bar

Before handoff, confirm:

- Every manual-config candidate is in the evidence register; scope matches the slice spec's expected config changes; nothing silently omitted.
- Evidence status is recorded for each item; every `Complete` item has a screenshot, export, or sufficient notes; every `Partial` item specifies what is missing.
- `Evidence Pending` items are explicitly acknowledged; high-risk ones are listed as closeout blockers.
- All referenced screenshot/export files exist at the stated paths and show the relevant settings (not just page titles).
- Notes identify resource name and environment and are sufficient for `manual-evidence-normalizer` to produce a structured closeout entry without further research.
- No credentials, keys, passwords, connection strings, SAS tokens, PHI, or PII (beyond non-sensitive identifiers) appear anywhere; all redaction concerns are identified and unresolved ones flagged for team action.
- Every item has a risk level (High / Medium / Low) with specific rationale; high-risk items have a GitHub Issue recommendation.
- GitHub Issues are recommended (type `manual-config-debt`), not created, with no duplicates of open issues.
- The report does not normalize evidence, does not approve debt as permanent, and does not claim merge readiness; handoff specifies evidence file locations and lists closeout blockers; evidence counts are correct.

---

## 11. Failure Modes to Avoid

- Treating the evidence summary as a permanent substitute for source control — it is a bridge, not an endpoint.
- Accepting incomplete evidence without flagging it, or proceeding past unacknowledged high-risk `Evidence Pending` items.
- Storing visible credentials in screenshots or notes (a repository security risk); confusing resource identifiers (safe) with secrets (not safe).
- Skipping Copilot Studio or Power Platform evidence because they are "low-code" — these are exactly where manual-config debt accumulates.

---

## 13. Handoff to Next Skill

- **Primary:** `deterministic-test-author` (Stage 8) — reference the evidence summary as context for tests that depend on manually-configured resources (e.g. a Copilot Studio channel or a Power Platform connection reference).
- **Stage 12 consumer:** `manual-evidence-normalizer` — receives this raw summary, screenshots, and exports; pass the summary location, file references, and any outstanding redaction concerns.

Downstream: `closeout-package-builder` (Stage 14), `definition-of-done-validator` (Stage 15, confirms manual evidence is complete), `manual-config-debt-monitor` (Stage 19, ingests risk summary and issue references). Recommend proceeding to Stage 8 or addressing pending evidence first. The agent must not approve manual-config debt as permanent, nor approve merge readiness.
