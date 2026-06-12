"""Foundry Agents seam stub — NON-FUNCTIONAL by design (live wiring deferred).

Contains no Azure SDK imports and no network code. It exists to pin the seam
contract shape against the agent-backed target (slice spec §15): wiring later
must be configuration, not restructuring. Any invocation raises
:class:`ProviderNotConfiguredError`. The deferred ADR
(docs/delivery/slices/slice-e1-candidate-evaluation-council/
adr-deferred-foundry-wiring.md) gates real wiring behind human approval; this
stub must not be wired, marked approved, or expanded in scope.
"""

from __future__ import annotations

from typing import Any

from hr_eval_lab.domain.schemas.audit import EvidencePacket
from hr_eval_lab.domain.schemas.provider import (
    ProviderNotConfiguredError,
    ProviderResult,
)
from hr_eval_lab.providers.base import CouncilProvider


class FoundryAgentProvider(CouncilProvider):
    """Lazy seam stub. Compiles against the same protocol and schema source as
    the deterministic mock (DT-013: no mock-only schema fork)."""

    ai_backend_type = "foundry_agents"

    def invoke_role(
        self,
        role_id: str,
        packet: EvidencePacket,
        role_context: dict[str, Any],
    ) -> ProviderResult:
        raise ProviderNotConfiguredError(
            "Foundry Agents backend is not configured in this slice; "
            "live wiring is deferred (PO §2.2.2)"
        )
