import pytest

from numerical_expressions import Options, describe


def phrases(initial, final, operation, **options):
    result = describe(initial, final, operation, Options(**options))
    assert result.error is None, result.error
    return result.phrases


def test_result_is_structured():
    result = describe(10, 15, "percentage_difference")
    assert result.operation == "percentage_difference"
    assert result.value == 50
    assert result.phrases == ["15 is 50% higher than 10", "15 is a 50% increase over 10"]
    assert result.warnings == [
        "Rises and falls aren't symmetrical: going back from 15 to 10 would be a 33.33% fall, not 50%."
    ]


def test_invalid_operation_raises():
    with pytest.raises(ValueError):
        describe(1, 2, "nope")


# Earlier bug fixes -------------------------------------------------------------


def test_negative_values_change_direction_correctly():
    assert phrases(-10, -5, "percentage_difference")[0] == "-5 is 50% higher than -10"


@pytest.mark.parametrize("operation", ["percentage_difference", "trend"])
def test_sign_change_is_an_error_with_suggestion(operation):
    result = describe(-10, 10, operation)
    assert result.value is None and result.phrases == []
    assert "10 is 20 more than -10" in result.error


def test_zero_base_suggests_absolute_change():
    assert "five is five more than zero" in describe(0, 5, "percentage").error


def test_tiny_change_is_not_reported_as_equal():
    assert phrases(100, 100.001, "percentage_difference") == ["100.001 is less than 0.01% higher than 100"]


def test_ratio_phrases_are_grammatical():
    assert phrases(10, 20, "ratio") == [
        "20 is double 10",
        "20 is 2 times as much as 10",
        "20 is a two-fold increase from 10",
    ]
    assert phrases(10, 15, "ratio")[0] == "15 is one and a half times 10"
    assert phrases(5, 2, "ratio")[0] == "Two is two-fifths of five"


def test_ratio_difference_never_says_times_less():
    result = describe(20, 10, "ratio_difference")
    assert result.phrases == ["20 is 2 times as much as 10"]
    assert "times less" in result.warnings[0]


# Rewriting numbers for readers ---------------------------------------------------


def test_large_numbers_use_scale_words():
    assert phrases(1_200_000, 1_550_000, "difference") == ["1.55 million is 350,000 more than 1.2 million"]


def test_ap_style_spells_out_small_whole_numbers():
    assert phrases(3, 5, "difference", unit="people") == ["Five people is two people more than three people"]
    assert phrases(3, 5, "difference", style="figures") == ["5 is 2 more than 3"]


def test_share_as_one_in_n():
    assert phrases(16_000_000, 3_200_000, "share") == [
        "One in five (3.2 million out of 16 million)",
        "One-fifth of the total (3.2 million out of 16 million)",
        "20% of the total (3.2 million out of 16 million)",
    ]
    assert phrases(1000, 12, "share")[0] == "About one in 83 (12 out of 1,000)"


def test_share_names_a_word_unit_once():
    assert phrases(16_000_000, 3_200_000, "share", unit="people")[0] == (
        "One in five (3.2 million out of 16 million people)"
    )
    # A currency symbol stays on both numbers.
    assert phrases(16_000_000, 3_200_000, "share", unit="$")[0] == "One in five ($3.2 million out of $16 million)"


def test_share_rejects_part_larger_than_total():
    assert describe(10, 20, "share").error


def test_relatable_comparison():
    result = describe(3_000_000, 3_000_000, "relatable", Options(unit="people"))
    assert result.phrases == [
        "3 million people is about the population of the city of Buenos Aires (3.12 million, INDEC Census 2022)"
    ]
    assert "Check that the benchmark" in result.warnings[0]


def test_relatable_without_match_warns():
    result = describe(10, 20, "relatable")
    assert result.phrases == [] and result.error is None
    assert "No benchmark" in result.warnings[0]


def test_custom_benchmarks(tmp_path):
    path = tmp_path / "benchmarks.json"
    path.write_text('[{"value": 50000, "label": {"en": "a full Wembley Stadium"}, "source": "venue"}]')
    assert phrases(48_000, 90_000, "relatable", benchmarks=str(path)) == [
        "48,000 is about a full Wembley Stadium (50,000, venue)"
    ]
    assert phrases(48_000, 90_000, "relatable", benchmarks=str(path), hedge="directional") == [
        "48,000 is nearly a full Wembley Stadium (50,000, venue)"
    ]


# Choosing the wording --------------------------------------------------------------


