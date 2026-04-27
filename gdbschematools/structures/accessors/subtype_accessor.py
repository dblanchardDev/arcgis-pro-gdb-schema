"""
Classes that simplify access to subtype properties.

Author: David Blanchard
"""

from typing import TYPE_CHECKING

from .. import validation, utility
from .base import Accessor, DictAccessor

if TYPE_CHECKING:
    from .field_accessor import FieldAccessor
    from ..field import Field
    from ..domain import Domain


class SubtypeFieldProperties:
    """Properties for a field within a subtype.

    Args:
        field (Field): Field structure to which these properties belong.
    """

    _field:"Field" = None
    _domain:"Domain" = None
    _default:any = None


    def __init__(self, field:"Field"):
        self._field = field


    @property
    def field(self) -> "Field":
        """Field associated to this subtype code."""
        return self._field


    @property
    def name(self) -> str:
        """Name of field to which these subtype properties belong."""
        return self._field.name


    @property
    def domain(self) -> "Domain":
        """Domain assigned to this field within this subtype."""
        return self._domain


    @domain.setter
    def domain(self, value:"Domain"):
        if value is not None:
            if not validation.is_structure_instance(value, "Domain"):
                raise TypeError("Value for domain must be a Domain object or None.")

            if not self._field.field_type == value.field_type:
                raise TypeError("The domain has a different field type than the field to which its being added.")

            if self.default is not None:
                if value.test_value(self.default) is False:
                    raise ValueError("Default value is not valid is new domain.")

            value._register_field(self._field) #pylint: disable=protected-access

        self._domain = value


    @property
    def default(self) -> any:
        """Default value assigned to this field within this subtype."""
        return self._default


    @default.setter
    def default(self, value:any):
        if value is None:
            self._default = None
        else:
            label = f"subtype field {self.name} default"
            converted = validation.by_field_type(value, self._field.field_type, label)

            if self.domain and self.domain.test_value(converted) is False:
                raise ValueError("Default value not valid in the domain.")

            self._default = converted

    def diff(self, other_subtype_field:"SubtypeFieldProperties") -> list:
        """compares name, default, domain name and domain schema of two Subtype Fields

        Args:
            other_subtype_field (SubtypeFieldProperties): Other Subtype Field to compare with

        Returns:
            list: a list of differences between two Subtype Fields
        """
        properties = ["name", "default"]
        diff_results = utility.diff(self, other_subtype_field, f"subtype field of {self.field.dataset.name} dataset", properties)

        if self.domain is not None and other_subtype_field.domain is not None:
            if self.domain.name != other_subtype_field.domain.name:
                diff_results.append(f"The domain name of {self.name} subtype field of {self.field.dataset.name} dataset is {self.domain.name} in the origin gdb and {other_subtype_field.domain.name} in the other gdb")
            if self.domain.schema != other_subtype_field.domain.schema:
                diff_results.append(f"The domain schema of {self.name} subtype field of {self.field.dataset.name} dataset is {self.domain.schema} in the origin gdb and {other_subtype_field.domain.schema} in the other gdb")
        elif self.domain is None and other_subtype_field.domain is not None:
            diff_results.append(f"{self.name} subtype field has no domain in {self.field.dataset.name} dataset in the origin gdb and {other_subtype_field.domain.name} domain in the other gdb.")
        elif self.domain is not None and other_subtype_field.domain is None:
            diff_results.append(f"{self.name} subtype field has no domain in {other_subtype_field.field.dataset.name} dataset in the other gdb and has {self.domain.name} domain in the origin gdb.")

        return diff_results


#pylint: disable=too-few-public-methods
class SubtypeFieldPropertiesAccessor(Accessor):
    """Access for the subtype field properties.

    Args:
        field_accessor (FieldAccessor): Accessor giving access to fields for this subtype.
    """

    _field_accessor:"FieldAccessor" = None
    _field_names_added:list[str] = None


    def __init__(self, field_accessor:"FieldAccessor"):
        super().__init__()
        self._field_accessor = field_accessor
        self._field_names_added = []


    def _append(self, value):
        self._elements_container.append(value)


    def _refresh_list(self):
        """Add any new fields that were added after initialization."""
        if len(self._field_names_added) != len(self._field_accessor):
            for field in self._field_accessor:
                if field.name not in self._field_names_added:
                    sfp = SubtypeFieldProperties(field)
                    self._append(sfp)
                    self._field_names_added.append(field.name)


    @property
    def _elements(self):
        self._refresh_list()
        return self._elements_container


    def __getitem__(self, key:int) -> object:
        return self._get(key)


