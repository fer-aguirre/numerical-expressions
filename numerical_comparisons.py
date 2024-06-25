import argparse
from num2words import num2words
from fractions import Fraction

MULTIPLIERS = {
    0.5: "half",
    0.25: "quarter",
    2: "double",
    3: "triple",
    4: "quadruple",
    5: "quintuple",
    6: "sextuple",
    7: "septuple",
    8: "octuple",
    9: "nonuple",
    10: "decuple",
}

def compute_comparison(initial_value: float, final_value: float, operation: str):
    if operation == "percentage":
        result = final_value / initial_value * 100
    elif operation == "percentage_difference":
        result = (final_value - initial_value) / initial_value * 100
    elif operation == "ratio":
        result = final_value / initial_value
    elif operation == "ratio_difference":
        result = final_value / initial_value - 1
    else:
        raise ValueError(f"Invalid operation: {operation}")
    return round(result, 2)

def describe_change(initial_value: float, final_value: float, operation: str) -> str:
    result = compute_comparison(initial_value, final_value, operation)
    if operation == "percentage":
        print(f"{final_value} equals {result}% of {initial_value}")
    elif operation == "percentage_difference":
        comparison_result = (
            "higher" if result > 0 else "lower" if result < 0 else "equal"
        )
        print(
            f"{final_value} is {abs(result)}% {comparison_result} than {initial_value}"
        )
    elif operation == "ratio":
        if multiplier := MULTIPLIERS.get(result):
            print(f"{final_value} is the {multiplier} of {initial_value}")
        else:
            if result < 1:
                fraction_result = Fraction(result).limit_denominator()
            print(f"{final_value} represents {fraction_result} of {initial_value}")
        print(f"{final_value} is {result} times as many as {initial_value}")
        change_category = (
            "increase" if result > 1 else "decrease" if result < 1 else "equal"
        )
        fold_result = num2words(abs(result)) if result.is_integer() else result
        print(f"{final_value} is a {fold_result}-fold {change_category} of {initial_value}")
    elif operation == "ratio_difference":
        comparison_result = (
            "higher" if result > 0 else "lower" if result < 0 else "equal"
        )
        print(
            f"{final_value} is {abs(result)} times {comparison_result} than {initial_value}"
        )
    else:
        raise ValueError(f"Invalid operation: {operation}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculates and describes the change between two numerical values in various ways. It takes two arguments: an initial value and a final value for comparison.')
    parser.add_argument('initial_value', type=float, help='Initial value for comparison')
    parser.add_argument('final_value', type=float, help='Final value for comparison')

    args = parser.parse_args()

    operations = ["percentage", "percentage_difference", "ratio", "ratio_difference"]
    for operation in operations:
        describe_change(args.initial_value, args.final_value, operation)
