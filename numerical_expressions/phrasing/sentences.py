"""One builder per operation: each takes the comparison and its computed value and
returns the suggested phrases, in the context's language."""

from __future__ import annotations

import bisect
from fractions import Fraction
from typing import TYPE_CHECKING, Callable, Dict, List, Optional

from ..calculations import (
    adjust_for_inflation,
    closest_fraction,
    closest_one_in,
    compute_percentage_difference,
    is_close,
    natural_frequency_base,
    relation,
    round_nicely,
)
from .benchmarks import closest_benchmarks, load_benchmarks

if TYPE_CHECKING:
    from ..context import Context

# Differences smaller than this are shown as "less than 0.01%" rather than "0%".
SMALLEST_PERCENT = 0.01


def _equal(ctx: Context) -> List[str]:
    return [ctx.locale.t("phrases.equal", final=ctx.final_text, initial=ctx.initial_text)]


def _percent_change(ctx: Context, value: float) -> str:
    if abs(value) < SMALLEST_PERCENT / 2:
        return ctx.locale.t("phrases.less_than", value=ctx.fmt.percent(SMALLEST_PERCENT, hedge=False))
    return ctx.fmt.percent(abs(value))


def describe_difference(ctx: Context, value: float) -> List[str]:
    if ctx.final == ctx.initial:
        return _equal(ctx)
    direction = "more" if value > 0 else "less"
    if ctx.options.percent_values:
        key, amount = f"phrases.difference_points_{direction}", ctx.fmt.points(value)
    else:
        key, amount = f"phrases.difference_{direction}", ctx.fmt.amount(value)
    return [ctx.locale.t(key, final=ctx.final_text, amount=amount, initial=ctx.initial_text)]


def describe_percentage(ctx: Context, value: float) -> List[str]:
    return [
        ctx.locale.t(
            "phrases.percentage",
            final=ctx.final_text,
            value=ctx.fmt.percent(value, article=True),
            initial=ctx.initial_text,
        )
    ]


def describe_percentage_difference(ctx: Context, value: float) -> List[str]:
    if ctx.final == ctx.initial:
        return _equal(ctx)
    key = "phrases.percentage_higher" if value > 0 else "phrases.percentage_lower"
    phrases = [
        ctx.locale.t(key, final=ctx.final_text, value=_percent_change(ctx, value), initial=ctx.initial_text)
    ]
    if abs(value) >= SMALLEST_PERCENT / 2:
        # Doig's newsroom phrasing: "a 60% increase over last year's $5 million budget".
        key = "phrases.percentage_increase_over" if value > 0 else "phrases.percentage_decrease_from"
        phrases.append(
            ctx.locale.t(
                key,
                final=ctx.final_text,
                value=ctx.fmt.percent(abs(value), article=True),
                initial=ctx.initial_text,
            )
        )
    if ctx.options.percent_values:
        phrases += describe_difference(ctx, ctx.final - ctx.initial)
    return phrases


def describe_ratio_in_words(ctx: Context, ratio: float, initial_text: str) -> Optional[str]:
    """A friendly phrase such as "about a third of 30", or None if none fits."""
    for key, template in ctx.locale.get("multipliers", {}).items():
        multiplier = Fraction(key)
        if is_close(ratio, multiplier):
            return ctx.fmt.approximate(template.format(initial=initial_text), relation(ratio, multiplier))

    fraction = closest_fraction(ratio)
    if fraction is not None:
        text = ctx.locale.t("fractions.of", fraction=ctx.fmt.fraction(fraction), initial=initial_text)
        return ctx.fmt.approximate(text, relation(ratio, fraction))
    return None


def describe_ratio(ctx: Context, value: float) -> List[str]:
    phrases = []
    if phrase := describe_ratio_in_words(ctx, value, ctx.initial_text):
        phrases.append(ctx.locale.t("phrases.ratio_phrase", final=ctx.final_text, phrase=phrase))
    phrases.append(
        ctx.locale.t(
            "phrases.ratio_times", final=ctx.final_text, value=ctx.fmt.times(value), initial=ctx.initial_text
        )
    )
    if ctx.locale.has("phrases.ratio_fold") and value > 1 and value.is_integer():
        phrases.append(
            ctx.locale.t(
                "phrases.ratio_fold",
                final=ctx.final_text,
                fold=ctx.locale.words(int(value)),
                initial=ctx.initial_text,
            )
        )
    return phrases


