# Process Conciseness & Simplification Review — Change Plan

> **Status: EXECUTED (Slices 1–5 complete).** All five open decisions were resolved as recommended in §7 and the plan was implemented in five slices. Headline result: the skill subsystem shrank ~55–60% (SKILL.md 8,568→3,627; support files 12,524→4,876; checklists folded into §10; examples removed bar two eval references), the Skills Doc went 969→315 (catalogue → index), the Process Doc 1,610→1,099, and the architecture guidelines 519→491 (already the leanest, so least removable). A single source of truth is now codified (SKILL.md authoritative, Skills Doc an index, AGENTS.md the one home for cross-cutting rules), role names are reconciled, and a one-page [Run Your First Slice](./run-your-first-slice.md) quickstart plus an out-of-lifecycle paths section (hotfix §28 / cadence §33) were added. Full-repo anchor scans pass with zero broken links. The proposal text below is retained as the design rationale.

> **Status: PROPOSAL (original).** This is a sequenced list of suggested changes from a second review of the development process, agent roles, skills, and architectural guidelines. The review brief: find gaps/inconsistencies, find places to shorten and clarify, and assess human understandability — with a strong bias toward **conciseness**, on the premise that Opus-class models no longer need exhaustive instruction to behave correctly.

## How this review was done

The full system (~25,000 lines across ~155 files) was read in four passes: the three governance docs (Process, Skills, Orchestration Map) and the architecture guidelines; the 33 `SKILL.md` packages; their ~111 support files (examples, templates, checklists, rubrics); and the wrapper layer (READMEs, two `AGENTS.md`, the authoring spec, the eight role files, the prior revision plan).

---

## 1. Headline finding

The 2024 revision succeeded at its goal — it removed *structural* duplication of the **stage list** and gave each governance doc one job. But the system has since grown a second, larger layer of redundancy that the revision plan didn't touch:

1. **The same facts are restated for the reader who "might not know," 3–4 times per file.** Every `SKILL.md` re-states the recommend-never-approve rule, the source-of-truth hierarchy, the default context allow/deny list, and the privacy/residency posture — rules that already live authoritatively in `AGENTS.md` and the Skills Doc. This is the single biggest source of bloat.

2. **Skill detail now lives in two authoritative-feeling places** — the Skills Doc §7 catalogue (≈736 lines) *and* the 33 `SKILL.md` packages it describes. The catalogue entry is a strict subset of each `SKILL.md`. Every skill edit must be made twice, and a human can't tell which copy wins (the docs themselves disagree: `AGENTS.md` says follow the SKILL.md; the authoring spec says "the catalogue wins").

3. **Role definitions live in 3–4 places** (Process Doc §37, Skills Doc §5, the eight `agents/*.md` files, `agents/README.md`) — with a name mismatch between them.

4. **Examples and checklists exist mainly to "show the model what good looks like" or "remind it what it already knows"** — exactly the scaffolding a strong model needs least.

**Realistic whole-system reduction: ~45–55% (~25,000 → ~12,000–13,500 lines) with no loss of executable meaning**, provided shared rules are hoisted to one place and referenced rather than restated.

---

## 2. Changes by leverage (highest impact first)

### A. Make `SKILL.md` the single home for skill detail; demote the catalogue to an index

*Fixes the worst dual-maintenance burden and the "which copy is the truth" ambiguity. ~600+ lines saved and every future skill edit halved.*

- **A1.** Replace Skills Doc §7 (the 736-line per-skill catalogue, §7.1–§7.8) with a **one-line-per-skill index**: `name → owning role → one-sentence purpose → relative link to its SKILL.md`. The `SKILL.md` package becomes the sole detailed source.
- **A2.** State once, unambiguously, in the README and both `AGENTS.md`: *the `SKILL.md` package is the only authoritative skill spec; the Skills Doc index is a non-authoritative table of contents.* Remove the contradicting "the catalogue wins" line from `_AUTHORING_SPEC.md`.
- **A3.** Keep the genuinely unique parts of the Skills Doc: §2 Core Design Principle (the authority / context-contamination seams — this reasoning lives nowhere else), §4 standard structure + three standardized fields, §5 role table (but see C), §10 + §12 + §15 creation/cross-cutting rules. Net Skills Doc: 969 → ~300 lines.
- **A4.** Delete the redundant skill enumerations: §8 Creation Order, §13 Active Packages, §14 Minimum Skill Set are three more copies of the 33-skill list. Keep at most one (the minimum-set is the only one with independent value) and generate the rest from the index.

