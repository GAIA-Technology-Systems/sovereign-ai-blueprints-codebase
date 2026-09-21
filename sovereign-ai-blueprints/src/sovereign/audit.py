"""Audit logging.

Prompts and responses are verbatim copies of whatever went into them. If your model
runs inside a boundary and your traces go to a third-party observability tool, the
data left the boundary anyway. This writer appends to storage you control, and never
records document *content* — only ids, hashes and the principal.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from collections.abc import Iterable
from dataclasses import dataclass

from .interfaces import Completion, Principal, Tier


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


@dataclass
class AuditLog:
    path: str

    def __post_init__(self) -> None:
        directory = os.path.dirname(os.path.abspath(self.path))
        os.makedirs(directory, exist_ok=True)

    def record(
        self,
        *,
        principal: Principal,
        tier: Tier,
        query: str,
        document_ids: Iterable[str],
        completion: Completion | None = None,
        decision: str = "answered",
    ) -> dict:
        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "principal": principal.id,
            "roles": sorted(principal.roles),
            "tier": tier.value,
            "query_sha256": _digest(query),
            "documents": sorted(document_ids),
            "decision": decision,
            "model": completion.model if completion else None,
            "response_sha256": _digest(completion.text) if completion else None,
        }
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def entries(self) -> list[dict]:
        if not os.path.exists(self.path):
            return []
        with open(self.path, encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
