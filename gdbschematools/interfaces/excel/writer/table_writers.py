"""
Excel writer components for making tables within another sheet (e.g. fields, subtypes, relationships).
"""

import inspect
import re
from typing import Callable, ClassVar, TYPE_CHECKING, Union

from openpyxl.utils import FORMULAE

from .. import cellar
from ..excel_converter import xl2st

if TYPE_CHECKING:
    from openpyxl import Workbook


CellValues = Union[str, float, int]


def make_table_name(sheet_name:str, suffix:str):
    """Make a name that can be used in an Excel table.

    Args:
        sheet_name (str): Name of sheet to which the table belongs.
        suffix (str): Suffix to describe the table.

    Returns:
        str: A table name safe for use in Excel.
    """
    # Create a name with only alpha-numeric characters and underscores
    clean_name = re.sub(r"[^\w\d_]", "_", sheet_name)
    clean_name = re.sub(r"_+", "_", clean_name)

    # Combine with the suffix
    return f"{clean_name}.{suffix}"


def make_domain_options(domain_name:str, get_cross_workbook_name:str,
                        get_cross_workbook_sheet_name:Callable) -> cellar.CellOptions:
    """Create a CellOption for a domain entry, with link to the corresponding domain sheet.

    Args:
        domain_name (str): Name of the domain.
        get_cross_workbook_name (Callable): Function to get the name of another workbook.
        get_cross_workbook_sheet_name (Callable): Function which returns the sheet name from another workbook.

    Returns:
        cellar.CellOption: A cell option with a link to the domain sheet.
    """
    # Decide on the cell option for the domain
    domain_options = cellar.CELL_OPTS_TEXT
    if domain_name is not None:
        workbook_name = get_cross_workbook_name("domains")
        sheet_name = get_cross_workbook_sheet_name("domains", domain_name)

        domain_options = cellar.make_link_options(
            workbook_name,
            sheet_name,
        )

    return domain_options


def make_value_options(value:CellValues) -> cellar.CellOptions:
    """Create a CellOption based on the type of data.

    Args:
        default_value (CellValues): Value that is to be checked for type.

    Returns:
        cellar.CellOption: A cell option that matches the type of the value.
    """
    # Decide on cell option for the default value
    default_options = cellar.CELL_OPTS_TEXT
    if isinstance(value, int):
        default_options = cellar.CELL_OPTS_INTEGER_LEFT
    elif isinstance(value, float):
        default_options = cellar.CELL_OPTS_FLOAT_LEFT

    return default_options


class TableWriter:

    """Write entries into a table to a particular sheet.

    Args:
        workbook (Workbook): Workbook to which the table will be written.
        cw (cellar.CellWriter): Cell writer to which the fields will be written.
        get_cross_workbook_name (Callable): Function to get the name of another workbook.
        get_cross_workbook_sheet_name (Callable): Function which returns the sheet name from another workbook.
    """

    workbook:"Workbook"  = None
    cw:cellar.CellWriter = None
    get_cross_workbook_name:Callable = None
    get_cross_workbook_sheet_name:Callable = None
    _table_top_row:int = None
    _table_bottom_row:int = None
    coordinates:list[list[int]] = None

    # To be overridden by children
    _heading:str = None
    _heading_cell_options:cellar.CellOptions = cellar.CELL_OPTS_HEADING
    _table_headers:list[str] = []
    _table_name_suffix:str = None


    def __init__(self, workbook:"Workbook", cw:cellar.CellWriter, get_cross_workbook_name:str,
                 get_cross_workbook_sheet_name:Callable):
        self.workbook = workbook
        self.cw = cw
        self.get_cross_workbook_name = get_cross_workbook_name
        self.get_cross_workbook_sheet_name = get_cross_workbook_sheet_name


    def __enter__(self) -> "TableWriter":
        self.start_table()
        return self


    def __exit__(self, exc_type, exc_value, exc_traceback):
        if not exc_type:
            self.finish_table()


    def start_table(self):
        """Output heading and table headers."""
        self.cw.write_cell(None)
        self.cw.write_cell(self._heading, self._heading_cell_options)

        coordinates = self.cw.write_block(
            value_block=[self._table_headers],
            default_cell_options=cellar.CELL_OPTS_TEXT
        )

        self._table_top_row = self._table_bottom_row = coordinates[1][0]


    def finish_table(self):
        """Transform the field list into a table."""

        # If no entries added, add an empty row (otherwise table is invalid)
        if self._table_top_row == self._table_bottom_row:
            arg_count = len(inspect.signature(self.add_entry).parameters)
            arguments = [None] * arg_count
            self.add_entry(*arguments)

        # Transform into a table
        self.cw.make_table(
            top_row=self._table_top_row,
            bot_row=self._table_bottom_row,
            left_col=1,
            right_col=len(self._table_headers),
            name=make_table_name(self.cw.worksheet.title, self._table_name_suffix),
        )

        self.coordinates = [[self._table_top_row, 1], [self._table_bottom_row, len(self._table_headers)]]


    def add_entry(self):
        """Add a new field to the field table. To be overridden by children."""
        raise NotImplementedError("Method add_entry must be overridden by its children.")


