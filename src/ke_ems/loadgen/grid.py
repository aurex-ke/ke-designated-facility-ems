"""Deterministic timestamp grid for generated time series.

Timestamps use a fixed UTC offset (Kenya has no daylight saving time), so the
grid never skips or repeats a local hour.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, time, timedelta, timezone, tzinfo

LOGGER = logging.getLogger(__name__)

MINUTES_PER_DAY = 1440
MAX_DAYS = 3660  # safety bound (about 10 years); fail rather than fill the disk


class GridError(ValueError):
    """Raised when grid parameters are invalid."""


def _require_int(name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise GridError(f"{name} must be an integer, got {value!r}")
    return value


def make_timezone(utc_offset_minutes: int) -> timezone:
    """Return a fixed-offset timezone.

    Args:
        utc_offset_minutes: Offset from UTC in minutes (Kenya is +180).

    Raises:
        GridError: If the offset is not an integer within -720..840.
    """
    offset = _require_int("utc_offset_minutes", utc_offset_minutes)
    if not -720 <= offset <= 840:
        raise GridError(f"utc_offset_minutes out of range: {offset}")
    return timezone(timedelta(minutes=offset))


def build_timestamps(
    start_date: date, days: int, step_minutes: int, tz: tzinfo
) -> list[datetime]:
    """Build the timestamp grid, starting at local midnight of ``start_date``.

    Args:
        start_date: First calendar day (a ``date``, not a ``datetime``).
        days: Number of whole days, 1..MAX_DAYS.
        step_minutes: Interval length; must be positive and divide 1440.
        tz: Fixed-offset timezone (see :func:`make_timezone`).

    Returns:
        ``days * 1440 / step_minutes`` timezone-aware datetimes, evenly spaced.

    Raises:
        GridError: On any invalid argument (nothing is generated).
    """
    if isinstance(start_date, datetime) or not isinstance(start_date, date):
        raise GridError(f"start_date must be a date, got {start_date!r}")
    n_days = _require_int("days", days)
    step = _require_int("step_minutes", step_minutes)
    if not 1 <= n_days <= MAX_DAYS:
        raise GridError(f"days must be 1..{MAX_DAYS}, got {n_days}")
    if step < 1 or MINUTES_PER_DAY % step != 0:
        raise GridError(f"step_minutes must be positive and divide 1440, got {step}")
    if tz is None:
        raise GridError("tz is required")

    first = datetime.combine(start_date, time(0, 0), tzinfo=tz)
    delta = timedelta(minutes=step)
    count = n_days * (MINUTES_PER_DAY // step)
    LOGGER.debug("building %d timestamps from %s", count, first.isoformat())
    return [first + i * delta for i in range(count)]
