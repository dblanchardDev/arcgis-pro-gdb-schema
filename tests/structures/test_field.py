"""Unit tests for Geodatabase Table fields."""
#pylint: disable=protected-access,redefined-outer-name,missing-function-docstring

import datetime

import pytest

from gdbschematools.structures import Field
from gdbschematools.structures import CodedDomain, RangeDomain


# Valid field types for fields
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
    "TIMESTAMPOFFSET",
    "BLOB",
    "GUID",
    "GLOBALID",
    "OBJECTID",
    "RASTER",
    "SHAPE",
]


# Constants to test fields with
NAME = "NewField"
FIELD_TYPE = "FLOAT"
PRECISION = 6
SCALE = 2
LENGTH = None
ALIAS = "New Field"
NULLABLE = False
REQUIRED = True
DEFAULT = 8.52
DOMAIN = RangeDomain("Test", "This is a test.", "FLOAT", "DUPLICATE", "DEFAULT", [0, 10.5])
META_SUMMARY = "This is a description of this field."


@pytest.fixture
def ranged_domain():
    """Ranged domain fixture."""
    return RangeDomain("Test", "This is a test", "SHORT", "DUPLICATE", "DEFAULT", (5, 10))


@pytest.fixture
def coded_domain():
    """Coded domain fixture."""
    domain = CodedDomain("My Coded Domain", "", "TEXT", "DUPLICATE", "DEFAULT")
    domain.codes.new("A", "Alpha")
    domain.codes.new("B", "Bravo")
    domain.codes.new("C", "Charlie")
    return domain


def test_field_initialization():
    field = Field(NAME, FIELD_TYPE, PRECISION, SCALE, LENGTH, ALIAS, NULLABLE, REQUIRED, DEFAULT, DOMAIN,
                  META_SUMMARY)

    assert field.name == NAME
    assert field.field_type == FIELD_TYPE
    assert field.precision == PRECISION
    assert field.scale == SCALE
    assert field.length == LENGTH
    assert field.alias == ALIAS
    assert field.nullable == NULLABLE
    assert field.required == REQUIRED
    assert field.default == DEFAULT
    assert field.domain == DOMAIN
    assert field.meta_summary == META_SUMMARY


@pytest.mark.parametrize("field_type", VALID_FIELD_TYPES)
def test_valid_field_types(field_type):
    Field(NAME, field_type)


def test_invalid_field_type():
    with pytest.raises(ValueError):
        Field(NAME, "Nonesense")


def test_invalid_precision():
    with pytest.raises(ValueError):
        Field(NAME, "SHORT", precision="abc")


def test_precision_with_non_numeric():
    with pytest.raises(ValueError):
        Field(NAME, "TEXT", precision=6)


def test_invalid_scale():
    with pytest.raises(ValueError):
        Field(NAME, "FLOAT", scale="abc")


def test_scale_with_non_numeric():
    with pytest.raises(ValueError):
        Field(NAME, "SHORT", scale=6)


def test_invalid_length():
    with pytest.raises(ValueError):
        Field(NAME, "TEXT", scale="abc")


def test_length_with_non_text():
    with pytest.raises(ValueError):
        Field(NAME, "SHORT", length=6)


def test_named_used_when_no_alias():
    field = Field(NAME, "SHORT")
    assert field.alias == NAME


def test_domain_wrong_field_type():
    with pytest.raises(TypeError):
        Field(NAME, "DATE", domain=DOMAIN)


@pytest.mark.parametrize("field_type, default", [
    ("TEXT", "Hello"),
    ("SHORT", 1234),
    ("LONG", 12345678),
    ("FLOAT", "123.45"),
    ("DOUBLE", 123.45),
    ("DATE", "2024-01-01T10:10:10"),
    ("DATE", datetime.datetime.now()),
])
def test_default_is_correct_type(field_type, default):
    Field(NAME, field_type, default=default)


@pytest.mark.parametrize("field_type,default", [
    ("LONG", "Nonesense"),
    ("DATE", 1234),
    ("SHORT", 123.456)
])
def test_default_is_wrong_type(field_type, default):
    with pytest.raises((TypeError, ValueError)):
        Field(NAME, field_type, default=default)


def test_default_and_domain_match_ranged(ranged_domain):
    Field("NewField", "SHORT", default=8, domain=ranged_domain)


def test_default_and_domain_match_coded(coded_domain):
    Field("NewField", "TEXT", default="B", domain=coded_domain)


def test_default_not_in_domain_ranged(ranged_domain):
    field = Field("NewField", "SHORT", domain=ranged_domain)
    with pytest.raises(ValueError):
        field.default = 0


def test_default_not_in_domain_coded(coded_domain):
    field = Field("NewField", "TEXT", domain=coded_domain)
    with pytest.raises(ValueError):
        field.default = "Nope"


def test_domain_not_in_default_ranged(ranged_domain):
    field = Field("NewField", "SHORT", default=0)
    with pytest.raises(ValueError):
        field.domain = ranged_domain


def test_domain_not_in_default_coded(coded_domain):
    field = Field("NewField", "TEXT", default="Nope")
    with pytest.raises(ValueError):
        field.domain = coded_domain