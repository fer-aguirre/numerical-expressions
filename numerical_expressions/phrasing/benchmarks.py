from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..calculations import is_close

DEFAULT_BENCHMARKS = Path(__file__).parent / "benchmarks.json"

# How close a value must be to a benchmark to be compared with it.
BENCHMARK_TOLERANCE = 0.10

# Several benchmarks often fit one value; offer a few so editors can pick a local one.
MAX_MATCHES = 3


@dataclass(frozen=True)
class Benchmark:
    """A familiar reference value, e.g. a city's population, labelled per language."""

    value: float
    labels: Tuple[Tuple[str, str], ...]
    sources: Tuple[Tuple[str, str], ...]
    region: str = ""

    def label(self, language: str) -> str:
        return _translate(self.labels, language)

    def source(self, language: str) -> str:
        return _translate(self.sources, language)


def _translate(texts: Tuple[Tuple[str, str], ...], language: str) -> str:
    by_language: Dict[str, str] = dict(texts)
    return by_language.get(language) or by_language.get("en", "")


def _texts(value) -> Tuple[Tuple[str, str], ...]:
    """A text given either as a plain string or as {language: text}."""
    if isinstance(value, dict):
        return tuple(value.items())
    return (("en", value or ""),)


@lru_cache(maxsize=None)
def load_benchmarks(path: Optional[str] = None) -> Tuple[Benchmark, ...]:
    """Load benchmarks from a JSON list of {"value", "label", "source", "region"}.

    "label" and "source" are either plain strings or {language: text}.
    """
    entries = json.loads(Path(path or DEFAULT_BENCHMARKS).read_text(encoding="utf-8"))
    return tuple(
        Benchmark(
            float(entry["value"]),
            _texts(entry["label"]),
            _texts(entry.get("source")),
            entry.get("region", ""),
        )
        for entry in entries
    )


def closest_benchmarks(
    value: float,
    benchmarks: Tuple[Benchmark, ...],
    region: Optional[str] = None,
    limit: int = MAX_MATCHES,
) -> List[Benchmark]:
    """The benchmarks within tolerance of value, closest first."""
    candidates = [
        b
        for b in benchmarks
        if is_close(value, b.value, BENCHMARK_TOLERANCE) and (not region or b.region == region)
    ]
    return sorted(candidates, key=lambda b: abs(value - b.value) / b.value)[:limit]
