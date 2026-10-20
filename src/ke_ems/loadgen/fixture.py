"""Flat TEST FIXTURE generator.

The values written here are constants chosen by the caller. They are NOT hotel
data and carry no shape assumption. Their only purpose is to prove the grid,
writer and metadata plumbing before any real profile is added.
"""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Mapping
from datetime import date
from pathlib import Path

from ke_ems.loadgen.grid import build_timestamps, make_timezone
from ke_ems.loadgen.writer import CsvWriteError, atomic_write_bytes, write_series_csv

LOGGER = logging.getLogger(__name__)

CATEGORY_COLUMNS = (
    "hvac_kw",
    "kitchen_kw",
    "laundry_kw",
    "hot_water_kw",
    "lighting_kw",
    "other_kw",
)
TOTAL_COLUMN = "total_kw"
CSV_NAME = "fixture_flat.csv"
METADATA_NAME = "fixture_flat.metadata.json"
METADATA_SCHEMA_VERSION = 1
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def generate_flat_fixture(
    out_dir: Path,
    *,
    start_date: date,
    days: int,
    step_minutes: int,
    utc_offset_minutes: int,
    seed: int,
    config_sha256: str,
    power_kw: Mapping[str, float],
) -> Path:
    """Write a flat fixture CSV plus a metadata JSON; return the CSV path.

    Args:
        out_dir: Output folder (created if missing).
        start_date: First day.
        days: Number of days.
        step_minutes: Interval length in minutes.
        utc_offset_minutes: Fixed UTC offset (Kenya: 180).
        seed: Recorded in the metadata. The flat fixture uses no randomness.
        config_sha256: SHA-256 of the config file the run used (64 hex chars).
        power_kw: One constant per name in ``CATEGORY_COLUMNS``, exactly.

    Raises:
        CsvWriteError: Bad power_kw keys, bad hash, or invalid values.
        GridError: Invalid grid parameters.
    """
    if set(power_kw) != set(CATEGORY_COLUMNS):
        raise CsvWriteError(f"power_kw keys must be exactly {sorted(CATEGORY_COLUMNS)}")
    if not isinstance(config_sha256, str) or not _SHA256_RE.match(config_sha256):
        raise CsvWriteError("config_sha256 must be 64 lowercase hex characters")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise CsvWriteError(f"seed must be an integer, got {seed!r}")

    tz = make_timezone(utc_offset_minutes)
    timestamps = build_timestamps(start_date, days, step_minutes, tz)
    n = len(timestamps)

    columns: dict[str, list[float]] = {
        name: [float(power_kw[name])] * n for name in CATEGORY_COLUMNS
    }
    total = sum(float(power_kw[name]) for name in CATEGORY_COLUMNS)
    columns[TOTAL_COLUMN] = [total] * n

    csv_path = Path(out_dir) / CSV_NAME
    output_sha256 = write_series_csv(csv_path, timestamps, columns)

    metadata = {
        "schema_version": METADATA_SCHEMA_VERSION,
        "data_kind": "test_fixture",
        "note": "Flat constants for plumbing tests. Not hotel data. Simulated only.",
        "seed": seed,
        "seed_used": False,
        "config_sha256": config_sha256,
        "output_file": CSV_NAME,
        "output_sha256": output_sha256,
        "rows": n,
        "columns": ["timestamp", *columns],
        "unit": "kW",
        "start": timestamps[0].isoformat(timespec="seconds"),
        "step_minutes": step_minutes,
        "utc_offset_minutes": utc_offset_minutes,
        "power_kw": {name: float(power_kw[name]) for name in CATEGORY_COLUMNS},
    }
    # No generation timestamp on purpose: identical inputs give identical bytes.
    payload = (json.dumps(metadata, indent=2, sort_keys=True) + "\n").encode("utf-8")
    atomic_write_bytes(Path(out_dir) / METADATA_NAME, payload)
    LOGGER.info("fixture written to %s", out_dir)
    return csv_path
