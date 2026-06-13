# Validation: E7 Workflow Storage Foundation

Validation status: complete for E7 deterministic/local scope.

## Command Results

| Command | Result |
|---|---|
| `python3 -m pytest tests/test_e7_workflow_schemas.py tests/test_e7_blob_paths.py tests/test_e7_queue_messages.py tests/test_e7_local_workflow_store.py tests/test_e7_non_goals.py` | Passed: 59 passed. |
| `python3 -m pytest` | Passed: 259 passed, 7 skipped. |
| `python3 scripts/export_openapi.py --check` | Passed: committed OpenAPI matched generated output. |
| `python3 scripts/export_copilot_openapi.py --check` | Passed: committed Copilot Swagger matched generated output. |
| `python3 scripts/smoke_storage_config.py` | Passed: local backend OK; live storage checks skipped by default. |
| `python3 scripts/smoke_foundry_config.py` | Passed: live Foundry checks skipped by default. |
| `git diff --check` | Passed: no whitespace errors. |

## Secret Scan

Changed-file scan result: reviewed.

Command:

```bash
{ git diff --name-only; git ls-files --others --exclude-standard; } | sort -u | xargs rg --pcre2 -n "<secret-pattern>"
```

Findings:

- `tests/test_e7_blob_paths.py` contains the fake query-string sentinel
  shown by the scan to prove unsafe Blob paths are rejected.
- `src/hr_eval_lab/domain/schemas/workflow_queue.py` contains the
  source-controlled forbidden-marker constant list used to reject raw-content
  and secret-bearing Queue payload values.
- `tests/test_e7_queue_messages.py` contains fake forbidden-marker strings
  shown by the scan to prove Queue payloads reject those values.
- `docs/product-current-state/candidate-evaluation-council.md` documents the
  existing synthetic evaluation API field names for inline fixture text.

No real connection string, SAS token, key, tenant ID, subscription ID,
Function key, or real applicant data was found in changed files.