### B. Hoist cross-cutting rules out of every `SKILL.md` into `AGENTS.md`

*The largest single line-saver in the skill set: ~1,500–2,000 lines. Reference rules by name; state exceptions only.*

- **B1.** Move these to `AGENTS.md` as the standing defaults, and **delete their per-skill restatements**: the recommend-never-approve mantra (currently repeated ~4× per file, ~120+ times across the set); the default-context allow/deny list ("not allowed: raw code, old specs, transcripts, screenshots…"); the source-of-truth hierarchy table; the privacy/PHI/Canadian-residency posture; "slice specs are intent, not truth."
- **B2.** In each `SKILL.md`, keep **one** clear statement of any safety boundary that is load-bearing for that skill (e.g. PHI handling in the eval skills, "drafts, does not grade" in verification skills). Remove the 2nd, 3rd, and 4th repetition — not the 1st.
- **B3.** Delete the consolidation-history paragraphs from `SKILL.md` §1 (e.g. "this skill consolidates four former skills…"). That provenance already lives in `AGENTS.md`'s consolidation note and helps no executing agent.

### C. Collapse role definitions to one canonical table

*Removes a 3–4× duplication and a standing name mismatch.*

- **C1.** Make the **`agents/*.md` role files the single home** for role detail (they are already thin and dual-use). Replace Process Doc §37's six role descriptions with the one-paragraph pointer it already half-contains, and reduce Skills Doc §5 to a name→file→stages link table.
- **C2.** Reconcile the role-name mismatch once: Process Doc calls them "Documentation Agent" / "Eval Review Agent"; the catalogue and role files call them "Documentation and Architecture Reconciliation Agent" / "Eval Execution and Review Agent." Pick one set of names everywhere and delete the footnote that currently explains the discrepancy.

### D. Slim the `SKILL.md` template itself (loosen the authoring spec)

*The 13-section structure is followed near-religiously; several sections are pure restatement. ~1,000+ lines.*

- **D1.** Amend `_AUTHORING_SPEC.md` to make these sections **optional and only-when-they-add-skill-specific-content**: §3 (Do Not Use), §5 (Default Context Rules), §6 (Source Authority), §9 (Output Format), §11 (Failure Modes), §12 (Final Response). Today the spec *mandates* all of them, which is what forces the bloat.
- **D2.** Delete §9 "Output Format" enumerations wholesale — they re-list the section names that the referenced template already defines (e.g. slice-spec-generator §9 lists all 22 sections that live in the template). Replace with a one-line template pointer + any non-obvious constraint.
- **D3.** Cut §11 "Failure Modes" to the 2–4 *non-obvious, skill-specific* traps; most current rows are negations of §7 steps a model infers.
- **D4.** Merge §12 "Final Response Requirements" into §13 "Handoff" (they overlap), and trim §2 "When to Use" to ~2 triggering bullets.
- **D5.** Define the **essential core of a SKILL.md** (~80–130 lines): header block (Used at / Execution model / Supports), §1 Purpose + the one boundary that matters most, §4 Required Inputs table, §7 Process Steps (the real domain logic), §10 Quality-Bar pointer, slim §13 Handoff.
- **D6.** Stop repeating a per-skill "why" sentence on the Execution model field — the revision plan already said the subagent model should be defined once (Orchestration Map §6) and referenced, not re-justified 33 times.

### E. Cut the support-file layer hard

*~111 files, ~12,500 lines. Realistic ~60–65% reduction (~8,000 lines).*

