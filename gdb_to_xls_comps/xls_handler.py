"""
Class to simplify the handling of work with XLWT to create Excel spreasheets.

Author: David Blanchard

Version: 0.1
"""

import datetime
import math
import os
import re
from typing import Union

import xlwt


_STYLE_NONE = xlwt.Style.easyxf("")
_STYLE_BOLD = xlwt.Style.easyxf("font: bold on")
_HEADING_FONT_SIZE = 12
_STYLE_HEADING = xlwt.Style.easyxf(f"font: bold on, height {_HEADING_FONT_SIZE * 20}")
_STYLE_HYPERLINK = xlwt.Style.easyxf("font: underline single, color ocean_blue")


_CHARWIDTHS = {
    "0": 262.637,
    "1": 262.637,
    "2": 262.637,
    "3": 262.637,
    "4": 262.637,
    "5": 262.637,
    "6": 262.637,
    "7": 262.637,
    "8": 262.637,
    "9": 262.637,
    "a": 262.637,
    "b": 262.637,
    "c": 262.637,
    "d": 262.637,
    "e": 262.637,
    "f": 146.015,
    "g": 262.637,
    "h": 262.637,
    "i": 117.096,
    "j": 88.178,
    "k": 233.244,
    "l": 88.178,
    "m": 379.259,
    "n": 262.637,
    "o": 262.637,
    "p": 262.637,
    "q": 262.637,
    "r": 175.407,
    "s": 233.244,
    "t": 117.096,
    "u": 262.637,
    "v": 203.852,
    "w": 321.422,
    "x": 203.852,
    "y": 262.637,
    "z": 233.244,
    "A": 321.422,
    "B": 321.422,
    "C": 350.341,
    "D": 350.341,
    "E": 321.422,
    "F": 291.556,
    "G": 350.341,
    "H": 321.422,
    "I": 146.015,
    "J": 262.637,
    "K": 321.422,
    "L": 262.637,
    "M": 379.259,
    "N": 321.422,
    "O": 350.341,
    "P": 321.422,
    "Q": 350.341,
    "R": 321.422,
    "S": 321.422,
    "T": 262.637,
    "U": 321.422,
    "V": 321.422,
    "W": 496.356,
    "X": 321.422,
    "Y": 321.422,
    "Z": 262.637,
    " ": 146.015,
    "!": 146.015,
    "\"": 175.407,
    "#": 262.637,
    "$": 262.637,
    "%": 438.044,
    "&": 321.422,
    "'": 88.178,
    "(": 175.407,
    ")": 175.407,
    "*": 203.852,
    "+": 291.556,
    ",": 146.015,
    "-": 175.407,
    ".": 146.015,
    "/": 146.015,
    ":": 146.015,
    ";": 146.015,
    "<": 291.556,
    "=": 291.556,
    ">": 291.556,
    "?": 262.637,
    "@": 496.356,
    "[": 146.015,
    "\\": 146.015,
    "]": 146.015,
    "^": 203.852,
    "_": 262.637,
    "`": 175.407,
    "{": 175.407,
    "|": 146.015,
    "}": 175.407,
    "~": 291.556,
}

_MIN_COL_WIDTH = _CHARWIDTHS["|"]
_MAX_COL_WIDTH = 65535


def adjust_width(width:Union[int, None])->Union[int, None]:
    """Convert a normal excel width into a BIFF width.

    Args:
        width (int|None): The standard excel width number.

    Returns:
        int|None: A BIFF width.
    """
    if width is None:
        return width

    adjusted_width = round(_CHARWIDTHS["0"] * width) * 1.1
    return min([adjusted_width, _MAX_COL_WIDTH])


