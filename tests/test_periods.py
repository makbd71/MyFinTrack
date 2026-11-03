from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from execution.periods import bounds, is_last_day_of_month, last_day_of_month, period_range

NY = ZoneInfo("America/New_York")


def at(y, m, d, h=9):
    return datetime(y, m, d, h, tzinfo=NY)


def test_daily_covers_previous_day():
    assert period_range("daily", at(2026, 11, 3)) == (date(2026, 11, 2), date(2026, 11, 2))


def test_daily_crosses_year():
    assert period_range("daily", at(2027, 1, 1)) == (date(2026, 12, 31), date(2026, 12, 31))


def test_weekly_on_sunday_is_monday_to_sunday():
    # 2026-11-08 is a Sunday
    assert period_range("weekly", at(2026, 11, 8, 20)) == (date(2026, 11, 2), date(2026, 11, 8))


@pytest.mark.parametrize("d,last", [
    (date(2026, 2, 10), date(2026, 2, 28)),
    (date(2028, 2, 10), date(2028, 2, 29)),   # leap year
    (date(2026, 12, 5), date(2026, 12, 31)),
    (date(2026, 4, 30), date(2026, 4, 30)),
])
def test_last_day_of_month(d, last):
    assert last_day_of_month(d) == last


def test_is_last_day_of_month():
    assert is_last_day_of_month(date(2026, 11, 30))
    assert not is_last_day_of_month(date(2026, 11, 29))


def test_monthly_range():
    assert period_range("monthly", at(2026, 11, 30, 19)) == (date(2026, 11, 1), date(2026, 11, 30))


def test_bounds_handle_dst_change():
    # DST ends in New York on 2026-11-01: that day is 25 hours long
    start, end = bounds(date(2026, 11, 1), date(2026, 11, 1), NY)
    # compare in UTC: same-zone subtraction in Python ignores the DST shift
    assert (end.astimezone(timezone.utc) - start.astimezone(timezone.utc)).total_seconds() == 25 * 3600
