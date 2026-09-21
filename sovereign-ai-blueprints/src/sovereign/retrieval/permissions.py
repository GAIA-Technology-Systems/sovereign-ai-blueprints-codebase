"""Access rules, evaluated per document per principal."""

from __future__ import annotations

from ..interfaces import Document, Principal


def can_access(principal: Principal, document: Document) -> bool:
    """Public documents are open. Anything else needs a matching role or scope.

    Note the ordering in `PermissionFilteredIndex`: this runs *before* scoring, so a
    document the principal cannot open never reaches the ranker, the prompt, or the
    model. Filtering after retrieval is a different system with a different threat
    model — see `NaiveIndex`.
    """
    if document.is_public:
        return True
    if document.acl_roles & principal.roles:
        return True
    if document.acl_scopes & principal.scopes:
        return True
    return False
