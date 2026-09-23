from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from ..calculations import compute_percentage_difference, margin_of_error
from ..phrasing.benchmarks import load_benchmarks
from ..phrasing.sentences import describe_difference

if TYPE_CHECKING:
    from ..context import Context

# Operations that compare the final value relative to the initial one.
RELATIVE_OPERATIONS = ("percentage", "percentage_difference", "ratio", "ratio_difference", "trend")
# Of those, the ones that stay meaningful for negative values of the same sign.
SIGNED_OPERATIONS = ("percentage_difference", "trend")
# Changes this large (in %) get a note that rises and falls aren't symmetrical.
ASYMMETRY_THRESHOLD = 25


def _warning(ctx: Context, key: str, **kwargs) -> str:
    return ctx.locale.finish(ctx.locale.t(f"warnings.{key}", **kwargs))


def validate(ctx: Context, operation: str) -> Optional[str]:
    """Return why this comparison would be misleading, or None if it is sound."""
    if operation == "share":
        if not 0 <= ctx.final <= ctx.initial or ctx.initial <= 0:
            return _warning(ctx, "invalid_share")
        return None
    if operation == "rate":
        if ctx.final <= 0 or ctx.initial < 0 or ctx.options.per <= 0:
            return _warning(ctx, "invalid_rate")
        return None
    if operation == "risk":
        if not ctx.options.percent_values or not (0 < ctx.initial <= 100 and 0 <= ctx.final <= 100):
            return _warning(ctx, "invalid_risk")
        return None
    if operation == "inflation":
        options = ctx.options
        if not options.cpi_then or not options.cpi_now or options.cpi_then <= 0 or options.cpi_now <= 0:
            return _warning(ctx, "missing_cpi")
        if options.percent_values or ctx.initial <= 0 or ctx.final < 0:
            return _warning(ctx, "invalid_inflation")
        return None
    if operation not in RELATIVE_OPERATIONS:
        return None

    suggestion = ctx.locale.finish(describe_difference(ctx, ctx.final - ctx.initial)[0])
    if ctx.initial == 0:
        return _warning(ctx, "zero_base", operation=operation, suggestion=suggestion)
    if operation in SIGNED_OPERATIONS:
        if (ctx.initial < 0) != (ctx.final < 0) and ctx.final != 0:
            return _warning(ctx, "sign_change", operation=operation, suggestion=suggestion)
    elif ctx.initial < 0 or ctx.final < 0:
        return _warning(ctx, "negative_values", operation=operation, suggestion=suggestion)
    return None


def cautions(ctx: Context, operation: str, value: Optional[float], phrases: List[str]) -> List[str]:
    """Editorial warnings about easy-to-make mistakes when writing up this result."""
    notes = []
    changed = ctx.final != ctx.initial

    if ctx.options.percent_values and operation in SIGNED_OPERATIONS and changed:
        difference = ctx.final - ctx.initial
        notes.append(
            _warning(
                ctx,
                "percentage_points",
                points=ctx.fmt.points(difference, hedge=False),
                relative=ctx.fmt.percent(abs(value), hedge=False),
                wrong=ctx.fmt.percent(abs(difference), hedge=False),
            )
        )

    sample = ctx.options.sample
    if sample and ctx.options.percent_values and operation in ("difference",) + SIGNED_OPERATIONS and changed:
        margin = margin_of_error(sample)
        change = abs(ctx.final - ctx.initial)
        notes.append(
            _warning(
                ctx,
                "margin_within" if change <= margin else "margin_outside",
                sample=ctx.fmt.figures(sample, 0),
                margin=ctx.fmt.points(round(margin, 1), hedge=False),
                change=ctx.fmt.points(change, hedge=False),
            )
        )

    if operation == "percentage_difference" and changed and ctx.initial > 0 and ctx.final > 0:
        if abs(value) >= ASYMMETRY_THRESHOLD:
            reverse = compute_percentage_difference(ctx.final, ctx.initial)
            notes.append(
                _warning(
                    ctx,
                    "asymmetry",
                    final=ctx.final_text,
                    initial=ctx.initial_text,
                    reverse=ctx.fmt.percent(abs(reverse), article=True, hedge=False),
                    reverse_dir=ctx.locale.get("words.fall" if reverse < 0 else "words.rise"),
                    same=ctx.fmt.percent(abs(value), article=True, hedge=False),
                )
            )

    if operation == "rate" and ctx.initial > ctx.final:
        notes.append(_warning(ctx, "rate_order"))

    if operation == "risk" and changed:
        notes.append(_warning(ctx, "risk_relative"))

    if operation == "inflation":
        notes.append(_warning(ctx, "price_index"))

    if operation == "ratio_difference" and changed:
        if value >= 1:
            notes.append(_warning(ctx, "times_more"))
        elif value < 0 and ctx.final != 0:
            notes.append(_warning(ctx, "times_less"))

    if operation == "relatable":
        regions = sorted({b.region for b in load_benchmarks(ctx.options.benchmarks) if b.region})
        if ctx.options.region and ctx.options.region not in regions:
            notes.append(_warning(ctx, "unknown_region", region=ctx.options.region,
                                  regions=", ".join(regions)))
        else:
            notes.append(_warning(ctx, "check_benchmark" if phrases else "no_benchmark"))

    return notes
