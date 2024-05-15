"""
Excel writer components that are specific to producing the info/index.

Author: David Blanchard
"""

from typing import TYPE_CHECKING

from .. import cellar
from ..cellar import CellWriter
from ..excel_converter import xl2st

if TYPE_CHECKING:
    from openpyxl.worksheet.worksheet import Worksheet
    from openpyxl.workbook.workbook import Workbook


class InfoSheet:
    """Writer and handler for the info/index worksheet.

    Args:
        workbook (Workbook): Reference to the workbook that will contain the info sheet.
        worksheet (Worksheet): Reference to the worksheet to which the info is to be written.
        label (str): Label identifying the type of element this workbook contains.
        database_name (str): Name of the geodatabase.
        workspace_type (str, optional): Type of workspace (local or remote). Defaults to None.
        remote_server (str, optional): Address/name of the geodatabase if any. Defaults to None.
        summary (str, optional): Metadata summary about the geodatabase. Defaults to None.
    """

    cw:CellWriter = None
    _table_top_row:int = None
    _table_bottom_row:int = None
    _dropdown_workspace_type:cellar.CellDropdown = None


    def __init__(self, workbook:"Workbook", worksheet:"Worksheet", label:str, database_name:str,
                 workspace_type:str=None, remote_server:str=None, summary:str=None):
        # Create the Cell Writer that will handle writing to sheet
        self.cw = CellWriter(worksheet)

        # Set the sheet's name and dimensions
        self.cw.worksheet.title = "_INFO_"
        self.cw.set_widths([30, 60])

        # Prepare the dropdowns
        self._prepare_dropdowns(workbook)

        # Populate initial information
        self._populate_source_info(database_name, workspace_type, remote_server, summary)
        self._populate_index_headings(label)


    def _prepare_dropdowns(self, workbook:"Workbook"):
        """Create the dropdowns for re-use throughout the workbook."""

        self._dropdown_workspace_type = cellar.CellDropdown(
            workbook=workbook,
            values=xl2st.workspace_types.keys(),
            label="workspace type",
        )


    def _populate_source_info(self, database_name:str, workspace_type:str=None, remote_server:str=None,
                              summary:str=None):
        """Populate the information about the source geodatabase.

        Args:
            database_name (str): Name of the geodatabase.
            workspace_type (str, optional): Type of workspace (local or remote). Defaults to None.
            remote_server (str, optional): Address/name of the geodatabase if any. Defaults to None.
            summary (str, optional): Metadata summary about the geodatabase. Defaults to None.
        """

        self.cw.write_cell("Source Information", cellar.CELL_OPTS_HEADING)

        coordinates = self.cw.write_block(value_block=[
            [
                "Database Name",
                database_name,
            ], [
                "Workspace Type",
                (workspace_type, self._dropdown_workspace_type),
            ], [
                "Remote Server",
                remote_server,
            ], [
                "Summary",
                (summary, cellar.CELL_OPTS_WRAP),
            ],
        ], default_cell_options=[
            cellar.CELL_OPTS_KEY,
            cellar.CELL_OPTS_TEXT,
        ])

        # Increase heigh of summary line
        row_with_summary = coordinates[1][0]
        self.cw.increase_basic_height(row_with_summary, factor=2)


    def _populate_index_headings(self, label:str):
        """Create the heading and table header for the index.

        Args:
            label (str): Label identifying the type of element this workbook contains.
        """

        # Heading
        self.cw.write_cell(None)
        self.cw.write_cell(f"{label.title()} Index", cellar.CELL_OPTS_HEADING)

        # Start of table
        coordinate = self.cw.write_cell("Name", cellar.CELL_OPTS_TEXT)
        self._table_top_row = self._table_bottom_row = coordinate[0]


    def add_index_entry(self, label:str, sheet_name:str) -> int:
        """Add a new sheet entry to the index.

        Args:
            label (str): Text to be displayed in the index.
            sheet_name (str): Name of the sheet to be linked.

        Returns:
            int: Row number where the index entry was added.
        """

        cell_options = cellar.make_link_options(sheet_name=sheet_name)
        coordinate = self.cw.write_cell(label, cell_options)
        self._table_bottom_row = coordinate[0]
        return coordinate[0]


    def create_index_table(self):
        """Finish up the index by making it a table."""

        if self._table_top_row == self._table_bottom_row:
            self._table_bottom_row += 1

        self.cw.make_table(
            top_row=self._table_top_row,
            bot_row=self._table_bottom_row,
            left_col=1,
            right_col=1,
            name="Index"
        )