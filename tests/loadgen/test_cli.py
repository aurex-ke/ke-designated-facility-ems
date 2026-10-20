"""Tests for ke_ems.loadgen.cli (end to end, using temporary configs)."""

import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ke_ems.loadgen.cli import EXIT_FAILED, EXIT_OK, main
from ke_ems.loadgen.config import load_config
from ke_ems.loadgen.fixture import CATEGORY_COLUMNS, CSV_NAME, METADATA_NAME

REPO = Path(__file__).resolve().parents[2]
SHIPPED = REPO / "config" / "hotel-60rooms-sim-v1.toml"
DEF = 'definition = "test"'


def make_config(out_dir: str, *, drop: str = "", days: int = 2) -> str:
    """Return a minimal valid TOML text; ``drop`` removes lines containing it."""
    lines = [
        "[meta]",
        "schema_version = 1",
        'id = "test"',
        "[simulation]",
        f"seed = {{ value = 1, {DEF} }}",
        f"start_date = {{ value = 2026-01-01, {DEF} }}",
        f"days = {{ value = {days}, {DEF} }}",
        f"step_minutes = {{ value = 15, {DEF} }}",
        f"utc_offset_minutes = {{ value = 180, {DEF} }}",
        "[output]",
        f'directory = {{ value = "{out_dir}", {DEF} }}',
        "[fixture]",
    ]
    lines += [f"{name} = {{ value = 1.5, {DEF} }}" for name in CATEGORY_COLUMNS]
    if drop:
        lines = [line for line in lines if drop not in line]
    return "\n".join(lines) + "\n"


def run_main(argv: list[str]) -> tuple[int, str]:
    err = io.StringIO()
    out = io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
        code = main(argv)
    return code, err.getvalue()


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write_config(self, **kwargs: object) -> Path:
        path = self.tmp / "cfg.toml"
        path.write_text(make_config(str(self.tmp / "out"), **kwargs))  # type: ignore[arg-type]
        return path

    def test_success_writes_csv_and_metadata_with_config_hash(self) -> None:
        cfg = self.write_config()
        code, _ = run_main(["fixture", str(cfg)])
        self.assertEqual(code, EXIT_OK)
        out = self.tmp / "out"
        meta = json.loads((out / METADATA_NAME).read_text())
        self.assertEqual(meta["config_sha256"], hashlib.sha256(cfg.read_bytes()).hexdigest())
        self.assertEqual(meta["rows"], 2 * 96)
        self.assertEqual(
            meta["output_sha256"], hashlib.sha256((out / CSV_NAME).read_bytes()).hexdigest()
        )

    def test_two_runs_are_byte_identical(self) -> None:
        cfg = self.write_config()
        run_main(["fixture", str(cfg)])
        first = {n: (self.tmp / "out" / n).read_bytes() for n in (CSV_NAME, METADATA_NAME)}
        run_main(["fixture", str(cfg)])
        for name, data in first.items():
            self.assertEqual(data, (self.tmp / "out" / name).read_bytes())

    def test_missing_parameter_fails_and_writes_nothing(self) -> None:
        cfg = self.write_config(drop="utc_offset_minutes")
        code, err = run_main(["fixture", str(cfg)])
        self.assertEqual(code, EXIT_FAILED)
        self.assertIn("utc_offset_minutes", err)
        self.assertFalse((self.tmp / "out").exists())

    def test_parameter_without_provenance_fails(self) -> None:
        path = self.tmp / "cfg.toml"
        text = make_config(str(self.tmp / "out")).replace(
            f"seed = {{ value = 1, {DEF} }}", "seed = { value = 1 }"
        )
        path.write_text(text)
        code, _ = run_main(["fixture", str(path)])
        self.assertEqual(code, EXIT_FAILED)
        self.assertFalse((self.tmp / "out").exists())

    def test_invalid_value_fails_and_writes_nothing(self) -> None:
        path = self.tmp / "cfg.toml"
        path.write_text(
            make_config(str(self.tmp / "out")).replace(
                f"step_minutes = {{ value = 15, {DEF} }}", f"step_minutes = {{ value = 7, {DEF} }}"
            )
        )
        code, err = run_main(["fixture", str(path)])
        self.assertEqual(code, EXIT_FAILED)
        self.assertIn("step_minutes", err)
        self.assertFalse((self.tmp / "out").exists())

    def test_missing_config_file_fails(self) -> None:
        code, _ = run_main(["fixture", str(self.tmp / "nope.toml")])
        self.assertEqual(code, EXIT_FAILED)

    def test_usage_errors_exit_2(self) -> None:
        for argv in ([], ["fixture"], ["bogus"]):
            with self.subTest(argv=argv):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as ctx:
                        main(argv)
                self.assertEqual(ctx.exception.code, 2)

    def test_module_entry_point(self) -> None:
        cfg = self.write_config()
        env = {**os.environ, "PYTHONPATH": str(REPO / "src")}
        result = subprocess.run(
            [sys.executable, "-m", "ke_ems.loadgen", "fixture", str(cfg)],
            capture_output=True, text=True, env=env, cwd=self.tmp, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.tmp / "out" / CSV_NAME).exists())


class ShippedConfigTests(unittest.TestCase):
    """Guards against drift between the shipped config and what the CLI reads."""

    def test_shipped_config_has_every_parameter_the_cli_reads(self) -> None:
        cfg = load_config(SHIPPED)
        cfg.int_value("simulation", "seed")
        cfg.date_value("simulation", "start_date")
        cfg.int_value("simulation", "days")
        cfg.int_value("simulation", "step_minutes")
        self.assertEqual(cfg.int_value("simulation", "utc_offset_minutes"), 180)
        cfg.str_value("output", "directory")
        for name in CATEGORY_COLUMNS:
            self.assertGreaterEqual(cfg.float_value("fixture", name), 0.0)


if __name__ == "__main__":
    unittest.main()
