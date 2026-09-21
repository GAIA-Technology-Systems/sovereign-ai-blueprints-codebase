"""A tiny lexical index.

Deliberately not a vector store: the point being demonstrated is *where the
permission check happens*, which is identical whether you rank by BM25 or cosine
similarity. Swap this for your real index and keep the filter-then-rank order.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..interfaces import Document, Principal
from .permissions import can_access

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return set(_TOKEN.findall(text.lower()))


def _score(query: str, document: Document) -> float:
    q = _tokens(query)
    if not q:
        return 0.0
    d = _tokens(document.title + " " + document.text)
    overlap = len(q & d)
    return overlap / len(q)


@dataclass
class PermissionFilteredIndex:
    """Enforces identity at query time. This is the one you want."""

    documents: list[Document] = field(default_factory=list)

    def add(self, *documents: Document) -> PermissionFilteredIndex:
        self.documents.extend(documents)
        return self

    def search(self, query: str, principal: Principal, k: int = 4) -> list[Document]:
        visible = [d for d in self.documents if can_access(principal, d)]
        scored = [(d, _score(query, d)) for d in visible]
        hits = [d for d, s in sorted(scored, key=lambda p: -p[1]) if s > 0]
        return hits[:k]


@dataclass
class NaiveIndex:
    """Anti-pattern, kept so the tests can prove the point.

    Ranks everything, then hands the top-k to the caller and hopes the prompt says
    "only use documents the user is allowed to see". The model sees the text either
    way, so the data has already left. `tests/test_permissions.py` demonstrates it.
    """

    documents: list[Document] = field(default_factory=list)

    def add(self, *documents: Document) -> NaiveIndex:
        self.documents.extend(documents)
        return self

    def search(self, query: str, principal: Principal, k: int = 4) -> list[Document]:
        scored = [(d, _score(query, d)) for d in self.documents]
        hits = [d for d, s in sorted(scored, key=lambda p: -p[1]) if s > 0]
        return hits[:k]
