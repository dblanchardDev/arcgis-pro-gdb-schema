"""Unit tests for the Excel writer methods."""
#pylint: disable=protected-access,redefined-outer-name,missing-function-docstring,missing-class-docstring

import glob
import os
import re
import xml.dom.minidom
import zipfile
from typing import TYPE_CHECKING

import pytest

from gdbschematools.interfaces import ExcelInterface
from gdbschematools.interfaces import GeodatabaseInterface
from gdbschematools.interfaces.excel.writer.gdb_writer import GDBWriter

if TYPE_CHECKING:
    from gdbschematools.structures import Geodatabase


#region GENERATE AND PREPARE XLSX XML FILES

@pytest.fixture(scope="module")
def expected_gdb_structure(tmpdir_factory) -> "Geodatabase":
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
def xls_paths(expected_gdb_structure:"Geodatabase", tmpdir_factory) -> tuple[str]:
    tmp_dir = str(tmpdir_factory.mktemp("excel_outputs"))
    paths = ExcelInterface.write(expected_gdb_structure, tmp_dir, template_visible=True)

    # Printout path to temp dir where Excel files landed
    printable_dir = os.path.dirname(paths[0].replace("\\", "/"))
    print(f"Excel Temp Directory: {printable_dir}")

    return paths


def _explode_xls(xls_path:str) -> str:
    """Explode an Excel spreadsheet file into XML files.

    Args:
        xls_path (str): Path to Excel spreadsheet.

    Returns:
        str: Path to the folder which contains the XML files.
    """
    root_dir = os.path.dirname(xls_path)
    file_name = os.path.splitext(os.path.basename(xls_path))[0]
    destin_path = os.path.join(root_dir, file_name)

    with zipfile.ZipFile(xls_path, "r") as zip_file:
        zip_file.extractall(destin_path)

    return destin_path


@pytest.fixture(scope="module")
def expl_xls_datasets(xls_paths:tuple[str]) -> str:
    """Path to an exploded version of the Excel File (provides access to internal XML files)."""
    return _explode_xls(xls_paths[0])


@pytest.fixture(scope="module")
def expl_xls_domains(xls_paths:tuple[str]) -> str:
    """Path to an exploded version of the Excel File (provides access to internal XML files)."""
    return _explode_xls(xls_paths[1])


@pytest.fixture(scope="module")
def expl_xls_relationships(xls_paths:tuple[str]) -> str:
    """Path to an exploded version of the Excel File (provides access to internal XML files)."""
    return _explode_xls(xls_paths[2])

#endregion
#region SUPPORT FOR XML TESTS

APPROVAL_SKIP_REASON = "The approvaltests modules is required to compare Excel's XML documents."


class Namer():
    """Name generator for the approval tests verification received and approved files."""

    DIRECTORY = "approved_files"

    _test_name:str = None
    _xml_directory:str = None
    _xml_file_name:str = None

    def __init__(self, test_name:str, xml_file_name:str) -> None:
        self._test_name = test_name

        self._xml_directory = str(os.path.dirname(xml_file_name))
        name_parts = os.path.splitext(os.path.basename(xml_file_name))
        self._xml_file_name = name_parts[0]
        if not name_parts[1] == ".xml":
            self._xml_file_name += name_parts[1]


    @property
    def _base(self) -> str:
        root = os.path.dirname(os.path.realpath(__file__))
        root = os.path.relpath(root, os.path.abspath(os.curdir))
        base = os.path.join(root, Namer.DIRECTORY, self._test_name, self._xml_directory, self._xml_file_name)
        return str(base)


    def get_received_filename(self, base:str = None) -> str:
        del base
        return str(os.path.join(f"{self._base}.received.xml"))


    def get_approved_filename(self, base:str = None) -> str:
        del base
        return str(os.path.join(f"{self._base}.approved.xml"))


EXCEL_DATE_REGEX = r"20\d\d-(?:0[1-9]|1[0-2])-(?:0[1-9]|[1-2][0-9]|3[0-1])(?:T| |-)(?:[0-1][0-9]|2[0-3])(?::|)[0-5]\d(?::[0-5]\d|)(?:Z|)" #pylint: disable=line-too-long


