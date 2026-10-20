"""Command-line entry point for the load generator.

Usage (from the repository root)::

    PYTHONPATH=src python3 -m ke_ems.loadgen fixture config/hotel-60rooms-sim-v1.toml

The ``fixture`` command writes a flat TEST FIXTURE (not hotel data) into the
output folder named in the configuration. Exit codes: 0 success, 1 the run
failed (nothing is written on invalid input), 2 wrong command-line usage.
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from ke_ems.loadgen.config import ConfigError, load_config
from ke_ems.loadgen.fixture import CATEGORY_COLUMNS, generate_flat_fixture
from ke_ems.loadgen.grid import GridError
from ke_ems.loadgen.writer import CsvWriteError

LOGGER = logging.getLogger(__name__)

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_USAGE = 2  # argparse exits with 2 on its own for usage errors


def run_fixture(config_path: Path) -> Path:
    """Load the configuration and write the flat fixture; return the CSV path.

    Raises:
        ConfigError: Configuration unreadable, invalid or missing a parameter.
        GridError, CsvWriteError: Invalid values reached the generator.
    """
    cfg = load_config(config_path)
    power_kw = {name: cfg.float_value("fixture", name) for name in CATEGORY_COLUMNS}
    return generate_flat_fixture(
        Path(cfg.str_value("output", "directory")),
        start_date=cfg.date_value("simulation", "start_date"),
        days=cfg.int_value("simulation", "days"),
        step_minutes=cfg.int_value("simulation", "step_minutes"),
        utc_offset_minutes=cfg.int_value("simulation", "utc_offset_minutes"),
        seed=cfg.int_value("simulation", "seed"),
        config_sha256=cfg.sha256,
        power_kw=power_kw,
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="python -m ke_ems.loadgen",
        description="Synthetic load generator (simulation only).",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    fixture = sub.add_parser(
        "fixture", help="write a flat TEST FIXTURE (not hotel data) from a config file"
    )
    fixture.add_argument("config", type=Path, help="path to the TOML configuration")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line; return the process exit code."""
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    try:
        csv_path = run_fixture(args.config)
    except (ConfigError, GridError, CsvWriteError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_FAILED
    print(f"wrote {csv_path}")
    return EXIT_OK
