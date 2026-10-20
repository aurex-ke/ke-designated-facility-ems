"""Tests for ke_ems.loadgen.grid."""

import unittest
from datetime import date, datetime

from ke_ems.loadgen.grid import GridError, build_timestamps, make_timezone

EAT = make_timezone(180)


class GridTests(unittest.TestCase):
    def test_one_day_15_minutes_is_96_rows(self) -> None:
        self.assertEqual(len(build_timestamps(date(2026, 1, 1), 1, 15, EAT)), 96)

    def test_year_is_35040_rows(self) -> None:
        self.assertEqual(len(build_timestamps(date(2026, 1, 1), 365, 15, EAT)), 35040)

    def test_leap_year_span(self) -> None:
        ts = build_timestamps(date(2028, 1, 1), 366, 60, EAT)
        self.assertEqual(ts[-1].isoformat(), "2028-12-31T23:00:00+03:00")

    def test_first_and_last(self) -> None:
        ts = build_timestamps(date(2026, 1, 1), 2, 15, EAT)
        self.assertEqual(ts[0].isoformat(), "2026-01-01T00:00:00+03:00")
        self.assertEqual(ts[-1].isoformat(), "2026-01-02T23:45:00+03:00")

    def test_even_spacing_and_unique(self) -> None:
        ts = build_timestamps(date(2026, 3, 1), 3, 30, EAT)
        gaps = {(b - a).total_seconds() for a, b in zip(ts, ts[1:])}
        self.assertEqual(gaps, {1800.0})
        self.assertEqual(len(set(ts)), len(ts))

    def test_repeatable(self) -> None:
        a = build_timestamps(date(2026, 1, 1), 5, 15, EAT)
        b = build_timestamps(date(2026, 1, 1), 5, 15, EAT)
        self.assertEqual(a, b)

    def test_rejects_bad_arguments(self) -> None:
        bad = [
            (date(2026, 1, 1), 0, 15),
            (date(2026, 1, 1), -1, 15),
            (date(2026, 1, 1), 3661, 15),
            (date(2026, 1, 1), 1, 0),
            (date(2026, 1, 1), 1, 7),  # does not divide 1440
            (date(2026, 1, 1), 1.5, 15),
            (date(2026, 1, 1), True, 15),
            (datetime(2026, 1, 1), 1, 15),
            ("2026-01-01", 1, 15),
        ]
        for start, days, step in bad:
            with self.subTest(start=start, days=days, step=step):
                with self.assertRaises(GridError):
                    build_timestamps(start, days, step, EAT)  # type: ignore[arg-type]

    def test_rejects_bad_offset(self) -> None:
        for off in (-721, 841, 3.0, True):
            with self.subTest(off=off):
                with self.assertRaises(GridError):
                    make_timezone(off)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
