"""Unit tests for structure validation functions."""
#pylint: disable=protected-access,redefined-outer-name,missing-function-docstring

from datetime import time
from datetime import datetime

import pytest

from gdbschematools.structures import validation


# Constants for use during validation
LABEL = "unit testing"
STRING = "bonjour & hello 1234"
STRING_ENUM = ["hello world", STRING, "something else"]
STRING_REGEX = "^[a-z0-9& ]*$"
INTEGER = 1234
FLOAT = 1.5
COMPLEX = 123.4j


#region: EXIST BY NAME

#pylint: disable-next=too-few-public-methods
class NamedItem:
    """A stand-in named item for testing.

    Args:
        name (str): Name given to the item.
    """
    name:str = None

    def __init__(self, name:str) -> None:
        self.name = name


@pytest.fixture
def named_list():
    """Fixture with simple list of 4 named items."""
    return [
        NamedItem("Alpha"),
        NamedItem("Bravo"),
        NamedItem("Charlie"),
        NamedItem("Delta"),
    ]


def test_exist_by_name_true(named_list):
    assert validation.item_exists_by_name("Alpha", named_list) is True
    assert validation.item_exists_by_name("Charlie", named_list) is True


def test_exist_by_name_false(named_list):
    assert validation.item_exists_by_name("Xylophone", named_list) is False
    assert validation.item_exists_by_name("Zebra", named_list) is False

#endregion
#region: STRING

def test_string_with_string_valid():
    result = validation.string(STRING, LABEL)
    assert result == STRING


def test_string_with_min_max_len_valid():
    result = validation.string(STRING, LABEL, min_len=len(STRING), max_len=len(STRING))
    assert result == STRING


def test_string_with_min_len_invalid():
    min_len = len(STRING) + 10
    with pytest.raises(ValueError):
        validation.string(STRING, LABEL, min_len=min_len)


def test_string_with_max_len_invalid():
    max_len = len(STRING) - 1
    with pytest.raises(ValueError):
        validation.string(STRING, LABEL, max_len=max_len)


def test_string_with_enum_valid():
    result = validation.string(STRING, LABEL, enum=STRING_ENUM)
    assert result == STRING


def test_string_with_enum_invalid():
    with pytest.raises(ValueError):
        validation.string(STRING.upper(), LABEL, enum=STRING_ENUM)


def test_string_with_regex_valid():
    result = validation.string(STRING, LABEL, regex=STRING_REGEX)
    assert result == STRING


def test_string_with_regex_invalid():
    with pytest.raises(ValueError):
        validation.string(STRING + "**", LABEL, regex=STRING_REGEX)


def test_string_from_number():
    result = validation.string(1234, LABEL, min_len=4, max_len=4, enum=["01234", "1234"], regex="\\d+",
                               allow_numbers=True)
    assert result == "1234"


def test_string_from_number_disallowed():
    with pytest.raises(TypeError):
        validation.string(1234, LABEL, allow_numbers=False)


def test_string_with_invalid_type():
    with pytest.raises(TypeError):
        validation.string([1, 2, 3], LABEL)


def test_string_or_none_with_string():
    result = validation.string_or_none(STRING, LABEL)
    assert result == STRING


def test_string_or_none_with_none():
    result = validation.string_or_none(None, LABEL)
    assert result is None


def test_string_or_none_with_invalid():
    with pytest.raises(ValueError):
        validation.string_or_none(STRING + "**", LABEL, regex=STRING_REGEX)

#endregion
#region: INTEGER

def test_integer_valid():
    result = validation.integer(INTEGER, LABEL)
    assert result == INTEGER


def test_integer_with_string_allowed():
    result = validation.integer(str(INTEGER), LABEL, allow_str=True)
    assert result == INTEGER


def test_integer_with_string_disallowed():
    with pytest.raises(TypeError):
        validation.integer(str(INTEGER), LABEL, allow_str=False)


def test_integer_with_whole_float():
    result = validation.integer(float(INTEGER), LABEL)
    assert result == INTEGER


def test_integer_with_fractional_float():
    with pytest.raises(ValueError):
        validation.integer(FLOAT, LABEL)


def test_integer_or_none_with_int():
    result = validation.integer_or_none(INTEGER, LABEL)
    assert result == INTEGER


def test_integer_or_none_with_none():
    result = validation.integer_or_none(None, LABEL)
    assert result is None


def test_integer_or_none_with_invalid():
    with pytest.raises(ValueError):
        validation.integer_or_none(FLOAT, LABEL)

#endregion
#region: NUMBER

def test_number_int():
    result = validation.number(INTEGER, LABEL)
    assert result == INTEGER


def test_number_float():
    result = validation.number(FLOAT, LABEL)
    assert result == FLOAT


def test_number_complex_allowed():
    result = validation.number(COMPLEX, LABEL, allow_complex=True)
    assert result == COMPLEX


def test_number_complex_disallowed():
    with pytest.raises(TypeError):
        validation.number(COMPLEX, LABEL, allow_complex=False)


def test_number_string_allowed_valid():
    result = validation.number(str(FLOAT), LABEL, allow_complex=True)
    assert result == FLOAT


def test_number_string_allowed_invalid():
    with pytest.raises(ValueError):
        validation.number("abc", LABEL, allow_str=True)


def test_number_string_disallowed():
    with pytest.raises(TypeError):
        validation.number("1.5", LABEL, allow_str=False)

#endregion
#region: DATE

