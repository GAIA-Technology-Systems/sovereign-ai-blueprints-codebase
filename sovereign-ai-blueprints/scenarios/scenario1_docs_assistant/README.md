# Scenario 1 — Internal knowledge assistant (tier 1)

**Company.** A 200-person SaaS vendor. Support and sales spend hours hunting through a
wiki, a docs site and four years of release notes.

**Everything in scope is already published.** No customer records, no personal data.

**The constraint that decided it: none.** There is no DPA clause, no residency
requirement, no Annex III classification. The instinct to "keep it in-house" had no
requirement behind it, so this runs on a managed API with retention disabled and an
EU region selected.

**What it traded.** A dependency on a provider and per-token cost that scales with
use. In exchange: live in weeks, no platform team, best available answer quality.

```bash
python scenarios/scenario1_docs_assistant/run.py            # offline mock
SOVEREIGN_TIER=tier1 MANAGED_API_KEY=... python scenarios/scenario1_docs_assistant/run.py
```

The discipline in this scenario is refusing to over-engineer. Note that every
document in `data/docs.jsonl` is public: the ACL machinery is present and does
nothing, which is exactly right here.
