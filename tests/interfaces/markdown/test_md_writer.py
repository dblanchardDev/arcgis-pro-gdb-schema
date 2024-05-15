"""Unit tests for the Markdown writer methods."""
#pylint: disable=protected-access,redefined-outer-name,missing-function-docstring,missing-class-docstring

import os
import re
import zipfile
from typing import TYPE_CHECKING

import pytest

from gdbschematools.interfaces import MarkdownInterface
from gdbschematools.interfaces import GeodatabaseInterface

if TYPE_CHECKING:
    from gdbschematools.structures import Geodatabase


DATE_RE = "20\\d\\d-(?:0[1-9]|1[0-2])-(?:0[1-9]|[1-2][0-9]|3[0-1])-(?:[0-1][0-9]|2[0-3])[0-5]\\d"


#region GENERATE AND PREPARE MARKDOWN FILES

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
def markdown_paths(expected_gdb_structure:"Geodatabase", tmpdir_factory) -> tuple[str]:
    """Runs the Markdown writer and returns the 3 markdown paths (datasets, domains, relationships)."""
    tmp_dir = str(tmpdir_factory.mktemp("excel_outputs"))
    paths = MarkdownInterface.write(expected_gdb_structure, tmp_dir)

    # Printout path to temp dir where Excel files landed
    try:
        printable_dir = os.path.dirname(paths[0].replace("\\", "/"))
        print(f"Markdown Temp Directory: {printable_dir}")
    except Exception: #pylint: disable=broad-exception-caught
        pass

    return paths


@pytest.fixture(scope="module")
def datasets_md_path(markdown_paths:tuple[str]) -> str:
    """Path to the datasets markdown file."""
    return markdown_paths[0]


@pytest.fixture(scope="module")
def domains_md_path(markdown_paths:tuple[str]) -> str:
    """Path to the domains markdown file."""
    return markdown_paths[1]


@pytest.fixture(scope="module")
def relationships_md_path(markdown_paths:tuple[str]) -> str:
    """Path to the relationships markdown file."""
    return markdown_paths[2]

#endregion
#region SUPPORT FOR APPROVAL TESTS

APPROVAL_SKIP_REASON = "The approvaltests modules is required to compare the markdown outputs to the expectation."


class Namer():
    """Name generator for the approval tests verification received and approved files."""

    DIRECTORY = "approved_files"

    _md_directory:str = None
    _md_file_name:str = None

    def __init__(self, md_file_name:str) -> None:
        self._md_directory = str(os.path.dirname(md_file_name))
        name_parts = os.path.splitext(os.path.basename(md_file_name))
        self._md_file_name = name_parts[0]
        if not name_parts[1] == ".md":
            self._md_file_name += name_parts[1]

        self._md_file_name = re.sub(DATE_RE, "date_time", self._md_file_name)


    @property
    def _base(self) -> str:
        root = os.path.dirname(os.path.realpath(__file__))
        root = os.path.relpath(root, os.path.abspath(os.curdir))
        base = os.path.join(root, Namer.DIRECTORY, self._md_directory, self._md_file_name)
        return str(base)


    def get_received_filename(self, base:str = None) -> str:
        del base
        return str(os.path.join(f"{self._base}.received.md"))


    def get_approved_filename(self, base:str = None) -> str:
        del base
        return str(os.path.join(f"{self._base}.approved.md"))


DATE_SCRUBBER_RE = fr"(?<=]\()([^\)]*){DATE_RE}"


def link_scrubber(text:str) -> str:
    """Scrub dates out of the links and add approved suffix."""
    text = re.sub(DATE_SCRUBBER_RE, r"\g<1>date_time", text)
    text = re.sub(r"(datasets|domains|relationships).md", r"\g<1>.approved.md", text)
    return text


def _approve_md_file(md_path:str):
    approvaltests = pytest.importorskip("approvaltests", reason=APPROVAL_SKIP_REASON)

    # Read the file
    md_data = None
    with open(md_path, "r", encoding="UTF-8") as md_file:
        md_data = md_file.read()

    # Run the approval test (compare received MD to approved)
    opts = approvaltests.approvals.Options({
        "namer": Namer(os.path.basename(md_path)),
        "scrubber_func": link_scrubber,
    })
    approvaltests.approvals.verify(md_data, encoding="UTF-8", options=opts)


#endregion
#region GENERAL TESTS


def test_markdown_files_created(markdown_paths:tuple[str]):
    assert isinstance(markdown_paths, tuple)
    assert len(markdown_paths) == 3
    assert os.path.exists(markdown_paths[0])
    assert os.path.exists(markdown_paths[1])
    assert os.path.exists(markdown_paths[2])


def test_markdown_file_names(expected_gdb_structure:"Geodatabase", markdown_paths:tuple[str]):
    gdb_name = expected_gdb_structure.name

    datasets_name = os.path.basename(markdown_paths[0])
    assert bool(re.search(
        pattern=f"^{gdb_name}_{DATE_RE}_datasets\\.md$",
        string=datasets_name,
    )) is True

    domains_name = os.path.basename(markdown_paths[1])
    assert bool(re.search(
        pattern=f"^{gdb_name}_{DATE_RE}_domains\\.md$",
        string=domains_name,
    )) is True

    relationships_name = os.path.basename(markdown_paths[2])
    assert bool(re.search(
        pattern=f"^{gdb_name}_{DATE_RE}_relationships\\.md$",
        string=relationships_name,
    )) is True

#endregion
#region MARKDOWN CONTENT

def test_datasets_md_file_content(datasets_md_path:str):
    """Will only run if approvaltests module is installed."""
    _approve_md_file(datasets_md_path)


def test_domains_md_file_content(domains_md_path:str):
    """Will only run if approvaltests module is installed."""
    _approve_md_file(domains_md_path)


def test_relationships_md_file_content(relationships_md_path:str):
    """Will only run if approvaltests module is installed."""
    _approve_md_file(relationships_md_path)

#endregion