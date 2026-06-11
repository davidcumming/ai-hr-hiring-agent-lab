# `slice-state.yaml` schema

The machine-readable state of a single slice as it moves through the lifecycle. One file per slice at `docs/delivery/slices/<slice-id>/slice-state.yaml`. See the [folder README](./README.md) and [Orchestration Map §2](../../../gentech_slice_lifecycle_orchestration_map.md#2-the-slice-orchestrator-skill).

The orchestrator reads this on resume and rewrites it after every stage transition. All stage numbers refer to the [Orchestration Map §3 stage table](../../../gentech_slice_lifecycle_orchestration_map.md#3-stage-indexed-table).

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `slice_id` | string | yes | Stable kebab-case identifier for the slice (matches the folder name). |
| `current_stage` | integer (0–20) | yes | The §3 stage the slice is currently in or about to enter. |
| `risk_tier` | enum: `low` \| `standard` \| `high-assurance` | yes | Drives the §3.1 collapse / lite path. |
| `gate_outcomes` | list of gate records | yes (may be empty) | One entry per gate evaluated so far. See below. |
| `pinned_versions` | mapping | yes | The versions in force for this slice; drives §21.1 re-eval triggers. See below. |
| `open_blockers` | list of strings | yes (may be empty) | Human-readable blockers currently preventing advance. |
| `artifacts` | mapping of name → pointer | yes (may be empty) | Pointers (repo paths / external refs) to artifacts the slice has produced. |
| `updated_at` | string (ISO-8601 date or datetime) | yes | When this file was last written. |

### `gate_outcomes[]` — gate record

| Field | Type | Required | Description |
|---|---|---|---|
| `gate` | string | yes | Gate name or stage (e.g. `stage-3-readiness`, `stage-16-merge`). |
| `outcome` | enum: `pass` \| `fail` \| `needs-revision` \| `blocked` \| `approved` \| `pending` | yes | The gate result. |
| `date` | string (ISO-8601 date) | yes | When the gate was evaluated. |
| `approver` | string | yes for human gates | Who approved (the human release authority for §16); `null` / omitted for automated checks. |

### `pinned_versions` — version manifest

These four are the re-eval trigger surface (Process Doc §21.1): a change to any of them may require eval re-runs.

| Field | Type | Required | Description |
|---|---|---|---|
| `model` | string | yes | Model + version in use (e.g. `gpt-4.1-2025-xx`). |
| `prompt` | string | yes | Prompt/version identifier. |
| `tool_schema` | string | yes | Tool-schema version. |
| `orchestration` | string | yes | Orchestration/workflow version. |

### `artifacts` — pointers

A free-form mapping from a short artifact name to a pointer. Pointers are repo-relative paths or external references (eval artifacts stay external per the source-of-truth rules). Example names: `slice_spec`, `eval_contract`, `eval_summary`, `closeout_package`, `traceability_matrix`.

## Notes

- This file records *where the slice is*, not *what it should do* — the slice spec is intent, not truth (see `Skills/.agents/AGENTS.md`).
- Keep raw eval transcripts and other noisy artifacts external; store only repo-safe pointers here.
- The template at [`_template/slice-state.yaml`](./_template/slice-state.yaml) is the canonical starting shape.
