"""Report period math. Deterministic: same input, same range."""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Literal
from zoneinfo import ZoneInfo

Period = Literal["daily", "weekly", "monthly"]


def period_range(period: Period, run_at: datetime) -> tuple[date, date]:
    """Inclusive (start, end) dates the report covers, given when it runs.

    daily   -> the previous calendar day
    weekly  -> Monday..Sunday of the week containing run_at (runs Sunday 20:00)
    monthly -> 1st..last day of run_at's month (runs on the last day 19:00)
    """
    today = run_at.date()
    if period == "daily":
        d = today - timedelta(days=1)
        return d, d
    if period == "weekly":
        start = today - timedelta(days=today.weekday())
        return start, start + timedelta(days=6)
    if period == "monthly":
        return today.replace(day=1), last_day_of_month(today)
    raise ValueError(f"unknown period {period!r}")


def last_day_of_month(d: date) -> date:
    first_next = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
    return first_next - timedelta(days=1)


def is_last_day_of_month(d: date) -> bool:
    return (d + timedelta(days=1)).day == 1


def bounds(start: date, end: date, tz: ZoneInfo) -> tuple[datetime, datetime]:
    """Timezone-aware [start 00:00, end+1 00:00) window for queries."""
    return (datetime.combine(start, time.min, tz),
            datetime.combine(end + timedelta(days=1), time.min, tz))
