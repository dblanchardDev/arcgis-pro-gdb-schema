"""Unit tests for Geodatabase Domain Structure classes."""
#pylint: disable=protected-access,redefined-outer-name,missing-function-docstring

import pytest

from gdbschematools.structures import CodedDomain, Domain, RangeDomain


# Valid field types for domains
VALID_FIELD_TYPES = [
    "SHORT",
    "LONG",
    "BIGINTEGER",
    "FLOAT",
    "DOUBLE",
    "TEXT",
    "DATE",
    "DATEONLY",
    "TIMEONLY",
]


# Valid split policies for domains
VALID_SPLIT_POLICIES = [
    "DEFAULT",
    "DUPLICATE",
    "GEOMETRY_RATIO",
]


# Valid merge policies for domains
VALID_MERGE_POLICIES = [
    "DEFAULT",
    "SUM_VALUES",
    "AREA_WEIGHTED",
]


# Constants for testing
NAME = "My Domain"
DESCRIPTION = "This is a description of my domain."
FIELD_TYPE = "SHORT"
SPLIT_POLICY = "DUPLICATE"
MERGE_POLICY = "DEFAULT"
MIN_VALUE = 0
MAX_VALUE = 10
CODES = [(1, "One", "Count of 1."), (2, "Two", "Count of 2."), (3, "Three", "Count of 3.")]
SCHEMA = "MySchema"


@pytest.fixture
def coded_domain():
    """Coded Value domain instance created using default value constants."""
    return CodedDomain(NAME, DESCRIPTION, FIELD_TYPE, SPLIT_POLICY, MERGE_POLICY, SCHEMA)


@pytest.mark.parametrize("field_type", VALID_FIELD_TYPES)
def test_field_types_valid(field_type):
    domain = Domain(NAME, DESCRIPTION, field_type, SPLIT_POLICY, MERGE_POLICY)
    assert domain.field_type == field_type


@pytest.mark.parametrize("field_type", ["BLOB", "SHAPE", "OBJECTID", "NONSENSE"])
def test_field_types_invalid(field_type):

    with pytest.raises(ValueError):
        Domain(NAME, DESCRIPTION, field_type, SPLIT_POLICY, MERGE_POLICY)


@pytest.mark.parametrize("split_policy", VALID_SPLIT_POLICIES)
def test_split_policies_valid(split_policy):
    domain = Domain(NAME, DESCRIPTION, FIELD_TYPE, split_policy, MERGE_POLICY)
    assert domain.split_policy == split_policy


def test_split_policies_invalid():
    split_policy = "NONSENSE"

    with pytest.raises(ValueError):
        Domain(NAME, DESCRIPTION, FIELD_TYPE, split_policy, MERGE_POLICY)


@pytest.mark.parametrize("merge_policy", VALID_MERGE_POLICIES)
def test_merge_policies_valid(merge_policy):
    domain = Domain(NAME, DESCRIPTION, FIELD_TYPE, SPLIT_POLICY, merge_policy)
    assert domain.merge_policy == merge_policy


def test_merge_policies_invalid():
    merge_policy = "NONSENSE"
    with pytest.raises(ValueError):
        Domain(NAME, DESCRIPTION, FIELD_TYPE, SPLIT_POLICY, merge_policy)


def test_range_initialization():
    domain = RangeDomain(NAME, DESCRIPTION, FIELD_TYPE, SPLIT_POLICY, MERGE_POLICY, [MIN_VALUE, MAX_VALUE], SCHEMA)

    assert domain.name == NAME
    assert domain.description == DESCRIPTION
    assert domain.field_type == FIELD_TYPE
    assert domain.split_policy == SPLIT_POLICY
    assert domain.merge_policy == MERGE_POLICY
    assert domain.minimum == MIN_VALUE
    assert domain.maximum == MAX_VALUE
    assert domain.schema == SCHEMA


def test_range_value_range_requirement():
    with pytest.raises(ValueError):
        RangeDomain(NAME, DESCRIPTION, FIELD_TYPE, SPLIT_POLICY, MERGE_POLICY, None)


def test_range_min_max_swapped():
    with pytest.raises(ValueError):
        RangeDomain(NAME, DESCRIPTION, FIELD_TYPE, SPLIT_POLICY, MERGE_POLICY, [MAX_VALUE, MIN_VALUE])


def test_coded_initialization(coded_domain):
    assert coded_domain.name == NAME
    assert coded_domain.description == DESCRIPTION
    assert coded_domain.field_type == FIELD_TYPE
    assert coded_domain.split_policy == SPLIT_POLICY
    assert coded_domain.merge_policy == MERGE_POLICY
    assert coded_domain.schema == SCHEMA


def test_coded_invalid_name():
    with pytest.raises(ValueError):
        CodedDomain("Name with invalid characters!", DESCRIPTION, FIELD_TYPE, SPLIT_POLICY, MERGE_POLICY)


def test_coded_add_codes(coded_domain):
    for code, desc, summary in CODES:
        coded_domain.codes.new(code, desc, summary)

    assert list(coded_domain.codes.keys()) == [e[0] for e in CODES]
    assert [e.description for e in coded_domain.codes.values()] == [e[1] for e in CODES]
    assert [e.meta_summary for e in coded_domain.codes.values()] == [e[2] for e in CODES]


def test_coded_add_duplicate(coded_domain):
    for code, desc, summary in CODES:
        coded_domain.codes.new(code, desc, summary)

    with pytest.raises(ValueError):
        coded_domain.codes.new(CODES[0][0], CODES[0][1], CODES[0][2])

    with pytest.raises(ValueError):
        coded_domain.codes.new(CODES[0][0], "Something Else")