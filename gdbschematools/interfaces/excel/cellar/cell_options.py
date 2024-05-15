"""
Utility to quickly write to worksheet cells in a consistent format.

Author: David Blanchard
"""

from openpyxl.styles import Alignment, NamedStyle, Font, numbers


class CellOptions:
    """Options to format and style the content of the cell.

    Args:
        num_format (str, optional): Name of the format to apply (see CellOptions.FORMAT). Defaults to GENERAL.
        style (str, optional): Name of the style to apply (see CellOptions.STYLES). Defaults to BASIC.
    """

    FORMATS = {
        # spell-checker:disable
        "GENERAL": numbers.FORMAT_GENERAL,
        "TEXT": numbers.FORMAT_TEXT,
        "NUMBER": numbers.FORMAT_NUMBER,
        "NUMBER_00": numbers.FORMAT_NUMBER_00,
        "NUMBER_COMMA_SEPARATED1": numbers.FORMAT_NUMBER_COMMA_SEPARATED1,
        "NUMBER_COMMA_SEPARATED2": numbers.FORMAT_NUMBER_COMMA_SEPARATED2,
        "PERCENTAGE": numbers.FORMAT_PERCENTAGE,
        "PERCENTAGE_00": numbers.FORMAT_PERCENTAGE_00,
        "DATE_YYYYMMDD2": numbers.FORMAT_DATE_YYYYMMDD2,
        "DATE_YYMMDD": numbers.FORMAT_DATE_YYMMDD,
        "DATE_DDMMYY": numbers.FORMAT_DATE_DDMMYY,
        "DATE_DMYSLASH": numbers.FORMAT_DATE_DMYSLASH,
        "DATE_DMYMINUS": numbers.FORMAT_DATE_DMYMINUS,
        "DATE_DMMINUS": numbers.FORMAT_DATE_DMMINUS,
        "DATE_MYMINUS": numbers.FORMAT_DATE_MYMINUS,
        "DATE_XLSX14": numbers.FORMAT_DATE_XLSX14,
        "DATE_XLSX15": numbers.FORMAT_DATE_XLSX15,
        "DATE_XLSX16": numbers.FORMAT_DATE_XLSX16,
        "DATE_XLSX17": numbers.FORMAT_DATE_XLSX17,
        "DATE_XLSX22": numbers.FORMAT_DATE_XLSX22,
        "DATE_DATETIME": numbers.FORMAT_DATE_DATETIME,
        "DATE_TIME1": numbers.FORMAT_DATE_TIME1,
        "DATE_TIME2": numbers.FORMAT_DATE_TIME2,
        "DATE_TIME3": numbers.FORMAT_DATE_TIME3,
        "DATE_TIME4": numbers.FORMAT_DATE_TIME4,
        "DATE_TIME5": numbers.FORMAT_DATE_TIME5,
        "DATE_TIME6": numbers.FORMAT_DATE_TIME6,
        "DATE_TIME7": numbers.FORMAT_DATE_TIME7,
        "DATE_TIME8": numbers.FORMAT_DATE_TIME8,
        "DATE_TIMEDELTA": numbers.FORMAT_DATE_TIMEDELTA,
        "DATE_YYMMDDSLASH": numbers.FORMAT_DATE_YYMMDDSLASH,
        "CURRENCY_USD_SIMPLE": numbers.FORMAT_CURRENCY_USD_SIMPLE,
        "CURRENCY_USD": numbers.FORMAT_CURRENCY_USD,
        "CURRENCY_EUR_SIMPLE": numbers.FORMAT_CURRENCY_EUR_SIMPLE,
        # spell-checker:enable
    }


    STYLES = {
        "BASIC": NamedStyle(
            name="Basic",
            font=Font(name="Arial", size=10),
            alignment=Alignment(horizontal="left", vertical="top"),
        ),

        "WRAPPED": NamedStyle(
            name="Wrapped",
            font=Font(name="Arial", size=10),
            alignment=Alignment(horizontal="left", vertical="top", wrap_text=True),
        ),

        "HEADING": NamedStyle(
            name="Heading",
            font=Font(name="Arial", bold=True, size=14),
            alignment=Alignment(horizontal="left", vertical="top"),
        ),

        "HEADING2": NamedStyle(
            name="Heading 2",
            font=Font(name="Arial", bold=True, size=12, italic=True),
            alignment=Alignment(horizontal="left", vertical="top"),
        ),

        "KEY": NamedStyle(
            name="Key",
            font=Font(name="Arial", bold=True, size=10),
            alignment=Alignment(horizontal="left", vertical="top"),
        ),

        "LINK": NamedStyle(
            name="Link",
            font=Font(name="Arial", size=10, color="1B5173", underline="single"),
            alignment=Alignment(horizontal="left", vertical="top"),
        ),

        "NUMERIC": NamedStyle(
            name="Numeric",
            font=Font(name="Arial", size=10),
            alignment=Alignment(horizontal="right", vertical="top"),
        ),
    }


    _num_format:str = None
    _style:str = None
    _link:str = None


    def __init__(self, num_format:str="GENERAL", style:str="BASIC", link:str=None) -> None:
        self.num_format = CellOptions.FORMATS.get(num_format, CellOptions.FORMATS["GENERAL"])
        self.style = CellOptions.STYLES.get(style, CellOptions.STYLES["BASIC"])
        self.link = link


    @property
    def num_format(self) -> str:
        """Formatting of the data stored in the cell. Valid values are found in CellOptions.FORMATS and correspond to the format types found in openpyxl.styles.numbers.""" #pylint: disable=line-too-long
        return self._num_format


    @num_format.setter
    def num_format(self, value:str):
        if value not in CellOptions.FORMATS.values():
            raise ValueError("Format must be from CellOptions.Format.")
        self._num_format = value


    @property
    def style(self) -> NamedStyle:
        """Styling applied to cell based on Excel named styles. Valid values are found in CellOptions.STYLES"""
        return self._style


    @style.setter
    def style(self, value:str):
        if value not in CellOptions.STYLES.values():
            raise ValueError("Data type must be from CellOptions.Styles.")
        self._style = value


    @property
    def link(self) -> str:
        """Hyperlink that gets applied to the cell."""
        return self._link


    @link.setter
    def link(self, value) -> str:
        self._link = None
        if value is not None:
            self._link = str(value)


