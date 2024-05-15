"""
Excel writer component that is used as the base for all other geodatabase element sheet writers.

Author: David Blanchard
"""

import os
import re

import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

from .. import cellar
from .table_writers import FieldWriter, SubtypeWriter
from .info_sheet import InfoSheet
from .theme import THEME_XML


CellWriterLookup = dict[str, cellar.CellWriter]


class GDBWriter:
    """Excel writer component that is used as the base for all other geodatabase element sheet writers.

    Args:
        workbook_path (str): Path where the XLSX file will be written, including the extension.
        database_name (str): Name of the geodatabase.
        workspace_type (str, optional): Type of workspace (local or remote). Defaults to None.
        remote_server (str, optional): Address/name of the geodatabase if any. Defaults to None.
        summary (str, optional): Metadata summary about the geodatabase. Defaults to None.
        template_visible (bool, optional): Whether the template sheets (used to create new datasets/domains from
          scratch) are visible.
    """

    TEMPLATE_TITLE:str = "_template_"

    workbook_path:str = None
    element_type:str = None
    workbook:openpyxl.Workbook = None
    info_sheet:InfoSheet = None
    sheet_names:list[str] = None
    cw_lookup:CellWriterLookup = None
    cross_workbook_paths:dict[str, str] = None
    cross_workbook_lookups:dict[str, CellWriterLookup] = None
    _column_widths:list[int] = None


    def __init__(self, workbook_path:str, database_name:str, workspace_type:str=None,
                 remote_server:str=None, summary:str=None, template_visible:bool=False) -> None:

        if self.element_type is None:
            raise ValueError("The element type must be set by children of this class before initializing.")

        self.workbook_path = workbook_path
        self.sheet_names = []
        self.cw_lookup = {}

        # Create workbook and initialize info-sheet
        self.workbook = self._create_workbook()
        self.info_sheet = InfoSheet(self.workbook, self.workbook.active, self.element_type, database_name,
                                    workspace_type, remote_server, summary)

        # Run optional methods
        self._prepare_dropdowns()
        self._create_template(template_visible)


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()


    def _create_workbook(self) -> openpyxl.Workbook:
        """Create a workbook with default styles and variables set.

        Returns:
            openpyxl.Workbook: Workbook that has been created.
        """

        # Set default font
        openpyxl.styles.DEFAULT_FONT.name = "Arial"
        openpyxl.styles.DEFAULT_FONT.size = 10

        # Open and return workbook
        workbook = openpyxl.Workbook(iso_dates=True)

        # Setting Arial default font doesn't work, modification of theme XML required
        workbook.loaded_theme = THEME_XML

        return workbook


    def close(self):
        """Close and save the workbook. Further edits cannot be saved."""
        if os.path.exists(self.workbook_path):
            raise FileExistsError(f"Failed to close and save workbook as a file already exists: {self.workbook_path}.")

        self.info_sheet.create_index_table()
        self.workbook.save(self.workbook_path)


    def _prepare_dropdowns(self):
        """Create the dropdowns for re-use throughout the workbook."""
        # Stub for abstraction


    def _create_template(self, visible:bool=False):
        """Create a template sheet which can be duplicated to create new datasets/domains.

        Args:
            visible (bool, optional): Whether this sheet will be visible by default. Defaults to False.
        """
        # Create template worksheet
        cw = self.prepare_sheet(self.TEMPLATE_TITLE)

        if not visible:
            cw.worksheet.sheet_state = Worksheet.SHEETSTATE_HIDDEN


    def prepare_sheet(self, base_name:str, alias:str=None) -> cellar.CellWriter:
        """Prepare a geodatabase element worksheet. Must be completed before populating a sheet.

        Args:
            base_name (str): Base name by which the element is uniquely known.
            alias (str, optional): Human readable name by which this element is known. Defaults to None.

        Returns:
            cellar.CellWriter: The cell writer for the prepared sheet.
        """
        label = alias or base_name

        # Derive a name for the sheet, ensuring no duplicates
        sheet_name = re.sub(r"[^\w\d _-]", "_", label[:31])

        if sheet_name in self.sheet_names:
            clipped_name = sheet_name[:-2]
            matches = [name for name in self.sheet_names if name.startswith(clipped_name)]
            count_tag = str(len(matches)).zfill(2)
            sheet_name = f"{clipped_name}{count_tag}"

        self.sheet_names.append(sheet_name)

        # Create the sheet
        worksheet:"Worksheet" = self.workbook.create_sheet(sheet_name)
        cw = cellar.CellWriter(worksheet)
        self.cw_lookup[base_name] = cw

        # Add sheet to index, and backlink to index
        index_row = 1
        if not sheet_name == self.TEMPLATE_TITLE:
            index_row = self.info_sheet.add_index_entry(label, sheet_name)

        go_to_index_options = cellar.make_link_options(sheet_name="_INFO_", cell=f"A{index_row}")
        cw.write_cell("Go to Index", go_to_index_options)

        # Set column widths if set in children classes
        if self._column_widths:
            cw.set_widths(self._column_widths)

        return cw


    def register_cross_book_lookups(self, datasets_path:str, datasets_lookup:CellWriterLookup, domains_path:str,
                                    domains_lookup:CellWriterLookup, relationships_path:str,
                                    relationships_lookup:CellWriterLookup):
        """Set the cross-workbook sheet name lookups. Must be set after preparing all the sheets, but before populating them in order for cross-workbook links to work.

        Args:
            datasets_path (str): Path to the datasets worksheet.
            datasets_lookup (CellWriterLookup): Cell Writer Lookup dictionary for datasets.
            domains_path (str): Path to the domains worksheet.
            domains_lookup (CellWriterLookup): Cell Writer Lookup dictionary for domains.
            relationships_path (str): Path to the relationships worksheet.
            relationships_lookup (CellWriterLookup): Cell Writer Lookup dictionary for relationship classes.
        """ #pylint: disable=line-too-long

        if self.cross_workbook_lookups is not None:
            raise ValueError("Cannot set cross-book lookups twice.")

        self.cross_workbook_paths = {
            "datasets": datasets_path,
            "domains": domains_path,
            "relationships": relationships_path,
        }

        self.cross_workbook_lookups = {
            "datasets": datasets_lookup,
            "domains": domains_lookup,
            "relationships": relationships_lookup,
        }


    def get_cross_workbook_name(self, workbook_type:str) -> str:
        """Use the cross-workbook lookups to get the name of another workbook.

        Args:
            workbook_type (str): Type of data this other workbook contains ("datasets", "domains", "relationships").

        Returns:
            str: Name of the workbook including the extension.
        """
        return os.path.basename(self.cross_workbook_paths[workbook_type])


    def get_cross_workbook_sheet_name(self, workbook_type:str, base_name:str) -> str:
        """Use the cross-workbook lookups to find a sheet name in another workbook.

        Args:
            workbook_type (str): Type of data this other workbook contains ("datasets", "domains", "relationships").
            base_name (str): Base name of the dataset, domain, or relationship.

        Returns:
            str: Sheet name or None if not found.
        """
        cw = self.cross_workbook_lookups[workbook_type].get(base_name, None)
        return cw.worksheet.title if cw else None