def date_scrubber(date: str) -> str:
    """Scrub dates out of the Excel XML"""
    approvaltests = pytest.importorskip("approvaltests", reason=APPROVAL_SKIP_REASON)
    return approvaltests.scrubbers.create_regex_scrubber(
        EXCEL_DATE_REGEX, lambda t: f"{{date-time-{t}}}"
    )(date)


def _approve_xml_file(test_name:str, expl_xls:str, xml_file_name:str):
    approvaltests = pytest.importorskip("approvaltests", reason=APPROVAL_SKIP_REASON)

    # Read the file
    full_path = os.path.join(expl_xls, xml_file_name)
    xml_data = None
    with open(full_path, "r", encoding="UTF-8") as xml_file:
        xml_data = xml_file.read()

    # Pretty print the XML data for readability
    xml_data = xml.dom.minidom.parseString(xml_data).toprettyxml()

    # Remove empty lines left behind by to pretty xml
    xml_data = "\n".join([s for s in xml_data.splitlines() if s.strip()])

    # Run the approval test (compare received XML to approved)
    opts = approvaltests.approvals.Options({
        "namer": Namer(test_name, xml_file_name),
        "scrubber_func": date_scrubber,
    })
    approvaltests.approvals.verify(xml_data, encoding="UTF-8", options=opts)


#endregion
#region GENERAL TESTS

DATE_RE = "20\\d\\d-(?:0[1-9]|1[0-2])-(?:0[1-9]|[1-2][0-9]|3[0-1])-(?:[0-1][0-9]|2[0-3])[0-5]\\d"


def test_excel_files_created(xls_paths:tuple[str]):
    assert os.path.exists(xls_paths[0])
    assert os.path.exists(xls_paths[1])
    assert os.path.exists(xls_paths[2])


def test_excel_file_names(expected_gdb_structure:"Geodatabase", xls_paths:tuple[str]):
    gdb_name = expected_gdb_structure.name

    datasets_name = os.path.basename(xls_paths[0])
    assert bool(re.search(
        pattern=f"^{gdb_name}_{DATE_RE}_datasets\\.xlsx$",
        string=datasets_name,
    )) is True

    domains_name = os.path.basename(xls_paths[1])
    assert bool(re.search(
        pattern=f"^{gdb_name}_{DATE_RE}_domains\\.xlsx$",
        string=domains_name,
    )) is True

    relationships_name = os.path.basename(xls_paths[2])
    assert bool(re.search(
        pattern=f"^{gdb_name}_{DATE_RE}_relationships\\.xlsx$",
        string=relationships_name,
    )) is True

#endregion
#region DATASETS CONTENT

# spell-checker: disable
DATASETS_XML_FILES = [
    r"_rels\.rels",
    r"docProps\app.xml",
    r"docProps\core.xml",
    r"xl\_rels\workbook.xml.rels",
    r"xl\tables\table1.xml",
    r"xl\tables\table2.xml",
    r"xl\tables\table3.xml",
    r"xl\tables\table4.xml",
    r"xl\tables\table5.xml",
    r"xl\tables\table6.xml",
    r"xl\tables\table7.xml",
    r"xl\tables\table8.xml",
    r"xl\tables\table9.xml",
    r"xl\tables\table10.xml",
    r"xl\tables\table11.xml",
    r"xl\tables\table12.xml",
    r"xl\tables\table13.xml",
    r"xl\tables\table14.xml",
    r"xl\tables\table15.xml",
    r"xl\theme\theme1.xml",
    r"xl\worksheets\_rels\sheet2.xml.rels",
    r"xl\worksheets\_rels\sheet3.xml.rels",
    r"xl\worksheets\_rels\sheet4.xml.rels",
    r"xl\worksheets\_rels\sheet5.xml.rels",
    r"xl\worksheets\_rels\sheet6.xml.rels",
    r"xl\worksheets\_rels\sheet7.xml.rels",
    r"xl\worksheets\_rels\sheet8.xml.rels",
    r"xl\worksheets\_rels\sheet9.xml.rels",
    r"xl\worksheets\sheet1.xml",
    r"xl\worksheets\sheet2.xml",
    r"xl\worksheets\sheet3.xml",
    r"xl\worksheets\sheet4.xml",
    r"xl\worksheets\sheet5.xml",
    r"xl\worksheets\sheet6.xml",
    r"xl\worksheets\sheet7.xml",
    r"xl\worksheets\sheet8.xml",
    r"xl\worksheets\sheet9.xml",
    r"xl\styles.xml",
    r"xl\workbook.xml",
    r"[Content_Types].xml",
]
DATASETS_XML_FILES.sort()
# spell-checker: enable


