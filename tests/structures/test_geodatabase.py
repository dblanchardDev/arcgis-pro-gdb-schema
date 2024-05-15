"""Unit tests for Geodatabase Structure classes."""
#pylint: disable=protected-access,redefined-outer-name,missing-function-docstring

import pytest

from arcpy import SpatialReference

from gdbschematools.structures import CodedDomain, FeatureClass, FeatureDataset, Geodatabase, RangeDomain
from gdbschematools.structures import Relationship, Table


# Constants for testing
NAME = "MyItem"
SERVER = "170.10.10.102"
META_SUMMARY = "This is a details used for unit testing."
WORKSPACE_TYPE = "REMOTE_DATABASE"
ALIAS = "Alpha Dataset"
SCHEMA = "myschema"
IS_ARCHIVED = True
IS_VERSIONED = True
OID_IS_64 = False
DSID = 38
GEOMETRY_TYPE = "POINT"
SPATIAL_REF = SpatialReference(4326)
HAS_M = True
HAS_Z = True

ALPHA_PRIMARY = "First"
ALPHA_FOREIGN = "Another"
BRAVO_PRIMARY = "One"
BRAVO_FOREIGN = BRAVO_PRIMARY

REL_NAME = "TestRelClass"
FORWARD_LABEL = "Alpha to Bravo"
BACKWARD_LABEL = "Bravo to Alpha"
CARDINALITY = "MANY_TO_MANY"
NOTIFICATION = "FORWARD"
RELATIONSHIP_TYPE = "SIMPLE"
ATTRIBUTED = False


@pytest.fixture
def geodatabase():
    """Fixture of a geodatabase instance created with default value constants and 2 codes."""
    return Geodatabase(NAME, SERVER, META_SUMMARY, WORKSPACE_TYPE)


@pytest.fixture
def g_with_codes(geodatabase:Geodatabase):
    """Fixture of a geodatabase instance with 2 coded values added."""
    geodatabase.domains.new("Beta", "First domain to be added.", "TEXT", "CODED", "DUPLICATE", "DEFAULT")
    geodatabase.domains.new("Alpha", "Second domain to be added.", "SHORT", "RANGE", "DUPLICATE", "DEFAULT",
                                   [0, 10])
    return geodatabase


@pytest.fixture
def g_with_feat_dts(geodatabase:Geodatabase):
    """Fixture of a geodatabase instance with 2 coded values added."""
    geodatabase.feature_datasets.new("Beta")
    geodatabase.feature_datasets.new("Alpha")
    return geodatabase


@pytest.fixture
def g_with_table(geodatabase:Geodatabase):
    """Fixture containing pre-built geodatabase with single table."""
    geodatabase.datasets.tables.new(NAME, ALIAS, SCHEMA, IS_ARCHIVED, IS_VERSIONED, OID_IS_64, DSID, META_SUMMARY)
    return geodatabase


@pytest.fixture
def g_with_fc(geodatabase:Geodatabase):
    """Fixture containing pre-built geodatabase with single feature class."""
    geodatabase.datasets.feature_classes.new(NAME, GEOMETRY_TYPE, SPATIAL_REF, HAS_M, HAS_Z, ALIAS, SCHEMA,
                                           IS_ARCHIVED, IS_VERSIONED, OID_IS_64, DSID, META_SUMMARY)
    return geodatabase


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


#region: Geodatabase

def test_gdb_initialization():
    gdb = Geodatabase(NAME, SERVER, META_SUMMARY, WORKSPACE_TYPE)

    assert gdb.name == NAME
    assert gdb.server == SERVER
    assert gdb.meta_summary == META_SUMMARY
    assert gdb.workspace_type == WORKSPACE_TYPE

#endregion
#region: Domains

def test_new_range_domain(geodatabase):
    domain:RangeDomain = geodatabase.domains.new("Alpha", "Second domain to be added.", "SHORT", "RANGE", "DUPLICATE",
                                                  "DEFAULT", [0, 10])
    assert isinstance(domain, RangeDomain)
    assert domain.name == "Alpha"
    assert domain.description == "Second domain to be added."
    assert domain.field_type == "SHORT"
    assert domain.domain_type == "RANGE"
    assert domain.split_policy == "DUPLICATE"
    assert domain.merge_policy == "DEFAULT"
    assert domain.minimum == 0
    assert domain.maximum == 10


def test_new_coded_domain(geodatabase:Geodatabase):
    domain:CodedDomain = geodatabase.domains.new("Alpha", "Second domain to be added.", "SHORT", "CODED", "DUPLICATE",
                                                 "DEFAULT")
    assert isinstance(domain, CodedDomain)
    assert domain.name == "Alpha"
    assert domain.description == "Second domain to be added."
    assert domain.field_type == "SHORT"
    assert domain.domain_type == "CODED"
    assert domain.split_policy == "DUPLICATE"
    assert domain.merge_policy == "DEFAULT"


def test_domain_list_and_sort(g_with_codes:Geodatabase):
    assert [d.name for d in g_with_codes.domains] == ["Alpha", "Beta"]


def test_domain_getter(g_with_codes:Geodatabase):
    assert g_with_codes.domains["Alpha"].name == "Alpha"
    assert g_with_codes.domains["Beta"].name == "Beta"


def test_adding_duplicate_domain(g_with_codes:Geodatabase):
    duplicate_name = g_with_codes.domains[0].name
    with pytest.raises(ValueError):
        g_with_codes.domains.new(duplicate_name, "Duplicate name", "TEXT", "CODED", "DUPLICATE", "DEFAULT")

