"""Load and validate the load-generator configuration.

Every parameter in the configuration file must say where its value comes
from. The loader refuses any parameter that does not, so an unsourced number
cannot enter the simulation unnoticed (project rule: record the source of
every number, fail safe on missing or invalid data).

A parameter is a TOML table with a ``value`` and exactly one provenance key:

``source``
    A citation (title, publisher, URL). Requires ``retrieved``, the date the
    source was read, as a TOML date such as ``2026-10-20``.
``assumption``
    A rationale. The value is the project's own estimate, not a measurement.
    Optional ``min`` and ``max`` give the plausible range.
``definition``
    A rationale. The value is a project choice that defines the simulated
    hotel or the run (for example the random seed). It is not claimed to
    describe any real hotel.

Optional ``unit`` is free text. Any other key is an error.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import logging
import math
import tomllib
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

SCHEMA_VERSION = 1

#: Provenance keys; exactly one must be present in each parameter table.
PROVENANCE_KEYS: tuple[str, ...] = ("source", "assumption", "definition")

_PARAMETER_KEYS = frozenset(
    {"value", "retrieved", "min", "max", "unit", *PROVENANCE_KEYS}
)
_META_KEYS = frozenset({"schema_version", "id", "description"})


class ConfigError(ValueError):
    """Raised when the configuration file is missing, malformed or incomplete."""


def _is_number(item: object) -> bool:
    """Return True for a finite int or float (booleans are not numbers here)."""
    if isinstance(item, bool) or not isinstance(item, (int, float)):
        return False
    return math.isfinite(item)


def _is_plain_date(item: object) -> bool:
    """Return True for a TOML date (not a date-time)."""
    return isinstance(item, dt.date) and not isinstance(item, dt.datetime)


@dataclass(frozen=True)
class Parameter:
    """One validated configuration parameter and its provenance."""

    section: str
    name: str
    value: Any
    provenance: str  # "sourced", "assumption" or "definition"
    note: str  # the citation or the rationale
    retrieved: dt.date | None = None
    minimum: float | None = None
    maximum: float | None = None
    unit: str | None = None

    @property
    def qualified_name(self) -> str:
        """Return ``section.name``."""
        return f"{self.section}.{self.name}"


@dataclass(frozen=True, eq=False)
class LoadgenConfig:
    """A validated configuration plus the identity of the file it came from."""

    path: Path
    sha256: str
    config_id: str
    parameters: Mapping[tuple[str, str], Parameter]

    def parameter(self, section: str, name: str) -> Parameter:
        """Return the parameter, or raise ConfigError if it does not exist."""
        try:
            return self.parameters[(section, name)]
        except KeyError:
            raise ConfigError(
                f"{self.path}: missing parameter [{section}.{name}]"
            ) from None

    def value(self, section: str, name: str) -> Any:
        """Return the raw value of a parameter."""
        return self.parameter(section, name).value

    def int_value(self, section: str, name: str) -> int:
        """Return an integer value; raise ConfigError for any other type."""
        item = self.value(section, name)
        if isinstance(item, bool) or not isinstance(item, int):
            raise ConfigError(f"[{section}.{name}] must be an integer, got {item!r}")
        return item

    def float_value(self, section: str, name: str) -> float:
        """Return a finite number as float; raise ConfigError otherwise."""
        item = self.value(section, name)
        if not _is_number(item):
            raise ConfigError(f"[{section}.{name}] must be a number, got {item!r}")
        return float(item)

    def str_value(self, section: str, name: str) -> str:
        """Return a string value; raise ConfigError for any other type."""
        item = self.value(section, name)
        if not isinstance(item, str):
            raise ConfigError(f"[{section}.{name}] must be a string, got {item!r}")
        return item

    def date_value(self, section: str, name: str) -> dt.date:
        """Return a date value; raise ConfigError for any other type."""
        item = self.value(section, name)
        if not _is_plain_date(item):
            raise ConfigError(f"[{section}.{name}] must be a date, got {item!r}")
        return item

    def __iter__(self) -> Iterator[Parameter]:
        """Iterate over parameters sorted by section and name."""
        for key in sorted(self.parameters):
            yield self.parameters[key]

    def provenance_counts(self) -> dict[str, int]:
        """Count parameters by provenance (sourced, assumption, definition)."""
        counts = {"sourced": 0, "assumption": 0, "definition": 0}
        for param in self.parameters.values():
            counts[param.provenance] += 1
        return counts


def _check_value(where: str, value: object) -> None:
    """Validate that a parameter value is a supported, finite type."""
    if isinstance(value, list):
        if not value:
            raise ConfigError(f"{where}: a list value must not be empty")
        if not all(_is_number(element) for element in value):
            raise ConfigError(f"{where}: list values must contain only finite numbers")
        return
    if isinstance(value, float) and not math.isfinite(value):
        raise ConfigError(f"{where}: value must be finite")
    if not isinstance(value, (bool, int, float, str, dt.date)):
        raise ConfigError(f"{where}: unsupported value type {type(value).__name__}")


def _check_range(where: str, value: object, raw: Mapping[str, Any]) -> None:
    """Validate the optional min/max bounds of an assumption."""
    low, high = raw.get("min"), raw.get("max")
    if low is None and high is None:
        return
    for label, bound in (("min", low), ("max", high)):
        if bound is not None and not _is_number(bound):
            raise ConfigError(f"{where}: {label} must be a finite number")
    if low is not None and high is not None and low > high:
        raise ConfigError(f"{where}: min is greater than max")
    elements = value if isinstance(value, list) else [value]
    if not all(_is_number(element) for element in elements):
        raise ConfigError(f"{where}: min/max need a numeric value")
    for element in elements:
        if low is not None and element < low:
            raise ConfigError(f"{where}: value {element} is below min {low}")
        if high is not None and element > high:
            raise ConfigError(f"{where}: value {element} is above max {high}")


def _parse_parameter(section: str, name: str, raw: object) -> Parameter:
    """Validate one parameter table and return it as a Parameter."""
    where = f"[{section}.{name}]"
    if not isinstance(raw, dict):
        raise ConfigError(f"{where}: must be a table with a value and a provenance key")
    unknown = sorted(set(raw) - _PARAMETER_KEYS)
    if unknown:
        raise ConfigError(f"{where}: unknown key(s) {unknown}")
    if "value" not in raw:
        raise ConfigError(f"{where}: missing 'value'")
    present = [key for key in PROVENANCE_KEYS if key in raw]
    if len(present) != 1:
        found = present if present else "none"
        raise ConfigError(
            f"{where}: exactly one of {list(PROVENANCE_KEYS)} is required, found {found}"
        )
    kind = present[0]
    note = raw[kind]
    if not isinstance(note, str) or not note.strip():
        raise ConfigError(f"{where}: '{kind}' must be a non-empty string")

    retrieved = raw.get("retrieved")
    if kind == "source":
        if not _is_plain_date(retrieved):
            raise ConfigError(
                f"{where}: a sourced value needs 'retrieved' as a date, e.g. 2026-10-20"
            )
    elif retrieved is not None:
        raise ConfigError(f"{where}: 'retrieved' is only allowed with 'source'")

    if kind != "assumption" and ("min" in raw or "max" in raw):
        raise ConfigError(f"{where}: 'min'/'max' are only allowed with 'assumption'")

    unit = raw.get("unit")
    if unit is not None and not isinstance(unit, str):
        raise ConfigError(f"{where}: 'unit' must be a string")

    value = raw["value"]
    _check_value(where, value)
    if kind == "assumption":
        _check_range(where, value, raw)

    return Parameter(
        section=section,
        name=name,
        value=value,
        provenance="sourced" if kind == "source" else kind,
        note=note.strip(),
        retrieved=retrieved if kind == "source" else None,
        minimum=raw.get("min"),
        maximum=raw.get("max"),
        unit=unit,
    )


def _parse_meta(path: Path, meta: object) -> str:
    """Validate the [meta] table and return the configuration id."""
    if not isinstance(meta, dict):
        raise ConfigError(f"{path}: missing [meta] table")
    unknown = sorted(set(meta) - _META_KEYS)
    if unknown:
        raise ConfigError(f"{path}: unknown key(s) in [meta]: {unknown}")
    version = meta.get("schema_version")
    if isinstance(version, bool) or version != SCHEMA_VERSION:
        raise ConfigError(
            f"{path}: [meta] schema_version must be {SCHEMA_VERSION}, got {version!r}"
        )
    config_id = meta.get("id")
    if not isinstance(config_id, str) or not config_id.strip():
        raise ConfigError(f"{path}: [meta] id must be a non-empty string")
    return config_id.strip()


def load_config(path: str | Path) -> LoadgenConfig:
    """Read, validate and return the configuration at ``path``.

    Raises:
        ConfigError: if the file cannot be read, is not valid TOML, or any
            parameter lacks a value or a provenance.
    """
    file_path = Path(path)
    try:
        raw_bytes = file_path.read_bytes()
    except OSError as exc:
        raise ConfigError(f"cannot read configuration {file_path}: {exc}") from exc
    try:
        data = tomllib.loads(raw_bytes.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"{file_path}: invalid TOML: {exc}") from exc

    config_id = _parse_meta(file_path, data.get("meta"))

    parameters: dict[tuple[str, str], Parameter] = {}
    for section, table in data.items():
        if section == "meta":
            continue
        if not isinstance(table, dict) or not table:
            raise ConfigError(f"{file_path}: [{section}] must be a non-empty table")
        for name, raw in table.items():
            parameters[(section, name)] = _parse_parameter(section, name, raw)
    if not parameters:
        raise ConfigError(f"{file_path}: no parameters defined")

    digest = hashlib.sha256(raw_bytes).hexdigest()
    LOGGER.info(
        "loaded %d parameters from %s (sha256 %s)",
        len(parameters),
        file_path,
        digest[:12],
    )
    return LoadgenConfig(
        path=file_path, sha256=digest, config_id=config_id, parameters=parameters
    )
