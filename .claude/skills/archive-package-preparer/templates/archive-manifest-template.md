# Archive Manifest

**Slice ID:** `<slice-id>` | **Slice name:** `<slice-name>` | **Manifest date:** `<YYYY-MM-DD>`
**Branch merged:** `<feature/branch-name>` → `main` | **By:** `archive-package-preparer`

> **This manifest requires human review and approval before any files are moved or deleted. No artifacts have been relocated or removed by the agent.**

---

## 1. Archive Manifest

*All slice artifacts, with disposition.*

| Artifact | Current location (rel. to repo root) | Disposition | Archive / keep destination | Notes |
|---|---|---|---|---|
| `<filename>` | `<path>` | Keep in main / Archive externally / External storage (keep) / Delete from main | `<destination or storage ref>` | `<notes>` |

**Disposition key:** Keep in main = durable, authoritative for future slices, do not move · Archive externally = historical slice artifact, move to external archive after confirmation, remove from main · External storage (keep) = already external, record location for audit, no action · Delete from main = no audit/historical value, remove after human confirmation.

---

## 2. Durable-Output Promotion List

*Process Doc §32 items that should be in main. Confirmed items marked; missing/incomplete items require action.*

| Durable output | Expected location | Status | Required action |
|---|---|---|---|
| Updated current-state documentation | `docs/current-state/` | Confirmed / Missing | `<action or "—">` |
| Approved ADRs | `docs/adr/` | Confirmed / Missing | `<action or "—">` |
| Architecture guideline updates | `docs/architecture/` | Confirmed / Missing | `<action or "—">` |
| Curated implementation lessons | `docs/lessons/implementation-lessons.md` | Confirmed / Missing / Pending Stage 18 | `<action or "—">` |
| Curated process lessons | `docs/lessons/process-lessons.md` | Confirmed / Missing / Pending Stage 18 | `<action or "—">` |
| Eval summary reference file | `docs/delivery/slices/<slice-id>/eval-summary.md` | Confirmed / Missing | `<action or "—">` |
| Open GitHub Issues | Issue tracker | Confirmed (issues #`<N>`) | — |

---

## 3. External Artifact Reference List

*Audit trail for artifacts outside the code repo. No action unless the destination needs updating.*

| Artifact | Type | External storage location | Data residency note | Related issue |
|---|---|---|---|---|
| `<eval run ID>` | Live eval artifact | `<storage path/bucket ref>` | `<residency note or "standard">` | — |
| `<evidence ID>` | Manual evidence | `<secure storage ref>` | `<residency note>` | `#<issue>` |

---

## 4. Deletion Candidate List

*Artifacts proposed for deletion from main: no audit value and not needed in external archive.*

> **Requires explicit human approval before any deletion.**

| Artifact | Location | Reason for deletion | Risk if deleted |
|---|---|---|---|
| `<filename>` | `<path>` | `<reason>` | Low / Medium / note |

*If none: "No deletion candidates. All removed artifacts are archived externally."*

---

## 5. Data Residency Flags

*Artifacts that contain or may contain Canadian-resident user data or other regulated data. Confirm the destination is compliant.*

| Artifact | Data type | Proposed archive destination | Residency compliance |
|---|---|---|---|
| `<artifact>` | `<data type>` | `<destination>` | Compliant / Needs review |

*If none: "No data residency flags for this slice."*

---

## 6. Manifest Status

| Check | Result |
|---|---|
| All slice artifacts listed | Yes / No — `<detail>` |
| All Process Doc §32 durable outputs confirmed or flagged | Yes / No |
| No durable outputs proposed for archive | Yes / No — `<detail>` |
| Deletion candidate list reviewed for audit value | Yes / No |
| Data residency flags reviewed | Yes / No / N/A |
| **Human approval received** | Pending / Approved by `<name>` on `<date>` |