# pylint: disable=abstract-method
class GDBWriterWithFields(GDBWriter):
    """Excel writer component that is used as the base for all other geodatabase element sheet writers. In addition to the methods available in GDBWriter, it has methods for field and subtype creators.

    Args:
        workbook_path (str): Path where the XLSX file will be written, including the extension.
        database_name (str): Name of the geodatabase.
        workspace_type (str, optional): Type of workspace (local or remote). Defaults to None.
        remote_server (str, optional): Address/name of the geodatabase if any. Defaults to None.
        summary (str, optional): Metadata summary about the geodatabase. Defaults to None.
        template_visible (bool, optional): Whether the template sheets (used to create new datasets/domains from
          scratch) are visible.
    """ #pylint: disable=line-too-long


    def field_adder(self, base_name:str) -> FieldWriter:
        """Returns an instance of FieldWriter initialized for a particular dataset.

        Args:
            base_name (str): Base name of the feature class, table, or relationship class.

        Returns:
            FieldWriter: Field writer initialized for that dataset.
        """
        return FieldWriter(
            workbook=self.workbook,
            cw=self.cw_lookup[base_name],
            get_cross_workbook_name=self.get_cross_workbook_name,
            get_cross_workbook_sheet_name=self.get_cross_workbook_sheet_name,
        )


    def subtype_adder(self, base_name:str, subtype_field_name:str,
                      fields_table_coordinates:list[list[int]]=None) -> SubtypeWriter:
        """Returns an instance of SubtypeWriter initialized for a particular dataset.

        Args:
            base_name (str): Base name of the feature class, table, or relationship class.
            subtype_field_name (str): Name of the field to which the subtype is applied.
            fields_table_coordinates (list[list[int]], optional): Coordinates for the fields table allowing for cross validation. If not provided, cross-validation will not be applied.

        Returns:
            SubtypeWriter: Subtype writer initialized for that dataset.
        """ #pylint: disable=line-too-long
        return SubtypeWriter(
            workbook=self.workbook,
            cw=self.cw_lookup[base_name],
            get_cross_workbook_name=self.get_cross_workbook_name,
            get_cross_workbook_sheet_name=self.get_cross_workbook_sheet_name,
            subtype_field_name=subtype_field_name,
            fields_table_coordinates=fields_table_coordinates,
        )