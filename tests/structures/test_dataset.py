"""Unit tests for Geodatabase generic Datasets."""
#pylint: disable=protected-access,redefined-outer-name,missing-function-docstring

import pytest

from gdbschematools.structures import CodedDomain, Dataset, FeatureDataset


# Dataset types that are supported
VALID_DATASET_TYPES = [
    "FeatureClass",
    "Table",
    "RelationshipClass"
]


# Dataset types that are not supported
UNSUPPORTED_DATASET_TYPES = [
    "Any",
    "CadastralFabric",
    "CadDrawing",
    "Container",
    "DiagramDataset",
    "FeatureDataset",
    "Geo",
    "LasDataset",
    "Locator",
    "MosaicDataset",
    "NetworkDataset",
    "ParcelDataset",
    "PlanarGraph",
    "RasterBand",
    "RasterDataset",
    "SchematicDataset",
    "Text",
    "TIN",
    "Tool",
    "Toolbox",
    "Topology",
    "Terrain",
    "UtilityNetwork",
]


# Constants for testing
NAME = "MyDataset1234"
ALIAS = "My Dataset 1234"
SCHEMA = "foo"
IS_ARCHIVED = True
IS_VERSIONED = True
OID_IS_64 = True
DSID = 12
META_SUMMARY = "This is what my dataset is for."

INSTANCE_WARNING = "The Dataset class should not be instantiated directly. Use the Table, FeatureClass, \
or RelationshipClass classes instead."


# Ignore warning regarding instantiating Dataset class directly
pytestmark = pytest.mark.filterwarnings(f"ignore:{INSTANCE_WARNING}")


#region DATASET

@pytest.fixture
def dataset() -> Dataset:
    """Simple dataset instance using default value constants"""
    return Dataset(NAME, SCHEMA, IS_ARCHIVED, IS_VERSIONED, OID_IS_64, DSID)


def test_dataset_initialization():
    with pytest.warns(UserWarning, match=INSTANCE_WARNING):
        dataset = Dataset(NAME, SCHEMA, IS_ARCHIVED, IS_VERSIONED, OID_IS_64, DSID, META_SUMMARY)

        assert dataset.name == NAME
        assert dataset.schema == SCHEMA
        assert dataset.is_archived == IS_ARCHIVED
        assert dataset.is_versioned == IS_VERSIONED
        assert dataset.oid_is_64 == OID_IS_64
        assert dataset.dsid == DSID
        assert dataset.meta_summary == META_SUMMARY


def test_dataset_invalid_name():
    with pytest.raises(ValueError):
        Dataset("Name with spaces")

    with pytest.raises(ValueError):
        Dataset("9StartWithNumber")

    with pytest.raises(ValueError):
        Dataset("Invalid;Char")


@pytest.mark.parametrize("dataset_type", VALID_DATASET_TYPES)
def test_valid_dataset_type(dataset:Dataset, dataset_type:str):
    dataset.dataset_type = dataset_type
    assert dataset.dataset_type == dataset_type


@pytest.mark.parametrize("dataset_type", UNSUPPORTED_DATASET_TYPES + ["Nonesense"])
def test_invalid_dataset_type(dataset:Dataset, dataset_type:str):
    with pytest.raises(ValueError):
        dataset.dataset_type = dataset_type


def test_block_change_to_dataset_type(dataset:Dataset):
    dataset.dataset_type = VALID_DATASET_TYPES[0]
    with pytest.raises(AttributeError):
        dataset.dataset_type = VALID_DATASET_TYPES[1]


def test_add_field_to_dataset(dataset):
    field = dataset.fields.new("Alpha", "TEXT")

    assert field.name == "Alpha"
    assert dataset.fields["Alpha"] == field


def test_field_order_in_dataset(dataset):
    dataset.fields.new("One", "TEXT")
    dataset.fields.new("Two", "TEXT")
    dataset.fields.new("Three", "TEXT")

    assert [f.name for f in dataset.fields] == ["One", "Two", "Three"]


def test_adding_duplicate_field_to_dataset(dataset):
    dataset.fields.new("One", "TEXT")

    with pytest.raises(ValueError):
        dataset.fields.new("One", "SHORT")


def test_feature_dataset_in_dataset():
    fd = FeatureDataset(NAME)
    dataset = Dataset(NAME, SCHEMA, IS_ARCHIVED, IS_VERSIONED, OID_IS_64, DSID, feature_dataset=fd)
    assert dataset.feature_dataset.name == NAME


