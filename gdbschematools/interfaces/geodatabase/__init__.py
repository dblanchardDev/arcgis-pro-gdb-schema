"""
Reader / Writer for File and Enterprise Geodatabases from ArcGIS.

Author: David Blanchard
"""

from typing import TYPE_CHECKING

from .gdb_reader import parse_full_geodatabase
from .gdb_writer import write_full_geodatabase
from .gdb_update_metadata import gdb_update_metadata
from .gdb_compare import compare_two_geodatabases
from ..interface import BaseInterface

if TYPE_CHECKING:
    from gdbschematools.structures import Geodatabase


#pylint: disable-next=abstract-method
class GeodatabaseInterface(BaseInterface):
    """Reader / Writer for File and Enterprise Geodatabases from ArcGIS."""


    @classmethod
    def read(cls, source:str) -> "Geodatabase":
        """Read the schema of a geodatabase.

        Args:
            source (str): Path to the file geodatabase or enterprise geodatabase connection file.

        Returns:
            Geodatabase: Geodatabase object abstracting the structure of the source.
        """
        return parse_full_geodatabase(source)


    @classmethod
    def write(cls, gdb_struct:"Geodatabase", path_to_gdb:str, skip_existings:bool=False): #pylint: disable=arguments-differ
        """Write the full geodatabase structure to a file or enterprise geodatabase from an existing geodatabase structure.

        Args:
            path_to_gdb (str): Path to the file or enterprise geodatabase. Should be empty.
            gdb_struct (Geodatabase): Geodatabase structure instance from which the gdb is to be populated.
            skip_existings (bool, optional): Whether to skip creating existing features including domain, featureclass, table, relationshipclass.
            Defaults to False.
        """ #pylint: disable=line-too-long
        return write_full_geodatabase(path_to_gdb, gdb_struct, skip_existings)

    @classmethod
    def update_metadata(cls, gdb_struct:"Geodatabase", path_to_gdb:str): #pylint: disable=arguments-differ
        """Update an existing geodatabase and its objects with the metadata from another entity.

        Args:
            path_to_gdb (str): Path to the file or enterprise geodatabase. Should be empty.
            gdb_struct (Geodatabase): Geodatabase structure instance from which the gdb is to be populated.
        """ #pylint: disable=line-too-long
        return gdb_update_metadata(path_to_gdb, gdb_struct)

    @classmethod
    def compare(cls, origin_gdb_struct:"Geodatabase", other_gdb_struct:"Geodatabase", output_dir:str) -> list:
        """Compares two Geodatabase structures.

        Args:
            origin_gdb_struct (Geodatabase): Geodatabase structure instance.
            other_gdb_struct (Geodatabase): Other Geodatabase structure to compare with the origin Geodatabase structure.
            output_dir (str): Directory in which the diff file will be written.
        Returns:
            list: a list of differences between two Geodatabase structures.
        """
        return compare_two_geodatabases(origin_gdb_struct, other_gdb_struct, output_dir)
