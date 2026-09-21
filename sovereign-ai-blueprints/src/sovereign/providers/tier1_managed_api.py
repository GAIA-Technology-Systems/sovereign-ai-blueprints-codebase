"""Tier 1 — managed API, public model.

What you control: the prompt, what you retrieve, retention settings, the region you
select, and above all *what you choose to send*. What you are trusting: provider
isolation and the contractual terms. For a large share of workloads that is the
correct trade, and this client makes no apology for it.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..config import Settings
from ..interfaces import Completion, Tier
from ._http import post_json


@dataclass
class ManagedAPIClient:
    settings: Settings
    tier: Tier = Tier.MANAGED_API

    def __post_init__(self) -> None:
        if not self.settings.managed_api_key:
            raise ValueError("MANAGED_API_KEY is not set")
        self.model = self.settings.managed_model

    def complete(self, prompt: str, *, system: str | None = None, max_tokens: int = 512) -> Completion:
        headers = {
            "x-api-key": self.settings.managed_api_key,
            "anthropic-version": "2023-06-01",
        }
        payload: dict = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            payload["system"] = system

        data = post_json(f"{self.settings.managed_api_base}/messages", payload, headers)
        text = "".join(block.get("text", "") for block in data.get("content", []))
        usage = data.get("usage", {})
        return Completion(
            text=text,
            model=data.get("model", self.model),
            tier=self.tier,
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
        )
