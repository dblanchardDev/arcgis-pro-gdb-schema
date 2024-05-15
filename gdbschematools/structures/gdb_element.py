"""
Base class for all other Geodatabase Structure Elements.

Author: David Blanchard
"""

from typing import TYPE_CHECKING

from . import validation

if TYPE_CHECKING:
    from .geodatabase import Geodatabase


class GDBElement:
    """Base class for all other geodatabase items.

    Attributes:
        VALID_NAME_REGEX (str): Regular expression that validates the name of the element.
    """

    # Regular expression which validate the name
    VALID_NAME_REGEX = "^[A-z0-9][A-z0-9 ;_.-]{1,97}[A-z0-9]$"


    # Instance Properties
    _name:str = None


    def __init__(self, name:str) -> None:
        """Base class for all other geodatabase items.

        Args:
            name (str): User-assigned name for the element.
        """
        self.name = name


    def __lt__(self, other:object) -> bool:
        return self.name < other.name


    def __repr__(self) -> str:
        return f"<structures.{self.__class__.__name__} name='{self.name}'>"


    @property
    def _element_type(self):
        return self.__class__.__name__.lower()


    @property
    def name(self) -> str:
        """The user-assigned name for the element."""
        return self._name


    @name.setter
    def name(self, value:str):
        label = f"{self._element_type} name"
        validation.string(value, label, regex=self.__class__.VALID_NAME_REGEX)
        self._name = value


class GDBElementWithParent(GDBElement):
    """Base class for geodatabase items that have the geodatabase as their parent.

    Attributes:
        VALID_NAME_REGEX (str): Regular expression that validates the name of the element.
    """

    _geodatabase:"Geodatabase" = None


    @property
    def geodatabase(self) -> "Geodatabase":
        """Geodatabase in which this element is contained."""
        return self._geodatabase


    def _register_geodatabase(self, geodatabase:"Geodatabase"):
        """Register a geodatabase as the container of this element.

        Args:
            geodatabase (Geodatabase): Geodatabase in which this element is contained.
        """
        if self._geodatabase is not None:
            raise AttributeError("Can only set the geodatabase once.")

        if not validation.is_structure_instance(geodatabase, "Geodatabase"):
            raise TypeError("Expecting an instance of the Geodatabase class.")

        self._geodatabase = geodatabase