# Pre-built cell options for re-use
CELL_OPTS_DEFAULT = CellOptions()
CELL_OPTS_HEADING = CellOptions("TEXT", "HEADING")
CELL_OPTS_HEADING2 = CellOptions("TEXT", "HEADING2")
CELL_OPTS_KEY = CellOptions("TEXT", "KEY")
CELL_OPTS_TEXT = CellOptions("TEXT")
CELL_OPTS_WRAP = CellOptions("TEXT", "WRAPPED")
CELL_OPTS_INTEGER = CellOptions("NUMBER", "NUMERIC")
CELL_OPTS_INTEGER_LEFT = CellOptions("NUMBER")
CELL_OPTS_FLOAT = CellOptions("NUMBER_COMMA_SEPARATED1", "NUMERIC")
CELL_OPTS_FLOAT_LEFT = CellOptions("NUMBER_COMMA_SEPARATED1")


def make_link_options(workbook_name:str=None, sheet_name:str=None, cell:str=None) -> CellOptions:
    """Create a CellOptions instance for links.

    Args:
        workbook_name (str, optional): Name of the workbook file with extension. Defaults to None.
        sheet_name (str, optional): Name of the sheet in the workbook. Defaults to None.
        cell (str, optional): Coordinates of the cell in letter-number format (e.g. 'A1'). Defaults to None.

    Returns:
        CellOptions: Instance of CellOptions for text links with the hyperlink pre-created.
    """

    #GDBSchemaTool_2024-02-16-1851_domains.xlsx#'Buidling - General'!A2

    link = ""
    if workbook_name:
        link += f"{workbook_name}"

    link += "#"

    if sheet_name:
        link += f"'{sheet_name}'!"

    if cell:
        link += cell
    else:
        link += "A1"

    return CellOptions(num_format="TEXT", style="LINK", link=link)