"""Unit tests for the updating of geodatabase metadata utilities."""
#pylint: disable=protected-access,redefined-outer-name,missing-function-docstring

import os
import zipfile
from typing import TYPE_CHECKING

import pytest

from gdbschematools.interfaces import GeodatabaseInterface, gdb_update_metadata
from gdbschematools.interfaces.geodatabase import gdb_metadata
from tests.interfaces.data import gdbschematool_gdb_expected as exp
from tests.interfaces.data.check_structures import StructureTests

if TYPE_CHECKING:
    from gdbschematools.structures import Geodatabase


class TestUpdateGDBMetadata(StructureTests):
    """Unit tests for the updating of geodatabase metadata utilities."""

    @pytest.fixture(scope="module")
    def geodatabase(self, tmpdir_factory) -> "Geodatabase":
        # Derive path to zip file containing test geodatabase
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        target_gdb_zip = os.path.join(root_dir, "data/GDBSchemaTool.gdb.zip")
        original_gdb_zip = os.path.join(root_dir, "data/GDBSchemaTool_MetadataToUpdate.gdb.zip")

        # Extract zip files
        tmp_path = tmpdir_factory.mktemp("file_gdb_extract")

        with zipfile.ZipFile(target_gdb_zip, "r") as zip_file:
            zip_file.extractall(tmp_path)
        target_file_gdb_path = os.path.join(tmp_path, "GDBSchemaTool.gdb")

        with zipfile.ZipFile(original_gdb_zip, "r") as zip_file:
            zip_file.extractall(tmp_path)
        original_file_gdb_path = os.path.join(tmp_path, "GDBSchemaTool_MetadataToUpdate.gdb")

        # Generate the target geodatabase structure
        target_structure = GeodatabaseInterface.read(target_file_gdb_path)

        # Update the geodatabase
        gdb_update_metadata(original_file_gdb_path, target_structure)

        # Read-in the schema of the update geodatabase and return that structure
        gdb_metadata.clear_caches()
        final_gdb_structure = GeodatabaseInterface.read(original_file_gdb_path)
        return final_gdb_structure


    def test_geodatabase_properties(self, geodatabase:"Geodatabase"):
        expected = exp.GEODATABASE
        assert geodatabase.meta_summary == expected["meta_summary"]