from fractions import Fraction

import pytest

from numerical_expressions.calculations import (
    closest_fraction,
    closest_one_in,
    compute_percentage_difference,
    round_nicely,
    safe_divide,
)


def test_percentage_difference_uses_magnitude_of_negative_base():
    assert compute_percentage_difference(-10, -5) == 50


def test_safe_divide_rejects_zero():
    with pytest.raises(ValueError):
        safe_divide(1, 0)


@pytest.mark.parametrize(
    "value, expected",
    [(29.17, (30, "below")), (40.4, (40, "above")), (350_000, (350_000, "exact")), (1.29, (1.3, "below"))],
)
def test_round_nicely(value, expected):
    assert round_nicely(value) == expected


def test_closest_fraction():
    assert closest_fraction(2 / 3) == Fraction(2, 3)
    assert closest_fraction(0.46) is None
    assert closest_fraction(1.5) is None


def test_closest_one_in():
    assert closest_one_in(12 / 1000) == 83
    assert closest_one_in(0.5) == 2
    assert closest_one_in(0.37) is None
