def compute_percentage(initial_value: float, final_value: float) -> str:
    percentage = final_value / initial_value * 100
    return f"{final_value} equals {percentage}% of {initial_value}"


def compute_percentage_difference(initial_value: float, final_value: float) -> str:
    percentage_difference = (final_value / initial_value - 1) * 100
    comparison_result = {
        percentage_difference > 0: "higher",
        percentage_difference < 0: "lower",
    }.get(True, "equal")
    return f"{final_value} is {abs(percentage_difference)}% {comparison_result} than {initial_value}"


def compute_ratio(initial_value: float, final_value: float) -> str:
    ratio = final_value / initial_value
    return f"{final_value} is {ratio} times as many as {initial_value}"


def compare_ratio(initial_number: float, final_value: float) -> str:
    ratio = (final_value - initial_number) / initial_number
    comparison_result = {
        ratio > 0: "higher",
        ratio < 0: "lower",
    }.get(True, "equal")
    return (
        f"{final_value} is {abs(ratio)} times {comparison_result} than {initial_number}"
    )


from num2words import num2words
def describe_ratio_change(initial_value: float, final_value: float) -> None:
    """
    This function calculates the ratio change between two values, checks if it's an integer,
    converts it to words if it is, and then categorizes the change as an increase, decrease, or equal.
    Returns a formatted string describing the ratio change.
    """
    ratio = final_value / initial_value
    def convert_integer_to_words(num: float) -> str:
        """
        This function checks if a number is an integer and if so, returns its name.
        """
        return num2words(num) if num.is_integer() else num
    def categorize_change(num: float) -> str:
        """
        This function categorizes a relation
        """
        if num > 1:
            return "increase"
        elif num < 1:
            return "decrease"
        else:
            return "equal"
    change_category = categorize_change(ratio)
    ratio = convert_integer_to_words(ratio)
    return f"{final_value} is a {ratio}-fold {change_category} of {initial_value}"


def compute_percentage_change(initial_value: float, final_value: float) -> None:
    """
    This function calculates the percentage difference between the initial and final values
    and converts the percentage difference to a word form multiplier.
    """
    def get_multiplier_word(num) -> str:
        """
        This function returns the word form of a multiplier for numbers from 100 to 900.
        """
        num = int(num)
        multipliers = {
            100: "double",
            200: "triple",
            300: "quadruple",
            400: "quintuple",
            500: "sextuple",
            600: "septuple",
            700: "octuple",
            800: "nonuple",
            900: "decuple",
        }
        return multipliers.get(num)
    percentage_difference = (final_value / initial_value - 1) * 100
    multiplier = get_multiplier_word(percentage_difference)
    if multiplier:
        return f"{final_value} is the {multiplier} of {initial_value}"



if __name__ == "__main__":
    initial_value = 10
    final_value = 100
    print(compute_percentage(initial_value, final_value))
    print(compute_percentage_difference(initial_value, final_value))
    print(compute_ratio(initial_value, final_value))
    print(compare_ratio(initial_value, final_value))
    print(describe_ratio_change(initial_value, final_value))
    print(compute_percentage_change(initial_value, final_value))