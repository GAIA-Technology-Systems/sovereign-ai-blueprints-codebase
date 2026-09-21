"""Tier 3 — self-hosted open weights.

Talks to any OpenAI-compatible server (vLLM, TGI, llama.cpp server). The guard here
asserts the endpoint is loopback or RFC1918: at this tier the whole claim is that
nothing crosses your own network edge, so a public hostname is a contradiction, not
a convenience.

What you inherit at this tier: serving, scaling, upgrades, guardrails and your own
evaluation harness. That is the bill people forget — see evals/.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from urllib.parse import urlparse

from ..config import Settings
from ..interfaces import Completion, Tier
from ._http import post_json


class EgressError(RuntimeError):
    """Raised when a self-hosted endpoint is not actually on your own network."""


def assert_no_egress(url: str) -> None:
    host = (urlparse(url).hostname or "").lower()
    if host in {"localhost", "127.0.0.1", "::1"} or host.endswith((".internal", ".local", ".svc")):
        return
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        raise EgressError(
            f"{host!r} is not an internal address. A tier 3 deployment must not egress."
        ) from None
    if not (address.is_private or address.is_loopback):
        raise EgressError(f"{host!r} is routable on the public internet")


@dataclass
class SelfHostedClient:
    settings: Settings
    tier: Tier = Tier.SELF_HOSTED

    def __post_init__(self) -> None:
        assert_no_egress(self.settings.self_hosted_endpoint)
        self.model = self.settings.self_hosted_model

    def complete(self, prompt: str, *, system: str | None = None, max_tokens: int = 512) -> Completion:
        messages = ([{"role": "system", "content": system}] if system else []) + [
            {"role": "user", "content": prompt}
        ]
        data = post_json(
            f"{self.settings.self_hosted_endpoint}/chat/completions",
            {"model": self.model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.2},
            {},
        )
        usage = data.get("usage", {})
        return Completion(
            text=data["choices"][0]["message"]["content"],
            model=self.model,
            tier=self.tier,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
        )