@pytest.mark.parametrize("date_string,date_values", [
    ["2024-01-10T12:30:25", (2024, 1, 10, 12, 30, 25)],
    ["2024-01-10 12:30:25", (2024, 1, 10, 12, 30, 25)],
    ["2024-01-10", (2024, 1, 10)],
    ["2024-01-10 12:30:25.123", (2024, 1, 10, 12, 30, 25, 123000)],
])
def test_date_with_iso_formatted_string(date_string, date_values):
    result = validation.date(date_string, LABEL)
    assert result == datetime(*date_values)


def test_date_with_datetime_object():
    dt = datetime(2024, 1, 10, 13, 30, 25)
    result = validation.date(dt, LABEL)
    assert result == dt


def test_date_with_bad_string():
    with pytest.raises(ValueError):
        validation.date("abcdef", LABEL)


def test_date_with_value_out_of_range():
    with pytest.raises(ValueError):
        validation.date("2024-02-31", LABEL)


def test_date_disallow_time_valid():
    result = validation.date("2024-01-10", LABEL, allow_time=False)
    assert result == datetime(2024, 1, 10)


def test_date_disallow_time_invalid():
    dt = datetime(2024, 1, 10, 12, 30, 25)
    with pytest.raises(ValueError):
        validation.date(dt, LABEL, allow_time=False)


def test_date_allow_timezone():
    validation.date("2024-01-10T12:30:25-05:00", LABEL, allow_tz=True)


def test_date_disallow_timezone():
    with pytest.raises(ValueError):
        validation.date("2024-01-10T12:30:25-05:00", LABEL, allow_tz=False)

#endregion
#region: TIME


@pytest.mark.parametrize("time_string,time_values", [
    ["12:30", (12, 30)],
    ["12:30:25", (12, 30, 25)],
    ["12:30:25.123", (12, 30, 25, 123000)],
])
def test_time_with_string(time_string, time_values):
    result = validation.time(time_string, LABEL)
    assert result == time(*time_values)


def test_time_with_datetime_object():
    tm = time(13, 30, 25)
    result = validation.time(tm, LABEL)
    assert result == tm


def test_time_with_time_out_of_range():
    with pytest.raises(ValueError):
        validation.time("26:30:25", LABEL)


def test_time_with_bad_string():
    with pytest.raises(ValueError):
        validation.time("abcdef", LABEL)


def test_time_allow_timezone():
    validation.time("12:30:25-05:00", LABEL, allow_tz=True)


def test_time_disallow_timezone():
    with pytest.raises(ValueError):
        validation.time("12:30:25-05:00", LABEL, allow_tz=False)

#endregion
#region: BOOLEAN

@pytest.mark.parametrize("value", [True, False])
def test_boolean_no_coerce(value):
    result = validation.boolean(value, LABEL)
    assert result == value

@pytest.mark.parametrize("value", [0, "", None])
def test_boolean_with_coerce_false(value):
    result = validation.boolean(value, LABEL, coerce=True)
    assert result is False

@pytest.mark.parametrize("value", [1, "abc", datetime(2023,12,11)])
def test_boolean_with_coerce_true(value):
    result = validation.boolean(value, LABEL, coerce=True)
    assert result is True

@pytest.mark.parametrize("value", [0, "", None, 1, "abc", datetime(2023,12,11)])
def test_boolean_disallow_coerce(value):
    with pytest.raises(TypeError):
        validation.boolean(value, LABEL, coerce=False)


def test_boolean_or_none_with_boolean():
    result = validation.boolean_or_none(True, LABEL)
    assert result is True


def test_boolean_or_none_with_none():
    result = validation.boolean_or_none(None, LABEL)
    assert result is None


def test_boolean_or_none_with_coerce_false():
    with pytest.raises(TypeError):
        validation.boolean(0, LABEL, coerce=False)


def test_boolean_or_none_with_coerce_true():
    result = validation.boolean(0, LABEL, coerce=True)
    assert result is False

#endregion
#region: BY FIELD TYPE

@pytest.mark.parametrize("value,field_type", [
    ["hello world", "TEXT"],
    [1, "SHORT"],
    [218356, "LONG"],
    [1384832834823842, "BIGINTEGER"],
    [5.24, "FLOAT"],
    [1234.5323, "DOUBLE"],
    [datetime(2023,12,11,12,25), "DATE"],
    [datetime(2023,12,10), "DATEONLY"],
    [time(12,30), "TIMEONLY"],
])
def test_by_field_type_with_valid_and_no_conversion(value, field_type):
    result = validation.by_field_type(value, field_type, LABEL)
    assert result == value


@pytest.mark.parametrize("value,field_type,expected", [
    [1234.5, "TEXT", "1234.5"],
    ["14", "SHORT", 14],
    ["218356", "LONG", 218356],
    ["1384832834823842", "BIGINTEGER", 1384832834823842],
    ["5.24", "FLOAT", 5.24],
    ["1234.5323", "DOUBLE", 1234.5323],
    ["2023-12-11T12:25", "DATE", datetime(2023,12,11,12,25)],
    ["2023-12-10", "DATEONLY", datetime(2023,12,10)],
    ["12:30", "TIMEONLY", time(12,30)],
])
def test_by_field_type_with_valid_and_with_conversion(value, field_type, expected):
    result = validation.by_field_type(value, field_type, LABEL)
    assert result == expected


@pytest.mark.parametrize("value,field_type", [
    [time(12,30), "TEXT"],
    [12j, "SHORT"],
    [datetime(2023,12,11), "LONG"],
    [[1,2,3], "BIGINTEGER"],
    [{"a": 123}, "FLOAT"],
    [time(12,30), "DOUBLE"],
    [1234, "DATE"],
    [54.12, "DATEONLY"],
    [999, "TIMEONLY"],
])
def test_by_field_type_with_invalid_type(value, field_type):
    with pytest.raises(TypeError):
        validation.by_field_type(value, field_type, LABEL)

#endregion