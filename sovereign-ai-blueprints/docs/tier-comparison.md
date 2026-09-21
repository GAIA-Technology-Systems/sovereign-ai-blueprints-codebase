# What you actually trade

| | 1 · Managed API | 2 · Private endpoints | 3 · Self-hosted |
|---|---|---|---|
| Where inference runs | Provider infrastructure | Your tenant, your region | Your hardware |
| Data boundary | Contractual | Contractual + network | Physical |
| Model quality ceiling | Highest available | Near-frontier | Open-weight, narrowing |
| Time to first value | Days | Weeks | Months |
| Cost profile | Per token, elastic | Per token + platform | Capex + fixed staffing |
| Ops burden | Near zero | Moderate — platform work | High — you run the stack |
| Defensible posture | DPA and retention terms | Residency, isolation, audit | No external processing |

## The cost line people skip

The compute bill is visible and gets approved. The engineering line is invisible and
decides whether the project survives year two. Tier 3 rarely fails on GPU spend — it
fails when the two people who understood the serving stack leave.

Before quoting any of this, index it to your own workload.
