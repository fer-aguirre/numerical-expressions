import argparse
from num2words import num2words
from fractions import Fraction
from typing import Dict, Callable

MULTIPLIERS = {
    0.1: "one-tenth",
    0.25: "a quarter",
    0.33: "a third",
    0.5: "half",
    0.75: "three-quarters",
    1.5: "one and a half times",
    2: "double",
    3: "triple",
    4: "quadruple",
    5: "quintuple",
    10: "ten times",
}

def safe_divide(numerator: float, denominator: float) -> float:
    """Safely divide two numbers, raising ValueError if denominator is zero."""
    if denominator == 0:
        raise ValueError("Cannot divide by zero")
    return numerator / denominator

def compute_percentage(initial_value: float, final_value: float) -> float:
    return round(safe_divide(final_value, initial_value) * 100, 2)

def compute_percentage_difference(initial_value: float, final_value: float) -> float:
    return round(safe_divide(final_value - initial_value, initial_value) * 100, 2)

def compute_ratio(initial_value: float, final_value: float) -> float:
    return round(safe_divide(final_value, initial_value), 2)

def compute_ratio_difference(initial_value: float, final_value: float) -> float:
    return round(safe_divide(final_value, initial_value) - 1, 2)

COMPUTATION_FUNCTIONS: Dict[str, Callable[[float, float], float]] = {
    "percentage": compute_percentage,
    "percentage_difference": compute_percentage_difference,
    "ratio": compute_ratio,
    "ratio_difference": compute_ratio_difference,
}

def describe_change(initial_value: float, final_value: float, operation: str) -> str:
    if operation not in COMPUTATION_FUNCTIONS:
        raise ValueError(f"Invalid operation: {operation}")
    
    result = COMPUTATION_FUNCTIONS[operation](initial_value, final_value)
    
    if operation == "percentage":
        return f"{final_value} equals {result}% of {initial_value}"
    
    elif operation == "percentage_difference":
        if result > 0:
            return f"{final_value} is {result}% higher than {initial_value}"
        elif result < 0:
            return f"{final_value} is {abs(result)}% lower than {initial_value}"
        return f"{final_value} is equal to {initial_value}"
    
    elif operation == "ratio":
        lines = []
        if multiplier := MULTIPLIERS.get(result):
            lines.append(f"{final_value} is {multiplier} of {initial_value}")
        elif 0 < result < 1:
            fraction_result = Fraction(result).limit_denominator(100)
            lines.append(f"{final_value} represents {fraction_result} of {initial_value}")
        
        lines.append(f"{final_value} is {result} times as much as {initial_value}")
        
        if result > 1 and result.is_integer():
            fold_word = num2words(int(result))
            lines.append(f"{final_value} is a {fold_word}-fold increase from {initial_value}")
        from typing import Dict, Callable
        return "\n".join(lines)
    
    elif operation == "ratio_difference":
        if result > 0:
            return f"{final_value} is {result} times greater than {initial_value}"
        elif result < 0:
            return f"{final_value} is {abs(result)} times less than {initial_value}"
        return f"{final_value} is equal to {initial_value}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Calculate and describe the change between two numerical values.'
    )
    parser.add_argument('initial_value', type=float, help='Initial value for comparison')
    parser.add_argument('final_value', type=float, help='Final value for comparison')
    parser.add_argument(
        '-o', '--operations',
        nargs='+',
        choices=list(COMPUTATION_FUNCTIONS.keys()),
        default=list(COMPUTATION_FUNCTIONS.keys()),
        help='Operations to perform'
    )

    args = parser.parse_args()
    
    try:
        for op in args.operations:
            print(describe_change(args.initial_value, args.final_value, op))
            print()
    except ValueError as e:
        print(f"Error: {e}")
