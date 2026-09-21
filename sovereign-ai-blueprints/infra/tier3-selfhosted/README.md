# Tier 3 infrastructure — self-hosted open weights

```bash
MODEL_DIR=/srv/models docker compose up -d
curl http://127.0.0.1:8000/v1/models
```

What you now own, and should budget for:

| You own | Why it costs more than the GPUs |
|---|---|
| Serving and scaling | Queueing, batching, concurrency limits, restarts at 02:00 |
| Model upgrades | New weights are a migration, with an eval run attached |
| Guardrails | No provider safety layer — you build it or you accept the gap |
| Evaluation | `evals/` is not optional here; it is the only quality signal you have |
| Key management | Weights are an asset with an access-control story of their own |

`HF_HUB_OFFLINE=1` is deliberate. At this tier a runtime download is an egress path,
and an egress path is the thing you said you did not have.