class Sheet:
    """A single sheet within a workbook.

    Args:
        workbook (object): The workbook to which a sheet is to be added.
        sheetname (str): The name of the sheet.
        col_max_widths (list[int]): The maximum width of each column, from left to right. Provide None for columns to be autoset. Default is to autoset all columns.
    """

    _sheet:xlwt.Worksheet
    _column_max_widths:list[Union[int, None]]
    _column_widths:dict
    _row:int

    def __init__(self, workbook:xlwt.Workbook, sheetname:str, col_max_widths:list[Union[int, None]]=None) -> None:
        self._sheet = workbook.add_sheet(sheetname)
        self._column_max_widths = [adjust_width(e) for e in col_max_widths or []]
        self._column_widths = {}
        self._row = 0
        return


    @property
    def name(self)->str:
        """The sheet's name."""
        return self._sheet.name


    def write_row(self, data:list[any], styles:list[str]=None):
        """Write a new row of data in the sheet.

        Args:
            data (list[any]): A list of strings to be written.
            styles (list[str], optional): A list of styles to apply to each column in the same order as the data list. Choose either "bold", "hyperlink", "heading, or None. Defaults to None.
        """

        for column, value in enumerate(data):

            is_bold = False
            col_style = _STYLE_NONE

            if styles and len(styles) > column:

                if styles[column] == "bold":
                    col_style = _STYLE_BOLD
                    is_bold = True
                elif styles[column] == "heading":
                    col_style = _STYLE_HEADING
                    is_bold = True
                elif styles[column] == "hyperlink":
                    col_style = _STYLE_HYPERLINK

            insert_to_cell = value
            text_for_width = str(value)
            if isinstance(value, XLSFormula):
                insert_to_cell = value.formula
                text_for_width = value.sample_text or ""

            self._sheet.write(self._row, column, insert_to_cell, col_style)
            self._update_column_width(column, text_for_width, is_bold)

        self._row += 1

        return


    def write_row_listing(self, label:str, value:any)->None:
        """Call write_row placing the label to the left in bold, and the value to the right.

        Args:
            label (str): The label to be bolded.
            value (any): The value to display.
        """

        self.write_row([label, value], ["bold", None])
        return


    def _update_column_width(self, column:int, data:str, is_bold:bool=False):
        """Update the column width if this content is wider.

        Args:
            column (int): Column number (0 based)
            data (str): String representation of cell content.
        """

        # Calculate data width
        width = 0
        for char in data:
            width += _CHARWIDTHS.get(char, 262)

        if is_bold:
            width *= 1.2
        else:
            width *= 1.1

        # Apply maximums and minimums
        max_width = _MAX_COL_WIDTH
        if len(self._column_max_widths) > column and self._column_max_widths[column] is not None:
            max_width = self._column_max_widths[column]

        width = max([min([width, max_width]), _MIN_COL_WIDTH])

        # Store the width if its larger than previous
        self._column_widths.setdefault(column, 0)
        if width > self._column_widths[column]:
            self._column_widths[column] = width

        return


    def apply_column_widths(self):
        """Apply the column widths to the sheet columns."""
        for column, width in self._column_widths.items():
            self._sheet.col(column).width = math.ceil(width)

        return


