"""RP-012, RP-013: local CLI demo writes artifacts with a safe stdout; smoke
scripts are disabled by default and perform no live work.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"


def _run(script: str, *args: str, env_extra: dict | None = None):
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")}
    env.pop("HRHA_ENABLE_LIVE_AZURE", None)
    env.pop("HRHA_PROVIDER_KILL_SWITCH", None)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO_ROOT,
        timeout=120,
    )


def test_rp012_cli_local_run_writes_artifacts_and_safe_stdout(tmp_path):
    data_root = tmp_path / "demo"
    result = _run("run_council_local.py", "--data-root", str(data_root))
    assert result.returncode == 0, result.stderr
    out = result.stdout
    assert "status              : completed" in out
    assert "human_review_required: True" in out

    eval_dirs = list((data_root / "evaluations").iterdir())
    assert len(eval_dirs) == 1
    assert (eval_dirs[0] / "record.json").exists()
    assert (eval_dirs[0] / "council").is_dir()

    # Safe summary only: no resume/cover-letter fixture text on stdout.
    resume_text = (
        REPO_ROOT / "fixtures" / "candidates" / "cand-sample-001" / "resume.md"
    ).read_text(encoding="utf-8")
    sentinels = [line for line in resume_text.splitlines() if len(line) > 25][:5]
    assert sentinels
    for sentinel in sentinels:
        assert sentinel not in out
    # And no prompt-template text either.
    assert "Mandatory constraints" not in out


def test_rp013_smoke_foundry_disabled_by_default():
    result = _run("smoke_foundry_config.py")
    assert result.returncode == 0, result.stderr
    assert "SKIPPED" in result.stdout
    assert "Traceback" not in result.stderr


def test_rp013_smoke_foundry_live_flag_alone_is_still_skipped():
    result = _run("smoke_foundry_config.py", "--live")
    assert result.returncode == 0
    assert "SKIPPED" in result.stdout


def test_rp013_smoke_foundry_live_fails_safely_without_config():
    result = _run(
        "smoke_foundry_config.py", "--live", env_extra={"HRHA_ENABLE_LIVE_AZURE": "true"}
    )
    assert result.returncode == 2
    assert "CONFIG ERROR (safe failure)" in result.stdout
    assert "Traceback" not in result.stderr


def test_rp013_smoke_foundry_respects_kill_switch():
    result = _run(
        "smoke_foundry_config.py",
        "--live",
        env_extra={"HRHA_ENABLE_LIVE_AZURE": "true", "HRHA_PROVIDER_KILL_SWITCH": "true"},
    )
    assert result.returncode == 2
    assert "BLOCKED" in result.stdout


def test_rp013_smoke_storage_disabled_by_default():
    result = _run("smoke_storage_config.py")
    assert result.returncode == 0, result.stderr
    assert "SKIPPED" in result.stdout
    assert "local_filesystem backend   : OK" in result.stdout
    assert "Traceback" not in result.stderr


def test_rp013_smoke_storage_live_fails_safely_without_config():
    result = _run(
        "smoke_storage_config.py", "--live", env_extra={"HRHA_ENABLE_LIVE_AZURE": "true"}
    )
    assert result.returncode == 2
    assert "CONFIG ERROR (safe failure)" in result.stdout
