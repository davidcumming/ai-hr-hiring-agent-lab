"""Foundry prompt-based agent (declarative prompt agent executed by the Foundry Agent Service) — SCAFFOLD ONLY.

NON-FUNCTIONAL by design: no Azure/Foundry SDK import, no network code, no
credentials. Any invocation raises ProviderNotConfiguredError. The choice of
live runtime shape is the deferred ADR's question 2 (human gate); this module
exists only so future wiring is configuration, not restructuring.
"""

from __future__ import annotations

from typing import Any

from hr_eval_lab.domain.schemas.audit import EvidencePacket
from hr_eval_lab.domain.schemas.provider import (
    ProviderNotConfiguredError,
    ProviderResult,
)
from hr_eval_lab.providers.base import CouncilProvider


class FoundryPromptAgentProvider(CouncilProvider):
    """Fail-closed scaffold for the 'prompt_agent' runtime shape."""

    ai_backend_type = "foundry_agents"
    provider_id = "foundry_prompt_agent"

    def invoke_role(
        self,
        role_id: str,
        packet: EvidencePacket,
        role_context: dict[str, Any],
    ) -> ProviderResult:
        raise ProviderNotConfiguredError(
            "foundry_prompt_agent is a scaffold: live Foundry wiring is deferred and "
            "human-gated (deferred ADR); no live call is possible in this batch"
        )
