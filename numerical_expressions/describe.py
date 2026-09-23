from __future__ import annotations

from typing import Iterable, List, Optional

from .calculations import COMPUTATION_FUNCTIONS, compute_rate, compute_real_change
from .context import Context
from .phrasing import BUILDERS
from .results import Options, Result
from .warnings import cautions, validate

OPERATIONS = list(BUILDERS)

# These read the two values differently (a total and a part, events and a population,
# two risks), need extra input (benchmarks, a price index), or use phrasing style guides
# warn against ("N times more"), so none of them runs unless asked for.
OPT_IN_OPERATIONS = ("ratio_difference", "share", "relatable", "rate", "risk", "inflation")
DEFAULT_OPERATIONS = [op for op in OPERATIONS if op not in OPT_IN_OPERATIONS]


def _sentence_case(text: str) -> str:
    """Capitalize a phrase that starts with a spelled-out number: "two is..." -> "Two is..."."""
    return text[:1].upper() + text[1:]


def _compute(ctx: Context, operation: str) -> Optional[float]:
    options = ctx.options
    if operation == "rate":
        return compute_rate(ctx.initial, ctx.final, options.per)
    if operation == "inflation":
        return compute_real_change(ctx.initial, ctx.final, options.cpi_then, options.cpi_now)
    compute = COMPUTATION_FUNCTIONS.get(operation)
    return compute(ctx.initial, ctx.final) if compute else None


def describe(
    initial_value: float,
    final_value: float,
    operation: str = "percentage_difference",
    options: Optional[Options] = None,
) -> Result:
    """Describe the change from initial_value to final_value with one operation."""
    if operation not in BUILDERS:
        raise ValueError(f"Invalid operation: {operation}")

    ctx = Context.create(initial_value, final_value, options or Options())
    error = validate(ctx, operation)
    if error:
        return Result(operation, None, error=error)

    value = _compute(ctx, operation)
    phrases = [_sentence_case(ctx.locale.finish(phrase)) for phrase in BUILDERS[operation](ctx, value)]
    return Result(operation, value, phrases, cautions(ctx, operation, value, phrases))


def describe_all(
    initial_value: float,
    final_value: float,
    operations: Optional[Iterable[str]] = None,
    options: Optional[Options] = None,
) -> List[Result]:
    return [
        describe(initial_value, final_value, operation, options)
        for operation in (operations or DEFAULT_OPERATIONS)
    ]
