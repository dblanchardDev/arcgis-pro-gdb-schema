"""
Method for comparing two elements with the same type

Author: Roya Shourouni
"""
def diff(origin_element:any, other_element:any, element_type: str, properties: list) -> list:
    """compares the properties of two GDB elements and add the differences to a list.

    Args:
        origin_element (any): Origin GDB element
        other_element (any): Other GDB element to compare with
        element_type (str): Type of elements
        properties (list): A list of properties to compare between two elements

    Returns:
        list: a list of differences between two GDB elements
    """
    diff_results = []

    for prop in properties:
        if getattr(origin_element, prop) != getattr(other_element, prop):
            diff_results.append(f"{prop} of {origin_element.name} {element_type} in the origin gdb is different than {other_element.name} {element_type} in the other gdb.")

    return diff_results