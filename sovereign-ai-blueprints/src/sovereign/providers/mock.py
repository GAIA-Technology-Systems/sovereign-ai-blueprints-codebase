"""Offline, deterministic client. Every scenario runs without credentials.

It is deliberately dumb: it echoes the context it was given and, for the triage
prompt, keyword-routes. The point of the demos is the boundary, not the model.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from ..interfaces import Completion, Tier

_CONTEXT_LINE = re.compile(r"^\[(?P<id>[^\]]+)\]\s*(?P<body>.*)$")

_ROUTES = {
    "housing": ("housing", ("housing", "rent", "subsidy", "tenant")),
    "taxation": ("taxation", ("tax", "assessment", "income")),
    "social_support": ("social_support", ("benefit", "allowance", "social")),
    "permits": ("permits", ("permit", "building", "extension", "inspector")),
}


@dataclass
class MockClient:
    tier: Tier = Tier.MOCK
    model: str = "mock-deterministic-1"

    def complete(self, prompt: str, *, system: str | None = None, max_tokens: int = 512) -> Completion:
        text = self._triage(prompt) if system and "department" in system else self._answer(prompt)
        return Completion(
            text=text,
            model=self.model,
            tier=self.tier,
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(text.split()),
        )

    @staticmethod
    def _answer(prompt: str) -> str:
        hits = []
        for line in prompt.splitlines():
            match = _CONTEXT_LINE.match(line.strip())
            if match:
                hits.append((match.group("id"), match.group("body")))
        if not hits:
            return "No context was retrieved that this user is permitted to see."
        first_id, first_body = hits[0]
        cited = ", ".join(f"[{h[0]}]" for h in hits)
        return f"{first_body.strip()} (drawn from {cited})"

    @staticmethod
    def _triage(prompt: str) -> str:
        lowered = prompt.lower()
        for department, keywords in _ROUTES.values():
            if any(keyword in lowered for keyword in keywords):
                payload = {
                    "department": department,
                    "summary": "Citizen reports an unresolved matter and asks for a decision.",
                    "confidence": 0.82,
                }
                break
        else:
            payload = {
                "department": "other",
                "summary": "Subject unclear from the letter text.",
                "confidence": 0.41,
            }
        return json.dumps(payload)
