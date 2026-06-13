# GitHub Issue Record

*One block per issue. All fields required unless marked optional. No PHI, PII, secrets, tenant/subscription IDs, real candidate data, sensitive screenshots, raw eval transcripts, or Canadian-residency-restricted data in any field.*

---

## Issue Record: `<sequential number>`

**Status:** Created / Draft
**Created issue:** `#<number>` — `<URL>` or `N/A — draft`
**Draft reason:** `N/A — created` / `Requested draft mode` / `GitHub tooling unavailable` / `Duplicate status could not be checked` / `Sensitive or disclosure-risky publication` / `<other>`

**Title (summary):** `<concise, action-oriented — e.g., "Add French language quality eval for summarization endpoint">`
**Type:** `<canonical type from Process Doc §27>`
**Severity:** Critical / High / Medium / Low
**Applied labels:** `<comma-separated, or "N/A — draft">`
**Recommended labels unavailable:** `<comma-separated or "None">`

### Source trace
*Trace the issue to the source that caused it.*

| Field | Value |
|---|---|
| Related slice | `<slice-id>` — `<slice-name>` |
| Source artifact | `<traceability matrix / validation report / eval summary / manual evidence / deviation log / implementation finding / other>` |
| Source finding ID | `<finding ID, scenario ID, gap ID, or "N/A">` |

### Context
*1–3 sentences: what the slice implemented and why this was not resolved before merge.*
`<context>`

### Reason created
*One of: traceability gap / non-blocking eval failure / documentation gap / source-control debt / manual-config debt / architecture gap / residual risk / scope deferral / other (describe).*
`<reason>`

### Description
*Concrete detail — what is missing, wrong, or deferred.*
`<description>`

### Acceptance criteria
*At least one testable statement (not "issue is fixed").*

- [ ] `<criterion 1>`
- [ ] `<criterion 2>`

### Verification / re-test criteria
*What test, eval, or evidence demonstrates closure.*
`<verification approach>`

### Risk
*Risk if unresolved; explicit for security-risk and manual-config-debt types.*
`<risk statement>`

### Related evidence
*Eval artifact, test run, validation report, or manual evidence — by reference, not raw data.*
`<references or "none">`

### Related docs
*Architecture guideline, ADR, or current-state doc.*
`<references or "none">`

### Owner (if known)
`<role/team, or "TBD — requires human input">`

### Priority (if known)
`<priority, or "TBD — requires human input">`

---

*Issue creation is backlog tracking only. This record does not approve an ADR, accept residual risk, authorize release, approve merge, or commit delivery scope.*
