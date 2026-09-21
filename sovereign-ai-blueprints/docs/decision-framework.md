# Which tier?

Start at tier 1. A **named** constraint moves you up. Nothing else should.

| Trigger | Lands at |
|---|---|
| Personal or special-category data in scope | Tier 2 |
| Contract forbids processing outside the EU | Tier 2 |
| Annex III classification — logging, oversight, traceability | Tier 2, often 3 |
| Trade-secret IP or source code in the prompt | Tier 2 / 3 |
| No lawful export path at all — national or sector rule | Tier 3 |
| None of the above | Tier 1 |

Run it:

```bash
python -m sovereign.cli which-tier --personal-data --eu-only-contract
python -m sovereign.cli which-tier --concern cloud_is_not_safe --concern foreign_vendor
```

The second command returns tier 1 and prints why each concern was dismissed. That is
the intended behaviour, and `tests/test_classifier.py` locks it in.

## What does not move you up

- *"The cloud isn't safe."* Unanchored nervousness is not a control objective.
- *"They'll train on our data."* Read the agreement. If it says they will not, that is a
  contractual control with a remedy attached. Verify it; don't assume it.
- *"It's a foreign vendor."* Follow the data flow and the processing terms, not the flag
  on the headquarters. Residency is a configuration, not a nationality.
- *"There was a headline."* An incident changes your posture only if it changes your
  data flow. Most don't.

Say all four kindly, then ask the question that ends the argument: **which data, which
system, which clause?**
