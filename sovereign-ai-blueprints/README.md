# Sovereign AI Blueprints

**One application. Three data boundaries.**

Companion code for the talk *Sovereign by Design: three blueprints for AI that can't
leave the building* (AI Tech Summit, Skopje, 22–23 September 2026).

The argument the repository is built to demonstrate: **the tier is a configuration
choice; the boundary is architecture.** `src/sovereign/assistant.py` contains no
provider names, no endpoints and no network configuration. What changes between the
three scenarios is the data, the access model and where the perimeter sits.

```bash
git clone https://github.com/GAIA-Technology-Systems/sovereign-ai-blueprints
cd sovereign-ai-blueprints
pip install -e ".[dev]"
make demo      # all three scenarios, offline, no credentials
make test
make evals     # quality assertions + leakage canaries
```

## The three blueprints

| | Tier 1 | Tier 2 | Tier 3 |
| --- | --- | --- | --- |
| **Blueprint** | Managed API, public model | Private endpoints in your tenant | Self-hosted open weights |
| **Scenario** | SaaS internal knowledge assistant | Insurer claims assist | Public administration correspondence |
| **Deciding constraint** | none — and that is the point | one DPA clause | no lawful export path |
| **Client** | `providers/tier1_managed_api.py` | `providers/tier2_private_endpoint.py` | `providers/tier3_self_hosted.py` |
| **Infrastructure** | — | `infra/tier2-azure/main.bicep` | `infra/tier3-selfhosted/` |

Full comparison: [docs/tier-comparison.md](docs/tier-comparison.md).

## Which tier do you need?

```bash
python -m sovereign.cli which-tier --personal-data --eu-only-contract
python -m sovereign.cli which-tier --concern cloud_is_not_safe
```

Start at tier 1 and let a **named** constraint push you up. Never start at tier 3 and
look for a reason. The second command demonstrates the difference: it returns tier 1
and prints why the concern was dismissed. See
[docs/decision-framework.md](docs/decision-framework.md).

## The part everyone gets wrong

Securing the model endpoint and leaving the retrieval layer open is the most common
failure in this whole space, so it has tests rather than prose:

- `PermissionFilteredIndex` enforces identity **at query time**, before ranking.
- `NaiveIndex` is the anti-pattern, kept deliberately so a test can demonstrate it
  leaking a canary string into the context.
- `audit.py` writes ids and hashes to storage you control, never document content.

```bash
pytest tests/test_permissions.py -v
```

More: [docs/retrieval-boundary.md](docs/retrieval-boundary.md).

## Boundary guards

A tier is a claim about where traffic goes, so the claim is asserted in code:

- `tier2_private_endpoint.assert_private_host` refuses to start against a public
  hostname. A private deployment reached over its public endpoint is a tier 1 system
  wearing a tier 2 diagram.
- `tier3_self_hosted.assert_no_egress` refuses anything that is not loopback or
  RFC1918.

Both are covered in `tests/test_boundaries.py`.

## Layout

```
src/sovereign/          core: interfaces, assistant, retrieval, audit, classifier
  providers/            one client per tier + an offline mock
  retrieval/            permission-filtered index and the anti-pattern
scenarios/              three runnable scenarios, one per tier
evals/                  quality assertions and leakage canaries
infra/tier2-azure/      bicep: private endpoint, no public access, no local auth
infra/tier3-selfhosted/ docker compose: vLLM bound to loopback, offline weights
docs/                   decision framework, retrieval boundary, tier comparison
```

## Caveats

Reference code for a conference talk, not a product. The retrieval index is lexical
and in-memory so the permission logic stays readable — swap it for your own index and
keep the filter-then-rank order. The infrastructure templates are illustrative: review
naming, SKUs and policy against your own landing zone before deploying anything.

MIT licensed.
