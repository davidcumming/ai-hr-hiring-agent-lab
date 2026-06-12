"""Foundry provider scaffolds (readiness pack) — NON-FUNCTIONAL by design.

Three future runtime shapes are scaffolded so the live-wiring slice is a
configuration exercise; **none is chosen** (deferred ADR question 2, human
gate). No module here imports any Azure/Foundry SDK at import time, performs
network I/O, or can execute a council role: every ``invoke_role`` raises
:class:`ProviderNotConfiguredError`.
"""

from __future__ import annotations

from hr_eval_lab.providers.base import CouncilProvider


def build_scaffold(provider_id: str) -> CouncilProvider:
    """Lazily construct the named scaffold (still fail-closed on use)."""
    if provider_id == "foundry_project_responses":
        from hr_eval_lab.providers.foundry.project_responses import (
            FoundryProjectResponsesProvider,
        )

        return FoundryProjectResponsesProvider()
    if provider_id == "foundry_prompt_agent":
        from hr_eval_lab.providers.foundry.prompt_agent import FoundryPromptAgentProvider

        return FoundryPromptAgentProvider()
    if provider_id == "foundry_hosted_agent":
        from hr_eval_lab.providers.foundry.hosted_agent import FoundryHostedAgentProvider

        return FoundryHostedAgentProvider()
    raise ValueError(f"not a foundry scaffold id: {provider_id!r}")
