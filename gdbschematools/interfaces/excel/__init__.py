"""
Reader / Writer for Excel Spreadsheets.

Author: David Blanchard
"""

from typing import TYPE_CHECKING

from .excel_reader import ingest_excel
from .excel_writer import output_excel
from ..interface import BaseInterface

if TYPE_CHECKING:
    from gdbschematools.structures import Geodatabase


#pylint: disable-next=abstract-method
class ExcelInterface(BaseInterface):
    """Reader / Writer for Excel Spreadsheets."""

    @classmethod
    #pylint: disable=arguments-renamed
    def read(cls, datasets_source:str, domains_source:str=None, relationships_source:str=None) -> "Geodatabase":
        """Read a set of Excel workbooks into an internal Geodatabase structure.

        Args:
            datasets_source (str): Path to the workbook containing dataset schemas.
            domains_source (str, optional): Path to the workbook containing domain schemas. If not provided, datasets and relationships cannot use domains. Defaults to None.
            relationships_source (str, optional): Path to the workbook containing relationship class schemas. If not provided, datasets cannot participate in relationships. Defaults to None.

        Returns:
            Geodatabase: Geodatabase structure resulting from reading the workbooks.
        """ #pylint: disable=line-too-long

        return ingest_excel(datasets_source, domains_source, relationships_source)


    @classmethod
    #pylint: disable-next=arguments-differ
    def write(cls, gdb:"Geodatabase", output_dir:str, template_visible:bool=False,
              skip_unchanged_fields:bool=True) -> tuple[str]:
        """Write from an internal Geodatabase structure to a set of Excel Spreadsheets.

        Args:
            gdb (Geodatabase): Geodatabase structure from which the data output is to be produced.
            output_dir (str): Directory in which the spreadsheets are to be written.
            template_visible (bool, optional): Whether the template sheets (used to create new datasets/domains from
              scratch) are visible.
            skip_unchanged_fields (bool, optional): Whether to skip fields in the subtype that don't have a domain or
              default value set for the subtype.

        Returns:
            tuple(str): The 3 paths to which the spreadsheets were written (datasets, domains, relationships).
        """
        return output_excel(gdb, output_dir, template_visible, skip_unchanged_fields)