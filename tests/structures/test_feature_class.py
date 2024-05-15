"""Unit tests for Geodatabase Feature Class classes."""
#pylint: disable=protected-access,redefined-outer-name,missing-function-docstring

from arcpy import SpatialReference
import pytest

from gdbschematools.structures import FeatureClass


# Valid geometry types
VALID_GEOMETRY_TYPES = (
    "POINT",
    "MULTIPOINT",
    "POLYGON",
    "POLYLINE",
    "MULTIPATCH",
)


# Constants for testing
NAME = "MyDataset1234"
GEOMETRY_TYPE = "POINT"
SPATIAL_REF = SpatialReference(4326)
HAS_M = True
HAS_Z = True
ALIAS = "My Dataset 1234"
SCHEMA = "foo"
IS_ARCHIVED = True
IS_VERSIONED = True
OID_IS_64 = False
DSID = 12
META_SUMMARY = "This is a description about my feature class."


def test_feature_class_initialization():
    fc = FeatureClass(NAME, GEOMETRY_TYPE, SPATIAL_REF, HAS_M, HAS_Z, ALIAS, SCHEMA, IS_ARCHIVED,
                      IS_VERSIONED, OID_IS_64, DSID, META_SUMMARY)

    assert fc.name == NAME
    assert fc.geometry_type == GEOMETRY_TYPE
    assert fc.spatial_ref == SPATIAL_REF
    assert fc.has_m == HAS_M
    assert fc.has_z == HAS_Z
    assert fc.alias == ALIAS
    assert fc.schema == SCHEMA
    assert fc.is_archived == IS_ARCHIVED
    assert fc.is_versioned == IS_VERSIONED
    assert fc.dsid == DSID
    assert fc.meta_summary == META_SUMMARY
    assert fc.dataset_type == "FeatureClass"


@pytest.mark.parametrize("geometry_type", VALID_GEOMETRY_TYPES)
def test_valid_geometry_types(geometry_type):
    fc = FeatureClass(NAME, geometry_type, SPATIAL_REF, HAS_M, HAS_Z, ALIAS, SCHEMA, IS_ARCHIVED,
                      IS_VERSIONED, OID_IS_64, DSID)
    assert fc.geometry_type == geometry_type


def test_invalid_geometry_type():
    with pytest.raises(ValueError):
        FeatureClass(NAME, "Nonesense", SPATIAL_REF, HAS_M, HAS_Z, ALIAS, SCHEMA, IS_ARCHIVED,
                     IS_VERSIONED, OID_IS_64, DSID)