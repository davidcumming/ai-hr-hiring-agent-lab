# Deviation Log

## 1. Report Metadata

| Field | Value |
|---|---|
| Slice ID | `<slice-id>` |
| Slice Name | `<slice-name>` |
| Date | `<yyyy-mm-dd>` |
| Agent / Author | `<agent-or-user>` |
| Branch | `<branch-name>` |
| Slice Spec Reference | `docs/delivery/slices/<slice-id>/slice-spec.md (version as of <date>)` |
| Eval Contract Reference | `docs/delivery/slices/<slice-id>/eval-contract.md` |
| Status | `Draft / Final` |

---

## 2. Deviation Summary

| Classification | Count | Highest Severity |
|---|---|---|
| `requirement-removed` | `<N>` | `High / Medium / Low / N/A` |
| `requirement-deferred` | `<N>` | |
| `approach-substituted` | `<N>` | |
| `scope-reduced` | `<N>` | |
| `interpretation-applied` | `<N>` | |
| `platform-forced` | `<N>` | |
| `architecture-driven` | `<N>` | |
| `eval-gap` | `<N>` | |
| **Total** | `<N>` | |

**Compliance flags:** `None / See Section 6` — **Lesson flags:** `<N>` — **GitHub Issue recommendations:** `<N>`

---

## 3. Deviation Entries

One row per deviation; detail entries follow.

| # | Classification | Severity | Spec Section Affected | Brief Description | Doc Impact | Lesson Flag | Issue Recommended |
|---|---|---|---|---|---|---|---|
| D-001 | `<classification>` | `High / Medium / Low` | `<section / requirement ID>` | `<one line>` | `Yes / No` | `Yes / No` | `Yes / No` |

### D-001 — `<Brief Title>`

- **Classification / Severity:** `<classification>` / `High / Medium / Low`
- **Spec section / requirement:** `<section or requirement ID + brief text>`
- **What the spec intended:** `<...>`
- **What was implemented:** `<...>`
- **Rationale:** `<specific cause — platform constraint, guideline, dependency, time, interpretation, etc.>`
- **Impact on current-state docs:** `<sections to update, or "None — doc impact minimal">`
- **Lesson flag:** `Yes — <what lesson>` / `No`
- **GitHub Issue recommendation:** `Yes — <title>` / `No`
- **Compliance flag:** `None` / `Yes — <privacy / security / residency / audit concern>`

> Add D-002, D-003, etc. for each deviation.

---

## 4. Current-State Documentation Impact Summary

Sections `current-state-reconciler` must update to reflect actual implementation rather than spec intent.

| # | Current-State Doc Section | What Needs to Change | Related Deviation(s) |
|---|---|---|---|
| 1 | `<section / path>` | `<change>` | `D-00X` |

> If none: `No current-state documentation changes required beyond the standard post-implementation update.`

---

## 5. Lesson Flags

Deviations representing durable implementation lessons — candidates for `slice-retro-and-lessons` (Stage 18), not lessons yet.

| # | Deviation | Lesson Candidate Summary | Why Durable? |
|---|---|---|---|
| 1 | `D-00X` | `<what the lesson would capture>` | `Platform constraint / architecture insight / approach comparison / etc.` |

> If none: `No lesson candidates identified in this slice's deviations.`

---

## 6. Compliance Flags

Deviations affecting privacy, security, residency, auditability, PHI/PII, or regulatory requirements — require explicit human acknowledgment.

| # | Deviation | Compliance Area | Description | Required Action |
|---|---|---|---|---|
| 1 | `D-00X` | `Privacy / Security / Data Residency / Audit / PHI-PII / Other` | `<concern>` | `Human review before proceeding / Document and monitor / Other` |

> If none: `No compliance concerns identified in the deviations for this slice.`

---

## 7. Recommended GitHub Issues

Deferred requirements and scope reductions needing tracking. Do **not** create without human approval.

| Title | Type | Severity | Related Deviation | Rationale |
|---|---|---|---|---|
| `<title>` | `requirement-debt / scope-debt / eval-gap / other` | `High / Medium / Low` | `D-00X` | `<rationale>` |

> If none: `No issues recommended for deviations in this slice.`

---

## 8. Handoff Notes

**To `live-eval-runner` (Stage 10):** `eval-gap` deviations that may require revisiting the eval contract — `<list or "None">`; key context `<eval-relevant summaries>`.

**To `current-state-reconciler` (Stage 12):** log location `docs/delivery/slices/<slice-id>/implementation/deviation-log.md`; doc sections requiring updates — see Section 4; deviations with doc impact `<N>`.

**To `slice-retro-and-lessons` (Stage 18):** lesson flag count `<N>`; key candidates — see Section 5.

**Summary for Closeout:** total deviations `<N>`; high-severity `<N>`; compliance flags `<N>`; issue recommendations `<N>`; lesson flags `<N>`.
