---
name: deterministic-test-author
description: "Adds or specifies all required deterministic tests for a slice, mapped to spec requirements and eval contract expectations. Use at Stage 8 for non-model test coverage."
---

# Skill: Deterministic Test Author

**Used at:** Stage 8 — Deterministic tests (Orchestration Map §3 stage table)
**Execution model:** `inline`
**Supports:** Process Doc §18 Testing and Eval Requirements, §24 Traceability

---

## 1. Purpose

Add or specify all required deterministic tests for a slice, mapped explicitly to slice spec requirements and eval contract expectations. Deterministic tests verify application logic, data transformations, state transitions, and API contracts — no model calls, predictable and repeatable outcomes. They are necessary for every slice but not sufficient: live-model evals (Stage 10) are required in addition to verify agentic behaviour (Process Doc §18). This skill produces test implementations (or test plans when it cannot write to the codebase) and a test gap report. It does not run tests, modify product logic to make tests pass, or claim a slice is complete.

---

## 3. Do Not Use This Skill For

- Running tests (coding agent's toolchain; results feed Stage 9/10), replacing live-model evals (Process Doc §18 requires both), or writing eval scenarios (`eval-contract-designer`, Stage 4).
- Covering integration scenarios that require live model calls — those are live-model eval scenarios.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Approved slice spec | Required | Requirements, acceptance criteria, business rules to test against. |
| 2 | Hardened eval contract | Required | Deterministic test expectations mapped to requirements — all must be covered. |
| 3 | Implementation plan (Stage 5) | Required | Test plan section lists test files, types, coverage expectations. |
| 4 | Existing test suite | Required | Folder structure, naming conventions, fixtures, framework version. |
| 5 | Current codebase (relevant modules) | Required | Production code under test — needed to write accurate tests. |
| 6 | Test framework conventions | Required | Parameterized patterns, fixture management, coverage tooling, CI/CD integration. |
| 7 | Known limitations | Recommended | What can be tested deterministically vs. what requires live evals. |

---

## 6. Source Authority Rules

| Question | Authority |
|---|---|
| What behaviour must be tested? | Approved slice spec (requirements, acceptance criteria, business rules) |
| What specific test expectations are required? | Hardened eval contract (deterministic test expectations) |
| What is the correct expected behaviour? | Approved slice spec — do not infer from implementation |
| What is out of scope for deterministic tests? | Eval contract (live-model section) + Process Doc §18 |

If production code behaviour contradicts the slice spec, this is a deviation — surface it. Do not write tests that validate incorrect behaviour as correct, and do not change product behaviour to make a test pass.

---

## 7. Process Steps

The standard testing fundamentals apply (one test per behaviour, assert on observable outcomes not internals, descriptive names) — apply them without belabouring; the value of this skill is coverage mapping and the live-model boundary.

1. **Load deterministic test expectations from the eval contract.** For each: note the requirement/criterion it maps to, the test type (unit, integration, workflow-state), and any fixtures/preconditions. This list is the mandatory minimum scope — do not produce fewer tests than the contract requires without an explicit gap flag.
2. **Review the existing test suite.** Identify files to extend, fixtures/utilities to reuse, and new infrastructure (fixtures, mocks, helpers) needed.
3. **Write/specify unit tests** for behaviour verifiable via a single function/class/module. Mock all external dependencies (database, API, model/prompt, Azure service calls). Cover edge cases, boundary values, and known failure paths. Naming (adapt to framework): `test_<unit>_<condition>_<expected_outcome>`, e.g. `test_reviewer_selector_when_no_reviewers_available_raises_assignment_error`.
4. **Write/specify integration tests** for acceptance criteria needing multiple units composed (e.g. a full API endpoint: validation + business logic + state update). Test through the real interface; mock only infrastructure that cannot run in CI; assert on observable outputs (response codes, state changes, events). Do not duplicate unit-level coverage.
5. **Write/specify workflow-state tests** for state transitions: valid transitions move correctly; invalid inputs/transitions are rejected; state persists and is readable (test double for storage). Map each to a state-transition requirement.
6. **Confirm model/prompt calls are mocked.** No deterministic test may make a real call to Azure OpenAI, Azure AI Foundry, any LLM endpoint, Copilot Studio agents/topics, or Power Platform AI/Prompt Builder. Any scenario needing a real model response is a live-model eval scenario and stays in the eval contract — not here.
7. **Build the coverage map and gap report.** For every requirement/criterion in the slice spec, list covering test(s) and type, and flag any with no coverage. For gaps, note whether the scenario is better covered by live-model evals (cross-reference the eval contract) or is a missing deterministic test to address.
8. **Confirm traceability.** Every test traces to at least one requirement/criterion in the slice spec or eval contract. Tests without a traceability link are noise and complicate the Stage 14 traceability matrix.
9. **Finalize.** If writing tests directly, produce a brief plan summary for the record; if specifying for a human or separate step, produce the full plan using `templates/deterministic-test-plan-template.md`.

---

## 8. Output Location

Test files: appropriate test directory per project conventions (`tests/unit/`, `tests/integration/`, `tests/workflow/`). Test plan: `docs/delivery/slices/<slice-id>/deterministic-test-plan.md`. Follow the project's convention if different and note the path.

---

## 9. Output Format

Use `templates/deterministic-test-plan-template.md` for the plan document. The gap report must be honest — do not suppress gaps to make coverage appear complete.

---

## 10. Quality Bar

Before handoff, confirm:

- Slice spec requirements/criteria and the eval contract's deterministic expectations were read; the implementation plan test section, existing test suite, and relevant production code were reviewed.
- Every deterministic test expectation in the eval contract has a corresponding test; none skipped without a documented gap flag.
- Every acceptance criterion and deterministically-verifiable business rule has a test or an explicit gap flag identifying whether it belongs in live-model evals or a future slice.
- Unit tests verify one behaviour per condition with descriptive names, assert on observable outputs, mock all external dependencies, and cover edge/boundary/error paths.
- Integration tests exercise the real interface, mock only true external infrastructure, assert on observable output, and do not duplicate unit coverage.
- Workflow-state tests cover valid and invalid transitions and verify persistence via a test double, each mapped to a state-transition requirement.
- No deterministic test makes a real LLM/Copilot/AI Builder call; model-dependent scenarios are flagged as live-model evals, not suppressed.
- Every test traces to a requirement/criterion; no orphan tests; the traceability table is complete.
- Code was checked against the spec; any mismatch is surfaced as a deviation flag for Stage 9, not silently accepted.
- Coverage summary counts are accurate; the plan is self-contained and does not claim the slice is done or merge-ready on these tests alone.

---

## 11. Failure Modes to Avoid

- Writing tests that rely on live model calls (breaks CI determinism; those belong in live-model evals).
- Claiming coverage is complete when it is not — suppressed gaps reach Stage 14 as false DoD claims.
- Changing product logic to make a failing test pass — surface a deviation instead.
- Missing workflow-state tests for stateful behaviour, or treating passing deterministic tests as sufficient for the definition of done.

---

## 13. Handoff to Next Skill

On completion, hand off with the test plan document, a coverage/gaps summary, and any deviation flags found during test writing.

- Implementation matched the spec: proceed to the Stage 9 check (conditional — if no deviation, skip to Stage 10 live eval).
- Deviations found: trigger Stage 9 `implementation-deviation-capture` before live evals.
- Tests fail: cycle back to Stage 7 implementation — do not proceed to Stage 10 with failing deterministic tests.

Do not claim the slice is done or merge-ready; passing deterministic tests satisfy only part of the definition of done — live-model evals (Stage 10) are also required.
