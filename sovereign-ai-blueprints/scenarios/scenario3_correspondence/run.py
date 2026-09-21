"""Scenario 3 — correspondence triage, tier 3. Classification and summarisation only."""

from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

from sovereign.audit import AuditLog  # noqa: E402
from sovereign.config import Settings  # noqa: E402
from sovereign.factory import build_client  # noqa: E402
from sovereign.interfaces import Principal  # noqa: E402

HERE = pathlib.Path(__file__).parent

DEPARTMENTS = ["housing", "taxation", "social_support", "permits", "other"]

SYSTEM = (
    "You triage citizen correspondence for a public administration. "
    "Return ONLY a JSON object with keys: department (one of "
    f"{DEPARTMENTS}), summary (max 25 words, no names), confidence (0.0-1.0). "
    "Never draft a reply. Never invent facts not present in the letter."
)

# Below this, a human decides. The model routes nothing on its own.
CONFIDENCE_THRESHOLD = 0.75


def load_letters() -> list[dict]:
    with open(HERE / "data" / "letters.jsonl", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def parse(raw: str) -> dict:
    """Tolerant parse — a self-hosted model will hand you imperfect JSON sooner or later."""
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        return {"department": "other", "summary": "", "confidence": 0.0}
    try:
        return json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return {"department": "other", "summary": "", "confidence": 0.0}


def main() -> None:
    settings = Settings.from_env()
    client = build_client(settings)
    audit = AuditLog(settings.audit_log_path)
    clerk = Principal.of("triage-service", roles=["correspondence_service"])

    for letter in load_letters():
        completion = client.complete(
            f"Letter {letter['id']}:\n{letter['text']}", system=SYSTEM, max_tokens=200
        )
        result = parse(completion.text)
        confident = float(result.get("confidence", 0.0)) >= CONFIDENCE_THRESHOLD
        destination = result.get("department", "other") if confident else "human_queue"

        audit.record(
            principal=clerk,
            tier=client.tier,
            query=letter["id"],
            document_ids=[letter["id"]],
            completion=completion,
            decision=f"routed:{destination}",
        )
        print(f"{letter['id']}: -> {destination}  (confidence {result.get('confidence', 0.0)})")

    print(
        "\nNothing was auto-routed below confidence "
        f"{CONFIDENCE_THRESHOLD}; those go to a person, not a department."
    )


if __name__ == "__main__":
    main()
