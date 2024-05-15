"""Unit tests for Geodatabase Structure classes."""
#pylint: disable=protected-access,redefined-outer-name,missing-function-docstring

import pytest

from gdbschematools.structures import Relationship, RelationshipMember, Table


# Valid relationship types
VALID_RELATIONSHIP_TYPES = [
    "SIMPLE",
    "COMPOSITE",
]


# Valid notification values
VALID_NOTIFICATIONS = [
    "NONE",
    "FORWARD",
    "BACKWARD",
    "BOTH",
]


# Valid cardinality values
VALID_CARDINALITIES = [
    "ONE_TO_ONE",
    "ONE_TO_MANY",
    "MANY_TO_MANY",
]


# Field types that are valid in an attributed field class.
VALID_FIELD_TYPES = (
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
    "RASTER",
)


# Testing value constants
ALPHA_PRIMARY = "First"
ALPHA_FOREIGN = "Another"
BRAVO_PRIMARY = "One"
BRAVO_FOREIGN = BRAVO_PRIMARY

NAME = "TestRelClass"
FORWARD_LABEL = "Alpha to Bravo"
BACKWARD_LABEL = "Bravo to Alpha"
CARDINALITY = "MANY_TO_MANY"
NOTIFICATION = "FORWARD"
RELATIONSHIP_TYPE = "SIMPLE"
ATTRIBUTED = False
SCHEMA = "FooBar"
IS_ARCHIVED = True
IS_VERSIONED = True
OID_IS_64 = False
DSID = 38
META_SUMMARY = "This is a description about my relationship class."


@pytest.fixture
def table_alpha():
    """Sample table with a few fields."""
    table = Table("Alpha", alias="Alpha Test Table")
    table.fields.new("OBJECTID", "OBJECTID", required=True, nullable=False)
    table.fields.new("First", "TEXT", length=100)
    table.fields.new("Second", "SHORT")
    table.fields.new("Third", "LONG")
    return table


@pytest.fixture
def table_bravo():
    """Sample table with a few fields."""
    table = Table("Bravo", alias="Bravo Test Table")
    table.fields.new("OBJECTID", "OBJECTID", required=True, nullable=False)
    table.fields.new("One", "TEXT", length=100)
    table.fields.new("Two", "SHORT")
    table.fields.new("Three", "LONG")
    return table


def test_relationship_member_initialization(table_alpha):
    rm = RelationshipMember(table_alpha, ALPHA_PRIMARY, ALPHA_FOREIGN)
    assert rm.table == table_alpha
    assert rm.primary_key == ALPHA_PRIMARY
    assert rm.foreign_key == ALPHA_FOREIGN


def test_relationship_member_with_invalid_table():
    with pytest.raises(TypeError):
        RelationshipMember("not a table", ALPHA_PRIMARY, ALPHA_FOREIGN)


def test_relationship_member_field_not_in_table(table_alpha):
    with pytest.raises(ValueError):
        RelationshipMember.confirm_key_in_table(table_alpha, "Field_Not_In_Table_Alpha")


def test_relationship_initialization(table_alpha, table_bravo):
    rel = Relationship(NAME, table_alpha, table_bravo, RELATIONSHIP_TYPE, FORWARD_LABEL, BACKWARD_LABEL, NOTIFICATION,
                       CARDINALITY, ATTRIBUTED, ALPHA_PRIMARY, ALPHA_FOREIGN, BRAVO_PRIMARY, BRAVO_FOREIGN, SCHEMA,
                       IS_ARCHIVED, IS_VERSIONED, OID_IS_64, DSID, META_SUMMARY)

    assert rel.name == NAME
    assert rel.origin.table == table_alpha
    assert rel.destination.table == table_bravo
    assert rel.forward_label == FORWARD_LABEL
    assert rel.backward_label == BACKWARD_LABEL
    assert rel.cardinality == CARDINALITY
    assert rel.notification == NOTIFICATION
    assert rel.relationship_type == RELATIONSHIP_TYPE
    assert rel.attributed == ATTRIBUTED
    assert rel.origin.primary_key == ALPHA_PRIMARY
    assert rel.origin.foreign_key == ALPHA_FOREIGN
    assert rel.destination.primary_key == BRAVO_PRIMARY
    assert rel.destination.foreign_key == BRAVO_FOREIGN
    assert rel.schema == SCHEMA
    assert rel.is_archived == IS_ARCHIVED
    assert rel.is_versioned == IS_VERSIONED
    assert rel.dsid == DSID
    assert rel.meta_summary == META_SUMMARY
    assert rel.dataset_type == "RelationshipClass"


