"""Scenario 1 — public product documentation, tier 1."""

from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

from sovereign.assistant import Assistant  # noqa: E402
from sovereign.audit import AuditLog  # noqa: E402
from sovereign.config import Settings  # noqa: E402
from sovereign.factory import build_client  # noqa: E402
from sovereign.interfaces import Document, Principal  # noqa: E402
from sovereign.retrieval import PermissionFilteredIndex  # noqa: E402

HERE = pathlib.Path(__file__).parent


def load_documents() -> list[Document]:
    documents = []
    with open(HERE / "data" / "docs.jsonl", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            documents.append(
                Document(
                    id=row["id"],
                    title=row["title"],
                    text=row["text"],
                    acl_roles=frozenset(row.get("acl_roles", [])),
                )
            )
    return documents


def main() -> None:
    settings = Settings.from_env()
    assistant = Assistant(
        client=build_client(settings),
        index=PermissionFilteredIndex().add(*load_documents()),
        audit=AuditLog(settings.audit_log_path),
    )

    # Everyone in the company is the same principal here: the corpus is public.
    staff = Principal.of("support-agent-14", roles=["staff"])

    for question in [
        "How do I rotate an API key?",
        "What is the retention period for exported reports?",
        "Does the platform support SSO?",
    ]:
        answer = assistant.ask(question, staff)
        print(f"\nQ: {question}")
        print(f"   tier: {assistant.client.tier.value}  docs: {[d.id for d in answer.documents]}")
        print(f"   {answer.text[:150]}")


if __name__ == "__main__":
    main()
