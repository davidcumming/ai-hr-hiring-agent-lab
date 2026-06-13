# Source Control Config Capture Report

## 1. Report Metadata

| Field | Value |
|---|---|
| Slice ID | `<slice-id>` |
| Slice Name | `<slice-name>` |
| Date | `<yyyy-mm-dd>` |
| Agent / Author | `<agent-or-user>` |
| Branch | `<branch-name>` |
| Status | `Draft / Final / Gaps Outstanding` |
| Prior Debt Issues | `<GitHub Issue numbers or "None">` |

---

## 2. Config Surface Summary

Every config area expected to change, with capture state. **Capture State** = `Committed` / `Partially Committed` / `Not Committed — Export Unsupported` / `Not Committed — Debt`. **Change Type** = `Added / Modified / Deleted / Unchanged`.

| Surface | Resource / Area | Change Type | Capture State |
|---|---|---|---|
| Azure services | `<resource name / type>` | | |
| Power Platform | `<solution / component>` | | |
| Copilot Studio | `<agent / topic / setting>` | | |
| Azure AI Foundry | `<project / deployment / index>` | | |
| GitHub Actions / pipelines | `<workflow / environment>` | | |
| Other | `<area>` | | |

---

## 3. Committed Config Assets

All IaC, solution files, and SDK-defined config files committed in this branch.

| Asset | File Path in Branch | Resource It Represents | Notes |
|---|---|---|---|
| `<asset>` | `<path/to/file>` | `<resource / service>` | `<notes>` |

---

## 4. Gaps Table

Every config item not fully committed.

| Item | Surface | Feasible to Source-Control? | Classification | Reason / Platform Limitation | Recommended Treatment |
|---|---|---|---|---|---|
| `<item>` | `<surface>` | `Yes / No / Partially / Unknown` | `Debt / Export Unsupported / Partially Captured / Under Investigation` | `<reason>` | `GitHub Issue / manual-config-evidence-capture / Monitor / Investigate` |

---

## 5. Manual-Config Debt Candidates

Items to pass to `manual-config-evidence-capture`, with enough detail to identify and scope each resource.

| Item | Surface | Resource / Setting Name | Environment | Why Not Source-Controlled | Evidence Required |
|---|---|---|---|---|---|
| `<item>` | `<surface>` | `<resource>` | `<env>` | `<reason>` | `Screenshot / Export / Notes / Other` |

> If none: `None identified in this slice.`

---

## 6. GitHub Issue Tracking Candidates

Recommended for feasible-but-omitted debt. Pass to `github-issue-drafter` to create safe tracking issues or draft when publication/tooling requires it.

| Title or Issue Ref | Type | Severity | Rationale | Related Item |
|---|---|---|---|---|
| `<title or #issue>` | `manual-config-debt` | `High / Medium / Low` | `<rationale>` | `<item from Gaps Table>` |

> If none: `No issues recommended for this slice.`

---

## 7. Known Platform Limitations

Platform-level export gaps that prevented capture — not agent errors or debt.

| Platform | Area | Limitation Description | Expected Future Resolution? |
|---|---|---|---|
| `<platform>` | `<area>` | `<what cannot be exported and why>` | `Yes / No / Unknown` |

> Example: Power Platform connection references cannot be source-controlled with premium connectors outside a managed environment; manual evidence is required.

---

## 8. Handoff Summary

**To `manual-config-evidence-capture`:** items needing manual evidence — `<list or "None">`. Context: Slice ID `<slice-id>`; platform limitations `<list or "None">`.

**To `deterministic-test-author` (Stage 8):** committed config assets tests may reference — `<list key IaC/config files>`.

**To Closeout:** report location `docs/delivery/slices/<slice-id>/implementation/source-control-config-capture-report.md`; debt candidate count `<N>`; recommended issue count `<N>`; platform limitation count `<N>`.
