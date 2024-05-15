"""
Set of tools to perform validation on geodatabase element inputs.

Author: David Blanchard
"""

import datetime
import re
from numbers import Number
from typing import Union


def item_exists_by_name(name:str, lst:list) -> bool:
    """Check whether a item exists in a list by the item's name attribute.

    Args:
        name (str): Name to search for.
        lst (list): List of sub-elements to search in.

    Returns:
        bool: Whether the item already exists.
    """

    matches = [e for e in lst if e.name == name]
    return len(matches) > 0


def string(value:Union[str, Number], label:str, min_len:int=None, max_len:int=None, enum:list[str]=None,
           regex:str=None, allow_numbers:bool=True) -> str:
    """Validate whether a string meets the requirements.

    Args:
        value (Union[str, Number]): Object to be checked whether it is a string.
        label (str): Text that describes what is being validated. Will be used in exception messages.
        min_len (int, optional): Minimum length of the string. Defaults to None.
        max_len (int, optional): Maximum length of the string. Defaults to None.
        enum (list[str], optional): List of valid values. Defaults to None.
        regex (str, optional): Regular expression which validates the string's content. Defaults to None.
        allow_numbers (bool, optional): Whether numeric formats that can be converted to strings are allowed.

    Raises:
        TypeError: Value isn't a string.
        ValueError: Value did not meet one of the requirements.

    Returns:
        str: The value converted to a string if needed.
    """

    converted = None

    # Check type
    if isinstance(value, str):
        converted = value
    elif allow_numbers and isinstance(value, (int, float)):
        converted = str(value)
    else:
        raise TypeError(f"Value for {label} must be a string.")

    # Check requirements
    if min_len is not None and len(converted) < min_len:
        raise ValueError(f"Value for {label} must contain no less than {min_len} characters.")

    if max_len is not None and len(converted) > max_len:
        raise ValueError(f"Value for {label} must contain no more than {max_len} characters.")

    if enum is not None and converted not in enum:
        raise ValueError(f"Value for {label} must be one of {enum}.")

    if regex is not None and not re.search(regex, converted):
        raise ValueError(f"Value for {label} contains invalid characters or is otherwise invalid.")

    return converted


def string_or_none(value:Union[str, None], label:str, min_len:int=None, max_len:int=None, enum:list[str]=None,
                   regex:str=None, allow_numbers:bool=True) -> Union[str, None]:
    """Validate whether value is string or None. If a string check requirements.

    Args:
        value (Union[str, None]): Object to be checked whether it is a string.
        label (str): Text that describes what is being validated. Will be used in exception messages.
        min_len (int, optional): Minimum length of the string. Defaults to None.
        max_len (int, optional): Maximum length of the string. Defaults to None.
        enum (list[str], optional): List of valid values. Defaults to None.
        regex (str, optional): Regular expression which validates the string's content. Defaults to None.
        allow_numbers (bool, optional): Whether numeric formats that can be converted to strings are allowed.

    Raises:
        TypeError: Value is not None and isn't a string.
        ValueError: Value did not meet one of the requirements.

    Returns:
        Union[str, None]: The value converted to a string if needed.
    """

    if value is not None:
        return string(value, label, min_len, max_len, enum, regex, allow_numbers)

    return value


def integer(value:Union[Number, str], label:str, allow_str:bool=True) -> int:
    """Ensure the value is either an integer, or a float/complex that is a whole number.

    Args:
        value (Union[Number, str]): Number value to validate.
        label (str): Text that describes what is being validated. Will be used in exception messages.
        allow_str (bool, True): Allow text values that can be converted to a number.

    Raises:
        TypeError: Value is not an int, float, or string (if allowed).
        ValueError: Value will loose precision after conversion or string is not an integer.

    Returns:
        int: The value converted to an integer if needed.
    """

    converted = None

    if isinstance(value, int):
        converted = value
    elif isinstance(value, float):
        if not value % 1 == 0:
            raise ValueError(f"Value for {label} will loose precision when converted to an integer.")
        converted = int(value)
    elif isinstance(value, complex):
        raise TypeError(f"Value for {label} cannot be of type complex as it cannot be converted to an integer.")
    elif allow_str and isinstance(value, str):
        try:
            converted = int(value)
        except ValueError as ex:
            raise ValueError(f"Value for {label} is not a valid integer.") from ex
    else:
        raise TypeError(f"Value for {label} must be a non-complex number.")

    return converted