class FieldWriter(TableWriter):
    """Write fields to a particular sheet.

    Args:
        cw (cellar.CellWriter): Cell writer to which the fields will be written.
        get_cross_workbook_name (Callable): Function to get the name of another workbook.
        get_cross_workbook_sheet_name (Callable): Function which returns the sheet name from another workbook.
    """

    _field_type_dropdowns:ClassVar[dict["Workbook", cellar.CellDropdown]] = {}

    _heading:str = "Fields"
    _table_headers:list[str] = [
        "Field Name",
        "Field Type",
        "Summary",
        "Alias Name",
        "Domain Name",
        "Default Value",
        "Is Nullable",
        "Length",
        "Precision",
        "Scale",
        "Order",
    ]
    _table_name_suffix:str = "fields"

    _field_count = 0


    def __enter__(self) -> "FieldWriter":
        # To override the return type
        return super().__enter__()


    def finish_table(self):
        super().finish_table()
        self._apply_validation_to_table()
        self._add_dropdowns_to_table()


    def _apply_validation_to_table(self):
        """Apply conditional formatting rules and dropdowns to the fields table."""

        top_row = self._table_top_row + 1
        bot_row = self._table_bottom_row


        # FIELD NAME VALIDATION
        # Cannot be empty if anything else is populated in the row
        name_missing = f"AND(ISBLANK(A{top_row}), COUNTA(B{top_row}:J{top_row})>0)"
        self.cw.add_rule(cellar.CellRule(name_missing),
                               top_row=top_row, bot_row=bot_row, left_col=1, right_col=1)

        # Disallow duplicate field names
        self.cw.add_rule(cellar.CELL_RULE_NO_DUPLICATES,
                               top_row=top_row, bot_row=bot_row, left_col=1, right_col=1)

        # FIELD TYPE
        # Cannot be empty if field name populated
        type_missing = f"AND(ISBLANK(B{top_row}), NOT(ISBLANK(A{top_row})))"
        self.cw.add_rule(cellar.CellRule(type_missing),
                               top_row=top_row, bot_row=bot_row, left_col=2, right_col=2)

        # ALIAS
        # Disallow duplicate aliases
        self.cw.add_rule(cellar.CELL_RULE_NO_DUPLICATES,
                               top_row=top_row, bot_row=bot_row, left_col=4, right_col=4)

        # LENGTH, PRECISION, SCALE
        # Must or must not be populated depending on field type
        type_range = f"B{top_row}"

        length_formula = f'=IF(OR({type_range} = "Text"), ISBLANK(<coordinate>)=TRUE, ISBLANK(<coordinate>)=FALSE)'
        self.cw.add_rule(cellar.CellRule(length_formula),
                               top_row=top_row, bot_row=bot_row, left_col=8, right_col=8)

        precision_formula = f'=IF(OR({type_range} = "Big Integer", {type_range} = "Long Integer", {type_range} = "Short Integer", {type_range} = "Double", {type_range} = "Float"), ISBLANK(<coordinate>)=TRUE, ISBLANK(<coordinate>)=FALSE)' #pylint: disable=line-too-long
        self.cw.add_rule(cellar.CellRule(precision_formula),
                               top_row=top_row, bot_row=bot_row, left_col=9, right_col=9)

        scale_formula = f'=IF(OR({type_range} = "Double", {type_range} = "Float"), ISBLANK(<coordinate>)=TRUE, ISBLANK(<coordinate>)=FALSE)' #pylint: disable=line-too-long
        self.cw.add_rule(cellar.CellRule(scale_formula),
                               top_row=top_row, bot_row=bot_row, left_col=10, right_col=10)


    def _add_dropdowns_to_table(self):
        """Add the dropdowns that allow selection of valid values."""
        top_row = self._table_top_row + 1
        bot_row = self._table_bottom_row

        if self.workbook not in FieldWriter._field_type_dropdowns:
            FieldWriter._field_type_dropdowns[self.workbook] = cellar.CellDropdown(
                workbook=self.workbook,
                values=xl2st.field_types.keys(),
                label="field type",
            )

        # Field types
        self.cw.add_dropdown(dropdown=FieldWriter._field_type_dropdowns[self.workbook],
                             top_row=top_row, bot_row=bot_row, left_col=2, right_col=2)

        # Is Nullable
        self.cw.add_dropdown(dropdown=cellar.get_dropdown_boolean(self.workbook),
                             top_row=top_row, bot_row=bot_row, left_col=7, right_col=7)


    #pylint: disable-next=arguments-differ,too-many-arguments
    def add_entry(self, field_name:str, field_type:str=None, summary:str=None, alias:str=None, domain_name:str=None,
                  default_value:CellValues=None, is_nullable:str=None, length:int=None, precision:int=None,
                  scale:int=None, default_type:type=str):
        """Add a new field to the field table.

        Args:
            field_name (str): Base name given to the field
            field_type (str, optional): Type of field. Defaults to None.
            summary (str, optional): Metadata summary for the field. Defaults to None.
            alias (str, optional): Alternate name for the field. Defaults to None.
            domain_name (str, optional): Name of the domain assigned to the field if any. Defaults to None.
            default_value (Union[str, int, float], optional): Default value assigned to the field. Defaults to None.
            is_nullable (str, optional): Whether field is nullable. Defaults to None.
            length (int, optional): Length of the field for text. Defaults to None.
            precision (int, optional): Precision of the field for numbers. Defaults to None.
            scale (int, optional): Scale of the field for floats and doubles. Defaults to None.
            default_type (type, optional): The type of data which the default should contain (used if default value is None). Defaults to str.
        """ #pylint: disable=line-too-long

        domain_options = make_domain_options(domain_name, self.get_cross_workbook_name,
                                             self.get_cross_workbook_sheet_name)

        default_options = cellar.CELL_OPTS_TEXT
        if default_value is not None:
            default_options = make_value_options(default_value)
        else:
            if default_type is int:
                default_options = cellar.CELL_OPTS_INTEGER_LEFT
            elif default_type is float:
                default_options = cellar.CELL_OPTS_FLOAT_LEFT

        coordinates = self.cw.write_block(value_block=[
            [
                field_name,
                field_type,
                (summary, cellar.CELL_OPTS_WRAP),
                alias,
                (domain_name, domain_options),
                (default_value, default_options),
                is_nullable,
                (length, cellar.CELL_OPTS_INTEGER),
                (precision, cellar.CELL_OPTS_INTEGER),
                (scale, cellar.CELL_OPTS_INTEGER),
                (self._field_count + 1, cellar.CELL_OPTS_INTEGER),
            ],
        ], default_cell_options=cellar.CELL_OPTS_TEXT)

        self._table_bottom_row = coordinates[1][0]
        self._field_count += 1


