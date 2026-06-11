# ADR Gap Report: <Slice Name>

## 1. Report Metadata

| Field | Value |
|---|---|
| Slice ID | `<slice-id>` |
| Slice Name | `<slice-name>` |
| Report Date | `<yyyy-mm-dd>` |
| Report Author | `<agent/user>` |
| Compliance Report Reference | `<path or reference>` |
| Implementation Plan Reference | `<path or reference>` |
| ADRs Reviewed | `<ADR IDs and titles, or "None">` |
| Status | `Draft / Final — Awaiting Human Decision` |

---

## 2. Gap Inventory

### 2.1 Gaps Closed by Existing ADRs

"Not covered" findings resolved by an existing ADR on closer inspection.

| Compliance Report Finding | Resolved By | ADR Section | Notes |
|---|---|---|---|
| `<finding ID + description>` | `<ADR-NNN Title>` | `<section>` | `<how the ADR covers this>` |

> If none: "All gaps here are confirmed; no findings were resolved by existing ADRs."

### 2.2 Confirmed Gaps

Gaps remaining after Step 1 — these require an architecture decision.

| Gap ID | Description | Blocking Severity |
|---|---|---|
| GAP-001 | `<brief description>` | `Blocking / Conditionally blocking / Non-blocking recommendation` |

---

## 3. Confirmed Gap Detail

One section per confirmed gap.

### GAP-001: <Short Title>

**Decision Question** — the specific decision the human must make, as a concrete, answerable question (e.g. "Should Azure Table Storage be the approved data store for lookup-only reference data, or should all data access use Cosmos DB / Azure SQL?"):

`<decision question>`

**Why This Decision Is Needed Now** — risk/constraint if coding proceeds undecided:

`<explanation>`

**Options to Consider** — 2–4 concrete options. Do not indicate a preferred option.

- **Option A: `<name>`** — What: `<description>`; Pros: `<pros in this context>`; Cons/risks: `<cons>`
- **Option B: `<name>`** — What: `<description>`; Pros: `<pros>`; Cons/risks: `<cons>`
- **Option C: `<name>`** (if applicable) — What: `<description>`; Pros: `<pros>`; Cons/risks: `<cons>`

**Affected Plan Components** — files/components/surfaces that cannot be built until decided:

| Component | Plan Section | Why Blocked |
|---|---|---|
| `<file or component>` | `<section>` | `<reason>` |

**Impact on Future Slices:** `<note, or "Impact limited to this slice.">`

**Blocking Severity:** `Blocking / Conditionally blocking / Non-blocking recommendation` — Rationale: `<why>`

**Draft ADR Input (only if user explicitly requested)** — input for the human ADR author, not an approved ADR:

| Field | Draft Value |
|---|---|
| Proposed ADR title | `ADR-NNN: <title>` |
| Status | `DRAFT — AWAITING HUMAN APPROVAL` |
| Context | `<one paragraph: situation driving this decision>` |
| Decision question | `<the question above>` |
| Options considered | `<brief list>` |
| Consequences if left undecided | `<what breaks>` |

*(Repeat Section 3 for each confirmed gap.)*

---

## 4. Gap Summary Table

| Gap ID | Description | Affected Components | Blocking Severity | ADR Needed? |
|---|---|---|---|---|
| GAP-001 | `<description>` | `<list>` | `<severity>` | `Yes — new ADR / No — existing ADR found / Uncertain` |

---

## 5. Development Pause Recommendation

### Components That Must Not Proceed Until ADR Approval

| Component | Gap Reference | Why Paused |
|---|---|---|
| `<component>` | `GAP-NNN` | `<reason>` |

### Components That May Proceed (if any)

| Component | Notes |
|---|---|
| `<component>` | `<no dependency on the gap>` |

> If all blocked: "All implementation work should pause until the human approves or rejects the decision(s) above."

---

## 6. Recommended Next Step

| Condition | Next Step |
|---|---|
| All gaps resolved by existing ADRs | Proceed to Stage 7 — Implementation & config capture. |
| Blocking gap confirmed | **STOP.** Present this report to the human release authority. |
| Human approves a new ADR | Run `architecture-guideline-updater`, then proceed to Stage 7. |
| Human rejects the approach | Revise the implementation plan (Stage 5) with a compliant approach. |
| Human proceeds at explicit risk | Document the decision and risk acceptance; proceed to Stage 7 with the risk flagged. |

### Current Recommendation

`<specific recommended next step for this report>`

### Handoff Notes

`<what the human or next skill needs to know>`
