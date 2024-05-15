"""
Writer for markdown files.

Author: Roya Shourouni, David Blanchard
"""

from typing import TYPE_CHECKING

from .md_writer import output_markdown
from ..interface import BaseInterface

if TYPE_CHECKING:
    from gdbschematools.structures import Geodatabase


#pylint: disable-next=abstract-method
class MarkdownInterface(BaseInterface):
    """Writer for markdown files."""


    @classmethod
    def write(cls, gdb:"Geodatabase", output_dir:str) -> tuple[str]: #pylint: disable=arguments-differ
        """Write the full geodatabase structure to a file or enterprise geodatabase from an existing geodatabase structure.

        Args:
            path_to_gdb (str): Path to the file or enterprise geodatabase. Should be empty.
            output_dir (str): Directory in which the markdown files will be written.

        Returns:
            tuple(str): The 3 paths to which the markdown files were written (datasets, domains, relationships).
        """ #pylint: disable=line-too-long
        return output_markdown(gdb, output_dir)