# Scenario 3 — Public administration, citizen correspondence (tier 3)

**The work.** Thousands of letters a month in the national language, manually sorted
and routed. Backlogs, inconsistent routing, and no reliable view of what citizens are
writing about.

**The constraint that decided it.** National rules leave no lawful export path for the
records, and the content includes special-category data. No contractual control
substitutes for that: the data cannot leave.

**What it built.** An open-weight model self-hosted on state infrastructure, scoped to
**classification and summarisation only**. Human sign-off on every routing decision,
and an eval set built from historical cases.

**What it traded.** Months to deliver, GPU capex, two people who now own serving and
upgrades, and a model that would lose a general benchmark — but not this narrow task.

```bash
python scenarios/scenario3_correspondence/run.py            # offline mock
docker compose -f infra/tier3-selfhosted/docker-compose.yml up -d
SOVEREIGN_TIER=tier3 SELF_HOSTED_ENDPOINT=http://127.0.0.1:8000/v1 \
  python scenarios/scenario3_correspondence/run.py
```

Narrowing the task is what rescues tier 3 quality. This pipeline never drafts a reply:
it routes, summarises, and puts a human in front of the decision. Every routing
decision is written to the audit log with a confidence value, and anything below the
threshold goes to a human queue rather than a department.