def describe_ratio_difference(ctx: Context, value: float) -> List[str]:
    # "N times more/less" is ambiguous (does "2 times more than 10" mean 20 or 30?),
    # so "times more" is paired with "times as much", and "times less" is never used.
    if ctx.final == ctx.initial:
        return _equal(ctx)
    if 0 < value < 1:
        # "0.28 times more" is meaningless to readers; a percentage says it plainly.
        return describe_percentage_difference(ctx, value * 100)
    if value > 0:
        return [
            ctx.locale.t(
                "phrases.ratio_more",
                final=ctx.final_text,
                value=ctx.fmt.times(value),
                initial=ctx.initial_text,
                times=ctx.fmt.times(value + 1),
            )
        ]
    if ctx.final == 0:
        return [
            ctx.locale.t(
                "phrases.percentage_lower",
                final=ctx.final_text,
                value=ctx.fmt.percent(100),
                initial=ctx.initial_text,
            )
        ]
    return [
        ctx.locale.t(
            "phrases.ratio_flip",
            initial=ctx.initial_text,
            value=ctx.fmt.times(ctx.initial / ctx.final),
            final=ctx.final_text,
        )
    ]


def trend_verb(ctx: Context, percent_change: float) -> str:
    """Pick a verb that matches the size of the change, so 2% is never a "surge"."""
    thresholds = ctx.locale.get("trend.thresholds")
    verbs = ctx.locale.get("trend.up" if percent_change > 0 else "trend.down")
    return verbs[bisect.bisect_right(thresholds, abs(percent_change))]


def describe_trend(ctx: Context, value: float) -> List[str]:
    if ctx.final == ctx.initial:
        return [ctx.locale.t("phrases.trend_unchanged", subject=ctx.subject, initial=ctx.initial_text)]
    verb = trend_verb(ctx, value)
    if ctx.options.percent_values:
        return [
            ctx.locale.t(
                "phrases.trend_points",
                subject=ctx.subject,
                verb=verb,
                change=ctx.fmt.points(ctx.final - ctx.initial),
                initial=ctx.initial_text,
                final=ctx.final_text,
                relative=_percent_change(ctx, value),
            )
        ]
    return [
        ctx.locale.t(
            "phrases.trend",
            subject=ctx.subject,
            verb=verb,
            change=_percent_change(ctx, value),
            initial=ctx.initial_text,
            final=ctx.final_text,
        ),
        # Starts with the subject, not a figure, so it can open a sentence (AP style).
        ctx.locale.t(
            "phrases.trend_amount",
            subject=ctx.subject,
            verb=verb,
            amount=ctx.fmt.hedge(abs(ctx.final - ctx.initial), ctx.fmt.count),
            initial=ctx.initial_text,
            final=ctx.final_text,
        ),
    ]


def describe_rate(ctx: Context, value: float) -> List[str]:
    """Events per so many residents: "16.5 murders per 100,000 residents"."""
    per = ctx.fmt.figures(ctx.options.per, 0)
    population = ctx.locale.get("rate.population")
    return [
        ctx.locale.t("phrases.rate", rate=ctx.fmt.rate(value), per=per, population=population),
        ctx.locale.t(
            "phrases.rate_sentence",
            events=ctx.fmt.count(ctx.initial),
            population_count=ctx.fmt.count(ctx.final, with_unit=False),
            rate=ctx.fmt.rate(value, with_unit=False),
            per=per,
            population=population,
        ),
    ]


def _frequency(ctx: Context, percentage: float, base: int) -> str:
    """A percentage as "N in base": 2% of 100 -> "two in 100"."""
    count = percentage * base / 100
    shown = round(count) if count >= 10 or float(round(count, 1)).is_integer() else round(count, 1)
    number = ctx.fmt.small_number(int(shown)) if float(shown).is_integer() else ctx.fmt.figures(shown, 1)
    text = ctx.locale.t("phrases.share_one_in", numerator=number, denominator=ctx.fmt.figures(base, 0))
    return ctx.fmt.approximate(text, relation(count, shown))


def describe_risk(ctx: Context, value: float) -> List[str]:
    """Relative and absolute change in a risk, in natural frequencies (Poynter's advice)."""
    base = natural_frequency_base([ctx.initial, ctx.final])
    phrases = [
        ctx.locale.t(
            "phrases.risk_frequency",
            initial_freq=_frequency(ctx, ctx.initial, base),
            final_freq=_frequency(ctx, ctx.final, base),
        )
    ]
    if ctx.final == ctx.initial:
        return phrases
    if ctx.initial < 10 and 0 < ctx.final < 10:
        # Small risks read best as "one in N": 1 in 3,000 -> 1 in 2,500.
        def one_in(percentage: float) -> str:
            n = 100 / percentage
            nice, rel = round_nicely(n)
            text = ctx.locale.t("phrases.risk_one_in_part", n=ctx.fmt.figures(nice, 0))
            return ctx.fmt.approximate(text, rel)

        phrases.append(ctx.locale.t("phrases.risk_one_in", initial=one_in(ctx.initial), final=one_in(ctx.final)))
    key = "phrases.risk_relative_absolute_up" if value > 0 else "phrases.risk_relative_absolute_down"
    phrases.append(
        ctx.locale.t(
            key,
            relative=ctx.fmt.percent(abs(value), article=True),
            points=ctx.fmt.points(ctx.final - ctx.initial),
        )
    )
    return phrases