def integer_or_none(value:Union[Number, str, None], label:str, allow_str:bool=True) -> Union[int, None]:
    """Ensure the value is either an integer, or a float/complex that is a whole number.

    Args:
        value (Union[Number, str, None]): Number value to validate.
        label (str): Text that describes what is being validated. Will be used in exception messages.
        allow_str (bool, True): Allow text values that can be converted to a number.

    Raises:
        TypeError: Value is not an int, float, or string (if allowed).
        ValueError: Value will loose precision after conversion or string is not an integer.

    Returns:
        Union[int, None]: The value converted to an integer if needed.
    """

    if value is None:
        return None

    return integer(value, label, allow_str)


def number(value:Union[Number, str], label:str, allow_complex:bool=False, allow_str:bool=True) -> Number:
    """Ensure the value is a number type.

    Args:
        value (Number): Value to validate.
        label (str): Text that describes what is being validated. Will be used in exception messages.
        allow_complex (bool, optional): Whether the complex number type is allowed. Defaults to False.
        allow_str (bool, True): Allow text values that can be converted to a number (will convert to float).

    Raises:
        TypeError: Value is not an int, float, complex (if allowed), or string (if allowed).
        ValueError: String cannot be converted to a float.

    Returns:
        Number: The value converted to a float if needed.
    """

    converted = None

    if allow_complex and isinstance(value, complex):
        converted = value
    elif allow_str and isinstance(value, str):
        try:
            converted = float(value)
        except ValueError as ex:
            raise ValueError(f"Value for {label} is not a valid number.") from ex
    elif isinstance(value, (int, float)):
        converted = value
    else:
        msg_types = "int, float, or complex" if allow_complex else "int, or float"
        raise TypeError(f"Value for {label} must be of type {msg_types}.")

    return converted


def date(value:Union[datetime.date, str], label:str, allow_time:bool=True, allow_tz:bool=False
         ) -> datetime.date:
    """Ensure the value is either a date or a string containing an ISO formatted date.

    Args:
        value (Union[datetime.date, str]): Value to be checked.
        label (str): Text that describes what is being validated. Will be used in exceptions messages.
        allow_time (bool, optional): Whether the date object is allowed to have a time set. When False, expects time to
            be 00:00:00 if included. Defaults to True.
        allow_tz (bool, optional): Whether the date object is allowed to have a timezone set. Defaults to False.

    Raises:
        TypeError: Value is not a datetime date object nor a string.
        ValueError: String cannot be converted to a date or does not meet requirements.

    Returns:
        datetime.date: The value converted to a date object if needed.
    """

    converted = None

    # Check type and convert
    if isinstance(value, datetime.date):
        converted = value
    elif isinstance(value, str):
        try:
            converted = datetime.datetime.fromisoformat(value)
        except ValueError as ex:
            raise ValueError(f"Value for {label} is invalid >> {ex.args[0]}.") from ex

    else:
        raise TypeError(f"Value for {label} must be of type datetime.date or string.")

    # Check requirements
    if not allow_time and (converted.hour != 0 or converted.minute != 0 or converted.second != 0 or
                           converted.microsecond != 0):
        raise ValueError(f"Value for {label} will loose its time component when converted to date only.")

    if not allow_tz and converted.tzinfo is not None:
        raise ValueError(f"Value for {label} has a timezone when this is not allowed.")

    return converted


