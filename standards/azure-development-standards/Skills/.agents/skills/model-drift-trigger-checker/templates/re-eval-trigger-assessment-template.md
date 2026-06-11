# Re-Eval Trigger Assessment

## 1. Assessment Metadata

| Field | Value |
|---|---|
| Slice ID / Name | `<slice-id>` / `<slice-name>` |
| Assessment Date / Produced By | `<yyyy-mm-dd>` / `<agent-or-user>` |
| Previous Eval Summary Reference | `<path-or-id>` |
| Eval Contract Reference | `<path-or-id>` |
| Change Source | `<PR / commit ref / coding agent summary / fix loop>` |

---

## 2. Version Comparison

### Versioned Artifacts (Process Doc §21.1)

| Artifact | Previous Eval Version | Current Version | Source File | Changed? |
|---|---|---|---|---|
| Model name | `<name>` | `<name>` | `/config/model-version-policy.md` | `Yes / No` |
| Model version | `<version>` | `<version>` | `/config/model-version-policy.md` | `Yes / No` |
| Prompt version | `<version>` | `<version>` | `/prompts/prompt-manifest.json` | `Yes / No` |
| Tool schema version | `<version>` | `<version>` | `/tools/tool-schema-version.json` | `Yes / No` |
| Orchestration version | `<version>` | `<version>` | `/orchestration/orchestration-version.json` | `Yes / No` |
| Workflow/state logic version | `<version>` | `<version>` | `<manifest file>` | `Yes / No` |

### Behaviour Area Assessments (from change notes)

| Behaviour Area | Changed? | Evidence / Source |
|---|---|---|
| Permissions | `Yes / No / Unknown` | `<change notes ref>` |
| Memory behaviour | `Yes / No / Unknown` | `<change notes ref>` |
| Evidence handling | `Yes / No / Unknown` | `<change notes ref>` |

---

## 3. Trigger Determination

*For each `Yes` above.*

| Change | Area | Affected Scenarios | Trigger? | Rationale |
|---|---|---|---|---|
| `<change>` | `<Model / Prompt / Tool schema / Orchestration / Workflow state / Permissions / Memory / Evidence>` | `<SCN-IDs from contract>` | `Yes — full / Yes — partial / No — see rationale` | `<rationale>` |

**Overall trigger result:**
```
[ ] Full re-run required (all scenarios)
[ ] Partial re-run required (scenarios in §4)
[ ] No re-run required (rationale in §5)
[ ] Blocked — cannot determine (see §6)
```

---

## 4. Required Re-Run Scenarios

*Complete only if re-run is required. Based on the eval-contract scenario-to-behaviour-area mapping.*

| Scenario ID | Name | Reason Re-Run Required |
|---|---|---|
| `SCN-XXX` | `<name>` | `<which change affects this scenario>` |

**Note for `live-eval-runner`:** re-run with the required run count for each scenario's risk tier (Process Doc §19.1); all manifests must be current before re-run.

---

## 5. Non-Triggering Changes with Rationale

| Change | Area | Why Not Triggering | Scenarios Verified Unaffected |
|---|---|---|---|
| `<change>` | `<area>` | `<explicit reasoning>` | `<SCN-IDs or "all">` |

---

## 6. Blockers

| ID | Description | Impact | Action Required |
|---|---|---|---|
| BLK-001 | `<e.g., prompt manifest not updated — current version unknown>` | `<cannot confirm no-change / cannot scope re-run>` | `<update manifest before re-running this assessment>` |

---

## 7. Handoff Recommendation

**Re-eval required:** `Yes — full / Yes — partial / No / Blocked`

**Action:**
- Full re-run: dispatch `live-eval-runner` with all contract scenarios and current manifests.
- Partial re-run: dispatch `live-eval-runner` with the §4 scenarios and current manifests.
- No re-run: proceed to Stage 11 with the existing eval summary; attach this assessment to the closeout package.
- Blocked: resolve the blocker (update manifests or obtain change notes) before dispatching.
