import pathlib

from sovereign.assistant import Assistant
from sovereign.audit import AuditLog
from sovereign.interfaces import Document, Principal
from sovereign.providers import MockClient
from sovereign.retrieval import PermissionFilteredIndex

DOC = Document(id="D-1", title="Excess", text="The standard excess is 250 EUR per event.")
USER = Principal.of("u1", roles=["staff"])


def build(tmp_path: pathlib.Path) -> Assistant:
    return Assistant(
        client=MockClient(),
        index=PermissionFilteredIndex().add(DOC),
        audit=AuditLog(str(tmp_path / "audit.jsonl")),
    )


def test_answer_cites_retrieved_document(tmp_path):
    answer = build(tmp_path).ask("What is the standard excess?", USER)
    assert "D-1" in answer.text
    assert [d.id for d in answer.documents] == ["D-1"]


def test_no_permitted_context_is_recorded_and_refused(tmp_path):
    assistant = build(tmp_path)
    answer = assistant.ask("zzzz nothing matches this query zzzz", USER)
    assert answer.completion is None
    entries = assistant.audit.entries()
    assert entries[-1]["decision"] == "no_permitted_context"


def test_audit_records_hashes_not_content(tmp_path):
    assistant = build(tmp_path)
    assistant.ask("What is the standard excess?", USER)
    entry = assistant.audit.entries()[-1]
    assert "excess" not in str(entry).lower()
    assert len(entry["query_sha256"]) == 16
    assert entry["documents"] == ["D-1"]