def time(value:Union[datetime.time, str], label:str, allow_tz:bool=False) -> datetime.time:
    """Ensure the value is either a time or a string containing an ISO formatted time.

    Args:
        value (Union[datetime.time, str]): Value to be checked.
        label (str): Text that describes what is being validated. Will be used in exceptions messages.
        allow_tz (bool, optional): Whether the time object is allowed to have a timezone set. Defaults to False.

    Raises:
        TypeError: Value is not a datetime time object nor a string.
        ValueError: String cannot be converted to a time or does not meet requirements.

    Returns:
        datetime.time: The value converted to a time object if needed.
    """

    converted = None

    # Check type
    if isinstance(value, datetime.time):
        converted = value
    elif isinstance(value, str):
        try:
            if value.startswith("1899-12-30"):
                converted = datetime.time.fromisoformat(value[11:])
            else:
                converted = datetime.time.fromisoformat(value)
        except ValueError as ex:
            details = ex.args[0].split(":")[0]
            raise ValueError(f"Value for {label} is invalid: {details}") from ex

    else:
        raise TypeError(f"Value for {label} must be of type datetime.time or string.")

    # Check requirements
    if not allow_tz and converted.tzinfo is not None:
        raise ValueError(f"Value for {label} has a timezone when this is not allowed.")

    return converted


def boolean(value:any, label:str, coerce:bool=False) -> bool:
    """Checks whether a value is boolean and optionally coerce into a boolean.

    Args:
        value (any): Value to be checked.
        label (str): Text that describes what is being validated. Will be used in exceptions messages.
        coerce (bool, optional): Whether to coerce non-boolean values into a boolean. Defaults to False.

    Raises:
        TypeError: Value is not a boolean and will not be coerced.

    Returns:
        bool: The resulting boolean.
    """

    if not coerce and not isinstance(value, bool):
        raise TypeError(f"Value for {label} must be a boolean.")

    return bool(value)


def boolean_or_none(value:any, label:str, coerce:bool=False) -> Union[bool, None]:
    """Checks whether a value is boolean or None and optionally coerce not None values into a boolean.

    Args:
        value (any): Value to be checked.
        label (str): Text that describes what is being validated. Will be used in exceptions messages.
        coerce (bool, optional): Whether to coerce non-boolean values into a boolean. Defaults to False.

    Raises:
        TypeError: Value is not a boolean nor None and will not be coerced.

    Returns:
        Union[bool, None]: The resulting boolean or None if value was None.
    """
    if value is None:
        return None

    return boolean(value, label, coerce)


def by_field_type(value:any, field_type:str, label:str) -> any:
    """Format and validate a value to work with a specific ArcGIS field type.

    Args:
        value (any): Value to validate and format.
        field_type (str): The ArcGIS field type.
        label (str): Text that describes what is being validated. Will be used in exceptions messages.

    Raises:
        TypeError: Value is not of the correct type and cannot be converted.
        ValueError: Value is invalid or does not meet requirements.

    Returns:
        any: The value converted if needed.
    """

    if field_type == "TEXT":
        return string(value, label)
    if field_type in ["SHORT", "LONG", "BIGINTEGER"]:
        return integer(value, label)
    if field_type in ["FLOAT", "DOUBLE"]:
        return number(value, label)
    if field_type == "DATE":
        return date(value, label)
    if field_type == "DATEONLY":
        return date(value, label, allow_time=False)
    if field_type == "TIMEONLY":
        return time(value, label)

    raise ValueError(f"Field type {field_type} is not handled by the format_for_field_type function.")


def is_structure_instance(obj:object, class_name:str):
    """Check by name and module whether the object is an instance of the gdbschematools.structures module and whether its name matches the expected one.

    Args:
        obj (object): Instance to validate.
        class_name (str): Name of the class expected. Can be inherited.

    Returns:
        bool: Whether instance matches.
    """ #pylint: disable=line-too-long
    cls = obj.__class__

    # Check that it is contained in same package
    package_leader = str(__name__).rsplit(".", 1)[0]
    if not cls.__module__.startswith(package_leader):
        return False

    # Class name is an immediate match
    if cls.__name__ == class_name:
        return True

    # Search inheritance
    return _check_inheritance(cls.__bases__, class_name)


def _check_inheritance(bases:tuple[object], class_name:str) -> bool:
    for bs in bases:
        if bs.__name__ == "object":
            return False

        if bs.__name__ == class_name:
            return True

        return _check_inheritance(bs.__bases__, class_name)