# Process Lessons

Durable operating-model lessons promoted from completed slices. Technical and Microsoft-stack implementation lessons live in `docs/delivery/implementation-lessons.md`.

## slice-e5-copilot-studio-registration-smoke

### PL-slice-e5-copilot-studio-registration-smoke-001

- **Title:** Manual configuration needs repo evidence.
- **Category:** documentation reconciliation
- **Lesson:** Manual Azure, Power Platform, Copilot Studio, and Dataverse configuration needs a repo evidence artifact even when the change itself cannot yet be represented as source-controlled configuration. The evidence should record what changed, where, why it matters, what is not source-controlled, and what follow-up issue tracks the gap.
- **Recommended change:** Recommend keeping manual evidence capture as a required closeout input for portal or low-code slices, even when screenshots or exports are not available.
- **Affected skill or template:** `manual-config-evidence-capture`, `manual-evidence-normalizer`, `closeout-package-builder`
- **Priority:** High
- **Follow-up issue recommended:** No; E5 follow-up issues already exist.
- **Source reference:** `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/manual-config-evidence.md` sections 1, 4, and 9; `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/closeout.md` section 7.

### PL-slice-e5-copilot-studio-registration-smoke-002

- **Title:** Caveated note-based evidence can be acceptable for narrow lab smoke.
- **Category:** closeout
- **Lesson:** Note-based evidence can be accepted for a narrow lab smoke slice when the closeout explicitly caveats the evidence depth, states what was not supplied, and limits the claim to the observed smoke behavior. This does not make note-based evidence the default for broader, production-like, security-sensitive, or regulated slices.
- **Recommended change:** Recommend that closeout packages call out the exact evidence limitation and scope boundary whenever screenshots, portal exports, managed solution exports, or replay artifacts are absent.
- **Affected skill or template:** `closeout-package-builder`, `definition-of-done-validator`
- **Priority:** Medium
- **Follow-up issue recommended:** No.
- **Source reference:** `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/traceability.md` BR-E5-01; `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/dod.md` discrepancies 1 and 4; `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/closeout.md` section 11.

### PL-slice-e5-copilot-studio-registration-smoke-003

- **Title:** Track current-state drift immediately.
- **Category:** documentation reconciliation
- **Lesson:** Current-state doc drift should be tracked as GitHub issues immediately, not left as informal memory. When a slice deliberately defers current-state reconciliation, closeout should name the contradictory files and lines and link the tracking issue that will repair the drift.
- **Recommended change:** Recommend that closeout and DoD validation preserve exact drift references when current-state docs are deferred under a narrow-scope exception.
- **Affected skill or template:** `current-state-reconciler`, `closeout-package-builder`, `definition-of-done-validator`
- **Priority:** High
- **Follow-up issue recommended:** No; issue #4 already tracks the E5 current-state drift.
- **Source reference:** `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/closeout.md` section 10; `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/dod.md` criterion 7 and discrepancy 2; issue #4.

### PL-slice-e5-copilot-studio-registration-smoke-004

- **Title:** Ordinary issue creation is backlog tracking, not approval.
- **Category:** governance gate
- **Lesson:** Ordinary non-destructive GitHub issue creation is backlog tracking and should not itself be treated as a human approval gate. Issue closing/deletion, committed priority or milestone changes, residual-risk acceptance, ADR approval, merge, and release remain human-governed actions.
- **Recommended change:** Recommend distinguishing safe issue creation from actions that change delivery commitments, close evidence, or approve risk. This keeps unresolved work visible without weakening human governance over irreversible or commitment-bearing decisions.
- **Affected skill or template:** `github-issue-drafter`, `manual-config-debt-monitor`, release-authority checklist
- **Priority:** High
- **Follow-up issue recommended:** No.
- **Source reference:** `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/manual-config-evidence.md` section 7; `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/closeout.md` sections 13 and 15.

### PL-slice-e5-copilot-studio-registration-smoke-005

- **Title:** Preserve human gates for risk and release decisions.
- **Category:** governance gate
- **Lesson:** Automation may generate, pre-fill, validate, or recommend artifacts, but residual-risk acceptance, ADR approval, merge, release, issue closing/deletion, and committed priority or milestone changes remain human-governed actions. E5 benefited from issue-backed tracking, but did not use that tracking as residual-risk acceptance or release approval.
- **Recommended change:** Recommend that governance cleanup artifacts separate "tracked" from "accepted" and "recommended" from "approved."
- **Affected skill or template:** `definition-of-done-validator`, `closeout-package-builder`, `manual-config-debt-monitor`
- **Priority:** High
- **Follow-up issue recommended:** No.
- **Source reference:** `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/manual-config-evidence.md` section 7; `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/dod.md` advisory statement.

### PL-slice-e5-copilot-studio-registration-smoke-006

- **Title:** Ask how automation can reduce manual operator work.
- **Category:** implementation workflow
- **Lesson:** Every slice with manual portal or low-code work should ask whether an agent can generate, pre-fill, validate, export, import, or replay configuration to reduce manual operator work. Even when a lab smoke accepts manual notes, the next slice should look for the smallest automation step that lowers repetition and evidence risk.
- **Recommended change:** Recommend adding an automation-reduction prompt to manual-config planning and closeout checks.
- **Affected skill or template:** `manual-config-evidence-capture`, `source-control-config-capture`, `manual-config-debt-monitor`
- **Priority:** Medium
- **Follow-up issue recommended:** No new issue from this cleanup.
- **Source reference:** `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/manual-config-evidence.md` sections 4 and 6; `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/closeout.md` sections 7 and 11.
