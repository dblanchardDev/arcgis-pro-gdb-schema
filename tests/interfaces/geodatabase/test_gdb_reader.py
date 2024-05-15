"""Unit tests for the base Geodatabase Interface class."""
#pylint: disable=protected-access,redefined-outer-name,missing-function-docstring

import os
import zipfile

import pytest

from gdbschematools.interfaces import GeodatabaseInterface
from gdbschematools.structures import Geodatabase
from tests.interfaces.data import gdbschematool_gdb_expected as exp
from tests.interfaces.data.check_structures import StructureTests


class TestReaderStructureTests(StructureTests):
    """Test the geodatabase reader, ensuring the output in the Geodatabase structure is the same as expected."""


    @pytest.fixture(scope="module")
    def geodatabase(self, tmpdir_factory) -> Geodatabase:
        # Derive path to zip file containing test geodatabase
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        gdb_zip = os.path.join(root_dir, "data/GDBSchemaTool.gdb.zip")

        # Extract zip file
        tmp_path = tmpdir_factory.mktemp("file_gdb_extract")

        with zipfile.ZipFile(gdb_zip, "r") as zip_file:
            zip_file.extractall(tmp_path)

        # Read the data into a Geodatabase structure
        file_gdb_path = os.path.join(tmp_path, "GDBSchemaTool.gdb")
        return GeodatabaseInterface.read(file_gdb_path)


    #region Geodatabase

    def test_geodatabase_properties(self, geodatabase:"Geodatabase"):
        expected = exp.GEODATABASE
        assert geodatabase.name == expected["name"]
        assert geodatabase.meta_summary == expected["meta_summary"]
        assert geodatabase.workspace_type == expected["workspace_type"]

    #endregion
    #region Datasets

    @pytest.mark.parametrize("table_name", list(exp.TABLES.keys()))
    def test_table_dsid(self, geodatabase:"Geodatabase", table_name):
        expected = exp.TABLES[table_name]
        table = geodatabase.datasets.tables[table_name]
        assert table.dsid == expected["dsid"]

    @pytest.mark.parametrize("feat_cl_name", list(exp.FEAT_CLS.keys()))
    def test_feature_class_dsid(self, geodatabase:"Geodatabase", feat_cl_name):
        expected = exp.FEAT_CLS[feat_cl_name]
        feat_cl = geodatabase.datasets.feature_classes[feat_cl_name]
        assert feat_cl.dsid == expected["dsid"]

    @pytest.mark.parametrize("rel_cl_name", list(exp.REL_CLS.keys()))
    def test_relationship_class_dsid(self, geodatabase:"Geodatabase", rel_cl_name:str):
        expected = exp.REL_CLS[rel_cl_name]
        rel_cl = geodatabase.datasets.relationship_classes[rel_cl_name]
        assert rel_cl.dsid == expected["dsid"]

    #endregion