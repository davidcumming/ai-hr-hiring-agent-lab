# Validation: E9 Case State Foundation API

Validation status: complete for E9 deterministic/local scope.

The commands were run with the local virtualenv interpreter
`.venv/bin/python` because this workstation's host `python3` environment does
not carry the repo's installed development dependencies.

## Command Results

| Command | Result |
|---|---|
| `.venv/bin/python -m pytest tests/test_e9_case_service.py tests/test_e9_case_api.py` | Passed: 13 passed, 1 warning. |
| `.venv/bin/python -m pytest tests/test_dt014_openapi.py tests/test_copilot_studio_openapi.py` | Passed: 16 passed, 1 warning. |
| `.venv/bin/python -m pytest` | Passed: 293 passed, 7 skipped, 1 warning. |
| `.venv/bin/python scripts/export_openapi.py --check` | Passed: committed source OpenAPI matched generated output. |
| `.venv/bin/python scripts/export_copilot_openapi.py --check` | Passed: curated Copilot Swagger matched generated output and remained evaluation-only. |
| `.venv/bin/python scripts/smoke_workflow_storage_config.py` | Passed: local workflow storage OK; Azure workflow storage checks skipped by default. |
| `git diff --check` | Passed: no whitespace errors. |

## Warning

Pytest reported the existing Starlette/FastAPI test-client deprecation warning:
`Using httpx with starlette.testclient is deprecated; install httpx2 instead.`
This is not introduced by E9 behavior and did not fail the suite.

## Scope Confirmation

- No live Azure workflow storage smoke was run or required.
- No live model, Foundry, Copilot Studio, Power Platform, applicant import,
  document upload, notification, queue worker, or candidate-contact behavior
  was exercised.