class SubtypeWriter(TableWriter):
    """Write fields to a particular sheet.

    Args:
        workbook (Workbook): Workbook to which the table will be written.
        cw (cellar.CellWriter): Cell writer to which the fields will be written.
        get_cross_workbook_name (Callable): Function to get the name of another workbook.
        get_cross_workbook_sheet_name (Callable): Function which returns the sheet name from another workbook.
        subtype_field_name (str): Name of the field to which the subtype is applied.
        fields_table_coordinates (list[list[int]], optional): Coordinates for the fields table allowing for cross validation. If not provided, cross-validation will not be applied.
    """ #pylint: disable=line-too-long

    _heading:str = "Subtype Details"
    _heading_cell_options:cellar.CellOptions = cellar.CELL_OPTS_HEADING2
    _table_headers:list[str] = [
        "Subtype Name",
        "Code",
        "Description",
        "Field Name",
        "Domain Name",
        "Default Value",
    ]
    _table_name_suffix:str = "subtypes"

    _subtype_summary_printed:list[int] = None
    _fields_table_coordinates:list[list[int]] = None
    _subtype_field_name_row:int = None


    def __init__(self, workbook:"Workbook", cw:cellar.CellWriter, get_cross_workbook_name:Callable,
                 get_cross_workbook_sheet_name:Callable, subtype_field_name:str,
                 fields_table_coordinates:list[list[int]]=None):
        super().__init__(workbook, cw, get_cross_workbook_name, get_cross_workbook_sheet_name)

        self._subtype_summary_printed = []

        self.populate_base_info(subtype_field_name)
        self._fields_table_coordinates = fields_table_coordinates


    def __enter__(self) -> "SubtypeWriter":
        # To override the return type
        return super().__enter__()


    def populate_base_info(self, subtype_field_name:str):
        """Output heading and table headers."""
        self.cw.write_cell(None)
        self.cw.write_cell("Subtype", cellar.CELL_OPTS_HEADING)

        coordinates = self.cw.write_block(value_block=[
            [
                "Subtype Field Name",
                subtype_field_name,
            ],
        ], default_cell_options=[
            cellar.CELL_OPTS_KEY,
            cellar.CELL_OPTS_TEXT,
        ])

        self._subtype_field_name_row = coordinates[0][0]


    def finish_table(self):
        super().finish_table()
        self._apply_validation_to_table()


    def _apply_validation_to_table(self):
        """Apply conditional formatting rules and dropdowns to the fields table."""

        top_row = self._table_top_row + 1
        bot_row = self._table_bottom_row

        # XLOOKUP is new function and requires flag in some cases
        xlookup = "XLOOKUP"
        if xlookup not in FORMULAE:
            xlookup = f"_xlfn.{xlookup}"

        # SUBTYPE NAME
        # Name is missing when other fields are populated
        name_missing = f"AND(ISBLANK(A{top_row}), COUNTA(B{top_row}:F{top_row})>0)"
        self.cw.add_rule(cellar.CellRule(name_missing),
                               top_row=top_row, bot_row=bot_row, left_col=1, right_col=1)

        # Same name associated different codes
        subtype_diff_codes = f"NOT({xlookup}(A{top_row}, A${top_row}:A${bot_row}, B${top_row}:B${bot_row})=B{top_row})"
        self.cw.add_rule(cellar.CellRule(subtype_diff_codes),
                               top_row=top_row, bot_row=bot_row, left_col=1, right_col=1)

        # CODE
        # Code is missing when name is populated
        code_missing = f"AND(ISBLANK(B{top_row}), NOT(ISBLANK(A{top_row})))"
        self.cw.add_rule(cellar.CellRule(code_missing),
                               top_row=top_row, bot_row=bot_row, left_col=2, right_col=2)

        # Same code associated with different names
        subtype_diff_codes = f"NOT({xlookup}(B{top_row}, B${top_row}:B${bot_row}, A${top_row}:A${bot_row})=A{top_row})"
        self.cw.add_rule(cellar.CellRule(subtype_diff_codes),
                               top_row=top_row, bot_row=bot_row, left_col=2, right_col=2)

        # FIELD NAME
        # Field is missing when name is populated
        field_name_missing = f"AND(ISBLANK(D{top_row}),OR(NOT(ISBLANK(E{top_row})),NOT(ISBLANK(F{top_row}))))"
        self.cw.add_rule(cellar.CellRule(field_name_missing),
                               top_row=top_row, bot_row=bot_row, left_col=4, right_col=4)

        # Field is present multiple times with the same code
        reused_field_in_code = f"COUNTIFS(B${top_row}:B${bot_row}, B{top_row}, D${top_row}:D${bot_row}, D{top_row}) > 1"
        self.cw.add_rule(cellar.CellRule(reused_field_in_code),
                               top_row=top_row, bot_row=bot_row, left_col=4, right_col=4)

        # COMPARISONS TO FIELDS TABLE
        if self._fields_table_coordinates:
            # Ensure field name is present in the fields table
            # Note: Range intentionally set 1 row above and 1 below force range to expand when new rows are added
            top_fields_row = self._fields_table_coordinates[0][0]
            bot_fields_row = self._fields_table_coordinates[1][0]

            subtype_field_not_in_fields = f"OR(COUNTIF(A${top_fields_row}:A${bot_fields_row + 1}, <coordinate>) = 0, D{top_row} = A{top_fields_row})"
            self.cw.add_rule(cellar.CellRule(subtype_field_not_in_fields),
                             top_row=self._subtype_field_name_row, left_col=2)

            not_in_fields = f"AND(ISBLANK(D{top_row}) = FALSE, OR(COUNTIF(A${top_fields_row}:A${bot_fields_row + 1}, D{top_row}) = 0, D{top_row} = A{top_fields_row}))" #pylint: disable=line-too-long
            self.cw.add_rule(cellar.CellRule(not_in_fields),
                             top_row=top_row, bot_row=bot_row, left_col=4, right_col=4)


    #pylint: disable-next=arguments-differ
    def add_entry(self, subtype_name:str, subtype_code:int, summary:str=None, field_name:str=None,
                  domain_name:str=None, default_value:CellValues=None):
        """Add an entry to the subtype table.

        Args:
            subtype_name (str): Name of the subtype being added.
            subtype_code (int): Code corresponding to the subtype.
            summary (str, optional): Metadata summary for the subtype. Only printed the first time. Defaults to None.
            field_name (str, optional): Name of the field being modified, if any. Defaults to None.
            domain_name (str, optional): Name of the domain applied to the field. Defaults to None.
            default_value (CellValues, optional): Default value being applied to the field. Defaults to None.
        """

        summary_printout = None
        if subtype_code not in self._subtype_summary_printed:
            summary_printout = summary
            self._subtype_summary_printed.append(subtype_code)

        domain_options = make_domain_options(domain_name, self.get_cross_workbook_name,
                                             self.get_cross_workbook_sheet_name)
        default_options = make_value_options(default_value)

        coordinates = self.cw.write_block(value_block=[
            [
                subtype_name,
                subtype_code,
                summary_printout,
                field_name,
                (domain_name, domain_options),
                (default_value, default_options),
            ],
        ], default_cell_options=[
            cellar.CELL_OPTS_TEXT,
            cellar.CELL_OPTS_INTEGER_LEFT,
            cellar.CELL_OPTS_WRAP,
            cellar.CELL_OPTS_TEXT,
            cellar.CELL_OPTS_TEXT
        ])

        self._table_bottom_row = coordinates[1][0]


