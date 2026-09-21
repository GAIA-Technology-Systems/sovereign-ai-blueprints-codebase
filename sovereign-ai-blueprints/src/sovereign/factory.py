"""Tier selection. The only place in the codebase that knows which tier is in use."""

from __future__ import annotations

from .config import Settings
from .interfaces import LLMClient, Tier
from .providers import ManagedAPIClient, MockClient, PrivateEndpointClient, SelfHostedClient


def build_client(settings: Settings | None = None) -> LLMClient:
    settings = settings or Settings.from_env()
    if settings.tier is Tier.MOCK:
        return MockClient()
    if settings.tier is Tier.MANAGED_API:
        return ManagedAPIClient(settings)
    if settings.tier is Tier.PRIVATE_ENDPOINT:
        return PrivateEndpointClient(settings)
    if settings.tier is Tier.SELF_HOSTED:
        return SelfHostedClient(settings)
    raise ValueError(f"unknown tier {settings.tier!r}")
