# Manual Config Evidence Summary

## 1. Report Metadata

| Field | Value |
|---|---|
| Slice ID | `<slice-id>` |
| Slice Name | `<slice-name>` |
| Date | `<yyyy-mm-dd>` |
| Agent / Author | `<agent-or-user>` |
| Source Control Capture Report | `docs/delivery/slices/<slice-id>/implementation/source-control-config-capture-report.md` |
| Status | `Draft / Evidence Pending / Complete` |
| Redaction Concerns | `None / See Section 6` |

---

## 2. Evidence Register

One row per config item that cannot be source-controlled. Link screenshots/exports by relative path.

| # | Item | Surface | Resource / Component Name | Environment | Evidence Status | Evidence File(s) | Notes Ref |
|---|---|---|---|---|---|---|---|
| 1 | `<config item>` | `Azure / Power Platform / Copilot Studio / Foundry / Other` | `<resource>` | `<dev / staging / prod>` | `Complete / Partial / Evidence Pending` | `evidence/screenshots/<file>` | See §3.1 |

---

## 3. Notes

One sub-section per item needing settings descriptions beyond screenshots.

### 3.1 `<Item Name>`

**Resource:** `<resource>` — **Environment:** `<environment>`

| Setting Name | Value / Description | Notes |
|---|---|---|
| `<setting>` | `<value or description — never a credential>` | `<context>` |

> Add 3.2, 3.3, etc. for each item requiring notes.

---

## 4. Risk Summary

Classify each item by the risk it carries as manual configuration.

| # | Item | Risk Level | Risk Rationale | Source-Control Migration Feasible? | Expected Timeline |
|---|---|---|---|---|---|
| 1 | `<item>` | `High / Medium / Low` | `<why>` | `Yes / No / Partially / Unknown` | `<timeline or N/A>` |

**Risk guidance:** **High** — security, identity, permissions, PHI/PII handling, approvals, external sharing, or audit logging; capture completely and flag for closeout review. **Medium** — functional behaviour (routing, workflow, integration endpoints); important for reproducibility. **Low** — UI labels, minor display settings, non-functional defaults; acceptable as manual with periodic review.

---

## 5. Recommended GitHub Issues

For items where source control is feasible now or soon. Do **not** create without human approval.

| Title | Type | Severity | Rationale | Related Evidence Item # |
|---|---|---|---|---|
| `<title>` | `manual-config-debt` | `High / Medium / Low` | `<rationale>` | `<#>` |

> If none: `No issues recommended for this slice.`

---

## 6. Redaction Concerns

Screenshots/notes containing sensitive data requiring redaction before repository storage.

| File / Note | Concern | Status | Action Required |
|---|---|---|---|
| `<filename or note ref>` | `Visible API key / PII / PHI / Other` | `Unresolved / Resolved` | `<request redacted replacement / remove field / other>` |

> If none: `No redaction concerns identified.`

---

## 7. Handoff Summary

### To `manual-evidence-normalizer` (Stage 12)

- Evidence summary: `docs/delivery/slices/<slice-id>/implementation/manual-config-evidence-summary.md`
- Screenshots: `docs/delivery/slices/<slice-id>/evidence/screenshots/`
- Exports: `docs/delivery/slices/<slice-id>/evidence/exports/`
- Pending redaction concerns: `<None / see Section 6>`
- `Evidence Pending` items: `<list or "None">`

### Closeout Blockers

| # | Item | Reason | Required Action |
|---|---|---|---|
| `<n>` | `<item>` | `Evidence Pending — high-risk item` | `Team must provide evidence before closeout` |

> If none: `No closeout blockers identified.`

### Evidence Counts

| Status | Count |
|---|---|
| Complete | `<N>` |
| Partial | `<N>` |
| Evidence Pending | `<N>` |
| **Total items** | `<N>` |
