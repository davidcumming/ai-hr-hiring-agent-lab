---
name: archive-package-preparer
description: "Prepares a merged slice's transient artifacts for external archive and identifies durable outputs that remain in main. Use at Stage 17 after closeout approval."
---

# Skill: Archive Package Preparer

**Used at:** Stage 17 — Archive (Orchestration Map §3 stage table)
**Execution model:** `inline`
**Supports:** Process Doc §7 Current-State vs Historical Documentation, §32 Post-Merge Process

---

## 1. Purpose

After the branch is merged and the Release Authority has approved closeout (Stage 16), prepare the slice's transient artifacts for external archive and identify the durable outputs that remain in main. The skill produces an archive manifest (instructions for what goes where), a durable-output promotion list, an external-artifact reference list, and a deletion-candidate list. It keeps main clean of stale slice history while preserving audit-relevant evidence externally — but it proposes only: it moves and deletes nothing without explicit human review and approval of the manifest.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Closeout package | Yes | Primary manifest seed; defines which artifacts exist |
| 2 | Slice folder contents | Yes | All files created during the slice |
| 3 | Manual evidence | Conditional | Screenshots, portal notes, config evidence |
| 4 | Eval artifact references | Yes | External artifact IDs/locations; never in the code repo |
| 5 | Current-state doc updates | Yes | Confirms which docs are already in main |
| 6 | ADRs and guideline updates | Yes | Confirms durable items that must remain in main |
| 7 | Implementation lessons | Conditional | May be partial; Stage 18 may add more |
| 8 | GitHub Issues summary | Yes | Issue numbers for the manifest |

---

## 7. Process Steps

### Step 1 — Identify all slice artifacts
List every file created or modified this slice (closeout package as index, supplemented by the slice folder). Categorize each:

| Category | Examples |
|---|---|
| **Durable — keep in main** | Current-state docs, ADRs, guideline updates, implementation/process lessons, eval summary reference file, traceability matrix (optional — Step 3) |
| **Transient — archive externally** | Slice spec, deviation log, closeout package, DoD report, issue draft list, implementation plan, eval contracts, test plans |
| **External only** | Raw eval artifacts, manual evidence with sensitive data, screenshots |
| **Already in tracker** | GitHub Issues (record numbers; no file action) |

### Step 2 — Confirm durable outputs in main
Per Process Doc §32, confirm these are in main and will not be archived: updated current-state docs, approved ADRs, guideline updates, curated implementation lessons, curated process lessons (after Stage 18 if not yet complete), eval summary reference file (not raw artifacts), open GitHub Issues (tracker). Flag any durable output missing from main.

### Step 3 — Decide traceability matrix disposition
Keep in main (evidence record for regulated/high-assurance slices) or archive externally (low-risk, purely historical). Note the risk tier, recommend a disposition, and let the Release Authority confirm.

### Step 4 — Build the archive manifest
One row per artifact: artifact, current location, disposition (keep in main / archive externally / external storage keep / delete from main), archive destination, notes.

### Step 5 — Identify missing durable outputs
For any Process Doc §32 durable item not in main (lessons not yet promoted, missing eval summary reference), create a gap entry for the human or Stage 18 to act on.

### Step 6 — Check data residency for manual evidence
Verify proposed archive destinations comply with Canadian data residency requirements where evidence relates to Canadian-resident user data or regulated systems. Flag any artifact needing a specific secure location.

### Step 7 — Produce manifest and lists
Use `templates/archive-manifest-template.md` to produce: the archive manifest; the durable-output promotion list; the external-artifact reference list (eval and manual-evidence locations for audit); and the deletion-candidate list (artifacts with no audit value and no external archive — requires explicit human approval before any action).

---

## 6. Source Authority Rules

| Question | Use this source |
|---|---|
| What is durable (stays in main)? | Process Doc §32 list + current-state docs already in main |
| What is transient (archive externally)? | Slice specs, draft closeout docs, draft issue lists, planning artifacts |
| Where do eval artifacts live? | External storage only (manifest records location, not content) |
| What can be deleted? | Nothing without human review and approval of the manifest |
| Which issues to preserve? | Open issues survive in the tracker; closed issues tracked by number only |

---

## 10. Quality Bar

Before handoff, confirm:

- [ ] The branch was merged and Stage 16 approved before this skill ran; the closeout package was available as input.
- [ ] Every file in the slice folder and every artifact referenced in the closeout package is listed in the manifest — none omitted.
- [ ] No "Keep in main" item is a slice spec, planning draft, or closeout working document.
- [ ] No durable Process Doc §32 output is proposed for archive or deletion.
- [ ] Raw eval artifact content is referenced only (external storage), never proposed for the code repo.
- [ ] The traceability matrix disposition recommendation notes the slice risk tier.
- [ ] All Process Doc §32 durable outputs are confirmed in main or flagged missing in the promotion list; lessons are confirmed or flagged pending Stage 18.
- [ ] Each deletion candidate has a stated reason explaining it has no audit/historical value; the list carries a prominent "Requires explicit human approval" notice.
- [ ] No deletion candidate could be needed for a future audit, incident investigation, or regulatory review.
- [ ] Artifacts that may contain Canadian-resident or regulated data are flagged with a proposed destination and residency note; no sensitive data is excerpted (referenced only).
- [ ] The manifest is clearly labeled as requiring human review before execution and does not modify documentation-repo content or create issues.
- [ ] The manifest explicitly states no files have been moved or deleted by the agent.

---

## 11. Failure Modes to Avoid

| Failure mode | Why it matters |
|---|---|
| Silently deleting artifacts | All dispositions require human review; silent deletion breaks the audit trail |
| Leaving raw slice specs in main | Specs are planning intent, not current-state records; they pollute main with stale history |
| Archiving eval artifact content into the code repo | Raw eval outputs must stay in external storage (Process Doc §19) |
| Archiving sensitive manual evidence to non-compliant storage | Canadian data residency rules apply |
| Running before merge is approved | The manifest must not be executed until Stage 16 is complete |
| Omitting the durable-output promotion list | Missing durable outputs (e.g., unpromoted lessons) leave main incomplete |

---

## 13. Handoff to Next Skill

After the manifest is reviewed and executed by a human-directed action: pass the confirmed archive details to `slice-retro-and-lessons` (Stage 18) for full delivery context; lessons from Stage 18 become the final durable outputs added to main. `manual-config-debt-monitor` (Stage 19) uses the archived manual evidence and issue list for ceiling tracking; `next-slice-recommender` (Stage 20) uses the updated main branch as its baseline. The skill response must include the archive manifest, the durable-output promotion list, the external-artifact reference list, the deletion-candidate list, data-residency flags for sensitive artifacts, and a clear statement that no artifacts have been moved or deleted and that the manifest requires human review and approval. Obeys the recommend-never-approve and source-of-truth rules in AGENTS.md.
