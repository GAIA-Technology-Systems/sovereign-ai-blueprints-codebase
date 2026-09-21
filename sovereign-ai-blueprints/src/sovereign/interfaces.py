"""Shared types and protocols.

The point of this module: application code depends on these protocols, never on a
specific provider. Moving between tiers is a configuration change, not a rewrite.
What changes between tiers is *where the boundary sits* — and that is infrastructure.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol


class Tier(str, Enum):
    """The three blueprints."""

    MANAGED_API = "tier1"       # hosted frontier model, provider perimeter
    PRIVATE_ENDPOINT = "tier2"  # model deployment inside your own tenant
    SELF_HOSTED = "tier3"       # open weights on hardware you control
    MOCK = "mock"               # offline, deterministic — for tests and demos

    @property
    def label(self) -> str:
        return {
            Tier.MANAGED_API: "Managed API, public model",
            Tier.PRIVATE_ENDPOINT: "Private endpoints in your own tenant",
            Tier.SELF_HOSTED: "Self-hosted open weights",
            Tier.MOCK: "Offline mock",
        }[self]


@dataclass(frozen=True)
class Principal:
    """Who is asking. Retrieval is filtered against this, at query time."""

    id: str
    roles: frozenset[str] = field(default_factory=frozenset)
    # Record-level scoping: claim ids, case ids, department codes...
    scopes: frozenset[str] = field(default_factory=frozenset)

    @classmethod
    def of(cls, id: str, roles: Sequence[str] = (), scopes: Sequence[str] = ()) -> Principal:
        return cls(id=id, roles=frozenset(roles), scopes=frozenset(scopes))


@dataclass(frozen=True)
class Document:
    """A retrievable document.

    `acl_roles` and `acl_scopes` are empty for public content. A document with either
    set is only visible to a principal holding at least one matching role/scope.
    """

    id: str
    text: str
    title: str = ""
    acl_roles: frozenset[str] = field(default_factory=frozenset)
    acl_scopes: frozenset[str] = field(default_factory=frozenset)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_public(self) -> bool:
        return not self.acl_roles and not self.acl_scopes


@dataclass(frozen=True)
class Completion:
    text: str
    model: str
    tier: Tier
    prompt_tokens: int = 0
    completion_tokens: int = 0


class LLMClient(Protocol):
    """Every tier implements exactly this. Application code sees nothing else."""

    tier: Tier
    model: str

    def complete(self, prompt: str, *, system: str | None = None, max_tokens: int = 512) -> Completion:
        ...


class RetrievalIndex(Protocol):
    """Retrieval is a boundary of its own. `principal` is not optional."""

    def search(self, query: str, principal: Principal, k: int = 4) -> list[Document]:
        ...
