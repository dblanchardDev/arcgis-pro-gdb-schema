"""Unit tests for the base Geodatabase Interface class."""
#pylint: disable=protected-access,redefined-outer-name,missing-function-docstring

import os
from typing import TYPE_CHECKING

import pytest

from gdbschematools.interfaces import ExcelInterface
from gdbschematools.interfaces.excel.reader.excel_to_json import parse_workbook
from tests.interfaces.data import gdbschematool_gdb_expected as exp
from tests.interfaces.data.check_structures import StructureTests

if TYPE_CHECKING:
    from gdbschematools.structures import Geodatabase
    from gdbschematools.interfaces.excel.reader.excel_to_json import KeyValuePair, WorksheetList


class TestXLSReaderStructureTests(StructureTests):
    """Test the Excel reader, ensuring the output in the Geodatabase structure is the same as expected."""

    @pytest.fixture(scope="module")
    #pylint: disable=arguments-differ
    def geodatabase(self) -> "Geodatabase":
        # Derive path to test excel files
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        excel_test_datasets = os.path.join(root_dir, "data/excel_test_datasets.xlsx")
        excel_test_domains = os.path.join(root_dir, "data/excel_test_domains.xlsx")
        excel_test_relationships = os.path.join(root_dir, "data/excel_test_relationships.xlsx")

        # Read the data into a Geodatabase structure
        return ExcelInterface.read(excel_test_datasets, excel_test_domains, excel_test_relationships)


    #region Geodatabase

    def test_geodatabase_properties(self, geodatabase:"Geodatabase"):
        expected = exp.GEODATABASE
        assert geodatabase.name == expected["name"]
        assert geodatabase.meta_summary == expected["meta_summary"]
        assert geodatabase.workspace_type == expected["workspace_type"]

    #endregion


@pytest.fixture(scope="module")
def parsed_workbook() -> tuple["KeyValuePair", "WorksheetList"]:
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excel_test_relationships = os.path.join(root_dir, "data/excel_test_relationships.xlsx")

    return parse_workbook(excel_test_relationships)


def test_gdb_info(parsed_workbook:tuple["KeyValuePair", "WorksheetList"]):
    data = parsed_workbook[0]

    assert data["Source Information"] is None
    assert data["Database Name"] == exp.GEODATABASE["name"]
    assert data["Workspace Type"] == "Local Database"
    assert data["Remote Server"] is None
    assert data["Summary"] == exp.GEODATABASE["meta_summary"]
    assert data["Relationship Class Index"] is None


def test_building_inspections_key_value_pairs(parsed_workbook:tuple["KeyValuePair", "WorksheetList"]):
    data = parsed_workbook[1][0]["key_value_pairs"]
    name = "Building_Inspections"
    expected = exp.REL_CLS[name]

    assert data["Name"] == name
    assert data["Schema"] == expected["schema"]
    assert data["Feature Dataset"] == expected["feature_dataset"]
    assert data["Summary"] == expected["meta_summary"]
    assert data["Relationship Type"] == "Composite"
    assert data["Origin Table"] == expected["origin_table"]
    assert data["Destination Table"] == expected["destination_table"]
    assert data["Forward Label"] == expected["forward_label"]
    assert data["Backward Label"] == expected["backward_label"]
    assert data["Origin Primary Key"] == expected["origin_primary_key"]
    assert data["Origin Foreign Key"] == expected["origin_foreign_key"]
    assert data["Destination Primary Key"] == expected["destination_primary_key"]
    assert data["Destination Foreign Key"] == expected["destination_foreign_key"]
    assert data["Notifications"] == "Forward"
    assert data["Cardinality"] == "One To Many"
    assert data["Is Attributed"] == "no"
    assert data["64-bit OID"] == "no"
    assert data["Is Archived"] == "no"
    assert data["Is Versioned"] == "no"
    assert data["DSID"] == expected["dsid"]


def test_building_inspections_tables(parsed_workbook:tuple["KeyValuePair", "WorksheetList"]):
    assert len(parsed_workbook[1][0]["tables"]) == 0


def test_rivers_and_lakes_key_value_pairs(parsed_workbook:tuple["KeyValuePair", "WorksheetList"]):
    data = parsed_workbook[1][1]["key_value_pairs"]
    name = "Rivers_and_Lakes"
    expected = exp.REL_CLS[name]

    assert data["Name"] == name
    assert data["Schema"] == expected["schema"]
    assert data["Feature Dataset"] == expected["feature_dataset"]
    assert data["Summary"] == expected["meta_summary"]
    assert data["Relationship Type"] == "Simple"
    assert data["Origin Table"] == expected["origin_table"]
    assert data["Destination Table"] == expected["destination_table"]
    assert data["Forward Label"] == expected["forward_label"]
    assert data["Backward Label"] == expected["backward_label"]
    assert data["Origin Primary Key"] == expected["origin_primary_key"]
    assert data["Origin Foreign Key"] == expected["origin_foreign_key"]
    assert data["Destination Primary Key"] == expected["destination_primary_key"]
    assert data["Destination Foreign Key"] == expected["destination_foreign_key"]
    assert data["Notifications"] == "None"
    assert data["Cardinality"] == "One To Many"
    assert data["Is Attributed"] == "yes"
    assert data["64-bit OID"] == "no"
    assert data["Is Archived"] == "no"
    assert data["Is Versioned"] == "no"
    assert data["DSID"] == expected["dsid"]


def test_rivers_and_lakes_tables(parsed_workbook:tuple["KeyValuePair", "WorksheetList"]):
    assert len(parsed_workbook[1][1]["tables"]) == 1

    fields = parsed_workbook[1][1]["tables"]["Fields"]
    assert fields[0] == {
        "Field Name": "RiverID",
        "Field Type": "Long Integer",
        "Summary": None,
        "Alias Name": "RiverID",
        "Domain Name": None,
        "Default Value": None,
        "Is Nullable": "yes",
        "Length": None,
        "Precision": 0,
        "Scale": None,
        "Order": 1,
    }

    assert fields[1] == {
        "Field Name": "LakesRiverID",
        "Field Type": "Long Integer",
        "Summary": None,
        "Alias Name": "LakesRiverID",
        "Domain Name": None,
        "Default Value": None,
        "Is Nullable": "yes",
        "Length": None,
        "Precision": 0,
        "Scale": None,
        "Order": 2,
    }

    assert fields[2] == {
        "Field Name": "RID",
        "Field Type": "OBJECTID",
        "Summary": None,
        "Alias Name": "RID",
        "Domain Name": None,
        "Default Value": None,
        "Is Nullable": "no",
        "Length": None,
        "Precision": None,
        "Scale": None,
        "Order": 3,
    }

    assert fields[3] == {
        "Field Name": "FlowDirection",
        "Field Type": "Text",
        "Summary": "Whether the river flows into or out of the lake (or both).",
        "Alias Name": "Flow Direction",
        "Domain Name": "Lake River Flow",
        "Default Value": None,
        "Is Nullable": "yes",
        "Length": 4,
        "Precision": None,
        "Scale": None,
        "Order": 4,
    }