"""
Classes that simplify children fields.

Author: David Blanchard
"""

from typing import TYPE_CHECKING, Union

from .base import Accessor
from ..field import Field

if TYPE_CHECKING:
    from ..domain import Domains
    from ..feature_class import FeatureClass
    from ..relationship import Relationship
    from ..table import Table


# Alias for the various dataset types
Datasets = Union["FeatureClass", "Table", "Relationship"]


class FieldAccessor(Accessor):
    """Sequence of fields, behaves like a sequence."""

    _dataset:Datasets = None
    _excluded_types:list[str] = None
    _has_objectid:bool = False
    _has_shape:bool = False
    _has_globalid:bool = False


    def __init__(self, dataset:Datasets, excluded_types:list[str]) -> None:
        super().__init__()
        self._dataset = dataset
        self._excluded_types = excluded_types


    #pylint: disable=too-many-arguments
    def new(self, name:str, field_type:str, precision:Union[int, None]=None, scale:Union[int, None]=None,
                 length:Union[int, None]=None, alias:str=None, nullable:bool=True, required:bool=False,
                 default:any=None, domain:Union["Domains", None]=None, meta_summary:str=None) -> None:
        """Create a new field in the dataset.

        Args:
            name (str): Name of the field.
            field_type (str): Data type of the field to be added. Valid values in Field.FIELD_TYPES.
            precision (int, optional): Number of digits to be stored in a numeric field. Defaults to None.
            scale (int, optional): Number of decimal places stored in a float or double field. Defaults to None.
            length (int, optional): Length of a text field. Defaults to None.
            alias (str, optional): Alternate name used for labeling. Defaults to the name.
            nullable (bool, optional): Whether the field can contain null values. Defaults to True.
            required (bool, optional): Whether the field is required by ArcGIS. Defaults to False.
            domain (Domains, optional): Domain that constrains values for this field. Defaults to None.
            meta_summary (str, optional): Metadata summary for the geodatabase. Defaults to None.

        Returns:
            Field: The newly created field.
        """ #pylint: disable=line-too-long

        if name in self:
            raise ValueError(f"A field with the '{name}' name already exists.")

        if field_type in self._excluded_types:
            raise ValueError(f"Fields of type {field_type} are not allowed in this type of dataset.")

        if field_type == "OBJECTID":
            if self._has_objectid:
                raise ValueError(f"Adding more then 1 OBJECTID field to {name} is not possible.")
            self._has_objectid = True

        if field_type == "SHAPE":
            if self._has_shape:
                raise ValueError(f"Adding more then 1 SHAPE field to {name} is not possible.")
            self._has_shape = True

        if field_type == "GLOBALID":
            if self._has_globalid:
                raise ValueError(f"Adding more then 1 GLOBALID field to {name} is not possible.")
            self._has_globalid = True

        field = Field(name, field_type, precision, scale, length, alias, nullable, required, default, domain,
                      meta_summary)
        field._register_dataset(self._dataset) #pylint: disable=protected-access

        self._elements.append(field)

        return field