# Current-State Reconciliation: <Slice ID> — <Slice Name>

| Field | Value |
|---|---|
| Slice ID | `<slice-id>` |
| Branch / Base | `<feature/branch-name>` / `main` |
| Date | `<yyyy-mm-dd>` |
| Produced By | `current-state-reconciler` |
| Status | `Draft / Applied / Blocked` |

**Inputs reviewed:** git diff `<ref>`, commit log, slice spec (intent only), implementation summary, deviation log `<or N/A>`, test/eval summaries, manual evidence `<or N/A>`, approved ADRs `<IDs or N/A>`.

---

## Branch-Diff Analysis

### Change Summary by Category

For each category, list `Area | Change Description | Source-Controlled? (where relevant) | Source Evidence (diff/impl-summary ref)`:

- **User-Visible / Agent Behaviour**
- **Backend / Service / API**
- **Infrastructure / IaC / Configuration** (include Source-Controlled? = Yes/No/Partial)
- **Power Platform / Copilot Studio / Foundry** (include Source-Controlled?)
- **Data / State / Persistence**
- **Security / Permissions / Identity**
- **Integration / External-System**
- **Test and Eval**
- **Documentation-Only**

### Documentation Impact Map

| Change Area | Affected Current-State Doc Sections | Affected Actual-Architecture Sections | Update Type |
|---|---|---|---|
| `<area>` | `<section(s)>` | `<section(s) or N/A>` | `Additive / Corrective / Removal / No change` |

### Manual-Evidence Gaps

| Area / Surface | What Changed | Evidence Type Available | Follow-Up Required |
|---|---|---|---|
| `<area>` | `<description>` | `Screenshot / Export / Notes / None` | `Yes / No / Issue ref` |

### Known-Limitation Impacts

| Existing / New Limitation | Status After This Branch | Source Evidence |
|---|---|---|
| `<ref>` | `Resolved / Partially resolved / Unchanged / New` | `<ref>` |

### Deviations from Slice Spec

| Spec Intent | Actual Implementation | Deviation Log Ref | Impact on Docs |
|---|---|---|---|
| `<spec item>` | `<what was built>` | `<ref or N/A>` | `<impact>` |

### Blockers / Assumptions

| ID | Item | Impact / Risk | Required Action / Basis |
|---|---|---|---|
| BD-001 | `<blocker>` | `Blocks Section B / C / Both` | `<action>` |
| AS-001 | `<assumption>` | `<risk if wrong>` | `<basis>` |

---

## Current-State Doc Update Plan

### Affected Documentation Files

| File Path | Nature of Change | Priority |
|---|---|---|
| `<path>` | `Additive / Corrective / Removal of stale content / Structural` | `High / Medium / Low` |

### Section-Level Update Plan

Repeat per affected section:

| Field | Content |
|---|---|
| Document / Section | `<path>` — `<heading>` |
| Current content summary | `<what is there now>` |
| Required change | `<what changes and why>` |
| Change type | `Additive / Corrective / Removal / Structural` |
| Source evidence | `<diff / impl-summary / manual-evidence / ADR ref>` |
| Checks | Confirmed: no slice-language; no copied aspirational text; no unimplemented feature shown as implemented |
| Updated text (draft) | `<present-tense, slice-agnostic draft>` |

### Sections Confirmed Unchanged

| File Path | Section | Reason No Change Required |
|---|---|---|

### Known Limitations — Updates

| Register Path | Action | Description | Source Evidence |
|---|---|---|---|
| `<path>` | `Add / Update / Remove / No change` | `<description>` | `<ref>` |

### Gaps, Assumptions, and Follow-Up Issue Candidates

| ID | Item | Affected Section | Risk | Treatment |
|---|---|---|---|---|
| DG-001 | `<gap/assumption>` | `<section>` | `High / Medium / Low` | `Blocker / Follow-up issue candidate / Accept as-is` |

Follow-up issue candidates (pass to `github-issue-drafter`, Stage 14): `Candidate | Type (documentation-gap / source-control-debt / technical-debt) | Priority | Notes`.

---

## Actual-Architecture Update

| Field | Value |
|---|---|
| Actual Architecture Document | `<path>` |
| Status | `Draft / Applied / Blocked` |

**Architecture change summary** (present tense: "The system now uses…"): `<brief description of what changed at the architecture level>`

### Components Added

| Component | Type | Description | Source Evidence | Source-Controlled? |
|---|---|---|---|---|
| `<name>` | `Service / API / Connector / Agent / Model / Store / IaC / Other` | `<desc>` | `<diff / ADR ref>` | `Yes / No / Partial` |

### Components Modified

| Component | What Changed | Reason | Source Evidence | ADR Reference |
|---|---|---|---|---|

### Components Removed or Deprecated

| Component | Status | Reason | Source Evidence |
|---|---|---|---|
| `<name>` | `Removed / Deprecated / Replaced by <X>` | `<reason>` | `<ref>` |

### Integration / Data Flow Changes

| Integration / Flow | Change Description | Direction | Source Evidence |
|---|---|---|---|
| `<name>` | `<desc>` | `Added / Modified / Removed` | `<ref>` |

### Security, Identity, and Permissions Changes

| Area | Change Description | Source Evidence |
|---|---|---|

### Manual-Configuration Architecture Notes

Components that are part of actual architecture but **not yet source-controlled** — each needs a follow-up issue reference.

| Component / Configuration | Surface | Description | Follow-Up Issue Ref |
|---|---|---|---|
| `<name>` | `Azure Portal / Power Platform / Copilot Studio / Foundry / Other` | `<desc>` | `<#issue or "candidate for drafter">` |

### Known Architecture Limitations (Updated)

Gaps between guidelines and what exists (distinct from feature-level limitations).

| Limitation | Description | Guideline Gap? | Follow-Up Issue Candidate |
|---|---|---|---|
| `<limitation>` | `<desc>` | `Yes / No / Unknown` | `Yes / No` |

### Architecture Guideline Cross-References (read-only)

Guidelines were **not** changed here. If a slice ADR requires a guideline change, that is delegated to `architecture-guideline-updater` (Stage 6, post-ADR-approval).

| Guideline Section | Compliance Status | Notes |
|---|---|---|
| `<section>` | `Compliant / Gap (see ADR) / Not applicable` | `<notes>` |
