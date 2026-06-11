# Retro and Lessons: <Slice Name>

| Field | Value |
|---|---|
| Slice ID | `<slice-id>` |
| Slice Name | `<slice-name>` |
| Date | `<yyyy-mm-dd>` |
| Stage 17 Completed | `<yyyy-mm-dd>` |
| Sources Reviewed | `<closeout-package-path>, <deviation-log-path>, <notes-ref>` |

> The three sections below are **strictly separate**. Implementation lessons (Section B) and process lessons (Section C) must NOT be mixed — this is a cross-cutting rule (AGENTS.md). A technical lesson never appears in C; a workflow lesson never appears in B.

---

## Process Retro

Answer all nine retro questions (Process Doc §34). For each: what worked / what did not / recommended change (if any). If a change rises to a durable process lesson, flag it for Section C — do not write it there.

1. Was the slice the right size?
2. Did the slice spec contain the right level of detail?
3. Were evals defined early enough?
4. Were evals too weak, too expensive, or too slow?
5. Did documentation reconciliation happen cleanly?
6. Did manual configuration debt increase? (note debt incurred and whether the ceiling held)
7. Did agents read the right context?
8. Did approval gates add value or create drag?
9. Should any template, prompt, checklist, or skill change?

**Summary of recommended changes:**

| # | Recommended Change | Affected Artifact | Priority | Follow-Up Issue? | Escalate to Process Lesson? |
|---|---|---|---|---|---|
| 1 | `<change>` | `<artifact>` | `High/Med/Low` | `Yes/No` | `Yes/No` |

---

## Implementation Lessons

Technical and Microsoft-stack lessons only — no process lessons. Duplicate-checked against `docs/lessons/implementation-lessons.md`. Promoted: `<count>` / Rejected: `<count>`. Repeat the block per lesson.

### IL-<slice-id>-001

- **Title:** `<concise title>`
- **Category:** `Microsoft-stack constraint | architecture pattern | configuration management | eval design | privacy/residency | performance/cost | integration | tooling | other`
- **Lesson:** `<1–5 sentences, present tense; the durable technical insight, stated so a future agent can act without the source artifacts>`
- **Future planning impact:** `<how it should change future planning, implementation, or eval design — be specific>`
- **Source reference:** `<closeout section / deviation log entry / eval summary>` (slice `<id>`, observed `<yyyy-mm-dd>`)
- **Strategic-doc update recommended:** `Yes / No` — if Yes, target file/section: `<doc repo file + section>`; rationale: `<why>`

<!-- Repeat for IL-<slice-id>-002, etc. -->

**Rejected candidates:**

| Candidate | Reason | 
|---|---|
| `<desc>` | `One-off / Duplicate / Insufficient evidence / Process lesson (→ Section C)` |

---

## Process Lessons

Operating-model and workflow lessons only — no technical lessons. Duplicate-checked against `docs/lessons/process-lessons.md`. Promoted: `<count>` / Rejected: `<count>`. Repeat the block per lesson.

### PL-<slice-id>-001

- **Title:** `<concise title>`
- **Category:** `slice sizing | spec quality | eval design | implementation workflow | documentation reconciliation | closeout | governance gate | skill/template gap | other`
- **Lesson:** `<1–5 sentences, present tense; what happened, why it mattered, what the operating model should do differently>`
- **Recommended change:** `Recommend: <specific change to a skill, template, checklist, rule, or gate — concrete enough to act on. "Recommend:" makes explicit this is not approved.>`
- **Affected skill or template:** `<name(s)>`
- **Priority:** `High / Medium / Low`
- **Follow-up issue recommended:** `Yes / No` — if Yes, type `<process-improvement | template-gap | skill-gap>`, suggested title `<title>`
- **Source reference:** `<retro section / closeout section / agent notes>` (slice `<id>`, observed `<yyyy-mm-dd>`)

<!-- Repeat for PL-<slice-id>-002, etc. -->

**Rejected candidates:**

| Candidate | Reason |
|---|---|
| `<desc>` | `One-off / Duplicate / Insufficient evidence / Implementation lesson (→ Section B)` |
