from __future__ import annotations

from dataclasses import dataclass

from .phrasing.locale import Locale, load_locale
from .phrasing.numbers import NumberFormatter
from .results import Options


@dataclass
class Context:
    """Everything a phrase or warning needs about one comparison."""

    initial: float
    final: float
    options: Options
    locale: Locale
    fmt: NumberFormatter

    @classmethod
    def create(cls, initial: float, final: float, options: Options) -> "Context":
        locale = load_locale(options.lang)
        return cls(initial, final, options, locale, NumberFormatter(locale, options))

    @property
    def initial_text(self) -> str:
        return self.fmt.value(self.initial)

    @property
    def final_text(self) -> str:
        return self.fmt.value(self.final)

    @property
    def subject(self) -> str:
        return self.options.subject or self.locale.get("trend.subject")
