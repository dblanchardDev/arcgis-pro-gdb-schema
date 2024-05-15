"""Unit tests for the base Geodatabase Interface class."""
#pylint: disable=protected-access,redefined-outer-name,missing-function-docstring

import os
import zipfile
from typing import TYPE_CHECKING

from arcpy.management import CreateFileGDB
import pytest

from gdbschematools.interfaces import GeodatabaseInterface
from tests.interfaces.data import gdbschematool_gdb_expected as exp
from tests.interfaces.data.check_structures import StructureTests

if TYPE_CHECKING:
    from gdbschematools.structures import Geodatabase


class TestWriterStructureTests(StructureTests):
    """Test the geodatabase writer, ensuring the output in the Geodatabase is the same as expected."""


    @pytest.fixture(scope="module")
    def expected_gdb_structure(self, tmpdir_factory) -> "Geodatabase":
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


    @pytest.fixture(scope="module")
    def file_gdb_from_struct(self, expected_gdb_structure:"Geodatabase", tmpdir_factory) -> str:
        # Create path for output file geodatabase
        gdb_name = "WriterOutput"
        tmp_dir = str(tmpdir_factory.mktemp("file_gdb_output"))
        fgdb_path = os.path.join(tmp_dir, f"{gdb_name}.gdb")

        # Create empty file geodatabase
        CreateFileGDB(tmp_dir, gdb_name, "CURRENT")

        # Write the structure to the file geodatabase
        GeodatabaseInterface.write(expected_gdb_structure, fgdb_path)

        return fgdb_path


    @pytest.fixture(scope="module")
    def geodatabase(self, file_gdb_from_struct) -> "Geodatabase": #pylint: disable=arguments-renamed
        return GeodatabaseInterface.read(file_gdb_from_struct)


    #region Geodatabase

    def test_geodatabase_properties(self, geodatabase:"Geodatabase"):
        expected = exp.GEODATABASE
        assert geodatabase.meta_summary == expected["meta_summary"]

    #endregion