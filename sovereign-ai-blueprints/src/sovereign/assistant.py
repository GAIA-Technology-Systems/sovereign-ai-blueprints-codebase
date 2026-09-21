"""The application.

Read this file and notice what is *not* in it: no provider names, no endpoints, no
network configuration. The three scenarios differ in their data, their ACL model and
their tier — not in this code path.
"""

from __future__ import annotations

from dataclasses import dataclass

from .audit import AuditLog
from .interfaces import Completion, Document, LLMClient, Principal, RetrievalIndex

DEFAULT_SYSTEM = (
    "You answer strictly from the provided context. If the context does not contain "
    "the answer, say so. Cite the document id in square brackets for every claim."
)


@dataclass
class Answer:
    text: str
    documents: list[Document]
    completion: Completion | None


@dataclass
class Assistant:
    client: LLMClient
    index: RetrievalIndex
    audit: AuditLog
    system: str = DEFAULT_SYSTEM
    k: int = 4

    def ask(self, question: str, principal: Principal) -> Answer:
        documents = self.index.search(question, principal, k=self.k)

        if not documents:
            self.audit.record(
                principal=principal,
                tier=self.client.tier,
                query=question,
                document_ids=[],
                decision="no_permitted_context",
            )
            return Answer(
                text="I could not find anything you have access to that answers this.",
                documents=[],
                completion=None,
            )

        prompt = self._build_prompt(question, documents)
        completion = self.client.complete(prompt, system=self.system)
        self.audit.record(
            principal=principal,
            tier=self.client.tier,
            query=question,
            document_ids=[d.id for d in documents],
            completion=completion,
        )
        return Answer(text=completion.text, documents=documents, completion=completion)

    @staticmethod
    def _build_prompt(question: str, documents: list[Document]) -> str:
        context = "\n".join(f"[{d.id}] {d.title}: {d.text}" for d in documents)
        return f"Context:\n{context}\n\nQuestion: {question}"
