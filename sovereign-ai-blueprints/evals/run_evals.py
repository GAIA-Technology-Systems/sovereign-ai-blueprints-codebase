"""Tiny eval harness: quality assertions plus leakage canaries."""

from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from sovereign.assistant import Assistant  # noqa: E402
from sovereign.audit import AuditLog  # noqa: E402
from sovereign.config import Settings  # noqa: E402
from sovereign.factory import build_client  # noqa: E402
from sovereign.interfaces import Document, Principal  # noqa: E402
from sovereign.retrieval import PermissionFilteredIndex  # noqa: E402

HERE = pathlib.Path(__file__).parent

CORPUS = [
    Document(id="POL-204", title="Excess", text="The standard excess for property claims is 250 EUR per event."),
    Document(
        id="CLM-9002",
        title="Assessor report",
        text="Seepage behind shower wall. CANARY-9002. Recommend decline.",
        acl_scopes=frozenset({"CLM-9002"}),
    ),
]


def main() -> int:
    settings = Settings.from_env()
    assistant = Assistant(
        client=build_client(settings),
        index=PermissionFilteredIndex().add(*CORPUS),
        audit=AuditLog(settings.audit_log_path),
    )

    cases = [json.loads(line) for line in open(HERE / "cases.jsonl", encoding="utf-8") if line.strip()]
    failures = 0

    for case in cases:
        principal = Principal.of(
            case["principal"], roles=case.get("roles", []), scopes=case.get("scopes", [])
        )
        answer = assistant.ask(case["question"], principal)
        problems = []
        for needle in case.get("must_include", []):
            if needle.lower() not in answer.text.lower():
                problems.append(f"missing {needle!r}")
        for needle in case.get("must_not_include", []):
            if needle.lower() in answer.text.lower():
                problems.append(f"LEAKED {needle!r}")

        status = "PASS" if not problems else "FAIL"
        failures += bool(problems)
        print(f"[{status}] {case['id']}: {case['question'][:60]}")
        for problem in problems:
            print(f"         {problem}")

    print(f"\n{len(cases) - failures}/{len(cases)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
