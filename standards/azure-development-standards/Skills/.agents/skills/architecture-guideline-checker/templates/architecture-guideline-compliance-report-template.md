# Architecture Guideline Compliance Report: <Slice Name>

## 1. Report Metadata

| Field | Value |
|---|---|
| Slice ID | `<slice-id>` |
| Slice Name | `<slice-name>` |
| Report Date | `<yyyy-mm-dd>` |
| Report Author | `<agent/user>` |
| Implementation Plan Reference | `<path or reference>` |
| Architecture Guidelines Version | `<version or date>` |
| ADR References Reviewed | `<ADR IDs and titles, or "None">` |
| Status | `Draft / Final` |

---

## 2. Compliance Surface Summary

Every planned item assessed (confirms scope).

| Area | Description | Plan Section |
|---|---|---|
| `<area>` | `<what was checked>` | `<plan section>` |

---

## 3. Compliance Findings

One row per planned item or pattern. Finding types: `Compliant` (matches guideline + any ADR); `Violation` (contradicts a guideline — **blocking**); `Not covered` (no governing guideline — flag for `adr-gap-detector`); `Ambiguous` (guideline unclear here); `ADR extends guideline` (an approved ADR governs this — record reference).

| # | Planned Item / Pattern | Finding Type | Guideline Section | ADR Reference | Rationale |
|---|---|---|---|---|---|
| C-001 | `<item>` | `<finding type>` | `<§X.Y Title>` | `<ADR-NNN or N/A>` | `<brief rationale>` |

---

## 4. Violations (Blocking)

Only if "Violation" findings exist. Must be resolved before coding.

| ID | Planned Item | Violation Description | Guideline Section Violated | Required Resolution |
|---|---|---|---|---|
| V-001 | `<item>` | `<what it violates and why>` | `<§X.Y Title>` | `<revise plan / request ADR / human decision>` |

> If none: "No violations found."

---

## 5. Ambiguities (Clarification Required)

Only if "Ambiguous" findings exist.

| ID | Planned Item | Ambiguity Description | Guideline Section | Clarification Needed From |
|---|---|---|---|---|
| A-001 | `<item>` | `<what is unclear>` | `<§X.Y Title>` | `Human / ADR process / guideline owner` |

> If none: "No ambiguities found."

---

## 6. Not-Covered Areas (ADR Gap Candidates)

Only if "Not covered" findings exist. Inputs to `adr-gap-detector`.

| ID | Planned Item / Pattern | Gap Description | Used in Actual Architecture? | Priority |
|---|---|---|---|---|
| G-001 | `<item>` | `<not covered by any guideline or ADR>` | `Yes / No / Unknown` | `High / Medium / Low` |

> If none: "No not-covered areas found."

---

## 7. Actual-Architecture Drift Flags

Where the plan differs from or extends the actual architecture document, unexplained by the plan or approved ADRs.

| # | Planned Item | Actual Architecture State | Drift Description | Recommended Follow-Up |
|---|---|---|---|---|
| D-001 | `<item>` | `<what the actual arch doc says>` | `<the drift>` | `<ADR gap / guideline update / no action>` |

> If none: "No actual-architecture drift identified."

---

## 8. Recommended Guideline Update Notes

Guideline gaps worth formalizing even if not blocking — recommendations, not approvals.

| Area | Note | Suggested Next Step |
|---|---|---|
| `<area>` | `<what is missing>` | `<log as process debt / raise ADR / defer>` |

> If none: "No guideline update recommendations at this time."

---

## 9. Compliance Verdict

Select one: `Clear` (all compliant; no violations/ambiguities/not-covered) / `Violations found` / `ADR check required` / `Blocked pending clarification`.

### Verdict

`<verdict>`

### Verdict Rationale

`<brief explanation>`

---

## 10. Recommended Next Step

| Verdict | Next Step |
|---|---|
| Clear | Stage 7 — Implementation & config capture |
| Violations found | Revise plan or initiate ADR process; re-run after resolution |
| ADR check required | Run `adr-gap-detector` for Section 6 items; coding paused |
| Blocked pending clarification | Human clarification on Section 5 ambiguities; re-run after resolved |

### Handoff Notes

`<what the next skill or human needs to know>`
