"""The decision framework from the talk, as code.

Start at tier 1. A *named* constraint moves you up. Nothing else should — and the
`REJECTED_REASONS` list is there so the common non-reasons have somewhere to go.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .interfaces import Tier

REJECTED_REASONS = {
    "cloud_is_not_safe": "Unanchored nervousness is not a control objective.",
    "they_will_train_on_our_data": "Read the agreement; if it says they will not, that is a contractual control.",
    "foreign_vendor": "Follow the data flow and the processing terms, not the flag on the headquarters.",
    "bad_headline": "An incident changes your posture only if it changes your data flow.",
}


@dataclass
class Constraints:
    """Every field is a fact somebody can point at, in a contract or a regulation."""

    personal_or_special_category_data: bool = False
    contract_forbids_processing_outside_eu: bool = False
    annex_iii_high_risk: bool = False
    trade_secret_ip_in_prompt: bool = False
    no_lawful_export_path: bool = False
    # Things people say that are not constraints. Recorded, then ignored.
    stated_concerns: list[str] = field(default_factory=list)


@dataclass
class Recommendation:
    tier: Tier
    reasons: list[str]
    dismissed: list[str]

    def __str__(self) -> str:  # pragma: no cover - presentation only
        lines = [f"Recommended: {self.tier.value} — {self.tier.label}"]
        lines += [f"  because: {r}" for r in self.reasons]
        lines += [f"  not a reason: {d}" for d in self.dismissed]
        return "\n".join(lines)


def recommend(constraints: Constraints) -> Recommendation:
    reasons: list[str] = []
    tier = Tier.MANAGED_API

    if constraints.no_lawful_export_path:
        tier = Tier.SELF_HOSTED
        reasons.append("no lawful export path — the data cannot leave at all")
    else:
        if constraints.personal_or_special_category_data:
            tier = Tier.PRIVATE_ENDPOINT
            reasons.append("personal or special-category data is in scope")
        if constraints.contract_forbids_processing_outside_eu:
            tier = Tier.PRIVATE_ENDPOINT
            reasons.append("a contract clause forbids processing outside the EU")
        if constraints.annex_iii_high_risk:
            tier = Tier.PRIVATE_ENDPOINT
            reasons.append("Annex III classification requires logging, oversight and traceability")
        if constraints.trade_secret_ip_in_prompt:
            tier = Tier.PRIVATE_ENDPOINT
            reasons.append("trade-secret IP would be sent in the prompt")

    if not reasons:
        reasons.append("no named constraint applies — stay at tier 1 and ship")

    dismissed = [
        REJECTED_REASONS[c] for c in constraints.stated_concerns if c in REJECTED_REASONS
    ]
    return Recommendation(tier=tier, reasons=reasons, dismissed=dismissed)
