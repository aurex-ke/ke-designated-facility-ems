"""Tests for ke_ems.loadgen.fixture (determinism and plumbing)."""

import csv
import hashlib
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from ke_ems.loadgen.fixture import (
    CATEGORY_COLUMNS,
    CSV_NAME,
    METADATA_NAME,
    generate_flat_fixture,
)
from ke_ems.loadgen.writer import CsvWriteError

CONFIG_HASH = "ab" * 32
POWER = {
    "hvac_kw": 10.0,
    "kitchen_kw": 5.0,
    "laundry_kw": 4.0,
    "hot_water_kw": 6.0,
    "lighting_kw": 3.0,
    "other_kw": 2.0,
}


def run(out: Path, **overrides) -> Path:
    args = dict(
        start_date=date(2026, 1, 1),
        days=3,
        step_minutes=15,
        utc_offset_minutes=180,
        seed=1,
        config_sha256=CONFIG_HASH,
        power_kw=POWER,
    )
    args.update(overrides)
    return generate_flat_fixture(out, **args)  # type: ignore[arg-type]


class FixtureTests(unittest.TestCase):
    def test_byte_identical_across_runs(self) -> None:
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            run(Path(a))
            run(Path(b))
            for name in (CSV_NAME, METADATA_NAME):
                self.assertEqual((Path(a) / name).read_bytes(), (Path(b) / name).read_bytes())

    def test_rerun_into_same_folder_is_identical(self) -> None:
        with tempfile.TemporaryDirectory() as a:
            run(Path(a))
            first = (Path(a) / CSV_NAME).read_bytes()
            run(Path(a))
            self.assertEqual(first, (Path(a) / CSV_NAME).read_bytes())

    def test_rows_values_and_total(self) -> None:
        with tempfile.TemporaryDirectory() as a:
            path = run(Path(a))
            rows = list(csv.DictReader(path.read_text().splitlines()))
            self.assertEqual(len(rows), 3 * 96)
            for row in rows:
                parts = [float(row[c]) for c in CATEGORY_COLUMNS]
                self.assertTrue(all(p >= 0 for p in parts))
                self.assertAlmostEqual(sum(parts), float(row["total_kw"]), places=3)

    def test_metadata_matches_output(self) -> None:
        with tempfile.TemporaryDirectory() as a:
            path = run(Path(a))
            meta = json.loads((Path(a) / METADATA_NAME).read_text())
            self.assertEqual(meta["output_sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(meta["rows"], 288)
            self.assertEqual(meta["data_kind"], "test_fixture")
            self.assertEqual(meta["config_sha256"], CONFIG_HASH)
            self.assertFalse(meta["seed_used"])
            self.assertEqual(meta["start"], "2026-01-01T00:00:00+03:00")

    def test_rejects_bad_inputs_and_writes_nothing(self) -> None:
        cases = [
            {"power_kw": {**POWER, "extra_kw": 1.0}},
            {"power_kw": {k: v for k, v in POWER.items() if k != "other_kw"}},
            {"power_kw": {**POWER, "hvac_kw": -1.0}},
            {"config_sha256": "XYZ"},
            {"seed": "1"},
        ]
        for override in cases:
            with self.subTest(override=override):
                with tempfile.TemporaryDirectory() as a:
                    with self.assertRaises(CsvWriteError):
                        run(Path(a), **override)
                    self.assertEqual(list(Path(a).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
