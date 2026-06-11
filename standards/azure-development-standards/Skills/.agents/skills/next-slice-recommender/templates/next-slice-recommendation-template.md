# Next Slice Recommendation: <Date> — Post-Slice <Slice ID>

## 1. Recommendation Metadata

| Field | Value |
|---|---|
| Recommendation ID | `<rec-id>` |
| Date Created | `<yyyy-mm-dd>` |
| Created By | `<agent/user>` |
| Prior Slice Closed | `<slice-id>` |
| Planning Context Reference | `<path/link>` |
| Status | `Draft / Complete` |

## 2. Debt Ceiling Check

Performed first. If exceeded, resolve debt before selecting a next slice (see `manual-config-debt-monitor`).

| Status | Details |
|---|---|
| Manual-config debt ceiling | `Clear / Exceeded` |
| Open high-priority GitHub Issues | `<count>` |
| Notes | `<concerns affecting all candidates>` |

## 3. Inputs Reviewed

| Input | Reference | Notes |
|---|---|---|
| Reconciled planning context | `<reference>` | `<notes>` |
| Current-state docs | `<reference>` | `<notes>` |
| Implementation lessons | `<reference>` | `<notes>` |
| Process lessons | `<reference>` | `<notes>` |
| ADRs and architecture guidelines | `<reference>` | `<notes>` |
| GitHub Issues (open) | `<reference>` | `<notes>` |
| Known limitations | `<reference>` | `<notes>` |
| Test/eval status | `<reference>` | `<notes>` |
| Manual-config debt status | `<reference>` | `<notes>` |
| Product priorities (if provided) | `<reference>` | `<notes>` |

## 4. Blocked Candidates

| Candidate | Blocking Reason | Required Resolution |
|---|---|---|
| `<candidate>` | `<reason>` | `<action before this candidate can be considered>` |

## 5. Assessed Candidates

Assess each unblocked candidate against the balanced sequencing dimensions (`rubrics/balanced-sequencing-score-rubric.md`).

### Candidate: <Candidate Name>

**Summary:** `<one-sentence description and primary outcome>`

| Dimension | Standing | Rationale |
|---|---|---|
| Business value | `Strong / Moderate / Weak / Blocked` | `<rationale>` |
| Dependency order | `Strong / Moderate / Weak / Blocked` | `<rationale>` |
| Testability | `Strong / Moderate / Weak / Blocked` | `<rationale>` |
| Eval readiness | `Strong / Moderate / Weak / Blocked` | `<rationale>` |
| Technical risk | `Strong / Moderate / Weak / Blocked` | `<rationale>` |
| Demo/stakeholder value | `Strong / Moderate / Weak / Blocked` | `<rationale>` |
| Unresolved issue impact | `Strong / Moderate / Weak / Blocked` | `<rationale>` |
| Architecture readiness | `Strong / Moderate / Weak / Blocked` | `<rationale>` |
| Manual-config/source-control risk | `Strong / Moderate / Weak / Blocked` | `<rationale>` |
| Implementation complexity | `Strong / Moderate / Weak / Blocked` | `<rationale>` |

**Ready for `slice-spec-generator`?** `Yes / No / Conditional — <condition>`

**Main risk:** `<risk>`

---

*(Repeat for each candidate)*

## 6. Dependency Map

| Candidate | Depends On | Enables |
|---|---|---|
| `<candidate>` | `<dependency or None>` | `<future candidates>` |

## 7. Ranked Recommendation

| Rank | Candidate | Overall Standing | Key Reason | Ready for Spec? |
|---|---|---|---|---|
| 1 | `<candidate>` | `<standing>` | `<reason>` | `Yes / No / Conditional` |
| 2 | `<candidate>` | `<standing>` | `<reason>` | `Yes / No / Conditional` |
| 3 | `<candidate>` | `<standing>` | `<reason>` | `Yes / No / Conditional` |

## 8. Recommended Default Next Action

**Top recommendation:** `<candidate name>`

**Rationale:** `<two to four sentences: scoring, dependencies, lessons learned>`

**Required first step if selected:** `<planning-context-reconciler at Stage 0 / resolve <issue> first / adr-gap-detector>`

**This is a recommendation. The human chooses the next slice.**

## 9. Notes from Implementation and Process Lessons

Implementation and process lessons kept distinct (AGENTS.md cross-cutting rule).

**Implementation lessons relevant to next planning:**

- `<lesson>`

**Process lessons relevant to next planning:**

- `<lesson>`
