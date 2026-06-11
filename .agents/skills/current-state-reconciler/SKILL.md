---
name: current-state-reconciler
description: "Turns a completed feature branch into updated current-state docs and actual architecture in one pass. Use at Stage 12 to reconcile what was built into present-tense reality."
context: fork
---

# Skill: Current-State Reconciler

**Used at:** Stage 12 — Current-state reconciliation (Orchestration Map §3 stage table)
**Execution model:** `recommended-subagent`
**Supports:** Process Doc §7 Current-State Documentation Versus Historical Slice Documentation, §9 Architecture Guidelines Versus Actual Architecture, §25 Documentation Reconciliation

---

## 1. Purpose

Turn the completed feature branch into updated current-state reality in one pass, producing three sections: (A) branch diff analysis, (B) updated current-state documentation (slice-agnostic, present-tense), and (C) updated actual architecture (only what was built). This skill drafts; independent validation is `documentation-consistency-validator` at Stage 13. Current-state docs describe what exists now — never slice intent, never aspirational future-state, never slice-specific framing.

---

## 3. Do Not Use This Skill For

- Updating **architecture guidelines** — that requires `architecture-guideline-updater` with an approved ADR.
- Validating documentation correctness — that is `documentation-consistency-validator` at Stage 13.
- Normalizing raw manual evidence — run `manual-evidence-normalizer` first (Stage 12 conditional) if raw evidence needs structuring before Sections B/C.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Main-branch baseline | Yes | HEAD of main before the branch |
| 2 | Completed feature branch | Yes | The branch being reconciled |
| 3 | Git diff and commit log | Yes | Full diff, not summary |
| 4 | Changed files list | Yes | Code, config, IaC, Power Platform, Copilot Studio, Foundry, tests, evals |
| 5 | Slice spec | Yes | Intent reference only — not current-state truth |
| 6 | Implementation summary | Yes | What was actually built |
| 7 | Deviation log | If exists | From Stage 9 |
| 8 | Test/eval summaries | If exists | Deterministic + live-model results |
| 9 | Manual evidence | If exists | Normalized (preferred) or raw |
| 10 | Approved ADRs | If exists | ADRs approved during this slice |
| 11 | Architecture guidelines | Yes | Read-only; never modified here |
| 12 | Actual-architecture document | Yes | Updated here |
| 13 | Known limitations register | Yes | |
| 14 | GitHub Issues | If exists | Open items affecting what to document |

If inputs 1–6 are missing, raise a blocker. Do not proceed with a partial diff — it produces false current-state claims.

---

## 6. Source Authority Rules

This skill **overrides the standard hierarchy**: it works from the diff and evidence, not the spec.

| Question | Source for this skill |
|---|---|
| What was actually built? | Code diff + config + IaC + implementation summary + approved manual evidence |
| What was the intent? | Slice spec (intent only — deviations override intent) |
| Why did architecture deviate? | Approved ADR |
| What work is unresolved? | GitHub Issues (reference; do not create here) |
| What has been physically built? | Actual-architecture document (update here) |
| What does the application currently do? | Current-state documentation (update here) |

Documentation-repo content is **not** authoritative for current-state claims; never copy aspirational text from it into current-state docs.

---

## 7. Process Steps

### Section A — Branch Diff Analysis

1. **Ingest inputs.** Load diff, commit log, changed files, slice spec, implementation summary, deviation log. Note discrepancies between intended and actual changes.
2. **Categorize changes** into: user-visible/agent behaviour; backend/service/API; infra/IaC/config; Power Platform/Copilot Studio/Foundry; data/state/persistence; security/permissions/identity; integration/external-system; test/eval; docs-only.
3. **Map documentation and test/eval impact** per category: affected current-state sections, affected actual-architecture sections, known limitations resolved or created, eval/test strategy impacts.
4. **Note manual-evidence gaps** where source-controlled evidence does not exist.
5. **Write Section A** to the template's Branch-Diff Analysis section. Factual and change-scoped, not aspirational.

### Section B — Updated Current-State Documentation

1. **Read existing current-state docs.** Identify every section needing update from A3.
2. **Produce an update plan** per affected section: old content, required change, source evidence, change type (additive/corrective/removal). Use the template's Doc Update Plan section.
3. **Apply updates.** Present tense ("The system supports…"). No slice-specific language ("Slice N added…", "This branch implemented…", "The next slice will…"). No aspirational documentation-repo text. Document what was built, not what was planned. Mark known limitations clearly where something was attempted but not fully implemented.
4. **Identify assumptions and gaps** where the diff lacks evidence to write with confidence — these become blockers (if a major claim's correctness is affected) or follow-up issue candidates (minor).
5. **Note follow-up issue candidates** for `github-issue-drafter` at Stage 14. Do not create issues here.

### Section C — Updated Actual Architecture

1. **Read the actual-architecture document.** Identify every component, integration, data flow, or service reference the diff changes.
2. **Apply updates.** Document only what was physically built and is now in the branch. Do not add aspirational components even if they appear in guidelines. Cross-reference the approved ADR where an ADR-authorized change was made. Note manual-config components not in source control, with their follow-up issue reference (by reference only).
3. **Write the architecture change summary** — components added/modified/removed, integration and data/state changes.
4. **Update known architecture limitations** for gaps between guidelines and what was built.

Use the template's Actual-Architecture Update section.

---

## 9. Output Format

Use `templates/current-state-reconciliation-template.md` (three sections: Branch-Diff Analysis, Doc Update Plan, Actual-Architecture Update). Write Section A to `docs/delivery/slices/<slice-id>/branch-diff-analysis.md`; Section B updates land in `/docs/product-current-state/`; Section C in `/docs/architecture/actual-technical-architecture.md`. Follow the project's paths if they differ. The final response includes each section's structured output, files changed, blockers, and Stage 13 handoff notes.

---

## 10. Quality Bar

Before handoff, confirm:

- All change categories are covered in Section A; manual-evidence gaps are identified.
- No slice-specific language remains in current-state docs.
- No aspirational features are documented as implemented; no documentation-repo aspirational text was copied.
- Every changed claim is traceable to the diff, implementation summary, or approved manual evidence.
- All updated current-state sections are present-tense; known limitations reflect what was and was not completed.
- Actual architecture lists only built components — nothing the guidelines merely prescribe for the future.
- Architecture guideline files were not modified.
- ADR cross-references are accurate; manual-config components carry follow-up issue references.
- Gaps and assumptions are explicitly listed; blockers are concrete, not vague.
- No GitHub Issues created (candidates only); files-changed list is complete.

---

## 11. Failure Modes to Avoid

- **Treating commits as sufficient context** — commits may be partial or misleading; use the full diff with the implementation summary.
- **Ignoring manual evidence** — portal config absent from the diff is still real; load the evidence summary before writing actual architecture.
- **Hiding major gaps behind vague language** — list gaps explicitly and raise blockers when correctness is at stake.

---

## 13. Handoff to Next Skill

Next is `documentation-consistency-validator` at Stage 13, which runs as an independent isolated-verification subagent — it did not produce these docs and must not share this session's working context. The handoff is artifact-based.

Pass forward: the branch-diff analysis artifact path; the list of updated current-state doc files and sections; the actual-architecture update summary; the blockers and gaps list; the suggested follow-up issue candidates; the manual-evidence summary reference (if `manual-evidence-normalizer` ran).
