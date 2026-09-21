"""Tier 2 — private endpoint inside your own tenant.

The model is the same class of thing as tier 1. What moved is the perimeter: the
deployment sits in your subscription, in your region, reachable only over private
networking, with diagnostics landing in your own storage.

`assert_private_host` is the guard that matters. A private deployment reached over
its public hostname is a tier 1 system wearing a tier 2 diagram.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from urllib.parse import urlparse

from ..config import Settings
from ..interfaces import Completion, Tier
from ._http import post_json

PRIVATE_SUFFIXES = (
    ".privatelink.openai.azure.com",
    ".privatelink.cognitiveservices.azure.com",
    ".privatelink.services.ai.azure.com",
    ".internal",
    ".local",
)


class BoundaryError(RuntimeError):
    """Raised when the configured endpoint would leave the tenant boundary."""


def assert_private_host(url: str) -> None:
    host = (urlparse(url).hostname or "").lower()
    if not host:
        raise BoundaryError(f"no host in endpoint {url!r}")
    if host.endswith(PRIVATE_SUFFIXES):
        return
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        raise BoundaryError(
            f"{host!r} is not a private-link or internal hostname. "
            "A tier 2 deployment must be reached over private networking."
        ) from None
    if not address.is_private:
        raise BoundaryError(f"{host!r} is a public address")


@dataclass
class PrivateEndpointClient:
    settings: Settings
    credential_token: str = ""   # Entra ID token; see docs/tier2-auth.md
    tier: Tier = Tier.PRIVATE_ENDPOINT

    def __post_init__(self) -> None:
        if not self.settings.private_endpoint or not self.settings.private_deployment:
            raise ValueError("PRIVATE_ENDPOINT and PRIVATE_DEPLOYMENT must be set")
        assert_private_host(self.settings.private_endpoint)
        self.model = self.settings.private_deployment

    def _token(self) -> str:
        if self.credential_token:
            return self.credential_token
        try:  # managed identity in production; no keys on disk
            from azure.identity import DefaultAzureCredential  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "install azure-identity, or pass credential_token explicitly"
            ) from exc
        credential = DefaultAzureCredential()
        return credential.get_token("https://cognitiveservices.azure.com/.default").token

    def complete(self, prompt: str, *, system: str | None = None, max_tokens: int = 512) -> Completion:
        url = (
            f"{self.settings.private_endpoint}/openai/deployments/"
            f"{self.settings.private_deployment}/chat/completions"
            f"?api-version={self.settings.private_api_version}"
        )
        messages = ([{"role": "system", "content": system}] if system else []) + [
            {"role": "user", "content": prompt}
        ]
        data = post_json(
            url,
            {"messages": messages, "max_tokens": max_tokens},
            {"authorization": f"Bearer {self._token()}"},
        )
        choice = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return Completion(
            text=choice,
            model=self.model,
            tier=self.tier,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
        )
