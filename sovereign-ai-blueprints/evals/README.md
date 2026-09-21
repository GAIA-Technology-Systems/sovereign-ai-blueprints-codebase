# Evals

Two things are checked here, and the second one is the reason this directory exists.

1. **Quality** — does the answer contain what it should (`must_include`)?
2. **Leakage** — does the answer contain a canary string planted in a document the
   principal is not allowed to see (`must_not_include`)?

A leakage case that passes tells you the boundary held for that query. A leakage case
that fails is a finding, not a regression in "answer quality".

```bash
python evals/run_evals.py                 # offline mock
SOVEREIGN_TIER=tier2 python evals/run_evals.py
```

Tier 3 is where this harness earns its keep: when you own the weights, nobody else is
running evaluations on your behalf.
