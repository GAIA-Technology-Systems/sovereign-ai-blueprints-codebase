# The model is not the boundary

Teams secure the endpoint and leave three copies of the same data outside the line
they just drew.

## 1. The retrieval index

Permissions filtered *after* the search instead of enforced *during* it. The model
answers from documents the user could never open, and a prompt instruction to "only
use documents the user is allowed to see" is not an access control.

`PermissionFilteredIndex` filters, then ranks. `NaiveIndex` ranks and hopes;
`tests/test_permissions.py::test_naive_index_leaks_the_canary` proves what that costs.

Filtering after ranking has a second, quieter failure: forbidden documents consume
the top-k slots, so the user gets a worse answer *and* the audit log shows a retrieval
that never reached them. See `test_filtering_happens_before_ranking`.

## 2. The embeddings

Vectors are derivative copies of sensitive text. A vector store outside the boundary
is the data outside the boundary. Classify the index at the same level as its source,
and put it inside the same perimeter as the model.

## 3. The traces and logs

Prompts, responses and debug traces are verbatim records — and they are usually the
first thing routed to a third-party observability tool. `src/sovereign/audit.py`
writes ids and hashes into storage you control, and never document content.

A sovereign model in front of a leaky index is not a sovereign system.