@pytest.mark.parametrize("xml_file_name", DATASETS_XML_FILES)
def test_datasets_xml_files_exists(expl_xls_datasets:str, xml_file_name:str):
    full_path = os.path.join(expl_xls_datasets, xml_file_name)

    # Check that file exists
    assert os.path.exists(full_path)


def test_datasets_xml_files_unchecked(expl_xls_datasets:str):
    all_paths = glob.glob(expl_xls_datasets + "/**/*", recursive=True)
    all_paths += glob.glob(expl_xls_datasets + "/**/.*", recursive=True)
    all_rel_files = [os.path.relpath(path, expl_xls_datasets) for path in all_paths if os.path.isfile(path)]
    all_rel_files.sort()

    assert DATASETS_XML_FILES == all_rel_files


@pytest.mark.parametrize("xml_file_name", DATASETS_XML_FILES)
def test_datasets_xml_files_content(expl_xls_datasets:str, xml_file_name:str):
    """Will only run if approvaltests module is installed."""
    _approve_xml_file("test_datasets_xml_files_content", expl_xls_datasets, xml_file_name)

#endregion
#region DOMAINS CONTENT

# spell-checker: disable
DOMAINS_XML_FILES = [
    r"_rels\.rels",
    r"docProps\app.xml",
    r"docProps\core.xml",
    r"xl\_rels\workbook.xml.rels",
    r"xl\tables\table1.xml",
    r"xl\tables\table2.xml",
    r"xl\tables\table3.xml",
    r"xl\tables\table4.xml",
    r"xl\tables\table5.xml",
    r"xl\tables\table6.xml",
    r"xl\tables\table7.xml",
    r"xl\tables\table8.xml",
    r"xl\tables\table9.xml",
    r"xl\tables\table10.xml",
    r"xl\tables\table11.xml",
    r"xl\tables\table12.xml",
    r"xl\tables\table13.xml",
    r"xl\tables\table14.xml",
    r"xl\tables\table15.xml",
    r"xl\tables\table16.xml",
    r"xl\tables\table17.xml",
    r"xl\tables\table18.xml",
    r"xl\tables\table19.xml",
    r"xl\theme\theme1.xml",
    r"xl\worksheets\_rels\sheet2.xml.rels",
    r"xl\worksheets\_rels\sheet3.xml.rels",
    r"xl\worksheets\_rels\sheet4.xml.rels",
    r"xl\worksheets\_rels\sheet5.xml.rels",
    r"xl\worksheets\_rels\sheet6.xml.rels",
    r"xl\worksheets\_rels\sheet7.xml.rels",
    r"xl\worksheets\_rels\sheet8.xml.rels",
    r"xl\worksheets\_rels\sheet9.xml.rels",
    r"xl\worksheets\_rels\sheet10.xml.rels",
    r"xl\worksheets\_rels\sheet11.xml.rels",
    r"xl\worksheets\_rels\sheet12.xml.rels",
    r"xl\worksheets\_rels\sheet13.xml.rels",
    r"xl\worksheets\sheet1.xml",
    r"xl\worksheets\sheet2.xml",
    r"xl\worksheets\sheet3.xml",
    r"xl\worksheets\sheet4.xml",
    r"xl\worksheets\sheet5.xml",
    r"xl\worksheets\sheet6.xml",
    r"xl\worksheets\sheet7.xml",
    r"xl\worksheets\sheet8.xml",
    r"xl\worksheets\sheet9.xml",
    r"xl\worksheets\sheet10.xml",
    r"xl\worksheets\sheet11.xml",
    r"xl\worksheets\sheet12.xml",
    r"xl\worksheets\sheet13.xml",
    r"xl\styles.xml",
    r"xl\workbook.xml",
    r"[Content_Types].xml",
]
DOMAINS_XML_FILES.sort()
# spell-checker: enable


