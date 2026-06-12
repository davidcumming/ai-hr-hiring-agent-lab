"""Provider registry (readiness pack, coding target 3).

Resolves a ``provider_id`` to a :class:`CouncilProvider` lazily — the default
path (``deterministic_mock``) never imports any Foundry module, and no module
in this package performs network I/O at import time or in default tests.

Guards (server-side only; request bodies can never reach these):

- ``HRHA_PROVIDER_KILL_SWITCH=true`` blocks every Foundry provider.
- ``HRHA_ENABLE_LIVE_AZURE`` unset/false keeps every live path disabled —
  Foundry providers resolve only to fail-closed scaffolds, and even those are
  refused unless the live flag is set (defense in depth: nothing live can be
  reached in this batch anyway because the scaffolds raise on use).
"""

from __future__ import annotations

from hr_eval_lab.config import (
    FOUNDRY_PROVIDER_IDS,
    LabConfig,
    live_azure_enabled,
    provider_kill_switch_active,
)
from hr_eval_lab.domain.schemas.provider import ProviderNotConfiguredError
from hr_eval_lab.providers.base import CouncilProvider


class ProviderBlockedError(ProviderNotConfiguredError):
    """A Foundry provider was requested but a server-side guard blocks it."""


def resolve_provider(config: LabConfig) -> CouncilProvider:
    """Resolve the configured provider_id. Lazy imports; fail closed."""
    provider_id = config.provider.provider_id

    if provider_id == "deterministic_mock":
        from hr_eval_lab.providers.mock import DeterministicMockProvider

        return DeterministicMockProvider()

    if provider_id in FOUNDRY_PROVIDER_IDS:
        if provider_kill_switch_active():
            raise ProviderBlockedError(
                f"provider '{provider_id}' is blocked: HRHA_PROVIDER_KILL_SWITCH is active"
            )
        if not live_azure_enabled():
            raise ProviderBlockedError(
                f"provider '{provider_id}' is unavailable: live Azure paths are "
                "disabled (HRHA_ENABLE_LIVE_AZURE is not 'true'); the "
                "deterministic_mock provider is the supported default"
            )
        # Even with the flags set, only fail-closed scaffolds exist this batch.
        from hr_eval_lab.providers import foundry

        return foundry.build_scaffold(provider_id)

    raise ProviderNotConfiguredError(f"unknown provider_id: {provider_id!r}")
