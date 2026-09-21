"""The retrieval boundary. These tests are the point of the repository."""

from __future__ import annotations

from sovereign.interfaces import Document, Principal
from sovereign.retrieval import NaiveIndex, PermissionFilteredIndex

PUBLIC = Document(id="PUB-1", title="Opening hours", text="The office is open on weekdays.")
SECRET = Document(
    id="CLM-9002",
    title="Assessor report",
    text="Long-term seepage behind shower wall CANARY-LEAK-9002 recommend decline.",
    acl_scopes=frozenset({"CLM-9002"}),
)

ANNA = Principal.of("anna", roles=["claims_agent"], scopes=["CLM-4471"])
BEN = Principal.of("ben", roles=["claims_agent"], scopes=["CLM-9002"])


def test_public_documents_are_visible_to_everyone():
    index = PermissionFilteredIndex().add(PUBLIC, SECRET)
    assert [d.id for d in index.search("office open weekdays", ANNA)] == ["PUB-1"]


def test_scoped_document_is_invisible_without_the_scope():
    index = PermissionFilteredIndex().add(PUBLIC, SECRET)
    hits = index.search("seepage shower wall decline", ANNA)
    assert SECRET.id not in [d.id for d in hits]


def test_scoped_document_is_visible_with_the_scope():
    index = PermissionFilteredIndex().add(PUBLIC, SECRET)
    assert SECRET.id in [d.id for d in index.search("seepage shower wall", BEN)]


def test_naive_index_leaks_the_canary():
    """Rank-then-hope. The model sees the text, so the data has already left."""
    index = NaiveIndex().add(PUBLIC, SECRET)
    leaked = index.search("seepage shower wall", ANNA)
    assert any("CANARY-LEAK-9002" in d.text for d in leaked), (
        "this test documents the anti-pattern; if it fails the anti-pattern was fixed"
    )


def test_filtering_happens_before_ranking():
    """A forbidden document must not consume one of the k slots."""
    fillers = [
        Document(id=f"PUB-{i}", title="water damage note", text="water damage guidance")
        for i in range(2, 6)
    ]
    index = PermissionFilteredIndex().add(SECRET, *fillers)
    hits = index.search("water damage", ANNA, k=4)
    assert len(hits) == 4
    assert all(d.id.startswith("PUB-") for d in hits)
