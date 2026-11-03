from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from execution.parsers.base import Transaction, mask_card
from execution.periods import bounds
from execution.store import Store

NY = ZoneInfo("America/New_York")


def tx(**kw):
    base = dict(
        message_id="<m1@bank>", sender="alerts@bank.example",
        occurred_at=datetime(2026, 11, 2, 18, 30, tzinfo=NY), type="expense",
        amount=Decimal("42.50"), currency="USD", card_or_account="VISA ••1234",
        merchant="Kroger #512", category="Groceries",
    )
    base.update(kw)
    return Transaction(**base)


def test_rejects_float_amount():
    with pytest.raises(TypeError):
        tx(amount=42.5)


def test_rejects_naive_datetime():
    with pytest.raises(ValueError):
        tx(occurred_at=datetime(2026, 11, 2, 18, 30))


def test_mask_card_keeps_last_four_only():
    assert mask_card("4111 1111 1111 1234", "VISA") == "VISA ••1234"
    assert mask_card("x") is None


def test_dedup_same_payment_from_two_emails():
    s = Store(":memory:")
    assert s.add(tx(message_id="<alert@bank>"))
    # Merchant receipt for the same purchase → same fingerprint → skipped
    assert not s.add(tx(message_id="<receipt@kroger>", merchant="  KROGER  #512 "))
    assert len(s.between(*bounds(date(2026, 11, 2), date(2026, 11, 2), NY))) == 1


def test_between_uses_local_day_boundaries():
    s = Store(":memory:")
    s.add(tx(message_id="a", occurred_at=datetime(2026, 11, 2, 23, 59, tzinfo=NY)))  # 04:59 UTC next day
    s.add(tx(message_id="b", occurred_at=datetime(2026, 11, 3, 0, 1, tzinfo=NY), amount=Decimal("1.00")))
    got = s.between(*bounds(date(2026, 11, 2), date(2026, 11, 2), NY))
    assert [t.message_id for t in got] == ["a"]
    assert got[0].amount == Decimal("42.50")


def test_checkpoints_and_processed_log():
    s = Store(":memory:")
    assert s.get_checkpoint("imap:FinComm:last_uid") is None
    s.set_checkpoint("imap:FinComm:last_uid", "1200")
    assert s.get_checkpoint("imap:FinComm:last_uid") == "1200"
    s.mark_processed("<p@x>", "promo@shop", "excluded", "promotional")
    assert s.is_processed("<p@x>")