@pytest.mark.parametrize("cardinality", VALID_CARDINALITIES)
def test_cardinalities_valid_value(table_alpha, table_bravo, cardinality):
    origin_foreign = ALPHA_FOREIGN
    destin_primary = BRAVO_PRIMARY
    destin_foreign = BRAVO_FOREIGN
    if cardinality != "MANY_TO_MANY":
        origin_foreign = BRAVO_PRIMARY
        destin_primary = None
        destin_foreign = None

    Relationship(NAME, table_alpha, table_bravo, RELATIONSHIP_TYPE, FORWARD_LABEL, BACKWARD_LABEL, NOTIFICATION,
                       cardinality, ATTRIBUTED, ALPHA_PRIMARY, origin_foreign, destin_primary, destin_foreign, SCHEMA,
                       IS_ARCHIVED, IS_VERSIONED, OID_IS_64, DSID, META_SUMMARY)


def test_cardinalities_invalid_value(table_alpha, table_bravo):
    with pytest.raises(ValueError):
        Relationship(NAME, table_alpha, table_bravo, RELATIONSHIP_TYPE, FORWARD_LABEL, BACKWARD_LABEL, NOTIFICATION,
                       "Nonesense", ATTRIBUTED, ALPHA_PRIMARY, ALPHA_FOREIGN, BRAVO_PRIMARY, BRAVO_FOREIGN, SCHEMA,
                       IS_ARCHIVED, IS_VERSIONED, OID_IS_64, DSID, META_SUMMARY)


def test_many_to_many_without_foreign_keys(table_alpha, table_bravo):
    with pytest.raises(ValueError):
        Relationship(NAME, table_alpha, table_bravo, RELATIONSHIP_TYPE, FORWARD_LABEL, BACKWARD_LABEL, NOTIFICATION,
                       "MANY_TO_MANY", ATTRIBUTED, ALPHA_PRIMARY, ALPHA_FOREIGN, BRAVO_PRIMARY)


@pytest.mark.parametrize("notification", VALID_NOTIFICATIONS)
def test_notifications_valid_value(table_alpha, table_bravo, notification):
    Relationship(NAME, table_alpha, table_bravo, RELATIONSHIP_TYPE, FORWARD_LABEL, BACKWARD_LABEL, notification,
                       CARDINALITY, ATTRIBUTED, ALPHA_PRIMARY, ALPHA_FOREIGN, BRAVO_PRIMARY, BRAVO_FOREIGN, SCHEMA,
                       IS_ARCHIVED, IS_VERSIONED, OID_IS_64, DSID, META_SUMMARY)


def test_notifications_invalid_value(table_alpha, table_bravo):
    with pytest.raises(ValueError):
        Relationship(NAME, table_alpha, table_bravo, RELATIONSHIP_TYPE, FORWARD_LABEL, BACKWARD_LABEL, "Nonesense",
                       CARDINALITY, ATTRIBUTED, ALPHA_PRIMARY, ALPHA_FOREIGN, BRAVO_PRIMARY, BRAVO_FOREIGN, SCHEMA,
                       IS_ARCHIVED, IS_VERSIONED, OID_IS_64, DSID, META_SUMMARY)


@pytest.mark.parametrize("relationship_type", VALID_RELATIONSHIP_TYPES)
def test_relationship_types_valid_value(table_alpha, table_bravo, relationship_type):
    Relationship(NAME, table_alpha, table_bravo, relationship_type, FORWARD_LABEL, BACKWARD_LABEL, NOTIFICATION,
                       CARDINALITY, ATTRIBUTED, ALPHA_PRIMARY, ALPHA_FOREIGN, BRAVO_PRIMARY, BRAVO_FOREIGN, SCHEMA,
                       IS_ARCHIVED, IS_VERSIONED, OID_IS_64, DSID, META_SUMMARY)


def test_relationship_types_invalid_value(table_alpha, table_bravo):
    with pytest.raises(ValueError):
        Relationship(NAME, table_alpha, table_bravo, "Nonesense", FORWARD_LABEL, BACKWARD_LABEL, NOTIFICATION,
                       CARDINALITY, ATTRIBUTED, ALPHA_PRIMARY, ALPHA_FOREIGN, BRAVO_PRIMARY, BRAVO_FOREIGN, SCHEMA,
                       IS_ARCHIVED, IS_VERSIONED, OID_IS_64, DSID, META_SUMMARY)


def test_non_attributed_bad_primary_key(table_alpha, table_bravo):
    attributed = False
    with pytest.raises(ValueError):
        Relationship(NAME, table_alpha, table_bravo, "SIMPLE", FORWARD_LABEL, BACKWARD_LABEL, NOTIFICATION,
                     "ONE_TO_ONE", attributed, "Nonesense", ALPHA_FOREIGN)


def test_non_attributed_bad_foreign_key(table_alpha, table_bravo):
    attributed = False
    with pytest.raises(ValueError):
        Relationship(NAME, table_alpha, table_bravo, "SIMPLE", FORWARD_LABEL, BACKWARD_LABEL, NOTIFICATION,
                     "ONE_TO_ONE", attributed, ALPHA_PRIMARY, "Nonesense")


