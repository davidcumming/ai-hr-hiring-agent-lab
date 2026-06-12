"""Server-side lab configuration: load + validate config/lab-config.toml.

The config file is source-controlled and is the only runtime configuration
surface this slice (slice spec §17; AF-006 defers the admin surface). Tests
exercise non-default states by constructing :class:`LabConfig` directly.

PLAN DEVIATION (recorded): the implementation plan assumed stdlib ``tomllib``
(Python 3.11+). This environment runs Python 3.10, so we fall back to the
``tomli`` package, which is API-compatible.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

try:  # Python 3.11+
    import tomllib  # type: ignore[import-not-found]
except ModuleNotFoundError:  # Python 3.10 fallback (see module docstring)
    import tomli as tomllib  # type: ignore[no-redef]

RigorMode = Literal["standard", "high_impact", "escalated"]
EscalationPolicy = Literal["record_only", "auto_escalate"]
AiBackendType = Literal["none", "foundry_agents"]

DEFAULT_CONFIG_PATH = Path("config") / "lab-config.toml"


class RigorConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    default_mode: RigorMode = "high_impact"


class EscalationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    policy: EscalationPolicy = "record_only"


class ProviderConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ai_backend_type: AiBackendType = "none"


class PersistenceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    root: str = "var/lab-data"


class LabConfig(BaseModel):
    """Typed, validated view of config/lab-config.toml."""

    model_config = ConfigDict(extra="forbid")

    rigor: RigorConfig = RigorConfig()
    escalation: EscalationConfig = EscalationConfig()
    provider: ProviderConfig = ProviderConfig()
    persistence: PersistenceConfig = PersistenceConfig()


def load_config(path: str | Path | None = None) -> LabConfig:
    """Read and validate the server-side config file (read once at app start)."""
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_PATH
    with open(config_path, "rb") as fh:
        raw = tomllib.load(fh)
    return LabConfig.model_validate(raw)
