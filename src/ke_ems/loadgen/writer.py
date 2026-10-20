"""Deterministic, atomic CSV writer for generated series."""

from __future__ import annotations

import hashlib
import logging
import math
import os
import tempfile
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path

LOGGER = logging.getLogger(__name__)


class CsvWriteError(ValueError):
    """Raised when data cannot be written safely."""


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Write ``data`` to ``path`` via a temp file and rename.

    On failure the temp file is removed and any existing ``path`` is untouched.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def render_series_csv(
    timestamps: Sequence[datetime],
    columns: Mapping[str, Sequence[float]],
    decimals: int = 3,
) -> bytes:
    """Render a CSV as bytes: UTF-8, ``\\n`` line endings, fixed decimals.

    The first column is ``timestamp`` (ISO 8601 with offset, seconds precision).

    Raises:
        CsvWriteError: Empty input, bad column names, length mismatch, naive
            timestamps, or any value that is not finite and non-negative.
    """
    if not timestamps:
        raise CsvWriteError("no timestamps")
    if not columns:
        raise CsvWriteError("no columns")
    if not isinstance(decimals, int) or isinstance(decimals, bool) or not 0 <= decimals <= 9:
        raise CsvWriteError(f"decimals must be an integer 0..9, got {decimals!r}")
    for name in columns:
        if (
            not isinstance(name, str)
            or not name
            or name == "timestamp"
            or any(ch in name for ch in ',"\r\n')
        ):
            raise CsvWriteError(f"invalid column name: {name!r}")
    n = len(timestamps)
    for name, values in columns.items():
        if len(values) != n:
            raise CsvWriteError(f"column {name!r} has {len(values)} values, expected {n}")
    if any(ts.tzinfo is None or ts.utcoffset() is None for ts in timestamps):
        raise CsvWriteError("timestamps must be timezone-aware")

    names = list(columns)
    lines = ["timestamp," + ",".join(names)]
    for i, ts in enumerate(timestamps):
        cells = [ts.isoformat(timespec="seconds")]
        for name in names:
            value = columns[name][i]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise CsvWriteError(f"{name!r}[{i}] is not a number: {value!r}")
            if not math.isfinite(value) or value < 0:
                raise CsvWriteError(f"{name!r}[{i}] must be finite and >= 0, got {value!r}")
            cells.append(f"{value + 0.0:.{decimals}f}")  # + 0.0 turns -0.0 into 0.0
        lines.append(",".join(cells))
    return ("\n".join(lines) + "\n").encode("utf-8")


def write_series_csv(
    path: Path,
    timestamps: Sequence[datetime],
    columns: Mapping[str, Sequence[float]],
    decimals: int = 3,
) -> str:
    """Render and atomically write the CSV; return the SHA-256 of the file bytes."""
    data = render_series_csv(timestamps, columns, decimals)
    atomic_write_bytes(path, data)
    digest = hashlib.sha256(data).hexdigest()
    LOGGER.info("wrote %s (%d bytes, sha256 %s)", path, len(data), digest)
    return digest
