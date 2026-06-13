# Manual Configuration Debt Report: E5 Copilot Studio Registration Smoke

| Field | Value |
|---|---|
| Slice ID / Name | `slice-e5-copilot-studio-registration-smoke` / E5 Copilot Studio Registration Smoke |
| Report Date | 2026-06-13 |
| Agent Role | `governance-and-process-improvement-agent` |
| Skill | `.claude/skills/manual-config-debt-monitor/SKILL.md` |
| Debt Ceiling Policy Source | `standards/azure-development-standards/gentech_slice_based_development_process_revised.md` section 17.3 |
| Open / Resolved-this-slice / New-this-slice | 4 related open follow-ups / 0 / 0 new issues in this cleanup |

## Debt Ceiling Policy

The default ceiling from Process Doc section 17.3 is used:

| Dimension | Threshold |
|---|---|
| Unresolved critical manual-config/source-control debt | 0 |
| Unresolved non-critical manual-config/source-control debt | 3 |
| Age limit without re-approval | More than 1 subsequent slice |

This report classifies issues #1, #2, and #3 as the E5 manual-config/source-control-adjacent open debt set. Issue #4 is tracked alongside the debt report because it records current-state documentation drift, but it is not counted toward the manual-config/source-control debt ceiling.

## Ceiling Check

| Dimension | Threshold | Current | Status |
|---|---:|---:|---|
| Unresolved critical | 0 | 0 | Pass |
| Unresolved non-critical | 3 | 3 | Pass |
| Age-limit violations without re-approval | 0 | 0 | Pass |

## Recommendation

**Recommendation:** `no-block`

**Rationale:** E5 leaves three non-critical manual-config/source-control-adjacent follow-ups open (#1, #2, #3), which is within the default ceiling. Issue #3 is high severity because lab-only Function key/header auth is not production identity, but the E5 artifacts do not mark it as critical and do not claim production-like identity. Issue #4 is documentation drift and should be fixed, but it is not counted as manual-config/source-control debt for the ceiling.

This recommendation does not close, delete, assign, reprioritize, or milestone any GitHub issue. It does not approve residual risk, ADRs, merge, release, or carry-over beyond the policy.

## Open Related Issue Inventory

| Issue | Title | Severity | Counted for ceiling? | Surface | Opened | Slices Survived | Re-approved? |
|---|---|---|---|---|---|---:|---|
| #1 | E6: Add explicit Copilot topic/workflow variable storage for `evaluation_id` | Medium | Yes | Copilot Studio topic/workflow | 2026-06-13 | 0 | N/A |
| #2 | Document Power Platform connection staleness / recreate-after-connector-change runbook | Medium | Yes | Power Platform / Copilot connection | 2026-06-13 | 0 | N/A |
| #3 | Replace lab-only Function key plus fake `X-Lab-*` headers with Entra delegated identity and role mapping | High, not marked critical | Yes | Power Platform connection / Azure Functions auth | 2026-06-13 | 0 | N/A |
| #4 | Reconcile current-state docs after E5 Copilot Studio registration smoke | Medium | No | Current-state documentation | 2026-06-13 | 0 | N/A |

## E5 Manual Configuration Debt Inventory

| Debt item | Surface | Source-control status | Issue ref | Risk if not resolved |
|---|---|---|---|---|
| Copilot Studio agent exists only as portal/low-code state. | Copilot Studio | Not source-controlled in E5 | #1 for workflow-state hardening; future ALM/export work remains outside E5 | Reproducibility depends on note-based evidence and manual portal state. |
| Dataverse provisioning and role assignment are manual evidence only. | Power Platform / Dataverse | Not source-controlled in E5 | #4 tracks doc drift; no new issue from this cleanup | Future operators may not know that Dataverse and available roles must be checked before agent work. |
| Custom connector import has source Swagger, but portal import and host correction are manual evidence. | Power Apps custom connector | API definition is source-controlled; portal import and host correction are not | #2 for stale connection guidance | The repo shows the API definition but cannot replay the portal import or host correction by itself. |
| Power Platform/Copilot connection contains secret credential binding and cannot be committed. | Power Platform / Copilot connection | Credential binding is intentionally not committed | #2, #3 | Tool calls may depend on unversioned connection state; secrets must remain outside repo artifacts. |
| Tool/action input mappings are manual evidence only. | Copilot Studio tool/action | Not source-controlled in E5 | #1 | Missing or changed mappings can break headers, body fields, and identifier handoff. |
| Topic/workflow orchestration is not robust yet. | Copilot Studio topic/workflow | Not implemented/source-controlled in E5 | #1 | `evaluation_id` handoff remains unreliable until explicit topic/workflow variable storage exists. |
| Connection staleness runbook is not documented yet. | Power Platform / Copilot connection | Not source-controlled in E5 | #2 | Operators may miss the need to refresh or recreate connections after connector host/security changes. |
| Lab-only Function key/header auth replacement remains future work. | Azure Functions / Power Platform connection | Lab-only auth remains manual evidence and secret-bound connection state | #3 | Production-like identity, authorization, and audit claims remain out of scope. |
| Current-state documentation drift remains open. | Current-state docs | Source-controlled docs not updated in E5 | #4 | Readers may confuse E4 source-controlled readiness with E5 note-evidenced Copilot Studio registration smoke. |

## New Debt This Cleanup

No new manual-config debt was created by this governance cleanup. This cleanup adds documentation only and does not modify Azure, Power Platform, Copilot Studio, GitHub issues, current-state docs, or application code.

## Debt Resolved This Cleanup

No debt was resolved or closed. All issue references remain open tracking records.

## Burn-Down Actions

| Priority | Action | Issue | Required Before |
|---:|---|---|---|
| 1 | Implement explicit Copilot topic/workflow variable storage for `evaluation_id`. | #1 | Reliable workflow interaction after E5 |
| 2 | Document and validate connection refresh/recreate guidance after connector host/security changes. | #2 | Repeated connector changes |
| 3 | Replace lab-only Function key plus fake `X-Lab-*` headers with Entra delegated identity and role mapping. | #3 | Production-like identity or audit claims |
| 4 | Reconcile current-state docs to distinguish E4 readiness from E5 note-evidenced registration smoke. | #4 | Current-state documentation accuracy |

## Aged Items Requiring Re-Approval

None. Issues #1, #2, #3, and #4 were opened from E5 and have not survived more than one subsequent slice.

## Related GitHub Issues

| Issue | URL | Status |
|---|---|---|
| #1 | https://github.com/davidcumming/ai-hr-hiring-agent-lab/issues/1 | Open |
| #2 | https://github.com/davidcumming/ai-hr-hiring-agent-lab/issues/2 | Open |
| #3 | https://github.com/davidcumming/ai-hr-hiring-agent-lab/issues/3 | Open |
| #4 | https://github.com/davidcumming/ai-hr-hiring-agent-lab/issues/4 | Open |