class InRelationshipsWriter(TableWriter):
    """Write the relationship classes in which a dataset participates to a particular sheet.

    Args:
        cw (cellar.CellWriter): Cell writer to which the fields will be written.
        get_cross_workbook_name (Callable): Function to get the name of another workbook.
        get_cross_workbook_sheet_name (Callable): Function which returns the sheet name from another workbook.
    """

    _heading:str = "Relationship Classes"
    _table_headers:list[str] = [
        "Name",
    ]
    _table_name_suffix:str = "relationships"


    def __enter__(self) -> "InRelationshipsWriter":
        # To override the return type
        return super().__enter__()


    #pylint: disable-next=arguments-differ,too-many-arguments
    def add_entry(self, relationship_name:str):
        """Add a new field to the field table.

        Args:
            relationship_name (str): Base name for the relationship class.
        """

        options = None

        if relationship_name is not None:
            workbook_name = self.get_cross_workbook_name("relationships")
            sheet_name = self.get_cross_workbook_sheet_name("relationships", relationship_name)
            options = cellar.make_link_options(
                workbook_name,
                sheet_name,
            )

        coordinate = self.cw.write_cell(relationship_name, options)

        self._table_bottom_row = coordinate[0]


class DomainCodesWriter(TableWriter):
    """Write the coded values that are part of a coded value domain.

    Args:
        cw (cellar.CellWriter): Cell writer to which the fields will be written.
        get_cross_workbook_name (Callable): Function to get the name of another workbook.
        get_cross_workbook_sheet_name (Callable): Function which returns the sheet name from another workbook.
    """

    _heading:str = "Coded Values"
    _table_headers:list[str] = [
        "Code",
        "Description",
        "Summary",
    ]
    _table_name_suffix:str = "codes"


    def __enter__(self) -> "DomainCodesWriter":
        # To override the return type
        return super().__enter__()


    def finish_table(self):
        super().finish_table()
        self._apply_validation_to_table()


    def _apply_validation_to_table(self):
        """Apply conditional formatting rules and dropdowns to the fields table."""

        top_row = self._table_top_row + 1
        bot_row = self._table_bottom_row

        # CODE
        # Code is missing when other fields are populated
        code_missing = f"AND(ISBLANK(A{top_row}), NOT(AND(ISBLANK(B{top_row}), ISBLANK(C{top_row}))))"
        self.cw.add_rule(cellar.CellRule(code_missing),
                               top_row=top_row, bot_row=bot_row, left_col=1, right_col=1)

        # Duplicate code (same code used twice)
        self.cw.add_rule(cellar.CELL_RULE_NO_DUPLICATES,
                               top_row=top_row, bot_row=bot_row, left_col=1, right_col=1)

        # DESCRIPTION
        desc_missing = f"AND(ISBLANK(B{top_row}), NOT(ISBLANK(A{top_row})))"
        self.cw.add_rule(cellar.CellRule(desc_missing),
                               top_row=top_row, bot_row=bot_row, left_col=2, right_col=2)

        # Duplicate description (same description used twice)
        self.cw.add_rule(cellar.CELL_RULE_NO_DUPLICATES,
                               top_row=top_row, bot_row=bot_row, left_col=2, right_col=2)


    #pylint: disable-next=arguments-differ
    def add_entry(self, code:CellValues, description:str=None, summary:str=None):
        """Add a coded value to the codes table.

        Args:
            code (Union[int, str, None]): The coded value.
            description (str, optional): The description of the coded value. Defaults to None.
            summary (str, optional): Metadata summary for the coded value. Defaults to None.
        """

        code_option = make_value_options(code)

        coordinates = self.cw.write_block(value_block=[
            [
                code,
                description,
                (summary, cellar.CELL_OPTS_WRAP),
            ],
        ], default_cell_options=[
            code_option,
            cellar.CELL_OPTS_TEXT,
            cellar.CELL_OPTS_TEXT,
        ])

        self._table_bottom_row = coordinates[1][0]