@pytest.mark.parametrize("oid_is_64", [True, False, None])
def test_valid_oid_is_64_in_dataset(oid_is_64):
    Dataset(NAME, SCHEMA, IS_ARCHIVED, IS_VERSIONED, oid_is_64)


@pytest.mark.parametrize("oid_is_64", [123, "Nonesense"])
def test_invalid_oid_is_64_in_dataset(oid_is_64):
    with pytest.raises(TypeError):
        Dataset(NAME, SCHEMA, IS_ARCHIVED, IS_VERSIONED, oid_is_64)


def test_two_objectid_fields_in_dataset(dataset):
    dataset.fields.new("OID_1", "OBJECTID")
    with pytest.raises(ValueError):
        dataset.fields.new("OID_2", "OBJECTID")


def test_two_shape_fields_in_dataset(dataset):
    dataset.fields.new("SHAPE_1", "SHAPE")
    with pytest.raises(ValueError):
        dataset.fields.new("SHAPE_2", "SHAPE")


def test_two_globalid_fields_in_dataset(dataset):
    dataset.fields.new("GLOBALID_1", "GLOBALID")
    with pytest.raises(ValueError):
        dataset.fields.new("GLOBALID_2", "GLOBALID")


#endregion
#region SUBTYPES


@pytest.fixture
def classif_field(dataset):
    return dataset.fields.new("Classification", "LONG", default=0)


@pytest.fixture
def group_field(dataset):
    return dataset.fields.new("Group", "TEXT")


@pytest.fixture
def subtype(dataset, classif_field):
    subtype = dataset.set_subtype(classif_field)
    subtype.codes.new(0, "Zero", "A description of 0.")
    subtype.codes.new(1, "One")
    return subtype


def test_subtype_set_valid(dataset, classif_field):
    subtype = dataset.set_subtype(classif_field)
    assert subtype.field == classif_field


def test_subtype_set_invalid_type(dataset, group_field):
    with pytest.raises(TypeError):
        dataset.set_subtype(group_field)


def test_subtype_set_nonmember_field(classif_field):
    other_dataset = Dataset("SomethingElse")
    with pytest.raises(ValueError):
        other_dataset.set_subtype(classif_field)


def test_subtype_properties(dataset, subtype, classif_field):
    assert subtype.dataset == dataset
    assert subtype.field == classif_field
    assert subtype.default == 0


def test_subtype_codes(subtype, classif_field, group_field):
    assert list(subtype.codes) == [0, 1]

    assert subtype.codes[0].description == "Zero"
    assert subtype.codes[0].meta_summary == "A description of 0."
    assert subtype.codes[0].field_props[classif_field.name].name == classif_field.name
    assert subtype.codes[0].field_props[classif_field.name].default is None
    assert subtype.codes[0].field_props[classif_field.name].domain is None
    assert subtype.codes[0].field_props[group_field.name].name == group_field.name
    assert subtype.codes[0].field_props[group_field.name].default is None
    assert subtype.codes[0].field_props[group_field.name].domain is None

    assert subtype.codes[1].description == "One"
    assert subtype.codes[1].meta_summary is None
    assert subtype.codes[1].field_props[classif_field.name].name == classif_field.name
    assert subtype.codes[1].field_props[classif_field.name].default is None
    assert subtype.codes[1].field_props[classif_field.name].domain is None
    assert subtype.codes[1].field_props[group_field.name].name == group_field.name
    assert subtype.codes[1].field_props[group_field.name].default is None
    assert subtype.codes[1].field_props[group_field.name].domain is None


def test_setting_valid_domain_in_subtype(subtype, group_field):
    domain_a = CodedDomain("Group Types A", "", "TEXT", "DUPLICATE","DEFAULT")
    domain_b = CodedDomain("Group Types B", "", "TEXT", "DUPLICATE","DEFAULT")

    subtype.codes[0].field_props[group_field.name].domain = domain_a
    subtype.codes[1].field_props[group_field.name].domain = domain_b

    assert subtype.codes[0].field_props[group_field.name].domain.name == domain_a.name
    assert domain_a.fields[0] == group_field

    assert subtype.codes[1].field_props[group_field.name].domain.name == domain_b.name
    assert domain_b.fields[0] == group_field


def test_setting_valid_default_in_subtype(subtype, group_field):
    subtype.codes[0].field_props[group_field.name].default = "Alpha"
    subtype.codes[1].field_props[group_field.name].default = "Bravo"

    assert subtype.codes[0].field_props[group_field.name].default == "Alpha"
    assert subtype.codes[1].field_props[group_field.name].default == "Bravo"

#endregion