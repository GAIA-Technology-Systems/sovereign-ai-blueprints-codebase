from sovereign.classifier import Constraints, recommend
from sovereign.interfaces import Tier


def test_no_constraints_stays_at_tier_one():
    result = recommend(Constraints())
    assert result.tier is Tier.MANAGED_API


def test_personal_data_moves_to_tier_two():
    result = recommend(Constraints(personal_or_special_category_data=True))
    assert result.tier is Tier.PRIVATE_ENDPOINT


def test_no_export_path_moves_to_tier_three():
    result = recommend(Constraints(no_lawful_export_path=True))
    assert result.tier is Tier.SELF_HOSTED


def test_stated_concerns_do_not_move_the_tier():
    result = recommend(
        Constraints(stated_concerns=["cloud_is_not_safe", "foreign_vendor", "bad_headline"])
    )
    assert result.tier is Tier.MANAGED_API
    assert len(result.dismissed) == 3


def test_export_constraint_dominates_the_others():
    result = recommend(
        Constraints(no_lawful_export_path=True, personal_or_special_category_data=True)
    )
    assert result.tier is Tier.SELF_HOSTED
