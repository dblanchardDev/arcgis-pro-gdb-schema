"""
Base reader / writer interface from which all other interface entry points inherit.

Author: David Blanchard
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..structures import Geodatabase


class BaseInterface():
    """Base reader / writer interface from which all other interface entry points inherit."""

    @classmethod
    def read(cls, source:str) -> "Geodatabase":
        """Read data from an external datasource to an internal Geodatabase structure.

        Args:
            source (str): Path to the input dataset that is to be read.

        Returns:
            Geodatabase: Geodatabase structure generated from the source data.
        """
        raise NotImplementedError(f"Read method not implemented for the {cls.__name__} interface.")


    @classmethod
    def write(cls, gdb:"Geodatabase") -> str:
        """Write from an internal Geodatabase structure to an external datasource.

        Args:
            gdb (Geodatabase): Geodatabase structure from which the data output is to be produced.

        Returns:
            str: Path to the directory or file that was generated as an output.
        """
        raise NotImplementedError(f"Write method not implemented for the {cls.__name__} interface.")