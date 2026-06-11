# Architecture Guideline Update: <ADR-ID>

| Field | Value |
|---|---|
| ADR ID / Title | `<ADR-ID>` — `<title>` |
| ADR Approval Date / By | `<yyyy-mm-dd>` / `<human release authority>` |
| Update Date | `<yyyy-mm-dd>` |
| Produced By | `architecture-guideline-updater` |
| Guidelines Document | `<path>` |
| Status | `Draft / Applied / Blocked — pending ADR clarification` |

**ADR decision (as it applies to this change):** `<one or two sentences: the ADR approves [X] as required for [Y] instead of [Z], effective this slice forward>`

---

## Sections Changed

| Guideline Section | Path | Change Type |
|---|---|---|
| `<heading>` | `<doc path #section>` | `Replace / Add / Remove / Restructure` |

---

## Section-Level Changes

Repeat per changed section:

**`<Section Heading>`** — change type `Replace / Add / Remove`

- **Existing text:** `<exact current text>`
- **Required change per ADR `<ADR-ID>`:** `<what the ADR requires this section to say>`
- **Updated text:** `<directive, present-tense, forward-looking text>` — include "ADR cross-reference: See ADR-<ID> for rationale."

---

## Sections Confirmed Unchanged

| Section | Review Notes |
|---|---|
| `<section>` | `Reviewed; not affected by this ADR` |

---

## Flagged Ambiguities

Sections that could not be updated because the ADR was ambiguous about scope.

| Section | Ambiguity Description | Recommended Action |
|---|---|---|
| `<section>` | `<description>` | `Request ADR clarification / Defer to next ADR / Accept as-is` |

---

## Guideline Change Summary

Present-tense narrative for future `planning-context-reconciler` and `architecture-guideline-checker` consumers: `<what changed and why>`

---

## Impact on Future Slices & Affected Issues

| Known Planned Slice / Area | Impact | Action Required |
|---|---|---|
| `<slice or area>` | `<impact>` | `No action / Revisit slice spec / New ADR candidate / Other` |

Open GitHub Issues potentially affected (list only; do not update here): `<#issue — reason>`

---

## Post-Application Checklist

- [ ] Every changed section cites the ADR ID; all changes are within ADR scope.
- [ ] No actual-architecture or aspirational documentation-repo content introduced.
- [ ] Directive, present-tense language used throughout; flagged ambiguities listed.
- [ ] Change summary complete; future slice impact assessed.
