# Manual Configuration Debt Report: <Slice Name>

| Field | Value |
|---|---|
| Slice ID / Name | `<slice-id>` / `<slice-name>` |
| Report Date | `<yyyy-mm-dd>` |
| Debt Ceiling Policy Source | `<file path, ADR, or user statement>` |
| Open / Resolved-this-slice / New-this-slice | `<count>` / `<count>` / `<count>` |

---

## Debt Ceiling Policy

Summarize the applicable policy and reference its source.

| Dimension | Threshold |
|---|---|
| Unresolved critical debt items | `0` (or custom) |
| Unresolved non-critical debt items | `3` (or custom) |
| Age limit without re-approval | `1 subsequent slice` (or custom) |

---

## Ceiling Check

| Dimension | Threshold | Current | Status |
|---|---|---|---|
| Unresolved critical | `<thr>` | `<count>` | `Pass / BLOCK` |
| Unresolved non-critical | `<thr>` | `<count>` | `Pass / BLOCK` |
| Age-limit violations (w/o re-approval) | `0` | `<count>` | `Pass / BLOCK / Review required` |

---

## Recommendation

**Recommendation:** `block-next-slice | conditional-re-approval-required | no-block`
**Rationale:** `<which dimension breached, or why all pass>`

---

## Open Debt Inventory

| Issue | Title | Severity | Surface | Opened | Slices Survived | Re-Approved? |
|---|---|---|---|---|---|---|
| `#<id>` | `<title>` | `Critical / Non-critical` | `Azure Portal / Power Platform / Copilot Studio / Foundry UI / Other` | `<date>` | `<count>` | `Yes / No / N/A` |

---

## New Debt This Slice

| Item | Surface | Issue Exists? | Issue ID | Risk if Not Source-Controlled |
|---|---|---|---|---|
| `<desc>` | `<surface>` | `Yes / No` | `#<id> or —` | `<risk>` |

> **Gap (per item without an Issue):** `<item>` — GitHub Issue required (via `github-issue-drafter`, human approval) before next slice begins.

---

## Debt Resolved This Slice

| Issue | Title | Resolution Evidence |
|---|---|---|
| `#<id>` | `<title>` | `<IaC merged / export committed / other>` |

---

## Burn-Down Actions

Complete only if any dimension is BLOCK or Review required.

| Priority | Action | Issue | Required Before |
|---|---|---|---|
| 1 | `<action>` | `#<id>` | `Next slice begins` |

---

## Aged Items Requiring Re-Approval

Complete only if age-limit violations exist.

| Issue | Title | Slices Survived | Re-Approval |
|---|---|---|---|
| `#<id>` | `<title>` | `<count>` | Yes — human must confirm carry-over |

---

## Related GitHub Issues

| Issue | Title | Status |
|---|---|---|
| `#<id>` | `<title>` | `Open / Closed this slice` |