class Workbook:
    """Create and save a spreadsheet workbook.

    Args:
        director (str): Path to the directory where to write the workbook.
        name (str): Workbook's filename.
        add_timestamp (bool, optional): Add a timestamp to the end of the filename. Defaults to True.
    """

    _directory:str = None
    _name:str = None
    _add_timestamp:bool = True

    _workbook:xlwt.Workbook = None
    _timestamp:str = None
    _sheets:list[Sheet] = []
    _sheet_names:list[str] = []
    _name_collisions:dict[str, int] = {}


    def __init__(self, directory:str, name:str, add_timestamp:bool=True) -> None:
        self._directory = directory
        self._name = name
        self._add_timestamp = add_timestamp

        self._workbook = xlwt.Workbook(encoding="utf-8")
        self._timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")

        return


    @property
    def directory(self)->str:
        """Directory to which the workbook will be saved."""
        return self._directory


    @property
    def timestamp(self)->str:
        """Timestamp when the workbook was first created."""
        return self._timestamp


    @property
    def file_name(self)->str:
        """Name that will be given to the file."""
        file_name = self._name
        if self._add_timestamp:
            file_name += "_" + self.timestamp

        return file_name + ".xls"


    @property
    def full_path(self)->str:
        """Full path to the workbook file."""
        return os.path.join(self.directory, self.file_name)


    @property
    def sheet_count(self)->int:
        """Number of sheets in workbook."""
        return len(self._sheets)


    def save(self):
        """Save the workbook to file."""
        # Update sheet column widths
        for sheet in self._sheets:
            sheet.apply_column_widths()

        # Save the file
        try:
            os.makedirs(self.directory)
        except FileExistsError:
            pass

        self._workbook.save(self.full_path)

        return


    def add_sheet(self, sheetname:str, col_max_widths:list=None)->Sheet:
        """Add a new sheet to the workbook.

        Args:
            sheetname (str): Name for the worksheet (must be valid)
            col_max_widths (list[int]): The maximum width of each column, from left to right. Provide None for columns to be autoset. Default is to autoset all columns.

        Returns:
            Sheet: Sheet class instance.
        """
        sheet = Sheet(self._workbook, sheetname, col_max_widths)
        self._sheets.append(sheet)

        if sheetname not in self._sheet_names:
            self._sheet_names.append(sheetname)

        return sheet


    def make_valid_sheet_name(self, base_name:str, append_index:bool=False)->str:
        """Take a sheet name and make it valid by removing invalid characters, making it short enough, and making it unique.

        Args:
            base_name (str): The desired name for the sheet.
            append_index (bool, optional): Whether to append the sheet number to the name. Defaults to False.

        Raises:
            NameError: Base name provided is invalid (blank or 'history').

        Returns:
            str: A valid name.
        """
        # Ensure name is valid
        if len(base_name) == 0 or base_name.upper() == "HISTORY":
            raise NameError("Spreadsheet base name cannot be blank nor can it be called 'history'.")

        left = base_name.strip().strip("'")
        left = re.sub('[^0-9a-zA-Z_]+', '_', left)
        right = ""

        # Add index if required
        if append_index:
            index = len(self._sheet_names)
            right = f"_{index}"

        combined = self._combine_names(left, right, 31)

        # Ensure name isn't duplicated
        if combined in self._sheet_names:
            uid = self._get_sheet_uid(combined)
            right += f"_{uid}"
            combined = self._combine_names(left, right, 31)

        # Add to reserve
        self._sheet_names.append(combined)

        return combined


    def _combine_names(self, left:str, right:str, max_length:int)->str:
        """Combine a left and right part of a name, triming the end of the left part to not exceed the max-length.

        Args:
            left (str): left part of name to be trimmed.
            right (str): right part of name to left as-is.
            max_length (int): maximum length of the combined string.

        Returns:
            str: the combine string not exceeding the max-lengt.
        """

        trim_length = len(left) + len(right) - max_length

        left_trimmed = left
        if trim_length > 0:
            left_trimmed = left[:trim_length * -1]

        return f"{left_trimmed}{right}"[:31]


    def _get_sheet_uid(self, name:str)->int:
        """Determine a unique ID that can be appended to a sheet name to make it unique.

        Args:
            name (str): The sheet name tha collided.

        Returns:
            int: The unique ID to be appended.
        """
        self._name_collisions.setdefault(name, 0)
        self._name_collisions[name] += 1
        return self._name_collisions[name]


class XLSFormula:
    """Convert a string to a formula for insertion into the sheet.

    Args:
        formula (str): The formula as a string. Omit the equal sign from the start of the formula.
        sample_text (str, optional): A string that can be used to determine the width required to fully display the content of this cell. Defaults to None.
    """

    _formula:xlwt.Formula = None
    _sample_text:str = None

    def __init__(self, formula:str, sample_text:str=None) -> None:
        self._formula = xlwt.Formula(formula)
        self._sample_text = sample_text


    @property
    def formula(self)->xlwt.Formula:
        """The XLWT Formula for use when writing the worksheet."""
        return self._formula


    @property
    def sample_text(self)->str:
        """The sample text for use in determining the width of the cell."""
        return self._sample_text


def make_hyperlink(sheet_name:str, label:str, workbook_path:str=None)->object:
    """Create a hyperlink to be inserted into sheet.

    Args:
        sheet_name (str): The name of the sheet to which to point the link.
        label (str): The display text for the end user.
        workbook_name (str, optional): The path to the workbook if pointing to a different workbook. Can be relative. Defaults to None.

    Returns:
        object: The formula object that can be written to the sheet.
    """

    prefix = "#"
    if workbook_path:
        prefix = f"[{workbook_path}]"

    link = XLSFormula(f"HYPERLINK(\"{prefix}{sheet_name}!A1\", \"{label}\")", label)

    return link