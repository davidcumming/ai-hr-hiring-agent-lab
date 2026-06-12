"""Shared fixtures for the deterministic suite DT-001…DT-018.

Provides:
- per-test temp ``var``-equivalent persistence isolation (every app instance
  gets its own ``tmp_path`` persistence root — no cross-test state);
- identity-header helpers (simulated lab identity, X-Lab-* headers);
- a scenario-scriptable provider helper (the DeterministicMockProvider script
  table, plus an invocation-counting wrapper for replay/efficiency assertions);
- config-override helper (tests exercise non-default config states by
  constructing LabConfig directly, per config.py's documented contract);
- a tampered-fixtures helper for the hash-mismatch -> ``blocked`` path.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

FIXTURES_ROOT = REPO_ROOT / "fixtures"

from fastapi.testclient import TestClient  # noqa: E402

from hr_eval_lab.api.app import create_app  # noqa: E402
from hr_eval_lab.config import (  # noqa: E402
    EscalationConfig,
    LabConfig,
    PersistenceConfig,
    ProviderConfig,
    RigorConfig,
)
from hr_eval_lab.providers.mock import DeterministicMockProvider  # noqa: E402

# ---------------------------------------------------------------------------
# Identity-header helpers (simulated lab identity, FR-002)
# ---------------------------------------------------------------------------

HR_HEADERS = {
    "X-Lab-Actor-Id": "u-hr-001",
    "X-Lab-Actor-Display": "Deterministic Suite HR User",
    "X-Lab-Roles": "hr,reviewer",
}


def identity_headers(
    actor_id: str = "u-hr-001",
    roles: str = "hr,reviewer",
    display: str | None = "Deterministic Suite HR User",
) -> dict[str, str]:
    headers = {"X-Lab-Actor-Id": actor_id, "X-Lab-Roles": roles}
    if display is not None:
        headers["X-Lab-Actor-Display"] = display
    return headers


# ---------------------------------------------------------------------------
# Provider helpers
# ---------------------------------------------------------------------------


class CountingProvider:
    """Provider-seam wrapper counting every invocation (DT-007/DT-008)."""

    ai_backend_type = "none"

    def __init__(self, inner: Any | None = None) -> None:
        self.inner = inner or DeterministicMockProvider()
        self.calls: list[str] = []

    def invoke_role(self, role_id: str, packet: Any, role_context: dict) -> Any:
        self.calls.append(role_id)
        return self.inner.invoke_role(role_id, packet, role_context)


def scripted_provider(script: dict) -> DeterministicMockProvider:
    """Scenario-scripted deterministic mock (test-composition-only seam)."""
    return DeterministicMockProvider(script=script)


# ---------------------------------------------------------------------------
# Config-override + app/client factories (per-test temp data isolation)
# ---------------------------------------------------------------------------


def make_config(
    tmp_path: Path,
    rigor: str = "high_impact",
    escalation: str = "record_only",
    backend: str = "none",
    subdir: str = "lab-data",
) -> LabConfig:
    return LabConfig(
        rigor=RigorConfig(default_mode=rigor),
        escalation=EscalationConfig(policy=escalation),
        provider=ProviderConfig(ai_backend_type=backend),
        persistence=PersistenceConfig(root=str(tmp_path / subdir)),
    )


@pytest.fixture()
def make_client(tmp_path):
    """Factory: isolated TestClient with optional config/provider overrides."""

    counter = {"n": 0}

    def _make(
        config: LabConfig | None = None,
        provider: Any | None = None,
        fixtures_root: Path | None = None,
        rigor: str = "high_impact",
        escalation: str = "record_only",
    ) -> TestClient:
        counter["n"] += 1
        if config is None:
            config = make_config(
                tmp_path,
                rigor=rigor,
                escalation=escalation,
                subdir=f"lab-data-{counter['n']}",
            )
        app = create_app(
            config=config,
            provider=provider,
            fixtures_root=fixtures_root or FIXTURES_ROOT,
        )
        client = TestClient(app)
        return client

    return _make


@pytest.fixture()
def client(make_client) -> TestClient:
    """Default isolated client: unscripted mock, default config states."""
    return make_client()


@pytest.fixture()
def tampered_fixtures_root(tmp_path) -> Path:
    """Copy of the fixtures tree with the resume content tampered so its
    sha256 no longer matches the manifest authority (DT-007 blocked path)."""
    dest = tmp_path / "tampered" / "fixtures"
    shutil.copytree(FIXTURES_ROOT, dest, ignore=shutil.ignore_patterns(".DS_Store"))
    resume = dest / "candidates" / "cand-sample-001" / "resume.md"
    resume.write_text(
        resume.read_text(encoding="utf-8") + "\nTAMPERED LINE (synthetic test mutation)\n",
        encoding="utf-8",
    )
    return dest


# ---------------------------------------------------------------------------
# Request helpers
# ---------------------------------------------------------------------------


def post_evaluation(
    client: TestClient,
    idempotency_key: str,
    position_id: str = "pos-sample-001",
    candidate_ref: str | None = "cand-sample-001",
    headers: dict[str, str] | None = None,
    **extra: Any,
):
    body: dict[str, Any] = {"position_id": position_id, "idempotency_key": idempotency_key}
    if candidate_ref is not None:
        body["candidate_ref"] = candidate_ref
    body.update(extra)
    return client.post("/api/evaluations", json=body, headers=headers or HR_HEADERS)


def get_record(client: TestClient, evaluation_id: str, headers: dict[str, str] | None = None) -> dict:
    response = client.get(f"/api/evaluations/{evaluation_id}", headers=headers or HR_HEADERS)
    assert response.status_code == 200, response.text
    return response.json()["result"]
