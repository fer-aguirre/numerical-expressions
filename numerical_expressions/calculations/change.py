from __future__ import annotations

import math
from typing import Callable, Dict


def safe_divide(numerator: float, denominator: float) -> float:
    """Safely divide two numbers, raising ValueError if denominator is zero."""
    if denominator == 0:
        raise ValueError("Cannot divide by zero")
    return numerator / denominator


# The compute functions return full precision; rounding happens only when formatting,
# so that decisions (higher/lower, exact multiplier or not) aren't made on rounded values.
def compute_difference(initial_value: float, final_value: float) -> float:
    return final_value - initial_value


def compute_percentage(initial_value: float, final_value: float) -> float:
    return safe_divide(final_value, initial_value) * 100


def compute_percentage_difference(initial_value: float, final_value: float) -> float:
    # Divide by the magnitude so a loss shrinking from -10 to -5 reads as an increase.
    return safe_divide(final_value - initial_value, abs(initial_value)) * 100


def compute_ratio(initial_value: float, final_value: float) -> float:
    return safe_divide(final_value, initial_value)


def compute_ratio_difference(initial_value: float, final_value: float) -> float:
    return safe_divide(final_value, initial_value) - 1


def compute_share(total: float, part: float) -> float:
    return safe_divide(part, total)


COMPUTATION_FUNCTIONS: Dict[str, Callable[[float, float], float]] = {
    "difference": compute_difference,
    "percentage": compute_percentage,
    "percentage_difference": compute_percentage_difference,
    "ratio": compute_ratio,
    "ratio_difference": compute_ratio_difference,
    "trend": compute_percentage_difference,
    "share": compute_share,
    "risk": compute_percentage_difference,
}


def compute_rate(events: float, population: float, per: float = 100_000) -> float:
    """Events per `per` people: 320 murders in 1,937,086 people -> 16.5 per 100,000."""
    return safe_divide(events, population) * per


def adjust_for_inflation(price_then: float, cpi_then: float, cpi_now: float) -> float:
    """What price_then is worth at today's prices: price now / price then = CPI now / CPI then."""
    return price_then * safe_divide(cpi_now, cpi_then)


def compute_real_change(initial_value: float, final_value: float, cpi_then: float, cpi_now: float) -> float:
    """Percent change after adjusting initial_value to today's prices."""
    return compute_percentage_difference(adjust_for_inflation(initial_value, cpi_then, cpi_now), final_value)


def margin_of_error(sample_size: int) -> float:
    """Rough maximum margin of error of a poll, in percentage points: 1/sqrt(N).

    For a simple random sample at 95% confidence; 625 respondents -> 4 points.
    """
    return 100 / math.sqrt(sample_size)
