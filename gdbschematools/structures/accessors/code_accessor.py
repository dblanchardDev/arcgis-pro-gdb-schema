"""
Base class into which domain coded values can be accessed and added as a dictionary.

Author: David Blanchard
"""

from typing import TYPE_CHECKING, Union

from .. import validation
from .base import DictAccessor

if TYPE_CHECKING:
    import datetime
    from ..domain import CodedDomain


CodesTypes = Union[str, int, float, "datetime.date", "datetime.time"]


class Code():
    """Code within a coded domain.

    Args:
        description (str): Description of the coded value.
        meta_summary (str, optional): Metadata extended summary of the code. Defaults to None.
    """

    _description:str = None
    _meta_summary:str = None


    def __init__(self, description:str, meta_summary:str=None):
        self.description = description
        self.meta_summary = meta_summary


    @property
    def description(self) -> str:
        """Description of the coded value."""
        return self._description


    @description.setter
    def description(self, value:str):
        self._description = validation.string(value, f"{value} code description")


    @property
    def meta_summary(self) -> str:
        """Summary describing the coded value in more details from the metadata."""
        return self._meta_summary


    @meta_summary.setter
    def meta_summary(self, value:str):
        self._meta_summary = validation.string_or_none(value, f"{value} code meta summary")


class CodeAccessor(DictAccessor):
    """Read-only dictionary like accessor for coded domain values.

    Args:
        coded_domain (CodedDomain): The coded domain to which these codes belong.
    """

    _domain:"CodedDomain" = None
    _lookup:dict[CodesTypes, str] = None
    _meta_summary:dict[CodesTypes, Code]


    def __init__(self, coded_domain:"CodedDomain"):
        super().__init__()
        self._domain = coded_domain


    def __repr__(self):
        return f"<structures.CodedAccessor domain='{self._domain.name}'>"


    def new(self, code:CodesTypes, description:str, meta_summary:str=None) -> any:
        """Add a new coded value to the domain.

        Args:
            code (CodesTypes): Code to be added.
            description (str): Description for the code.
            meta_summary (str, optional): Metadata extended summary of the code. Defaults to None.

        Returns:
            any: The code as it was added (may have been converted).
        """
        code_converted = validation.by_field_type(code, self._domain.field_type, f"{self._domain.name} domain code")

        if code_converted in self._lookup:
            raise ValueError(f"A code value with the '{code}' code already exists in the {self._domain.name} domain.")

        self._lookup[code_converted] = Code(description, meta_summary)

        return (code_converted, code)