- **E1. Eliminate EXAMPLES wholesale (~4,200 lines).** Each is its template re-rendered with invented data — no schema information the template lacks. A strong model produces equivalent output from template + checklist. *Optional:* keep the two chained eval examples (eval-risk-profiler → eval-contract-designer), trimmed to ~40 lines each, as the one reference for a cross-skill handoff.
- **E2. Merge CHECKLISTS into the SKILL.md (~2,200 standalone lines removed).** Replace the 33 separate files with a short "before handoff, confirm:" list (8–12 bullets) inside §10 of each SKILL.md. They currently restate the template's fields as pass/fail bullets.
- **E3. Compress TEMPLATES ~30–40% (~1,700 lines).** Strip instructional prose to field labels + a one-line hint where genuinely non-obvious. Collapse the three multi-file template sets (`slice-retro-and-lessons` 3 files, `current-state-reconciler` 3, `eval-contract-designer` 3) into one file each. Templates are the one support type that earns its keep (they pin the output schema) — keep them, just deflate them.
- **E4. Keep RUBRICS (policy, not formatting) but trim two.** The eval rubrics (risk-tier, failure-severity, pass/fail, unsafe-mode) encode real governance thresholds — keep. Collapse `next-slice-recommender`'s 10-dimension / 50-point scoring matrix to the 10 dimension prompts + the 2 real hard rules (false precision otherwise). Consolidate `eval-risk-profiler`'s four overlapping rubrics into two.

### F. Trim the Process Doc (~30–40%, 1,610 → ~1,000–1,100)

- **F1.** Collapse the **release-authority approval list** (verbatim in §29, §31, §36, §37.6) to one canonical copy (§31) that the others link to.
- **F2.** Collapse the **source-of-truth restatements** — the §3 table is canonical; remove the re-derived baseline list in §4 and the recurring "code/config/approved-evidence is truth" sentence (appears 6+ times).
- **F3.** Move the **field enumerations** (§12.2 spec content, §18 eval package, §24 traceability, §29 closeout, §40.3 spec template) into the templates that already hold them; keep the *rule* in the Process Doc, not the field list.
- **F4.** Shrink §6 Repository Roles (~60%), §8 Code Repo Structure (50-line tree → 10-line sketch or appendix), §7.1/§7.2 "should say / should not say" example lists (halve).
- **F5.** Reduce §37 Agent Roles to the pointer described in C1.

### G. Trim the Architecture Guidelines (40.2) (~25–30%, 519 → ~370)

- **G1.** Keep the load-bearing reference: §1.1 stack diagram, §1.2 ten principles, §1.3 responsibility table, §2 request flow, §17 envelope, §18 data-placement table, and every per-section "Must not" guardrail.
- **G2.** Cut the repeated rationale prose. The invariants "memory/RAG are context not authority," "no silent premium licensing/manual config," and "authoritative state lives in Azure Storage" are each restated in 6–9 sections — state once, reference after.
- **G3.** Merge the overlapping §20 Anti-patterns and §21 Summary (they restate the whole document a third time) — keep §20 (the more useful defect-list form), drop or fold §21.

---

## 3. Gaps & inconsistencies to fix (not primarily length)

- **H1. Reconcile the skill count.** "33" (AGENTS.md, Skills Doc §13) vs "38 / ~30 / 31" (revision plan §0, §4.3, Appendix A). Disk = 33. Make 33 canonical everywhere; mark the revision-plan numbers as historical.
- **H2. Fix the stale "forward reference" note** in the Orchestration Map (lines 6–7): it warns that `#skill-<name>` anchors don't resolve yet, but the Skills Doc headings already exist, so the links *do* resolve. The note now misleads.
- **H3. Remove `## 11. (reserved)`** placeholder in the Skills Doc — stale noise for a human reader.
- **H4. Cover the hotfix/incident path in the Orchestration Map.** Process Doc §28 defines a rollback/incident/hotfix path, but the Map's stage table and control flow cover only the forward lifecycle (Stages 0–20). A human following the Map has no gate guidance for incidents. Add a short conditional flow or explicitly note it's out of the Map's scope.
- **H5. Give the multi-slice strategic-reconciliation cadence a trigger.** §33 says "after every few slices," but only the per-slice conditional Stage 19 exists; the cross-slice cadence has no home.
- **H6. Close out the revision plan's own checklist** — two boxes (anchor verification, post-edit re-validation) remain unchecked while the doc is marked EXECUTED. Run the anchor/link audit and check them, or note them as deferred.
- **H7. Narrow the README's de-dup claim.** "No list of stages or skills is duplicated" is true only for *stages*. Either fix the duplication (A, C) and keep the claim, or soften it to "stages."