@pytest.mark.parametrize("xml_file_name", DOMAINS_XML_FILES)
def test_domains_xml_files_exists(expl_xls_domains:str, xml_file_name:str):
    full_path = os.path.join(expl_xls_domains, xml_file_name)

    # Check that file exists
    assert os.path.exists(full_path)


def test_domains_xml_files_unchecked(expl_xls_domains:str):
    all_paths = glob.glob(expl_xls_domains + "/**/*", recursive=True)
    all_paths += glob.glob(expl_xls_domains + "/**/.*", recursive=True)
    all_rel_files = [os.path.relpath(path, expl_xls_domains) for path in all_paths if os.path.isfile(path)]
    all_rel_files.sort()

    assert DOMAINS_XML_FILES == all_rel_files


@pytest.mark.parametrize("xml_file_name", DOMAINS_XML_FILES)
def test_domains_xml_files_content(expl_xls_domains:str, xml_file_name:str):
    """Will only run if approvaltests module is installed."""
    _approve_xml_file("test_domains_xml_files_content", expl_xls_domains, xml_file_name)

#endregion
#region RELATIONSHIPS CONTENT

# spell-checker: disable
RELATIONSHIPS_XML_FILES = [
    r"_rels\.rels",
    r"docProps\app.xml",
    r"docProps\core.xml",
    r"xl\_rels\workbook.xml.rels",
    r"xl\tables\table1.xml",
    r"xl\tables\table2.xml",
    r"xl\tables\table3.xml",
    r"xl\tables\table4.xml",
    r"xl\theme\theme1.xml",
    r"xl\worksheets\_rels\sheet2.xml.rels",
    r"xl\worksheets\_rels\sheet3.xml.rels",
    r"xl\worksheets\_rels\sheet4.xml.rels",
    r"xl\worksheets\_rels\sheet5.xml.rels",
    r"xl\worksheets\sheet1.xml",
    r"xl\worksheets\sheet2.xml",
    r"xl\worksheets\sheet3.xml",
    r"xl\worksheets\sheet4.xml",
    r"xl\worksheets\sheet5.xml",
    r"xl\styles.xml",
    r"xl\workbook.xml",
    r"[Content_Types].xml",
]
RELATIONSHIPS_XML_FILES.sort()
# spell-checker: enable


@pytest.mark.parametrize("xml_file_name", RELATIONSHIPS_XML_FILES)
def test_relationships_xml_files_exists(expl_xls_relationships:str, xml_file_name:str):
    full_path = os.path.join(expl_xls_relationships, xml_file_name)

    # Check that file exists
    assert os.path.exists(full_path)


def test_relationships_xml_files_unchecked(expl_xls_relationships:str):
    all_paths = glob.glob(expl_xls_relationships + "/**/*", recursive=True)
    all_paths += glob.glob(expl_xls_relationships + "/**/.*", recursive=True)
    all_rel_files = [os.path.relpath(path, expl_xls_relationships) for path in all_paths if os.path.isfile(path)]
    all_rel_files.sort()

    assert RELATIONSHIPS_XML_FILES == all_rel_files


@pytest.mark.parametrize("xml_file_name", RELATIONSHIPS_XML_FILES)
def test_relationships_xml_files_content(expl_xls_relationships:str, xml_file_name:str):
    """Will only run if approvaltests module is installed."""
    _approve_xml_file("test_relationships_xml_files_content", expl_xls_relationships, xml_file_name)

#endregion
#region Additional Coverage Tests

SHEET_NAME_ONE = "This is a longer then 31 character name that should get truncated"
SHEET_NAME_TWO = "This is a longer then 31 character name that should get truncated and become duplicate"

class GDBWriterTest(GDBWriter):
    element_type:str = "Test"

    def _create_template(self, visible:bool=False):
        return


def test_sheet_naming():
    """Ensure sheet names are correctly truncated and duplicate names are indexed."""

    gdb_writer = GDBWriterTest("", "")
    gdb_writer.prepare_sheet(SHEET_NAME_ONE)
    gdb_writer.prepare_sheet(SHEET_NAME_TWO)

    assert gdb_writer.cw_lookup[SHEET_NAME_ONE].worksheet.title == SHEET_NAME_ONE[:31]
    assert gdb_writer.cw_lookup[SHEET_NAME_TWO].worksheet.title == f"{SHEET_NAME_TWO[:29]}01"

#endregion