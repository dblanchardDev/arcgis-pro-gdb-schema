def string_to_set(input_string):
    # If the string is None or empty/whitespace, return an empty set
    if not input_string or not input_string.strip():
        return set()

    # Split by comma, strip whitespace, and filter out any empty strings
    return {item.strip() for item in input_string.split(",") if item.strip()}


def compare_comma_strings(str1, str2):
    # Convert both inputs to clean sets and compare them
    return string_to_set(str1) == string_to_set(str2)