def describe_inflation(ctx: Context, value: float) -> List[str]:
    """Nominal vs. real change, after adjusting the initial value to today's prices."""
    options = ctx.options
    adjusted = adjust_for_inflation(ctx.initial, options.cpi_then, options.cpi_now)
    phrases = [
        ctx.locale.t("phrases.inflation_worth", initial=ctx.initial_text, adjusted=ctx.fmt.count(adjusted))
    ]
    real = _percent_change(ctx, value)
    real_dir = ctx.locale.get("words.higher" if value > 0 else "words.lower")
    if ctx.final == ctx.initial:
        phrases.append(
            ctx.locale.t(
                "phrases.inflation_unchanged",
                final=ctx.final_text,
                initial=ctx.initial_text,
                real=real,
                real_dir=real_dir,
            )
        )
        return phrases

    nominal = compute_percentage_difference(ctx.initial, ctx.final)
    conjunction = ctx.locale.get("words.and" if (nominal > 0) == (value > 0) else "words.but")
    phrases.append(
        ctx.locale.t(
            "phrases.inflation_change",
            final=ctx.final_text,
            initial=ctx.initial_text,
            nominal=_percent_change(ctx, nominal),
            nominal_dir=ctx.locale.get("words.higher" if nominal > 0 else "words.lower"),
            conj=conjunction,
            real=real,
            real_dir=real_dir,
        )
    )
    phrases.append(
        ctx.locale.t(
            "phrases.inflation_trend",
            subject=ctx.subject,
            verb=trend_verb(ctx, nominal),
            nominal=_percent_change(ctx, nominal),
            conj=conjunction,
            real_verb=trend_verb(ctx, value),
            real=real,
        )
    )
    return phrases


def describe_share(ctx: Context, value: float) -> List[str]:
    """Describe the second value as a part of the first: "one in five (3.2 million out of 16 million)"."""
    part, whole = ctx.fmt.value(ctx.final, with_unit=False), ctx.initial_text
    phrases = []

    fraction = closest_fraction(value)
    candidate = fraction
    if candidate is None and (n := closest_one_in(value)):
        candidate = Fraction(1, n)
    if candidate is not None:
        text = ctx.locale.t(
            "phrases.share_one_in",
            numerator=ctx.fmt.small_number(candidate.numerator),
            denominator=ctx.fmt.small_number(candidate.denominator),
        )
        phrase = ctx.fmt.approximate(text, relation(value, candidate))
        phrases.append(ctx.locale.t("phrases.share_one_in_sentence", phrase=phrase, part=part, whole=whole))
    if fraction is not None:
        phrase = ctx.fmt.approximate(ctx.fmt.fraction(fraction), relation(value, fraction))
        phrases.append(ctx.locale.t("phrases.share_fraction_sentence", phrase=phrase, part=part, whole=whole))

    phrases.append(
        ctx.locale.t(
            "phrases.share_percent_sentence",
            value=ctx.fmt.percent(value * 100, article=True),
            part=part,
            whole=whole,
        )
    )
    return phrases


def describe_relatable(ctx: Context, value: Optional[float]) -> List[str]:
    """Compare the values (and their difference) with familiar benchmarks."""
    benchmarks = load_benchmarks(ctx.options.benchmarks)
    phrases = []
    seen = set()
    for number in (ctx.initial, ctx.final, abs(ctx.final - ctx.initial)):
        if number in seen or number <= 0:
            continue
        seen.add(number)
        for benchmark in closest_benchmarks(number, benchmarks, ctx.options.region):
            target = ctx.fmt.approximate(benchmark.label(ctx.locale.language), relation(number, benchmark.value))
            phrases.append(
                ctx.locale.t(
                    "phrases.relatable",
                    value=ctx.fmt.count(number),
                    target=target,
                    reference=ctx.fmt.count(benchmark.value, with_unit=False),
                    source=benchmark.source(ctx.locale.language),
                )
            )
    return phrases


BUILDERS: Dict[str, Callable[["Context", Optional[float]], List[str]]] = {
    "difference": describe_difference,
    "percentage": describe_percentage,
    "percentage_difference": describe_percentage_difference,
    "ratio": describe_ratio,
    "ratio_difference": describe_ratio_difference,
    "trend": describe_trend,
    "share": describe_share,
    "relatable": describe_relatable,
    "rate": describe_rate,
    "risk": describe_risk,
    "inflation": describe_inflation,
}
