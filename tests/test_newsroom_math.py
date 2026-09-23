"""Rates, inflation, margins of error, risk and AP details.

Examples come from Steve Doig's Newsroom Math Crib Sheet and Poynter's Numeracy Primer
wherever possible, so the results can be checked against the originals.
"""

import pytest

from numerical_expressions import Options, describe
from numerical_expressions.calculations import (
    adjust_for_inflation,
    compute_rate,
    margin_of_error,
    natural_frequency_base,
)
from numerical_expressions.cli import main


def phrases(initial, final, operation, **options):
    result = describe(initial, final, operation, Options(**options))
    assert result.error is None, result.error
    return result.phrases


# Doig's worked examples ---------------------------------------------------------------


def test_doig_murder_rate():
    assert round(compute_rate(320, 1_937_086), 1) == 16.5


def test_doig_inflation_gas_price():
    assert round(adjust_for_inflation(0.30, 30.8, 213.2), 2) == 2.08


def test_doig_margin_of_error():
    assert margin_of_error(625) == 4


def test_doig_percent_change_wording():
    assert phrases(5, 8, "percentage_difference")[1] == "Eight is a 60% increase over five"
    assert phrases(8, 5, "percentage_difference")[1] == "Five is a 37.5% decrease from eight"


def test_rises_and_falls_are_not_symmetrical():
    assert describe(5, 8, "percentage_difference").warnings == [
        "Rises and falls aren't symmetrical: going back from eight to five would be a 37.5% fall, not 60%."
    ]
    # Small changes are close to symmetrical, so there's no note.
    assert describe(100, 110, "percentage_difference").warnings == []


# Rates ---------------------------------------------------------------------------------


def test_rate_phrases():
    assert phrases(320, 1_937_086, "rate", unit="murders") == [
        "16.5 murders per 100,000 residents",
        "320 murders in a population of 1.94 million is a rate of 16.5 per 100,000 residents",
    ]


def test_rate_per_other_base_and_language():
    assert phrases(320, 1_937_086, "rate", per=1000)[0] == "0.17 per 1,000 residents"
    assert phrases(320, 1_937_086, "rate", lang="es", unit="homicidios")[0] == (
        "16,5 homicidios por cada 100.000 habitantes"
    )


def test_rate_rejects_zero_population():
    assert describe(320, 0, "rate").error


# Risk (Poynter) -------------------------------------------------------------------------


def test_natural_frequency_base():
    assert natural_frequency_base([2, 3]) == 100
    assert natural_frequency_base([0.0333, 0.04]) == 10_000


def test_risk_relative_and_absolute():
    result = describe(2, 3, "risk", Options(percent_values=True))
    assert result.phrases == [
        "The risk went from two in 100 to three in 100",
        "That is from one in 50 to about one in 33",
        "That is a 50% increase in relative risk, or 1 percentage point in absolute risk",
    ]
    assert "Report the absolute risk too" in result.warnings[0]


def test_poynter_lightning_example():
    # Poynter: a 20% increase on a one-in-3,000 risk is roughly one in 2,500.
    assert phrases(100 / 3000, 100 / 2500, "risk", percent_values=True)[1] == (
        "That is from one in 3,000 to one in 2,500"
    )


def test_risk_needs_percentages():
    assert describe(2, 3, "risk").error


# Inflation ------------------------------------------------------------------------------


def test_inflation_nominal_rise_real_fall():
    result = describe(5_000_000, 9_000_000, "inflation", Options(cpi_then=100, cpi_now=211, subject="The budget"))
    assert result.phrases == [
        "5 million then is equivalent to 10.55 million at today's prices",
        "9 million is 80% higher than 5 million in nominal terms, but 14.69% lower after adjusting for inflation",
        "The budget surged 80% in nominal terms, but fell 14.69% after adjusting for inflation",
    ]
    assert "same price index" in result.warnings[0]


def test_inflation_real_rise_uses_and():
    assert phrases(5_000_000, 12_000_000, "inflation", cpi_then=100, cpi_now=211, lang="es")[1] == (
        "12 millones es 140 % mayor que 5 millones en términos nominales, "
        "y 13,74 % mayor en términos reales (descontada la inflación)"
    )


def test_inflation_needs_both_indexes():
    assert describe(5, 9, "inflation", Options(cpi_then=100)).error


# Margin of error (Doig) -------------------------------------------------------------------


def test_change_within_margin_of_error():
    result = describe(42, 45, "difference", Options(percent_values=True, sample=625))
    assert result.warnings == [
        "With a sample of 625 people, the margin of error is about ±4 percentage points. "
        "This change of 3 percentage points is within it, so it may not be a real change."
    ]


def test_change_outside_margin_of_error():
    result = describe(42, 51, "difference", Options(percent_values=True, sample=625))
    assert "is larger than that" in result.warnings[0]


def test_margin_of_error_ignored_without_percentages():
    assert describe(42, 45, "difference", Options(sample=625)).warnings == []


# AP style -----------------------------------------------------------------------------


def test_ap_zero_percent():
    assert phrases(10, 0, "percentage") == ["Zero equals zero percent of 10"]
    assert phrases(10, 0, "percentage", style="figures") == ["0 equals 0% of 10"]


def test_ap_figures_for_measurements():
    assert phrases(3, 7, "difference", unit="km") == ["7 km is 4 km more than 3 km"]
    assert phrases(3, 7, "difference", unit="toneladas", lang="es") == [
        "7 toneladas es 4 toneladas más que 3 toneladas"
    ]
    assert phrases(3, 7, "difference", unit="people") == ["Seven people is four people more than three people"]


def test_trend_sentence_can_open_a_paragraph():
    assert phrases(48_200, 61_500, "trend", subject="Homicides")[1] == (
        "Homicides jumped by 13,300, from 48,200 to 61,500"
    )


# Command line ---------------------------------------------------------------------------


def run(capsys, *argv):
    with pytest.raises(SystemExit) as exit_info:
        main(list(argv))
    captured = capsys.readouterr()
    return exit_info.value.code, captured.out, captured.err


def test_cli_inflation_runs_with_price_indexes(capsys):
    code, out, _ = run(capsys, "5000000", "9000000", "--cpi-then", "100", "--cpi-now", "211", "-o", "difference")
    assert code == 0
    assert "14.69% lower after adjusting for inflation" in out


def test_cli_rejects_one_price_index(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["5", "9", "--cpi-then", "100"])
    assert exit_info.value.code == 2


def test_cli_sample_needs_percentages(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["42", "45", "--sample", "625"])
    assert exit_info.value.code == 2


def test_cli_rate_per(capsys):
    code, out, _ = run(capsys, "320", "1937086", "-o", "rate", "--per", "1000")
    assert "0.17 per 1,000 residents" in out


def test_rate_warns_when_values_look_swapped():
    result = describe(1200, 950, "rate")
    assert "Check the order" in result.warnings[0]
    assert describe(320, 1_937_086, "rate").warnings == []
