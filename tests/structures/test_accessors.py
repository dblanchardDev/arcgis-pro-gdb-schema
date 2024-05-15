"""
Unit tests for accessors that manage the relationship between items.

Most accessor logic is tested as part of the other structure tests.
"""
#pylint: disable=protected-access,redefined-outer-name,missing-function-docstring

import pytest

from arcpy import SpatialReference

from gdbschematools.structures import Geodatabase


@pytest.fixture
def geodatabase():
    """A simple geodatabase object for testing."""
    return Geodatabase("My Geodatabase")


@pytest.fixture
def table_a(geodatabase):
    """A simple table already added to the geodatabase fixture."""
    table = geodatabase.datasets.tables.new("TableAlpha")
    table.fields.new("KeyA", "TEXT")
    return table


@pytest.fixture
def table_b(geodatabase):
    """Another simple table already added to the geodatabase fixture."""
    table = geodatabase.datasets.tables.new("TableBravo")
    table.fields.new("KeyB", "TEXT")
    return table


@pytest.fixture
def table_for_field(geodatabase):
    """Fixture table part of geodatabase fixture to which fields can be added."""
    return geodatabase.datasets.tables.new("MyDataset")


@pytest.fixture
def field_in_table(table_for_field):
    """Field which has been added to the table_for_field table fixture."""
    return table_for_field.fields.new("MyField", "TEXT")


@pytest.fixture
def field_with_domain(table_for_field, domain):
    """A field that is part of the geodatabase fixture, table_for_field fixture, and domain fixture."""
    return table_for_field.fields.new("MyField", "SHORT", domain=domain)


@pytest.fixture
def feat_cl(geodatabase):
    """A simple feature class already added to the geodatabase fixture."""
    spatial_ref = SpatialReference(4326)
    return geodatabase.datasets.feature_classes.new("MyTable", "POINT", spatial_ref)


@pytest.fixture
def rel_cl(geodatabase, table_a, table_b):
    """A simple relationship class already added to the geodatabase fixture, using table_a and table_b."""
    return geodatabase.datasets.relationship_classes.new("RelClass", table_a, table_b, "SIMPLE", "A to B", "B to A",
                                                         "NONE", "ONE_TO_ONE", False, "KeyA", "KeyB")


@pytest.fixture
def feat_dts(geodatabase):
    """A feature dataset already added to the geodatabase fixture."""
    return geodatabase.feature_datasets.new("MyFeatureDataset")


@pytest.fixture
def domain(geodatabase):
    """A domain already added to the geodatabase fixture (without fields)."""
    return geodatabase.domains.new("My Domain", "A new domain", "SHORT", "CODED", "DUPLICATE", "DEFAULT")


@pytest.fixture
def table_in_feat_dts(geodatabase, feat_dts):
    """A table that is in the feat_dts fixture."""
    table = geodatabase.datasets.tables.new("TableInFD", feature_dataset=feat_dts)
    table.fields.new("MyField", "TEXT")
    return table


def test_geodatabase_to_table(geodatabase, table_a):
    assert geodatabase.datasets.tables[0] == table_a


def test_table_to_geodatabase(geodatabase, table_a):
    assert table_a.geodatabase == geodatabase


def test_geodatabase_to_feature_class(geodatabase, feat_cl):
    assert geodatabase.datasets.feature_classes[0] == feat_cl


def test_feature_class_to_geodatabase(geodatabase, feat_cl):
    assert feat_cl.geodatabase == geodatabase


def test_geodatabase_to_relationship_class(geodatabase, rel_cl):
    assert geodatabase.datasets.relationship_classes[0] == rel_cl


def test_relationship_class_to_geodatabase(geodatabase, rel_cl):
    assert rel_cl.geodatabase == geodatabase


def test_geodatabase_to_feature_dataset(geodatabase, feat_dts):
    assert geodatabase.feature_datasets[0] == feat_dts


def test_feature_dataset_to_geodatabase(geodatabase, feat_dts):
    assert feat_dts.geodatabase == geodatabase


def test_feature_dataset_to_dataset(feat_dts, table_in_feat_dts):
    assert feat_dts.datasets[0] == table_in_feat_dts
    assert feat_dts.datasets.tables[0] == table_in_feat_dts


def test_dataset_to_feature_dataset(feat_dts, table_in_feat_dts):
    assert table_in_feat_dts.feature_dataset == feat_dts


def test_geodatabase_to_domain(geodatabase, domain):
    assert geodatabase.domains[0] == domain


def test_domain_to_geodatabase(geodatabase, domain):
    assert domain.geodatabase == geodatabase


def test_domain_to_field(field_with_domain, domain):
    assert domain.fields[0] == field_with_domain


def test_field_to_domain(field_with_domain, domain):
    assert field_with_domain.domain == domain


def test_table_to_field(table_for_field, field_in_table):
    assert table_for_field.fields[0] == field_in_table


def test_field_to_table(table_for_field, field_in_table):
    assert field_in_table.dataset == table_for_field


def test_table_to_relationship(rel_cl, table_a, table_b):
    assert table_a.relationship_classes[0] == rel_cl
    assert table_b.relationship_classes[0] == rel_cl


def test_relationship_to_table(rel_cl, table_a, table_b):
    assert rel_cl.origin.table == table_a
    assert rel_cl.destination.table == table_b


def test_dataset_walk(geodatabase, table_a, table_b, rel_cl, feat_dts, table_in_feat_dts):
    spatial_ref = SpatialReference(4326)
    feat_cl = geodatabase.datasets.feature_classes.new("MyFC", "POINT", spatial_ref, feature_dataset=feat_dts)

    expected = [
        (feat_dts, (feat_cl,), (table_in_feat_dts,), ()),
        (None, (), (table_a, table_b), (rel_cl,))
    ]

    for result in geodatabase.datasets.walk():
        assert result == expected.pop(0)