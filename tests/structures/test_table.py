"""Unit tests for Geodatabase Tables (non-geographic)."""
#pylint: disable=protected-access,redefined-outer-name,missing-function-docstring

from gdbschematools.structures import Table


# Constants for testing
NAME = "MyDataset1234"
ALIAS = "My Dataset 1234"
SCHEMA = "foo"
IS_ARCHIVED = True
IS_VERSIONED = True
OID_IS_64 = False
DSID = 12
META_SUMMARY = "This is a description about my table."


def test_table_initialization():
    dataset = Table(NAME, ALIAS, SCHEMA, IS_ARCHIVED, IS_VERSIONED, OID_IS_64, DSID, META_SUMMARY)

    assert dataset.name == NAME
    assert dataset.alias == ALIAS
    assert dataset.schema == SCHEMA
    assert dataset.is_archived == IS_ARCHIVED
    assert dataset.is_versioned == IS_VERSIONED
    assert dataset.oid_is_64 == OID_IS_64
    assert dataset.dsid == DSID
    assert dataset.meta_summary == META_SUMMARY
    assert dataset.dataset_type == "Table"