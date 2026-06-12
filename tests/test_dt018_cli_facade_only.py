"""DT-018 — CLI runner accesses the system via the HTTP facade ONLY.

Related: AC-018, FR-013.

Static: the cli module's import graph is stdlib + httpx only — no application,
store, or orchestrator internals (no privileged side door). Behavioral: a
submit -> get round trip driven through the CLI entrypoint travels strictly
over the HTTP client seam against the app.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import hr_eval_lab.cli as cli_module

from tests.conftest import FIXTURES_ROOT, make_config

ALLOWED_IMPORTS = {"argparse", "json", "sys", "httpx", "__future__"}


def _imported_top_level_modules(source: str) -> set[str]:
    tree = ast.parse(source)
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module.split(".")[0])
    return modules


def test_cli_import_graph_is_stdlib_plus_httpx_only():
    source = Path(cli_module.__file__).read_text(encoding="utf-8")
    modules = _imported_top_level_modules(source)
    assert modules <= ALLOWED_IMPORTS, f"forbidden CLI imports: {modules - ALLOWED_IMPORTS}"
    assert "hr_eval_lab" not in modules  # no app/store/orchestrator internals
    # Belt-and-braces: no textual reference to internal seams either.
    for forbidden in ("persistence", "orchestrator", "LocalStore", "run_council", "fixture_store"):
        assert forbidden not in source


def test_cli_submit_then_get_over_http_facade(make_client, monkeypatch, capsys, tmp_path):
    """Behavioral: the CLI works end to end with its httpx client redirected
    at the facade — proving HTTP is a sufficient (and its only) access path."""
    from fastapi.testclient import TestClient

    from hr_eval_lab.api.app import create_app

    config = make_config(tmp_path, subdir="dt018-data")
    app = create_app(config=config, fixtures_root=FIXTURES_ROOT)

    def _client_factory(**kwargs):
        # Same interface the CLI expects (context manager, .post/.get).
        return TestClient(app)

    monkeypatch.setattr(cli_module.httpx, "Client", _client_factory)

    exit_code = cli_module.main(
        [
            "--actor-id",
            "u-hr-cli",
            "--roles",
            "hr",
            "submit",
            "--position-id",
            "pos-sample-001",
            "--candidate-ref",
            "cand-sample-001",
            "--idempotency-key",
            "dt018-cli",
        ]
    )
    assert exit_code == 0
    submit_envelope = json.loads(capsys.readouterr().out)
    assert submit_envelope["status"] == "completed"
    evaluation_id = submit_envelope["evaluation_id"]

    exit_code = cli_module.main(
        ["--actor-id", "u-hr-cli", "--roles", "hr", "get", evaluation_id]
    )
    assert exit_code == 0
    get_envelope = json.loads(capsys.readouterr().out)
    assert get_envelope["status"] == "completed"
    assert get_envelope["result"]["evaluation_id"] == evaluation_id
    assert get_envelope["result"]["actor"]["actor_id"] == "u-hr-cli"