def test_attributed_bad_origin_primary_key(table_alpha, table_bravo):
    attributed = True
    with pytest.raises(ValueError):
        Relationship(NAME, table_alpha, table_bravo, "COMPOSITE", FORWARD_LABEL, BACKWARD_LABEL, NOTIFICATION,
                     "MANY_TO_MANY", attributed, "Nonesense", ALPHA_FOREIGN, BRAVO_PRIMARY, BRAVO_FOREIGN)


def test_attributed_bad_destination_primary_key(table_alpha, table_bravo):
    attributed = True
    with pytest.raises(ValueError):
        Relationship(NAME, table_alpha, table_bravo, "COMPOSITE", FORWARD_LABEL, BACKWARD_LABEL, NOTIFICATION,
                     "MANY_TO_MANY", attributed, ALPHA_PRIMARY, ALPHA_FOREIGN, "Nonesense", BRAVO_FOREIGN)


def test_attributed_missing_origin_foreign_keys(table_alpha, table_bravo):
    attributed = True
    with pytest.raises(ValueError):
        Relationship(NAME, table_alpha, table_bravo, RELATIONSHIP_TYPE, FORWARD_LABEL, BACKWARD_LABEL, NOTIFICATION,
                     "ONE_TO_ONE", attributed, ALPHA_PRIMARY, None, BRAVO_PRIMARY, BRAVO_FOREIGN)


def test_attributed_missing_destination_foreign_keys(table_alpha, table_bravo):
    attributed = True
    with pytest.raises(ValueError):
        Relationship(NAME, table_alpha, table_bravo, RELATIONSHIP_TYPE, FORWARD_LABEL, BACKWARD_LABEL, NOTIFICATION,
                     "ONE_TO_ONE", attributed, ALPHA_PRIMARY, ALPHA_FOREIGN, BRAVO_PRIMARY, None)



def test_attributed_to_false_with_fields(table_alpha, table_bravo):
    attributed = True
    rel = Relationship(NAME, table_alpha, table_bravo, RELATIONSHIP_TYPE, FORWARD_LABEL, BACKWARD_LABEL, NOTIFICATION,
                       CARDINALITY, attributed, ALPHA_PRIMARY, ALPHA_FOREIGN, BRAVO_PRIMARY, BRAVO_FOREIGN, SCHEMA,
                       IS_ARCHIVED, IS_VERSIONED, OID_IS_64, DSID, META_SUMMARY)

    rel.fields.new("One", "SHORT")

    with pytest.raises(ValueError):
        rel.attributed = False


@pytest.mark.parametrize("field_type", VALID_FIELD_TYPES)
def test_adding_valid_field(table_alpha, table_bravo, field_type):
    attributed = True
    rel = Relationship(NAME, table_alpha, table_bravo, RELATIONSHIP_TYPE, FORWARD_LABEL, BACKWARD_LABEL, NOTIFICATION,
                       CARDINALITY, attributed, ALPHA_PRIMARY, ALPHA_FOREIGN, BRAVO_PRIMARY, BRAVO_FOREIGN, SCHEMA,
                       IS_ARCHIVED, IS_VERSIONED, OID_IS_64, DSID, META_SUMMARY)

    field = rel.fields.new("One", field_type)
    assert list(rel.fields) == [field]


@pytest.mark.parametrize("field_type", ["Nonesense", "SHAPE"])
def test_adding_invalid_field(table_alpha, table_bravo, field_type):
    attributed = True
    rel = Relationship(NAME, table_alpha, table_bravo, RELATIONSHIP_TYPE, FORWARD_LABEL, BACKWARD_LABEL, NOTIFICATION,
                       CARDINALITY, attributed, ALPHA_PRIMARY, ALPHA_FOREIGN, BRAVO_PRIMARY, BRAVO_FOREIGN, SCHEMA,
                       IS_ARCHIVED, IS_VERSIONED, OID_IS_64, DSID, META_SUMMARY)

    with pytest.raises(ValueError):
        rel.fields.new("One", field_type)


def test_add_field_with_attributed_off(table_alpha, table_bravo):
    attributed = False
    rel = Relationship(NAME, table_alpha, table_bravo, RELATIONSHIP_TYPE, FORWARD_LABEL, BACKWARD_LABEL, NOTIFICATION,
                       CARDINALITY, attributed, ALPHA_PRIMARY, ALPHA_FOREIGN, BRAVO_PRIMARY, BRAVO_FOREIGN, SCHEMA,
                       IS_ARCHIVED, IS_VERSIONED, OID_IS_64, DSID, META_SUMMARY)

    with pytest.raises(AttributeError):
        rel.fields.new("One", "SHORT")