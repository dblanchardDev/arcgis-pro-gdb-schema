"""
Excel writer for the domains workbook.

Author: David Blanchard
"""

from typing import Union

from .. import cellar
from ..excel_converter import xl2st
from .gdb_writer import GDBWriter
from .table_writers import DomainCodesWriter, DomainUsersWriter, make_value_options


CellValues = Union[str, float, int]


class DomainsWriter(GDBWriter):
    """Excel writer component used specifically for the domains workbook.

    Args:
        workbook_path (str): Path where the XLSX file will be written, including the extension.
        database_name (str): Name of the geodatabase.
        workspace_type (str, optional): Type of workspace (local or remote). Defaults to None.
        remote_server (str, optional): Address/name of the geodatabase if any. Defaults to None.
        summary (str, optional): Metadata summary about the geodatabase. Defaults to None.
        template_visible (bool, optional): Whether the template sheets (used to create new datasets/domains from
          scratch) are visible.
    """

    element_type = "domain"
    _dropdown_field_type:cellar.CellDropdown = None
    _dropdown_domain_type:cellar.CellDropdown = None
    _dropdown_split_policy:cellar.CellDropdown = None
    _dropdown_merge_policy:cellar.CellDropdown = None
    _column_widths:list[int] = [25, 25, 80]


    def _prepare_dropdowns(self):
        """Create the dropdowns for re-use throughout the workbook."""

        self._dropdown_field_type = cellar.CellDropdown(
            workbook=self.workbook,
            values=xl2st.domain_field_types.keys(),
            label="field type",
        )

        self._dropdown_domain_type = cellar.CellDropdown(
            workbook=self.workbook,
            values=xl2st.domain_types.keys(),
            label="domain type",
        )

        self._dropdown_split_policy = cellar.CellDropdown(
            workbook=self.workbook,
            values=xl2st.split_policies.keys(),
            label="split policy",
        )

        self._dropdown_merge_policy = cellar.CellDropdown(
            workbook=self.workbook,
            values=xl2st.merge_policies.keys(),
            label="merge policy",
        )


    def _create_template(self, visible:bool=False):
        super()._create_template(visible)

        # Populate with empty data
        self.populate_base_info(self.TEMPLATE_TITLE)
        self.populate_range_info(self.TEMPLATE_TITLE)

        code_writer = self.code_adder(self.TEMPLATE_TITLE)
        with code_writer:
            for idx in range(40):
                del idx
                code_writer.add_entry(None)

        domain_user_writer = self.domain_user_adder(self.TEMPLATE_TITLE)
        with domain_user_writer:
            for idx in range(2):
                del idx
                domain_user_writer.add_entry(None)


    def populate_base_info(self, domain_name:str, schema:str=None, description:str=None, field_type:str=None,
                           domain_type:str=None, split_policy:str=None, merge_policy:str=None):
        """Populate the base information about the domain.

        Args:
            domain_name (str): Domain's base name.
            schema (str, optional): Schema to which the domain belongs. Defaults to None.
            description (str, optional): Summary describing the purpose of the domain. Defaults to None.
            field_type (str, optional): Type of data for the field to which the domain belongs.
            domain_type (str, optional): Whether the domain is range or coded value.
            split_policy (str, optional): Strategy used when splitting a record that uses this domain.
            merge_policy (str, optional): Strategy used when merging two records that use this domain.
        """

        cw = self.cw_lookup[domain_name]

        if domain_name == self.TEMPLATE_TITLE:
            domain_name = None

        coordinates = cw.write_block(value_block=[
            [
                # empty row
            ], [
                "Name",
                (domain_name, cellar.CELL_RULE_TEXT_MIN_3),
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Schema",
                schema,
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Description",
                (description, cellar.CELL_OPTS_WRAP),
                cellar.MERGE_CELL_WITH_LEFT,
            ],
        ], default_cell_options=[
            cellar.CELL_OPTS_KEY,
            cellar.CELL_OPTS_TEXT,
        ])

        row_with_description = coordinates[1][0]
        cw.increase_basic_height(row_with_description, factor=2)

        cw.write_block(value_block=[
            [
                "Field Type",
                (field_type, cellar.CELL_RULE_NOT_BLANK, self._dropdown_field_type),
            ], [
                "Domain Type",
                (domain_type, cellar.CELL_RULE_NOT_BLANK, self._dropdown_domain_type),
            ], [
                "Split Policy",
                (split_policy, self._dropdown_split_policy),
            ], [
                "Merge Policy",
                (merge_policy, self._dropdown_merge_policy),
            ],
        ], default_cell_options=[
            cellar.CELL_OPTS_KEY,
            cellar.CELL_OPTS_TEXT,
        ])


    def populate_range_info(self, domain_name:str, minimum:CellValues=None, maximum:CellValues=None):
        """Populate the minimum and maximum of a range domain.

        Args:
            domain_name (str): Domain's base name.
            minimum (Union[str, int, float], optional): Minimum value in the range. Defaults to None.
            maximum (Union[str, int, float], optional): Maximum value in the range. Defaults to None.
        """

        cw = self.cw_lookup[domain_name]

        # Headings
        cw.write_cell(None)
        cw.write_cell("Range Values", cellar.CELL_OPTS_HEADING)

        # Minimum and Maximum
        cw.write_block(value_block=[
            [
                "Minimum",
                (minimum, make_value_options(minimum), cellar.CELL_RULE_NOT_BLANK),
            ], [
                "Maximum",
                (maximum, make_value_options(maximum), cellar.CELL_RULE_NOT_BLANK),
            ],
        ], default_cell_options=[
            cellar.CELL_OPTS_KEY,
            cellar.CELL_OPTS_TEXT,
        ])


    def code_adder(self, domain_name:str) -> DomainCodesWriter:
        """Returns an instance of DomainCodesWriter initialized for a particular sheet.

        Args:
            domain_name (str): Name of the domain to which codes are to be added.

        Returns:
            DomainCodesWriter: Domain Codes Writer initialized for that domain.
        """

        return DomainCodesWriter(
            workbook=self.workbook,
            cw=self.cw_lookup[domain_name],
            get_cross_workbook_name=self.get_cross_workbook_name,
            get_cross_workbook_sheet_name=self.get_cross_workbook_sheet_name,
        )


    def domain_user_adder(self, base_name:str) -> DomainUsersWriter:
        """Returns an instance of DomainUserWriter initialized for a particular domain.

        Args:
            base_name (str): Base name of the domain.

        Returns:
            DomainUsersWriter: Domain User writer initialized for that domain.
        """
        return DomainUsersWriter(
            workbook=self.workbook,
            cw=self.cw_lookup[base_name],
            get_cross_workbook_name=self.get_cross_workbook_name,
            get_cross_workbook_sheet_name=self.get_cross_workbook_sheet_name,
        )