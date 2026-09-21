# Scenario 2 — Insurer, customer service over policy data (tier 2)

**The work.** Agent-assist drafting replies against a 400-page policy library and live
claim records. The draft must cite the clause it relied on; a human sends every reply.

**The constraint that decided it.** Personal and financial data, a DPA prohibiting
processing outside the EU, and a procurement questionnaire demanding a named
subprocessor list and residency evidence. Nothing about the model decided this — one
clause in a data processing agreement did.

**What it built.** Private endpoints in the customer's own tenant, EU region, no
public egress. Retrieval enforces **claim-level** permissions at query time. Every
prompt and response lands in their audit storage.

**What it traded.** Weeks instead of days, a platform engineer on the project, and
slightly behind the frontier on model quality — irrelevant for a scoped drafting task.

```bash
python scenarios/scenario2_claims_assist/run.py             # offline mock
SOVEREIGN_TIER=tier2 PRIVATE_ENDPOINT=https://x.privatelink.openai.azure.com \
  PRIVATE_DEPLOYMENT=gpt-4o-eu python scenarios/scenario2_claims_assist/run.py
```

The run prints the same question asked by two agents scoped to different claims. Both
see the shared policy wording; only the assigned agent sees the assessment for
CLM-4471. The second agent is not told to ignore it — the record never reaches the
ranker, the prompt, or the model, because the permission check happens first. `infra/tier2-azure/` has the deployment that makes the diagram true.
