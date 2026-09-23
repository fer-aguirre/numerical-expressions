import pytest

from numerical_expressions import OPERATIONS, Options, describe
from numerical_expressions.phrasing import available_locales, load_locale


def phrases(initial, final, operation, **options):
    result = describe(initial, final, operation, Options(**options))
    assert result.error is None, result.error
    return result.phrases


def test_available_locales():
    assert available_locales() == ["en", "es", "es-MX", "pt"]


def test_unknown_language():
    with pytest.raises(ValueError, match="Unknown language"):
        load_locale("xx")


@pytest.mark.parametrize("lang", ["en", "es", "es-MX", "pt"])
@pytest.mark.parametrize("operation", OPERATIONS)
@pytest.mark.parametrize("values", [(10, 20), (20, 10), (3, 2), (5, 5)])
def test_every_template_renders(lang, operation, values):
    """Catch missing keys or bad placeholders in any locale file."""
    result = describe(*values, operation, Options(lang=lang))
    assert result.error or result.phrases or result.warnings


def test_spanish():
    assert phrases(10, 20, "ratio", lang="es") == ["20 es el doble de 10", "20 equivale a 2 veces 10"]
    assert phrases(1_200_000, 1_550_000, "difference", lang="es", unit="$") == [
        "$1,55 millones es $350.000 más que $1,2 millones"
    ]
    assert phrases(3_000_000, 3_400_000, "difference", lang="es", unit="personas") == [
        "3,4 millones de personas es 400.000 personas más que 3 millones de personas"
    ]


def test_spanish_contractions():
    assert phrases(10, 21, "percentage", lang="es") == ["21 equivale al 210 % de 10"]
    assert phrases(10, 20.3, "ratio", lang="es", hedge="directional")[0] == "20,3 es más del doble de 10"


def test_mexican_spanish_number_format():
    assert phrases(1_200_000, 1_550_000, "percentage_difference", lang="es-MX", hedge="directional") == [
        "1.55 millones es casi 30% mayor que 1.2 millones",
        "1.55 millones supone un aumento de casi el 30% respecto a 1.2 millones",
    ]


def test_spanish_percentage_points():
    result = describe(5, 7, "percentage_difference", Options(lang="es", percent_values=True))
    assert result.phrases[1] == "7 % supone un aumento del 40 % respecto a 5 %"
    assert result.phrases[2] == "7 % supera en 2 puntos porcentuales a 5 %"
    assert "puntos porcentuales" in result.warnings[0]


def test_spanish_share_and_trend():
    assert phrases(16_000_000, 3_200_000, "share", lang="es")[0] == "Uno de cada cinco (3,2 millones de 16 millones)"
    assert phrases(100, 160, "trend", lang="es", subject="El desempleo")[0] == (
        "El desempleo se disparó 60 %, de 100 a 160"
    )


def test_portuguese():
    assert phrases(10, 20.3, "ratio", lang="pt", hedge="directional")[0] == "20,3 é mais do dobro de 10"
    assert phrases(1_000_000, 1_500_000, "difference", lang="pt", unit="pessoas") == [
        "1,5 milhão de pessoas supera 1 milhão de pessoas em 500.000 pessoas"
    ]
    assert phrases(100, 40, "trend", lang="pt")[0] == "O número despencou 60%, de 100 para 40"


def test_portuguese_relatable_contraction():
    assert phrases(9_100_000, 1, "relatable", lang="pt", region="latin-america")[0] == (
        "9,1 milhões equivale a cerca da população da Cidade do México (9,21 milhões, Censo INEGI 2020)"
    )