---

## 4. Human understandability

- **I1. Add a one-page "Run your first slice" quickstart.** Today a human must traverse 6 artifact types and 3,000+ lines to follow one slice. A plain-language Stage 0→16 walkthrough with the three mandatory human gates called out would be the single biggest usability win. None exists.
- **I2. State the source-of-truth ladder for *documents* once, plainly:** for any skill, read the SKILL.md; for control flow, read the Orchestration Map; for rules, read the Process Doc; for a role, read its `agents/*.md` file. Put this in the README so a reader never wonders which copy is authoritative. (Depends on A2/C1.)
- **I3. After A–C, the README's "three-document model" framing becomes honest** — each piece of information genuinely lives once. Update the README hub diagram to show the SKILL.md packages as the skill detail layer rather than implying the Skills Doc holds it.

---

## 5. Estimated impact

| Area | Now (lines) | After | Reduction |
|---|---|---|---|
| 33 × `SKILL.md` | ~8,570 | ~4,000–4,700 | ~45–55% |
| Support files (examples/templates/checklists/rubrics) | ~12,520 | ~4,500 | ~60–65% |
| Process Doc | 1,610 | ~1,000–1,100 | ~30–40% |
| Skills Doc | 969 | ~300 | ~70% |
| Architecture guidelines (40.2) | 519 | ~370 | ~25–30% |
| Role files / READMEs / AGENTS / authoring spec | ~970 | ~900 (net of additions) | small |
| **Total** | **~25,000** | **~12,000–13,500** | **~45–55%** |

The reduction is *not* uniform: narrow, heavily-scaffolded skills (`architecture-guideline-updater`, `manual-evidence-normalizer`, `eval-result-summarizer`) can lose 50–60%; genuinely dense ones (`eval-failure-classifier`, `eval-risk-profiler`, `slice-orchestrator`) only 20–30%. Cut by redundancy, not by a flat target.

---

## 6. Suggested sequencing

Do these in an order that avoids editing content you're about to move:

1. **Decide the source-of-truth model (A2, C1, C2)** — this governs everything else. Lock "SKILL.md is authoritative; catalogue is an index; role files are the role home."
2. **Hoist cross-cutting rules into `AGENTS.md` (B1)** — so skills have somewhere to point before you trim them.
3. **Amend the authoring spec (D1, D5)** — define the new slim SKILL.md core before editing 33 files against it.
4. **Slim the `SKILL.md` files (B2–B3, D2–D6)** and **cut support files (E1–E4)** — the bulk of the line savings; can be parallelized across skills.
5. **Collapse the Skills Doc to an index (A1, A3, A4)** and **trim the Process Doc (F)** and **architecture guidelines (G)**.
6. **Fix gaps/inconsistencies (H1–H7)** and **add the quickstart (I1–I3)**.
7. **Final verification pass:** anchor/link resolution audit across all docs; confirm every skill appears once in the index and once as a SKILL.md; confirm no cross-cutting rule is restated more than once per skill; confirm role names match everywhere.

---

## 7. Open decisions for you

- **Examples:** delete all 33, or keep the two trimmed eval examples? (Recommendation: delete all but the two.)
- **Checklists:** fold into SKILL.md §10, or keep as separate files but cut to ~10 bullets? (Recommendation: fold in.)
- **Skills Doc:** collapse §7 to a one-line index (recommended), or keep a medium catalogue and instead thin the SKILL.md files? You should not maintain both at full detail.
- **Reduction philosophy:** trim aggressively to the "essential core" now, or stage it conservatively (rules-hoist + examples first, measure, then trim SKILL.md bodies)?
- **Safety floor:** confirm the rule that *one* clear statement of each human-gate / PHI / residency boundary stays per relevant skill — we remove repetition, never the last copy.
