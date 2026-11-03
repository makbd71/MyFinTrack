# 02 — Add a parser for a new sender

1. Save 2+ real emails from the sender as `.eml`, **anonymize** them (names, full card/account
   numbers, addresses), and put them in `tests/fixtures/<slug>/`.
2. Create `execution/parsers/<slug>.py` with a `Parser` subclass (see `execution/parsers/base.py`).
   - Return `[]` for promotional / non-transaction emails from that sender.
   - Raise `ValueError` for an unrecognized template (it then lands in the Unparsed sheet).
   - Amounts as `Decimal`; datetimes timezone-aware; cards masked with `mask_card()`.
3. Add `tests/parsers/test_<slug>.py` asserting the exact fields for each fixture.
4. Register the sender in `config/senders.yaml`.
5. Run `pytest -q`. All tests must pass.
