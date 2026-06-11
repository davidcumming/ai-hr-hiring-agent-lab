# Manual Evidence Summary: <Slice ID>

| Field | Value |
|---|---|
| Slice ID / Branch | `<slice-id>` / `<feature/branch-name>` |
| Summary Date | `<yyyy-mm-dd>` |
| Produced By | `manual-evidence-normalizer` |
| Source-Control Capture Report Ref | `<path>` |
| Raw Evidence Folder | `<path>` |
| Total Evidence Items | `<count>` |
| Status | `Complete / Gaps Present — see Gaps` |

---

## Evidence Inventory

| # | Evidence Item | Type | Surface | Configuration Area | Complete? |
|---|---|---|---|---|---|
| 1 | `<filename>` | `Screenshot / Export / Note / CLI output` | `Azure Portal / Power Platform / Copilot Studio / Foundry / Other` | `<area>` | `Yes / No — see Gaps` |

---

## Normalized Configuration Records

Repeat per manual configuration item:

| Field | Value |
|---|---|
| Configuration item | `<name>` |
| What changed | `<description>` |
| Surface / Resource / Environment | `<surface>` / `<exact name>` / `Dev / Test / Staging / Production` |
| Who / When changed | `<name or "not recorded">` / `<date or "not recorded">` |
| Why needed | `<slice requirement or implementation reason>` |
| Evidence reference | `<filename in evidence folder>` |
| In source control | `Yes / No / Partial` |
| Source-control debt risk | `Critical / High / Medium / Low` — `<rationale>` |
| Source-control recommendation | `<IaC / solution export / version-controlled config / script / not feasible — notes>` |
| Follow-up issue candidate | `Yes / No / Already exists — <#issue ref>` |

---

## Risk Classification Summary

| Risk Level | Count | Items |
|---|---|---|
| Critical | `<n>` | `<names>` |
| High | `<n>` | `<names>` |
| Medium | `<n>` | `<names>` |
| Low | `<n>` | `<names>` |

---

## Source-Control Debt Recommendations

| Item | Risk | Recommended Representation | Feasible Now? | Notes |
|---|---|---|---|---|
| `<name>` | `Critical / High / Medium / Low` | `<IaC / export / script / config file / other>` | `Yes / No / Partially` | `<notes>` |

---

## Follow-Up Issue Candidates

Candidates for `github-issue-drafter` at Stage 14 — do not create issues here.

| Item | Suggested Type | Priority | Notes |
|---|---|---|---|
| `<name>` | `source-control-debt / manual-config-debt / technical-debt` | `High / Medium / Low` | `<notes>` |

---

## Gaps and Clarification Requests

| # | Item | Gap Description | What Is Needed | Risk If Unresolved |
|---|---|---|---|---|
| G-001 | `<item>` | `<what is missing or unclear>` | `<what would resolve it>` | `High / Medium / Low` |

---

## Sensitive Data Handling

If any evidence contained credentials, PHI, PII, or sensitive business data:

| Item | Sensitive Data Type | Handling |
|---|---|---|
| `<item>` | `Credential / PHI / PII / Sensitive business data` | `Placeholder used / Excluded / Stored externally at <ref>` |