def test_units_prefix_and_suffix():
    assert phrases(1_200_000, 1_550_000, "difference", unit="$") == [
        "$1.55 million is $350,000 more than $1.2 million"
    ]
    assert phrases(10, -5, "difference", unit="$") == ["-$5 is $15 less than $10"]
    assert phrases(3400, 3500, "difference", unit="people") == ["3,500 people is 100 people more than 3,400 people"]


@pytest.mark.parametrize(
    "hedge, expected",
    [
        ("off", "1.55 million is 29.17% higher than 1.2 million"),
        ("directional", "1.55 million is nearly 30% higher than 1.2 million"),
        ("roughly", "1.55 million is roughly 30% higher than 1.2 million"),
    ],
)
def test_hedge_modes(hedge, expected):
    assert phrases(1_200_000, 1_550_000, "percentage_difference", hedge=hedge)[0] == expected


def test_hedged_difference_never_says_more_than_twice():
    assert phrases(48_200, 61_500, "difference", hedge="directional") == ["61,500 is about 13,000 more than 48,200"]
    assert phrases(48_200, 35_500, "difference", hedge="directional") == ["35,500 is nearly 13,000 less than 48,200"]


def test_ratio_difference_below_double_uses_percentage():
    result = describe(48_200, 61_500, "ratio_difference", Options(hedge="directional"))
    assert result.phrases[0] == "61,500 is nearly 28% higher than 48,200"
    assert not any("times more" in phrase for phrase in result.phrases)
    assert result.warnings == []


def test_hedge_on_approximate_ratio_phrase():
    assert phrases(100, 33, "ratio", hedge="directional")[0] == "33 is nearly a third of 100"
    assert phrases(100, 34, "ratio")[0] == "34 is about a third of 100"


@pytest.mark.parametrize(
    "final, verb",
    [(102, "edged up"), (110, "rose"), (130, "jumped"), (160, "surged"), (98, "edged down"), (40, "plunged")],
)
def test_trend_verb_matches_size_of_change(final, verb):
    assert phrases(100, final, "trend")[0].startswith(f"The figure {verb} ")


def test_trend_subject():
    assert phrases(100, 110, "trend", subject="Unemployment") == [
        "Unemployment rose 10%, from 100 to 110",
        "Unemployment rose by 10, from 100 to 110",
    ]


# Percentage points -----------------------------------------------------------------


def test_percentage_points_vs_percent_change():
    result = describe(5, 7, "percentage_difference", Options(percent_values=True))
    assert result.phrases == [
        "7% is 40% higher than 5%",
        "7% is a 40% increase over 5%",
        "7% is 2 percentage points higher than 5%",
    ]
    assert "Don't write '2%'" in result.warnings[0]


def test_percentage_points_in_difference_and_trend():
    assert phrases(5, 6, "difference", percent_values=True) == ["6% is 1 percentage point higher than 5%"]
    assert phrases(5, 7, "trend", percent_values=True, subject="Unemployment") == [
        "Unemployment jumped 2 percentage points, from 5% to 7% (a 40% relative change)"
    ]


STADIUMS = """[
  {"value": 81000, "label": {"en": "a full Westfalenstadion"}, "source": "club", "region": "europe"},
  {"value": 78000, "label": {"en": "a full Maracanã"}, "source": "venue", "region": "latin-america"},
  {"value": 83000, "label": {"en": "a full Estadio Azteca"}, "source": "venue", "region": "latin-america"}
]"""


def test_relatable_offers_several_benchmarks_closest_first(tmp_path):
    path = tmp_path / "stadiums.json"
    path.write_text(STADIUMS, encoding="utf-8")
    assert phrases(80_000, 80_000, "relatable", benchmarks=str(path)) == [
        "80,000 is about a full Westfalenstadion (81,000, club)",
        "80,000 is about a full Maracanã (78,000, venue)",
        "80,000 is about a full Estadio Azteca (83,000, venue)",
    ]


def test_relatable_region_filter(tmp_path):
    path = tmp_path / "stadiums.json"
    path.write_text(STADIUMS, encoding="utf-8")
    assert phrases(80_000, 80_000, "relatable", benchmarks=str(path), region="latin-america") == [
        "80,000 is about a full Maracanã (78,000, venue)",
        "80,000 is about a full Estadio Azteca (83,000, venue)",
    ]


def test_relatable_sources_are_translated():
    assert describe(214_000_000, 214_000_000, "relatable", Options(lang="es")).phrases == [
        "214 millones equivale a alrededor de la población de Brasil (214,21 millones, estimación IBGE 2026)"
    ]


def test_unknown_region_lists_available_regions():
    result = describe(5_000_000, 5_000_000, "relatable", Options(region="europe"))
    assert result.phrases == []
    assert result.warnings == [
        "There are no benchmarks for the region 'europe'. Available regions: latin-america."
    ]
