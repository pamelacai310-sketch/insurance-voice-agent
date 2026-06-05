from datetime import date

from insurance_voice_agent.window import default_window, subtract_months


def test_subtract_months_clamps_to_month_length() -> None:
    assert subtract_months(date(2026, 3, 31), 1) == date(2026, 2, 28)


def test_default_window_uses_six_calendar_months() -> None:
    assert default_window(date(2026, 6, 5)) == (date(2025, 12, 5), date(2026, 6, 5))
