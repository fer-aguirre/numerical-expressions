import argparse
from num2words import num2words
from fractions import Fraction

MULTIPLIERS = {
    0.5: "half",
    0.25: "a quarter",
    2: "the double",
    3: "the triple",
    4: "the quadruple",
    5: "the quintuple",
    6: "the sextuple",
    7: "the septuple",
    8: "the octuple",
    9: "the nonuple",
    10: "the decuple",
}

def compute_percentage(initial_value: float, final_value: float):
    return round(final_value / initial_value * 100, 2)

def compute_percentage_difference(initial_value: float, final_value: float):
    return round((final_value - initial_value) / initial_value * 100, 2)

def compute_ratio(initial_value: float, final_value: float):
    return round(final_value / initial_value, 2)

def compute_ratio_difference(initial_value: float, final_value: float):
    return round(final_value / initial_value - 1, 2)

COMPUTATION_FUNCTIONS = {
    "percentage": compute_percentage,
    "percentage_difference": compute_percentage_difference,
    "ratio": compute_ratio,
    "ratio_difference": compute_ratio_difference,
}

def describe_change(initial_value: float, final_value: float, operation: str) -> str:
    result = COMPUTATION_FUNCTIONS[operation](initial_value, final_value)
    description = ""
    if operation == "percentage":
        description = f"{final_value} equals {result}% of {initial_value}"
    elif operation == "percentage_difference":
        comparison_result = (
            "higher" if result > 0 else "lower" if result < 0 else "equal"
        )
        description = (
            f"{final_value} is {abs(result)}% {comparison_result} than {initial_value}"
        )
    elif operation == "ratio":
        if multiplier := MULTIPLIERS.get(result):
            description = f"{final_value} is {multiplier} of {initial_value}"
        elif result < 1:
                fraction_result = Fraction(result).limit_denominator()
                description = f"{final_value} represents {fraction_result} of {initial_value}"
        description += f"\n{final_value} is {result} times as many as {initial_value}"
        change_category = (
            "increase" if result > 1 else "decrease" if result < 1 else "equal"
        )
        fold_result = num2words(abs(result)) if result.is_integer() else result
        description += f"\n{final_value} is a {fold_result}-fold {change_category} of {initial_value}"
    elif operation == "ratio_difference":
        comparison_result = (
            "higher" if result > 0 else "lower" if result < 0 else "equal"
        )
        description = (
            f"{final_value} is {abs(result)} times {comparison_result} than {initial_value}"
        )
    else:
        raise ValueError(f"Invalid operation: {operation}")
    return description

def get_descriptions(initial_value: float, final_value: float, operations: list):
    return [describe_change(initial_value, final_value, operation) for operation in operations]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculates and describes the change between two numerical values in various ways. It takes two arguments: an initial value and a final value for comparison.')
    parser.add_argument('initial_value', type=float, help='Initial value for comparison')
    parser.add_argument('final_value', type=float, help='Final value for comparison')

    args = parser.parse_args()

    operations = ["percentage", "percentage_difference", "ratio", "ratio_difference"]
    descriptions = get_descriptions(args.initial_value, args.final_value, operations)
    for description in descriptions:
        print(description)
