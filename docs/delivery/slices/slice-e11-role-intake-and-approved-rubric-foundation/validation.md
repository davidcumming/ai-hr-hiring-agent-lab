# Validation: E11 Role Intake and Approved Rubric Foundation

## Commands

```bash
".venv/bin/python" -m pytest tests/test_e11_role_intake_rubric_service.py tests/test_e11_role_intake_rubric_api.py
".venv/bin/python" -m pytest tests/test_dt014_openapi.py tests/test_copilot_studio_openapi.py
".venv/bin/python" -m pytest
".venv/bin/python" scripts/export_openapi.py --check
".venv/bin/python" scripts/export_copilot_openapi.py --check
".venv/bin/python" scripts/smoke_workflow_storage_config.py
git diff --check && git diff --cached --check
```

## Results

- `".venv/bin/python" -m pytest tests/test_e11_role_intake_rubric_service.py tests/test_e11_role_intake_rubric_api.py`
  - Passed: 12 passed, 1 warning.
- `".venv/bin/python" -m pytest tests/test_dt014_openapi.py tests/test_copilot_studio_openapi.py`
  - Passed: 16 passed, 1 warning.
- `".venv/bin/python" -m pytest`
  - Passed: 314 passed, 7 skipped, 1 warning.
- `".venv/bin/python" scripts/export_openapi.py --check`
  - Passed: source OpenAPI matches the committed file.
- `".venv/bin/python" scripts/export_copilot_openapi.py --check`
  - Passed: curated Copilot Swagger matches generated output.
- `".venv/bin/python" scripts/smoke_workflow_storage_config.py`
  - Passed local workflow storage config smoke; live Azure workflow storage
    checks were skipped by default as expected.
- `git diff --check && git diff --cached --check`
  - Passed.
- Additional trailing-whitespace scan across untracked new files
  - Passed.

## Caveats

- No live Azure smoke was required or run for E11.
- No Copilot Studio, Power Platform, Foundry/model, queue worker, applicant, or
  candidate workflow was changed.
- No cross-Blob/Table transaction exists; E11 checks duplicate versions before
  Blob writes and records this as a known storage-boundary caveat.
