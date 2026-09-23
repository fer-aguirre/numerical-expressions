import json

import pytest

from numerical_expressions.cli import main


def run(capsys, *argv):
    with pytest.raises(SystemExit) as exit_info:
        main(list(argv))
    captured = capsys.readouterr()
    return exit_info.value.code, captured.out, captured.err


def test_text_output(capsys):
    code, out, _ = run(capsys, "10", "20", "-o", "percentage_difference", "ratio_difference")
    assert code == 0
    assert "20 is 100% higher than 10" in out
    assert "Note: Readers often misread 'times more'" in out


def test_percent_values_are_detected(capsys):
    code, out, _ = run(capsys, "5%", "7%", "-o", "difference")
    assert code == 0
    assert "7% is 2 percentage points higher than 5%" in out


def test_mixed_percent_values_are_rejected(capsys):
    with pytest.raises(SystemExit):
        main(["5", "7%"])


def test_errors_go_to_stderr_with_exit_code(capsys):
    code, out, err = run(capsys, "0", "5", "-o", "percentage", "difference")
    assert code == 1
    assert "Error: percentage: cannot compare" in err
    assert "Five is five more than zero" in out


def test_negative_values(capsys):
    code, out, _ = run(capsys, "-10", "-5", "-o", "percentage_difference")
    assert code == 0
    assert "-5 is 50% higher than -10" in out


def test_json_output(capsys):
    code, out, _ = run(capsys, "10", "20", "-o", "ratio", "--json", "--lang", "es")
    payload = json.loads(out)
    assert code == 0
    assert payload["options"]["lang"] == "es"
    assert payload["results"][0]["value"] == 2
    assert payload["results"][0]["phrases"][0] == "20 es el doble de 10"


def test_relatable_flag_adds_operation(capsys):
    code, out, _ = run(capsys, "3000000", "9000000", "-o", "difference", "--relatable")
    assert code == 0
    assert "the population of the city of Buenos Aires" in out
    assert "the population of Mexico City" in out


def test_default_operations_skip_ratio_difference(capsys):
    code, out, _ = run(capsys, "1200000", "1550000", "--hedge", "directional")
    assert code == 0
    assert out.count("nearly 30% higher") == 1
    assert "times more" not in out


def test_single_value_compares_with_benchmarks(capsys):
    code, out, _ = run(capsys, "9000000")
    assert code == 0
    assert out.startswith("9 million is about the population of Mexico City")


def test_single_value_rejects_comparisons(capsys):
    with pytest.raises(SystemExit):
        main(["9000000", "-o", "difference"])
