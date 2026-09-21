"""Scenario 2 — claims assist, tier 2. Two agents, different scopes, same question."""

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


def load(name: str) -> list[Document]:
    documents = []
    with open(HERE / "data" / name, encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            documents.append(
                Document(
                    id=row["id"],
                    title=row["title"],
                    text=row["text"],
                    acl_roles=frozenset(row.get("acl_roles", [])),
                    acl_scopes=frozenset(row.get("acl_scopes", [])),
                    metadata=row.get("metadata", {}),
                )
            )
    return documents


def main() -> None:
    settings = Settings.from_env()
    index = PermissionFilteredIndex().add(*load("policies.jsonl"), *load("claims.jsonl"))
    assistant = Assistant(
        client=build_client(settings),
        index=index,
        audit=AuditLog(settings.audit_log_path),
    )

    assigned = Principal.of("agent-anna", roles=["claims_agent"], scopes=["CLM-4471"])
    other = Principal.of("agent-ben", roles=["claims_agent"], scopes=["CLM-9002"])

    question = "What did the assessor find on claim CLM-4471 and is water damage covered?"

    for agent in (assigned, other):
        answer = assistant.ask(question, agent)
        retrieved = [d.id for d in answer.documents]
        saw_the_claim = "CLM-4471-ASSESSMENT" in retrieved
        print(f"\n{agent.id} (scopes={sorted(agent.scopes)})")
        print(f"  retrieved:            {retrieved}")
        print(f"  CLM-4471 assessment:  {'yes' if saw_the_claim else 'NO — filtered at query time'}")
        print(f"  answer:               {answer.text[:100]}")

    print("\nAudit trail (written inside the tenant):")
    for entry in AuditLog(settings.audit_log_path).entries()[-2:]:
        print(f"  {entry['principal']} -> {entry['documents']} [{entry['decision']}]")


if __name__ == "__main__":
    main()
