from __future__ import annotations

import math
from fractions import Fraction
from typing import Optional, Tuple

# How far (relative) a value may be from a friendly phrase ("a third", "one in five")
# and still be described with it, hedged as "about"/"nearly"/"more than".
APPROXIMATION_TOLERANCE = 0.02

# How far a figure may be rounded when hedging: 29.17% -> "nearly 30%".
ROUNDING_TOLERANCE = 0.03

EXACT_TOLERANCE = 1e-9


def is_close(value: float, target: float, rel_tol: float = APPROXIMATION_TOLERANCE) -> bool:
    return math.isclose(value, float(target), rel_tol=rel_tol)


def relation(value: float, target: float) -> str:
    """Where value sits relative to target: "exact", "below" ("nearly") or "above" ("more than")."""
    if is_close(value, target, EXACT_TOLERANCE):
        return "exact"
    return "below" if value < float(target) else "above"


def round_nicely(value: float, rel_tol: float = ROUNDING_TOLERANCE) -> Tuple[float, str]:
    """Round to the coarsest "nice" number within rel_tol, and say which side value is on.

    round_nicely(29.17) -> (30.0, "below"); round_nicely(350_000) -> (350000.0, "exact").
    """
    if value == 0 or not math.isfinite(value):
        return value, "exact"
    magnitude = 10 ** math.floor(math.log10(abs(value)))
    for step in (magnitude, magnitude / 2, magnitude / 10, magnitude / 20, magnitude / 100):
        nice = round(round(value / step) * step, 10)
        if nice != 0 and is_close(value, nice, rel_tol):
            return nice, relation(value, nice)
    return value, "exact"


def closest_fraction(value: float, max_denominator: int = 10) -> Optional[Fraction]:
    """The simple proper fraction close to value (0.66 -> 2/3), or None."""
    if not 0 < value < 1:
        return None
    fraction = Fraction(value).limit_denominator(max_denominator)
    if 0 < fraction < 1 and is_close(value, fraction):
        return fraction
    return None


def closest_one_in(value: float, max_n: int = 1000) -> Optional[int]:
    """n such that value is close to "one in n" (0.083 -> 12), or None."""
    if not 0 < value < 1:
        return None
    n = round(1 / value)
    if 2 <= n <= max_n and is_close(value, 1 / n):
        return n
    return None


def natural_frequency_base(percentages, bases=(100, 1_000, 10_000, 100_000, 1_000_000)) -> int:
    """The smallest "in N" base at which every percentage is at least one person.

    (2, 3) -> 100 ("2 in 100 to 3 in 100"); (0.033, 0.04) -> 10,000.
    """
    positive = [p for p in percentages if p > 0]
    for base in bases:
        if all(p * base / 100 >= 1 for p in positive):
            return base
    return bases[-1]
