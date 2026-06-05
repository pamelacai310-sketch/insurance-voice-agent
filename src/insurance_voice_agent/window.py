"""Date-window helpers for rolling six-month collection jobs."""

from __future__ import annotations

import calendar
from datetime import date, datetime, timezone
from typing import Optional


def subtract_months(value: date, months: int) -> date:
    """Subtract calendar months while clamping the day to month length."""

    if months < 0:
        raise ValueError("months must be non-negative")

    month_index = value.month - 1 - months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def default_window(today: Optional[date] = None, months: int = 6) -> tuple[date, date]:
    """Return the inclusive collection window ending on today."""

    end = today or datetime.now(timezone.utc).date()
    return subtract_months(end, months), end
