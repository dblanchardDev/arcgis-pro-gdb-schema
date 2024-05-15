"""Unit tests for Geodatabase generic Feature Datasets."""
#pylint: disable=protected-access,redefined-outer-name,missing-function-docstring

from gdbschematools.structures import FeatureDataset


# Constants for testing
NAME = "MyDataset1234"
SCHEMA = "foo"
META_SUMMARY = "This is what my dataset is for."


def test_feature_dataset():
    fd = FeatureDataset(NAME, SCHEMA, META_SUMMARY)
    assert fd.name == NAME
    assert fd.schema == SCHEMA
    assert fd.meta_summary == META_SUMMARY