#endregion
#region: Feature datasets

def test_new_feat_dts(geodatabase:Geodatabase):
    feat_dts = geodatabase.feature_datasets.new("Alpha")
    assert isinstance(feat_dts, FeatureDataset)
    assert feat_dts.name == "Alpha"


def test_feat_dts_list_and_sort(g_with_feat_dts:Geodatabase):
    assert [d.name for d in g_with_feat_dts.feature_datasets] == ["Alpha", "Beta"]


def test_feat_dts_getter(g_with_feat_dts:Geodatabase):
    assert g_with_feat_dts.feature_datasets["Alpha"].name == "Alpha"
    assert g_with_feat_dts.feature_datasets["Beta"].name == "Beta"


def test_adding_duplicate_feat_dts(g_with_feat_dts:Geodatabase):
    duplicate_name = g_with_feat_dts.feature_datasets[0].name
    with pytest.raises(ValueError):
        g_with_feat_dts.feature_datasets.new(duplicate_name)


#endregion
#region Table


def test_new_table(geodatabase:Geodatabase):
    table = geodatabase.datasets.tables.new(NAME, ALIAS, SCHEMA, IS_ARCHIVED, IS_VERSIONED, OID_IS_64, DSID,
                                            META_SUMMARY)

    assert isinstance(table, Table)
    assert table.name == NAME
    assert table.alias == ALIAS
    assert table.schema == SCHEMA
    assert table.is_archived == IS_ARCHIVED
    assert table.is_versioned == IS_VERSIONED
    assert table.oid_is_64 == OID_IS_64
    assert table.dsid == DSID
    assert table.meta_summary == META_SUMMARY


def test_second_table(g_with_table:Geodatabase):
    g_with_table.datasets.tables.new("AAAAA")
    assert g_with_table.datasets[0].name == "AAAAA"
    assert g_with_table.datasets[1].name == NAME


def test_second_table_same_name(g_with_table:Geodatabase):
    with pytest.raises(ValueError):
        g_with_table.datasets.tables.new(NAME)


#endregion
#region: Feature Class

def test_new_feature_class(geodatabase:Geodatabase):
    feat_cl = geodatabase.datasets.feature_classes.new(NAME, GEOMETRY_TYPE, SPATIAL_REF, HAS_M, HAS_Z, ALIAS, SCHEMA,
                                                   IS_ARCHIVED, IS_VERSIONED, OID_IS_64, DSID, META_SUMMARY)

    assert isinstance(feat_cl, FeatureClass)
    assert feat_cl.name == NAME
    assert feat_cl.geometry_type == GEOMETRY_TYPE
    assert feat_cl.spatial_ref == SPATIAL_REF
    assert feat_cl.has_m == HAS_M
    assert feat_cl.has_z == HAS_Z
    assert feat_cl.alias == ALIAS
    assert feat_cl.schema == SCHEMA
    assert feat_cl.is_archived == IS_ARCHIVED
    assert feat_cl.is_versioned == IS_VERSIONED
    assert feat_cl.dsid == DSID
    assert feat_cl.meta_summary == META_SUMMARY


def test_second_fc(g_with_fc:Geodatabase):
    g_with_fc.datasets.feature_classes.new("AAAAA", GEOMETRY_TYPE, SPATIAL_REF)
    assert g_with_fc.datasets[0].name == "AAAAA"
    assert g_with_fc.datasets[1].name == NAME


def test_second_dataset_same_name(g_with_fc:Geodatabase):
    with pytest.raises(ValueError):
        g_with_fc.datasets.tables.new(NAME)

#endregion
#region: Relationship Class


def test_new_relationship_class(geodatabase:Geodatabase, table_alpha:Table, table_bravo:Table):
    rel_cl = geodatabase.datasets.relationship_classes.new(REL_NAME, table_alpha, table_bravo, RELATIONSHIP_TYPE,
                                                           FORWARD_LABEL, BACKWARD_LABEL, NOTIFICATION, CARDINALITY,
                                                           ATTRIBUTED, ALPHA_PRIMARY, ALPHA_FOREIGN, BRAVO_PRIMARY,
                                                           BRAVO_FOREIGN, SCHEMA, IS_ARCHIVED, IS_VERSIONED, OID_IS_64,
                                                           DSID, META_SUMMARY)

    assert isinstance(rel_cl, Relationship)
    assert rel_cl.name == REL_NAME
    assert rel_cl.origin.table == table_alpha
    assert rel_cl.destination.table == table_bravo
    assert rel_cl.forward_label == FORWARD_LABEL
    assert rel_cl.backward_label == BACKWARD_LABEL
    assert rel_cl.cardinality == CARDINALITY
    assert rel_cl.notification == NOTIFICATION
    assert rel_cl.relationship_type == RELATIONSHIP_TYPE
    assert rel_cl.attributed == ATTRIBUTED
    assert rel_cl.origin.primary_key == ALPHA_PRIMARY
    assert rel_cl.destination.primary_key == BRAVO_PRIMARY
    assert rel_cl.origin.foreign_key == ALPHA_FOREIGN
    assert rel_cl.destination.foreign_key == BRAVO_FOREIGN
    assert rel_cl.schema == SCHEMA
    assert rel_cl.is_archived == IS_ARCHIVED
    assert rel_cl.is_versioned == IS_VERSIONED
    assert rel_cl.oid_is_64 == OID_IS_64
    assert rel_cl.dsid == DSID
    assert rel_cl.meta_summary == META_SUMMARY


#endregion