from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import List, Optional


@dataclass
class Options:
    """How numbers should be written.

    lang: locale code, e.g. "en", "es", "es-MX", "pt".
    unit: added to amounts, e.g. "$" (prefix) or "people" (suffix).
    unit_position: "auto" puts currency symbols before the number, anything else after.
    hedge: "off" keeps exact figures; "directional" rounds to "nearly 30%" / "more than 30%";
        "roughly" rounds to "roughly 30%".
    style: "ap" spells out whole numbers under 10 (AP Stylebook); "figures" never does.
    percent_values: the inputs are themselves percentages (e.g. rates of 5% and 7%).
    subject: what the numbers measure, used in trend sentences ("Unemployment").
    benchmarks: path to a JSON file of reference values for relatable comparisons.
    region: only compare with benchmarks from this region, e.g. "latin-america".
    per: the population base for rates, e.g. 100,000 for "16.5 per 100,000 residents".
    cpi_then, cpi_now: a price index (e.g. the CPI) for the initial and final dates,
        to adjust the initial value for inflation.
    sample: the number of people surveyed, when the values are poll percentages,
        to check changes against the margin of error.
    """

    lang: str = "en"
    unit: Optional[str] = None
    unit_position: str = "auto"
    hedge: str = "off"
    style: str = "ap"
    percent_values: bool = False
    subject: Optional[str] = None
    benchmarks: Optional[str] = None
    region: Optional[str] = None
    per: float = 100_000
    cpi_then: Optional[float] = None
    cpi_now: Optional[float] = None
    sample: Optional[int] = None


@dataclass
class Result:
    """The outcome of one operation: its value, suggested phrases and editorial warnings.

    When the comparison would be misleading, value is None, phrases is empty and
    error explains why.
    """

    operation: str
    value: Optional[float]
    phrases: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)