class SubtypeProperties():
    """Properties for the subtype code.

    Args:
        description (str): Description of the subtype code.
        field_accessor (FieldAccessor): Accessor giving access to fields for this subtype.
        meta_summary (str, optional): Metadata summary for the subtype code. Defaults to None.
    """

    _description:str = None
    _meta_summary:str = None
    _fields_props:SubtypeFieldPropertiesAccessor = None


    def __init__(self, description:str, field_accessor:"FieldAccessor", meta_summary:str=None) -> None:
        self._description = description
        self.meta_summary = meta_summary
        self._fields_props = SubtypeFieldPropertiesAccessor(field_accessor)


    @property
    def description(self) -> str:
        """Description of the subtype code."""
        return self._description


    @property
    def meta_summary(self) -> str:
        """Subtype code's metadata summary."""
        return self._meta_summary


    @meta_summary.setter
    def meta_summary(self, value:str):
        validation.string_or_none(value, label="subtype code's metadata summary")
        self._meta_summary = value


    @property
    def field_props(self) -> SubtypeFieldPropertiesAccessor:
        """Sequence like list of fields and their subtype properties."""
        return self._fields_props

    def diff(self, other_code:"SubtypeProperties") -> list:
        """Compares meta_summary, description and fields's properties of two Subtypes

        Args:
            other_code (SubtypeProperties): _description_

        Returns:
            list: A list of differences between two Subtypes
        """
        properties = ["meta_summary", "description"]
        diff_results = utility.diff(self, other_code, f"subtype code of {self} subtype", properties)

        origin_subtype_fields_name = {field.name for field in self.field_props}
        other_subtype_fields_name = {field.name for field in other_code.field_props}

        subtype_fields_missing_in_origin = other_subtype_fields_name.difference(origin_subtype_fields_name)
        if subtype_fields_missing_in_origin:
            diff_results.append(f"The following subtype fields are in the other GDB but not in the origin GDB: {', '.join(subtype_fields_missing_in_origin)}.")

        subtype_fields_missing_in_other = origin_subtype_fields_name.difference(other_subtype_fields_name)
        if subtype_fields_missing_in_other:
            diff_results.append(f"The following subtype fields are in the origin GDB but not in the other GDB: {', '.join(subtype_fields_missing_in_other)}.")

        for field in origin_subtype_fields_name.intersection(other_subtype_fields_name):
            origin_field:"SubtypeFieldProperties" = self.field_props[field]
            other_field:"SubtypeFieldProperties" = other_code.field_props[field]
            fields_diff_result = origin_field.diff(other_field)
            diff_results.extend(fields_diff_result)

        return diff_results


class SubtypeCodeAccessor(DictAccessor):
    """Dictionary like accessor for the subtype codes.

    Args:
        field_accessor (FieldAccessor): Accessor giving access to fields for this subtype.
    """

    _lookup:dict[int, SubtypeProperties] = None
    _field_accessor:"FieldAccessor" = None


    def __init__(self, field_accessor:"FieldAccessor"):
        super().__init__()
        self._field_accessor = field_accessor


    def new(self, code:int, description:str, meta_summary:str=None) -> SubtypeProperties:
        """Add a new subtype code to the subtype.

        Args:
            code (int): Code for the subtype.
            description (str): Description of the subtype code.
            meta_summary (str, optional): Metadata summary for the subtype code. Defaults to None.

        Returns:
            SubtypeProperties: Resulting properties to which field domains and defaults can be set.
        """
        validation.integer(code, "subtype code", allow_str=False)

        subtype_props = SubtypeProperties(description, self._field_accessor, meta_summary)
        self._lookup[code] = subtype_props

        return subtype_props