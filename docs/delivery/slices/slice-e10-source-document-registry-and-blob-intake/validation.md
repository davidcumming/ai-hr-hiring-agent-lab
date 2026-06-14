# Validation: E10 Source Document Registry and Blob Intake Foundation

## Deterministic Test Results

| Command | Result |
|---|---|
| `.venv/bin/python -m pytest tests/test_e10_source_documents_service.py tests/test_e10_source_documents_api.py` | Pass: 9 passed, 1 warning |
| `.venv/bin/python -m pytest tests/test_dt014_openapi.py tests/test_copilot_studio_openapi.py` | Pass: 16 passed, 1 warning |
| `.venv/bin/python -m pytest` | Pass: 302 passed, 7 skipped, 1 warning |

The warning in each pytest run is the existing Starlette/httpx deprecation
warning from FastAPI's test client import. No test failed.

## Contract And Smoke Checks

| Command | Result |
|---|---|
| `.venv/bin/python scripts/export_openapi.py --check` | Pass: source OpenAPI matches the committed file with no drift |
| `.venv/bin/python scripts/export_copilot_openapi.py --check` | Pass: curated Copilot Swagger matches generated output |
| `.venv/bin/python scripts/smoke_workflow_storage_config.py` | Pass: local workflow storage OK; live Azure workflow checks skipped by default guard |
| `git diff --check` | Pass |
| `git diff --cached --check` | Pass |
| `rg -n "[ \t]+$" <new E10 files>` | Pass: no trailing whitespace in new untracked files |

## Validation Notes

- No live Azure smoke was run or required for E10.
- No Foundry/model calls, queue messages, Copilot Studio changes, Power
  Platform changes, or Azure resource creation were performed.
- The curated Copilot Swagger remains evaluation-only.
