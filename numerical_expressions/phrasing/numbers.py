from __future__ import annotations

import unicodedata
from fractions import Fraction
from typing import Callable

from ..calculations import round_nicely
from ..results import Options
from .locale import Locale

HEDGE_MODES = ("off", "directional", "roughly")
STYLES = ("ap", "figures")
UNIT_POSITIONS = ("auto", "prefix", "suffix")


def unit_is_prefix(unit: str, position: str = "auto") -> bool:
    """Currency symbols ("$", "US$", "R$", "€") go before the number; words go after."""
    if position != "auto":
        return position == "prefix"
    return unicodedata.category(unit[-1]) == "Sc"


class NumberFormatter:
    """Writes numbers the way a reader expects them in a given language and house style."""

    def __init__(self, locale: Locale, options: Options):
        self.locale = locale
        self.options = options
        self.prefix_unit = bool(options.unit) and unit_is_prefix(options.unit, options.unit_position)
        measurements = {unit.lower() for unit in locale.get("number.measurement_units", [])}
        # AP uses figures before units of measure ("5 km", "6 pounds"), even under 10.
        self.measurement_unit = bool(options.unit) and options.unit.lower() in measurements

    def figures(self, value: float, decimals: int = 2) -> str:
        """Digits with the locale's separators and no trailing zeros: 1234.50 -> "1,234.5"."""
        text = f"{value:,.{decimals}f}"
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        if text == "-0":
            text = "0"
        decimal = self.locale.get("number.decimal")
        thousands = self.locale.get("number.thousands")
        return text.replace(",", "\x00").replace(".", decimal).replace("\x00", thousands)

    def _scale(self, magnitude: float):
        for threshold, singular, plural in self.locale.get("number.scales"):
            if magnitude >= threshold:
                scaled = magnitude / threshold
                if self.locale.get("number.scale_singular") == "below_two":
                    use_singular = scaled < 2
                else:
                    use_singular = scaled == 1
                return scaled, singular if use_singular else plural
        return None

    def count(self, value: float, decimals: int = 2, with_unit: bool = True) -> str:
        """An amount for prose: "3.4 million people", "$1.2 million", "five", "3,400"."""
        magnitude = abs(float(value))
        unit = self.options.unit if with_unit else None
        prefix = bool(unit) and self.prefix_unit
        scaled = self._scale(magnitude)
        if scaled:
            number = f"{self.figures(scaled[0])} {scaled[1]}"
        elif (
            self.options.style == "ap"
            and magnitude.is_integer()
            and magnitude < 10
            and value >= 0
            and not prefix
            and not (unit and self.measurement_unit)
        ):
            number = self.locale.words(int(magnitude))
        else:
            number = self.figures(magnitude, decimals)

        if unit and prefix:
            number = unit + number
        elif unit:
            joiner = self.locale.get("number.scale_unit_joiner") if scaled else " "
            number = number + joiner + unit
        return f"-{number}" if value < 0 else number

    def value(self, value: float, with_unit: bool = True) -> str:
        """An input value. Inputs keep their own precision; results are rounded to 2 decimals.

        with_unit=False drops a suffix unit ("3.2 million out of 16 million people"), but keeps
        a prefix one, since "$3.2 million out of 16 million" would be wrong.
        """
        if self.options.percent_values:
            return self.locale.t("number.percent", value=self.figures(value, 6))
        return self.count(value, decimals=6, with_unit=with_unit or self.prefix_unit)

    def small_number(self, number: int) -> str:
        """A whole number that AP style spells out below 10: "one in five", "one in 12"."""
        if self.options.style == "ap" and 0 <= number < 10:
            return self.locale.words(number)
        return self.figures(number)

    def hedge(
        self, value: float, render: Callable[[float], str], hedge: bool = True, allow_above: bool = True
    ) -> str:
        """Render value, rounded to a nice number with a hedge word if hedging is on."""
        if not hedge or self.options.hedge == "off":
            return render(value)
        nice, relation = round_nicely(value)
        if relation == "exact":
            return render(value)
        return self.approximate(render(nice), relation, allow_above)

    def approximate(self, text: str, relation: str, allow_above: bool = True) -> str:
        """Hedge text that is only approximately true: "about a third", "nearly double".

        allow_above=False falls back to "about" where "more than" would clash with the
        sentence, as in "more than 13,000 more than 48,200".
        """
        if relation == "exact":
            return text
        mode = self.options.hedge
        if mode == "roughly":
            return self.locale.t("hedges.roughly", value=text)
        if mode == "directional" and (relation == "below" or allow_above):
            return self.locale.t(f"hedges.{relation}", value=text)
        return self.locale.t("hedges.approximate", value=text)

    def percent(self, value: float, article: bool = False, hedge: bool = True) -> str:
        def render(v: float) -> str:
            if v == 0 and self.options.style == "ap" and self.locale.has("number.percent_zero"):
                text = self.locale.get("number.percent_zero")  # AP: "zero percent", not "0%"
            else:
                text = self.locale.t("number.percent", value=self.figures(v))
            return self.locale.t("number.percent_article", value=text) if article else text

        return self.hedge(value, render, hedge)

    def points(self, value: float, hedge: bool = True) -> str:
        singular, plural = self.locale.get("number.points")

        def render(v: float) -> str:
            return f"{self.figures(v)} {singular if v == 1 else plural}"

        return self.hedge(abs(value), render, hedge)

    def rate(self, value: float, with_unit: bool = True, hedge: bool = True) -> str:
        """A rate with the unit: "16.5 murders", "0.17 murders". One decimal, or two below 1."""

        def render(v: float) -> str:
            number = self.figures(v, 1 if v >= 1 else 2)
            if with_unit and self.options.unit:
                return self.options.unit + number if self.prefix_unit else f"{number} {self.options.unit}"
            return number

        return self.hedge(value, render, hedge)

    def times(self, value: float, hedge: bool = True) -> str:
        return self.hedge(value, self.figures, hedge)

    def amount(self, value: float, hedge: bool = True) -> str:
        """An absolute difference. Never hedged with "more than", since the sentences around
        it already say "more than" or "less than"."""
        return self.hedge(abs(value), self.count, hedge, allow_above=False)

    def fraction(self, fraction: Fraction) -> str:
        """Spell out a proper fraction: 2/5 -> "two-fifths", "dos quintos", "dois quintos"."""
        special = self.locale.get("fractions.special", {}).get(str(fraction))
        if special:
            return special
        singular, plural = self.locale.get(f"fractions.denominators.{fraction.denominator}")
        if fraction.numerator == 1:
            return self.locale.t("fractions.singular", denominator=singular)
        return self.locale.t(
            "fractions.plural", numerator=self.locale.words(fraction.numerator), denominator=plural
        )
