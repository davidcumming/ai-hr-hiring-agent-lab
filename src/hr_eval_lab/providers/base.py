"""CouncilProvider — the provider seam (FR-012).

Every model-backed council role executes ONLY through this interface. The
orchestrator, gates, and persistence depend on this protocol plus the
provider-contract schemas — never on a concrete backend (anti-goal: the mock
must not become the architecture center).

``select_provider`` resolves the backend class lazily: the default path
(``ai_backend_type = "none"``) never instantiates or imports the Foundry stub.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from hr_eval_lab.config import LabConfig
from hr_eval_lab.domain.schemas.audit import EvidencePacket
from hr_eval_lab.domain.schemas.provider import ProviderResult


class CouncilProvider(ABC):
    """Seam contract: one role invocation in, one schema-bearing result out."""

    ai_backend_type: str = "none"

    @abstractmethod
    def invoke_role(
        self,
        role_id: str,
        packet: EvidencePacket,
        role_context: dict[str, Any],
    ) -> ProviderResult:
        """Execute one model-backed council role against the evidence packet.

        ``role_context`` carries prior validated role outputs, mode/rigor
        info, anomaly flags from the Deterministic Rules Validator, and (on a
        bounded corrective retry) a ``corrective_hint``.
        """


def select_provider(config: LabConfig) -> CouncilProvider:
    """Resolve the configured backend. Lazy: the Foundry stub module is only
    imported when explicitly configured (and even then raises on use)."""
    backend = config.provider.ai_backend_type
    if backend == "none":
        from hr_eval_lab.providers.mock import DeterministicMockProvider

        return DeterministicMockProvider()
    if backend == "foundry_agents":
        from hr_eval_lab.providers.foundry_stub import FoundryAgentProvider

        return FoundryAgentProvider()
    raise ValueError(f"unknown ai_backend_type: {backend}")  # unreachable via config validation
