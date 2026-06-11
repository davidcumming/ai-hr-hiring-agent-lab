# Strategic Documentation Update Recommendations: <Slice Name>

| Field | Value |
|---|---|
| Slice ID / Name | `<slice-id>` / `<slice-name>` |
| Date | `<yyyy-mm-dd>` |
| Total Recommendations / Rejected | `<count>` / `<count>` |
| Source Lessons / ADRs | `<retro-and-lessons.md path>` / `<ADR IDs reviewed>` |

---

## Reconciliation Triggers (Process Doc §33.1)

| Trigger | Applies? | Notes |
|---|---|---|
| After every few completed slices | `Yes/No` | |
| After a major ADR | `Yes/No` | `<ADR ID>` |
| After a recurring deviation pattern | `Yes/No` | |
| After a material Microsoft-stack constraint | `Yes/No` | |
| Before major roadmap or planning work | `Yes/No` | |
| Planning agents hitting stale assumptions | `Yes/No` | |

---

## Recommendations

Repeat per recommendation.

### SDU-<slice-id>-001

- **Target:** `<doc repo path>` → `<section heading>`
- **Nature:** `Add / Revise / Deprecate / Delete` — **Priority:** `High / Med / Low`
- **Source:** `Implementation lesson / Process lesson / ADR` — `<IL-/PL-/ADR- ID>` — `<brief insight>`
- **Rationale:** `<why warranted: which stale assumption, missing constraint, or new durable planning knowledge>`
- **Change:** `<specific text to add/remove/replace; do not write full doc-repo content unless draft text was requested>`
- **Draft text (only if user requested):**
  ```text
  <draft — omit block otherwise>
  ```
- **Approval required:** Yes

<!-- Repeat for SDU-<slice-id>-002, etc. -->

---

## Rejection Log

| Candidate | Source | Reason |
|---|---|---|
| `<desc>` | `<lesson/ADR ID>` | `Current-state / Not durable / Already present / Out of scope / Slice-specific language` |

---

## Human Approval Checklist

No documentation repo file has been modified — recommendations only. Approved changes are applied manually or via a separate task.

| # | Decision | Recommendation | Notes |
|---|---|---|---|
| 1 | Approve SDU-<slice-id>-001 | `Approve / Reject / Modify` | |