class DomainUsersWriter(TableWriter):
    """Write the feature classes, tables, and relationship classes to which a domain is assigned.

    Args:
        cw (cellar.CellWriter): Cell writer to which the fields will be written.
        get_cross_workbook_name (Callable): Function to get the name of another workbook.
        get_cross_workbook_sheet_name (Callable): Function which returns the sheet name from another workbook.
    """

    _heading:str = "Domain Users"
    _table_headers:list[str] = [
        "Name",
    ]
    _table_name_suffix:str = "users"


    def __enter__(self) -> "DomainUsersWriter":
        # To override the return type
        return super().__enter__()


    #pylint: disable-next=arguments-differ,too-many-arguments
    def add_entry(self, base_name:str):
        """Add a new field to the field table.

        Args:
            base_name (str): Base name for the feature class, table, or relationship class.
        """

        options = None

        if base_name is not None:
            workbook_name = self.get_cross_workbook_name("datasets")
            sheet_name = self.get_cross_workbook_sheet_name("datasets", base_name)

            if sheet_name is None:
                workbook_name = self.get_cross_workbook_name("relationships")
                sheet_name = self.get_cross_workbook_sheet_name("relationships", base_name)

            options = cellar.make_link_options(
                workbook_name,
                sheet_name,
            )

        coordinate = self.cw.write_cell(base_name, options)

        self._table_bottom_row = coordinate[0]