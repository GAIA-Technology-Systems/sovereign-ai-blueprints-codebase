"""Small CLI: `python -m sovereign.cli --help`."""

from __future__ import annotations

import argparse
import json

from .classifier import Constraints, recommend
from .config import Settings
from .factory import build_client
from .interfaces import Tier


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sovereign")
    sub = parser.add_subparsers(dest="command", required=True)

    which = sub.add_parser("which-tier", help="run the decision framework")
    for flag in (
        "personal-data",
        "eu-only-contract",
        "annex-iii",
        "trade-secret-ip",
        "no-export-path",
    ):
        which.add_argument(f"--{flag}", action="store_true")
    which.add_argument("--concern", action="append", default=[], help="a stated concern to test")

    sub.add_parser("tier-info", help="show the configured tier")

    args = parser.parse_args(argv)

    if args.command == "which-tier":
        result = recommend(
            Constraints(
                personal_or_special_category_data=args.personal_data,
                contract_forbids_processing_outside_eu=args.eu_only_contract,
                annex_iii_high_risk=args.annex_iii,
                trade_secret_ip_in_prompt=args.trade_secret_ip,
                no_lawful_export_path=args.no_export_path,
                stated_concerns=args.concern,
            )
        )
        print(result)
        return 0

    if args.command == "tier-info":
        settings = Settings.from_env()
        client = build_client(settings)
        print(
            json.dumps(
                {"tier": client.tier.value, "label": Tier(client.tier).label, "model": client.model},
                indent=2,
            )
        )
        return 0

    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
