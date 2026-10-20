"""Tests for ke_ems.loadgen.writer."""

import hashlib
import tempfile
import unittest
from pathlib import Path

from datetime import date

from ke_ems.loadgen.grid import build_timestamps, make_timezone
from ke_ems.loadgen.writer import CsvWriteError, render_series_csv, write_series_csv

TS = build_timestamps(date(2026, 1, 1), 1, 360, make_timezone(180))  # 4 rows


class WriterTests(unittest.TestCase):
    def test_exact_bytes(self) -> None:
        data = render_series_csv(TS, {"a_kw": [1, 2.5, 0, 3.14159]})
        expected = (
            "timestamp,a_kw\n"
            "2026-01-01T00:00:00+03:00,1.000\n"
            "2026-01-01T06:00:00+03:00,2.500\n"
            "2026-01-01T12:00:00+03:00,0.000\n"
            "2026-01-01T18:00:00+03:00,3.142\n"
        ).encode()
        self.assertEqual(data, expected)

    def test_negative_zero_is_normalised(self) -> None:
        data = render_series_csv(TS, {"a": [-0.0, 0, 0, 0]})
        self.assertNotIn(b"-0.000", data)

    def test_rejects_invalid_values(self) -> None:
        for bad in (-1.0, float("nan"), float("inf"), "x", None, True):
            with self.subTest(bad=bad):
                with self.assertRaises(CsvWriteError):
                    render_series_csv(TS, {"a": [1, 1, 1, bad]})  # type: ignore[list-item]

    def test_rejects_bad_shapes_and_names(self) -> None:
        with self.assertRaises(CsvWriteError):
            render_series_csv(TS, {"a": [1, 2, 3]})
        with self.assertRaises(CsvWriteError):
            render_series_csv([], {"a": []})
        with self.assertRaises(CsvWriteError):
            render_series_csv(TS, {})
        for name in ("", "timestamp", "a,b", 'a"b', "a\nb"):
            with self.subTest(name=name):
                with self.assertRaises(CsvWriteError):
                    render_series_csv(TS, {name: [1, 1, 1, 1]})

    def test_rejects_naive_timestamps(self) -> None:
        from datetime import datetime

        naive = [datetime(2026, 1, 1)]
        with self.assertRaises(CsvWriteError):
            render_series_csv(naive, {"a": [1]})

    def test_file_hash_matches_and_no_temp_left(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sub" / "x.csv"
            digest = write_series_csv(path, TS, {"a": [1, 2, 3, 4]})
            self.assertEqual(digest, hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual([p.name for p in path.parent.iterdir()], ["x.csv"])
            self.assertNotIn(b"\r", path.read_bytes())

    def test_failed_write_keeps_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.csv"
            write_series_csv(path, TS, {"a": [1, 2, 3, 4]})
            before = path.read_bytes()
            with self.assertRaises(CsvWriteError):
                write_series_csv(path, TS, {"a": [1, 2, 3, -4]})
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual([p.name for p in path.parent.iterdir()], ["x.csv"])


if __name__ == "__main__":
    unittest.main()
