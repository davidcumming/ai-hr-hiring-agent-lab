# Per-slice state files

Each active slice gets one folder here:

```text
docs/delivery/slices/<slice-id>/
  slice-state.yaml        # machine-readable lifecycle state for this slice
  ...                     # other per-slice delivery artifacts
```

## What `slice-state.yaml` is for

The `slice-orchestrator` tracks which stage a slice is in, but that state otherwise lives only in the model's context window — sessions end, context compacts, and the team switches between Claude Code and Codex. `slice-state.yaml` is the durable, tool-portable record of where a slice is.

The orchestrator **reads it on resume** and **writes it after every stage transition**, so the lifecycle is resumable, auditable, and portable across tools. It is also what CI can validate.

See the [Orchestration Map §2 — the `slice-orchestrator` skill](../../../gentech_slice_lifecycle_orchestration_map.md#2-the-slice-orchestrator-skill) for the orchestrator's read-on-resume / write-on-transition responsibility, and the stage list in [§3](../../../gentech_slice_lifecycle_orchestration_map.md#3-stage-indexed-table).

## Files in this folder

- [`slice-state.schema.md`](./slice-state.schema.md) — the field-by-field schema for `slice-state.yaml`.
- [`_template/slice-state.yaml`](./_template/slice-state.yaml) — a fill-in template with placeholder values; copy it to `<slice-id>/slice-state.yaml` to start a new slice.

## Conventions

- `<slice-id>` is a stable kebab-case identifier (e.g. `quicktodo-crud`), not a number.
- Treat `slice-state.yaml` as current-state truth for *where the slice is*, not as the slice spec (which is intent — see `Skills/.agents/AGENTS.md`).
- Per the root `AGENTS.md`, use `docs/delivery/slices/<slice-id>/...` for active per-slice delivery artifacts and `docs/planning/...` only for planning artifacts not yet attached to an approved slice.
