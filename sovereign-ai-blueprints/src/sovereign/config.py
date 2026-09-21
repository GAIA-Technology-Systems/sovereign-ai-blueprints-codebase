"""Configuration, read from the environment. See .env.example."""

from __future__ import annotations

import os
from dataclasses import dataclass

from .interfaces import Tier


@dataclass(frozen=True)
class Settings:
    tier: Tier = Tier.MOCK

    # tier 1 — managed API
    managed_api_base: str = "https://api.anthropic.com/v1"
    managed_api_key: str = ""
    managed_model: str = "claude-sonnet-4-6"
    managed_region: str = "eu"
    disable_provider_retention: bool = True

    # tier 2 — private endpoint in your own tenant
    private_endpoint: str = ""          # e.g. https://my-aoai.privatelink.openai.azure.com
    private_deployment: str = ""        # your deployment name
    private_api_version: str = "2024-10-21"
    private_region: str = "westeurope"

    # tier 3 — self hosted
    self_hosted_endpoint: str = "http://10.0.0.10:8000/v1"
    self_hosted_model: str = "open-weights/instruct"

    # audit log — always inside your own boundary
    audit_log_path: str = "./var/audit/audit.jsonl"

    @classmethod
    def from_env(cls) -> Settings:
        def s(key: str, default: str) -> str:
            return os.environ.get(key, default)

        def b(key: str, default: bool) -> bool:
            raw = os.environ.get(key)
            return default if raw is None else raw.strip().lower() in {"1", "true", "yes", "on"}

        return cls(
            tier=Tier(s("SOVEREIGN_TIER", Tier.MOCK.value)),
            managed_api_base=s("MANAGED_API_BASE", cls.managed_api_base),
            managed_api_key=s("MANAGED_API_KEY", ""),
            managed_model=s("MANAGED_MODEL", cls.managed_model),
            managed_region=s("MANAGED_REGION", cls.managed_region),
            disable_provider_retention=b("DISABLE_PROVIDER_RETENTION", True),
            private_endpoint=s("PRIVATE_ENDPOINT", ""),
            private_deployment=s("PRIVATE_DEPLOYMENT", ""),
            private_api_version=s("PRIVATE_API_VERSION", cls.private_api_version),
            private_region=s("PRIVATE_REGION", cls.private_region),
            self_hosted_endpoint=s("SELF_HOSTED_ENDPOINT", cls.self_hosted_endpoint),
            self_hosted_model=s("SELF_HOSTED_MODEL", cls.self_hosted_model),
            audit_log_path=s("AUDIT_LOG_PATH", cls.audit_log_path),
        )
