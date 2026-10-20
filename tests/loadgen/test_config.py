"""Tests for the load-generator configuration loader (standard library only)."""

from __future__ import annotations

import datetime as dt
import tempfile
import textwrap
import unittest
from pathlib import Path

from ke_ems.loadgen import ConfigError, load_config

REPO_ROOT = Path(__file__).resolve().parents[2]
SHIPPED = REPO_ROOT / "config" / "hotel-60rooms-sim-v1.toml"

HEADER = """
[meta]
schema_version = 1
id = "test-config"
"""


class ConfigTestCase(unittest.TestCase):
    """Base class with a helper that writes a temporary TOML file."""

    def write(self, body: str, header: str = HEADER) -> Path:
        """Write header plus body to a temporary file and return its path."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "config.toml"
        path.write_text(textwrap.dedent(header + body), encoding="utf-8")
        return path

    def assertRejects(self, body: str, fragment: str, header: str = HEADER) -> None:
        """Assert that loading raises ConfigError mentioning ``fragment``."""
        with self.assertRaises(ConfigError) as ctx:
            load_config(self.write(body, header))
        self.assertIn(fragment, str(ctx.exception))


class ShippedConfigTests(ConfigTestCase):
    """The configuration committed in the repository must itself be valid."""

    def test_shipped_config_loads(self) -> None:
        cfg = load_config(SHIPPED)
        self.assertEqual(cfg.config_id, "hotel-60rooms-sim-v1")
        self.assertEqual(cfg.int_value("hotel", "rooms"), 60)
        self.assertEqual(cfg.int_value("simulation", "seed"), 1)
        self.assertEqual(cfg.int_value("simulation", "step_minutes"), 15)
        self.assertEqual(cfg.date_value("simulation", "start_date"), dt.date(2026, 1, 1))
        self.assertEqual(cfg.str_value("output", "directory"), "data/loadgen")

    def test_every_shipped_parameter_has_provenance(self) -> None:
        cfg = load_config(SHIPPED)
        for param in cfg:
            self.assertIn(param.provenance, {"sourced", "assumption", "definition"})
            self.assertTrue(param.note, param.qualified_name)

    def test_hash_is_stable_across_loads(self) -> None:
        self.assertEqual(load_config(SHIPPED).sha256, load_config(SHIPPED).sha256)

    def test_step_divides_a_day(self) -> None:
        step = load_config(SHIPPED).int_value("simulation", "step_minutes")
        self.assertGreater(step, 0)
        self.assertEqual(1440 % step, 0)


class ValidConfigTests(ConfigTestCase):
    """Accepted shapes."""

    def test_all_three_provenance_kinds(self) -> None:
        cfg = load_config(
            self.write(
                """
                [s]
                a = { value = 1.5, source = "Some report, publisher, URL", retrieved = 2026-10-20 }
                b = { value = 0.5, assumption = "estimate", min = 0.1, max = 0.9 }
                c = { value = "x", definition = "project choice" }
                """
            )
        )
        self.assertEqual(
            cfg.provenance_counts(), {"sourced": 1, "assumption": 1, "definition": 1}
        )
        self.assertEqual(cfg.parameter("s", "a").retrieved, dt.date(2026, 10, 20))
        self.assertEqual(cfg.parameter("s", "b").minimum, 0.1)

    def test_list_value_with_range(self) -> None:
        cfg = load_config(
            self.write(
                """
                [s]
                profile = { value = [0.1, 0.5, 0.9], assumption = "shape", min = 0.0, max = 1.0 }
                """
            )
        )
        self.assertEqual(cfg.value("s", "profile"), [0.1, 0.5, 0.9])

    def test_iteration_is_sorted(self) -> None:
        cfg = load_config(
            self.write(
                """
                [b]
                z = { value = 1, definition = "d" }
                [a]
                y = { value = 1, definition = "d" }
                x = { value = 1, definition = "d" }
                """
            )
        )
        self.assertEqual([p.qualified_name for p in cfg], ["a.x", "a.y", "b.z"])


class RejectedConfigTests(ConfigTestCase):
    """Fail-safe behaviour: anything doubtful is refused."""

    def test_missing_file(self) -> None:
        with self.assertRaises(ConfigError):
            load_config(Path("/nonexistent/definitely-missing.toml"))

    def test_invalid_toml(self) -> None:
        self.assertRejects("[s\nbroken", "invalid TOML")

    def test_missing_meta(self) -> None:
        self.assertRejects(
            "[s]\na = { value = 1, definition = 'd' }", "missing [meta]", header=""
        )

    def test_wrong_schema_version(self) -> None:
        header = '[meta]\nschema_version = 2\nid = "x"\n'
        self.assertRejects("[s]\na = { value = 1, definition = 'd' }", "schema_version", header)

    def test_missing_id(self) -> None:
        header = "[meta]\nschema_version = 1\n"
        self.assertRejects("[s]\na = { value = 1, definition = 'd' }", "id must be", header)

    def test_unknown_meta_key(self) -> None:
        header = '[meta]\nschema_version = 1\nid = "x"\nextra = 1\n'
        self.assertRejects("[s]\na = { value = 1, definition = 'd' }", "unknown key", header)

    def test_no_parameters(self) -> None:
        self.assertRejects("", "no parameters defined")

    def test_bare_value_without_table(self) -> None:
        self.assertRejects("[s]\na = 5", "must be a table")

    def test_missing_value(self) -> None:
        self.assertRejects("[s]\na = { definition = 'd' }", "missing 'value'")

    def test_no_provenance(self) -> None:
        self.assertRejects("[s]\na = { value = 1 }", "exactly one of")

    def test_two_provenance_keys(self) -> None:
        self.assertRejects(
            "[s]\na = { value = 1, definition = 'd', assumption = 'a' }", "exactly one of"
        )

    def test_empty_rationale(self) -> None:
        self.assertRejects("[s]\na = { value = 1, definition = '  ' }", "non-empty string")

    def test_source_without_retrieved(self) -> None:
        self.assertRejects("[s]\na = { value = 1, source = 'Report' }", "needs 'retrieved'")

    def test_retrieved_must_be_a_date_not_datetime(self) -> None:
        self.assertRejects(
            "[s]\na = { value = 1, source = 'R', retrieved = 2026-10-20T10:00:00 }",
            "needs 'retrieved'",
        )

    def test_retrieved_without_source(self) -> None:
        self.assertRejects(
            "[s]\na = { value = 1, definition = 'd', retrieved = 2026-10-20 }",
            "only allowed with 'source'",
        )

    def test_min_max_only_with_assumption(self) -> None:
        self.assertRejects(
            "[s]\na = { value = 1, definition = 'd', min = 0 }", "only allowed with 'assumption'"
        )

    def test_value_below_min(self) -> None:
        self.assertRejects(
            "[s]\na = { value = 0.0, assumption = 'a', min = 0.1, max = 0.9 }", "below min"
        )

    def test_value_above_max(self) -> None:
        self.assertRejects(
            "[s]\na = { value = 1.0, assumption = 'a', min = 0.1, max = 0.9 }", "above max"
        )

    def test_min_greater_than_max(self) -> None:
        self.assertRejects(
            "[s]\na = { value = 0.5, assumption = 'a', min = 0.9, max = 0.1 }",
            "min is greater than max",
        )

    def test_list_element_out_of_range(self) -> None:
        self.assertRejects(
            "[s]\na = { value = [0.5, 2.0], assumption = 'a', min = 0.0, max = 1.0 }",
            "above max",
        )

    def test_range_on_string_value(self) -> None:
        self.assertRejects(
            "[s]\na = { value = 'x', assumption = 'a', min = 0 }", "need a numeric value"
        )

    def test_non_finite_value(self) -> None:
        self.assertRejects("[s]\na = { value = inf, definition = 'd' }", "finite")

    def test_empty_list(self) -> None:
        self.assertRejects("[s]\na = { value = [], definition = 'd' }", "must not be empty")

    def test_list_with_strings(self) -> None:
        self.assertRejects(
            "[s]\na = { value = ['a'], definition = 'd' }", "only finite numbers"
        )

    def test_unknown_parameter_key(self) -> None:
        self.assertRejects("[s]\na = { value = 1, definition = 'd', colour = 'red' }", "unknown key")

    def test_bad_unit_type(self) -> None:
        self.assertRejects("[s]\na = { value = 1, definition = 'd', unit = 5 }", "'unit' must be")


class AccessorTests(ConfigTestCase):
    """Lookups and typed accessors."""

    def setUp(self) -> None:
        self.cfg = load_config(
            self.write(
                """
                [s]
                n = { value = 3, definition = "d" }
                f = { value = 2.5, definition = "d" }
                t = { value = "text", definition = "d" }
                flag = { value = true, definition = "d" }
                """
            )
        )

    def test_missing_parameter(self) -> None:
        with self.assertRaises(ConfigError):
            self.cfg.value("s", "nope")

    def test_missing_section(self) -> None:
        with self.assertRaises(ConfigError):
            self.cfg.value("nope", "n")

    def test_int_value_rejects_bool_and_float(self) -> None:
        with self.assertRaises(ConfigError):
            self.cfg.int_value("s", "flag")
        with self.assertRaises(ConfigError):
            self.cfg.int_value("s", "f")

    def test_float_value_accepts_int_rejects_bool(self) -> None:
        self.assertEqual(self.cfg.float_value("s", "n"), 3.0)
        with self.assertRaises(ConfigError):
            self.cfg.float_value("s", "flag")

    def test_str_and_date_type_errors(self) -> None:
        self.assertEqual(self.cfg.str_value("s", "t"), "text")
        with self.assertRaises(ConfigError):
            self.cfg.str_value("s", "n")
        with self.assertRaises(ConfigError):
            self.cfg.date_value("s", "t")


if __name__ == "__main__":
    unittest.main()
