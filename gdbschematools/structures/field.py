"""
Structure for geodatabase table fields.

Author: David Blanchard
"""

from typing import TYPE_CHECKING, Union

from . import validation
from .gdb_element import GDBElement

if TYPE_CHECKING:
    from .domain import Domains
    from .feature_class import FeatureClass
    from .relationship import Relationship
    from .table import Table


# Alias for the various dataset types
Datasets = Union["FeatureClass", "Table", "Relationship"]


#pylint: disable-next=too-many-instance-attributes
class Field(GDBElement):
    """Field for a table or feature class.

    Args:
        name (str): Name of the field.
        field_type (str): Data type of the field to be added. Valid values in Field.FIELD_TYPES.
        precision (int, optional): Number of digits to be stored in a numeric field. Defaults to None.
        scale (int, optional): Number of decimal places stored in a float or double field. Defaults to None.
        length (int, optional): Length of a text field. Defaults to None.
        alias (str, optional): Alternate name used for labeling. Defaults to the name.
        nullable (bool, optional): Whether the field can contain null values. Defaults to True.
        required (bool, optional): Whether the field is required by ArcGIS. Defaults to False.
        default (any, optional): Default value assigned to field. Defaults to None.
        domain (Domains, optional): Domain that constrains values for this field. Defaults to None.
        meta_summary (str, optional): Metadata summary for the geodatabase. Defaults to None.

    Attributes:
        FIELD_TYPES (tuple[str]): Valid field types for Fields.
    """

    # Regular expression which validate the name
    VALID_NAME_REGEX = "^[A-z][A-z0-9_]{1,97}[A-z0-9]$"

    # Valid field types for fields
    FIELD_TYPES = (
        "SHORT",
        "LONG",
        "BIGINTEGER",
        "FLOAT",
        "DOUBLE",
        "TEXT",
        "DATE",
        "DATEONLY",
        "TIMEONLY",
        "TIMESTAMPOFFSET",
        "BLOB",
        "GUID",
        "GLOBALID",
        "OBJECTID",
        "RASTER",
        "SHAPE",
    )


    # Instance Properties
    _dataset:Datasets = None
    _field_type:str = None
    _precision:Union[int, None] = None
    _scale:Union[int, None] = None
    _length:Union[int, None] = None
    _alias:str = None
    _nullable:bool = None
    _required:bool = None
    _default:any = None
    _domain:Union["Domains", None] = None
    _meta_summary:str = None


    #pylint: disable-next=too-many-arguments
    def __init__(self, name:str, field_type:str, precision:Union[int, None]=None, scale:Union[int, None]=None,
                 length:Union[int, None]=None, alias:str=None, nullable:bool=True, required:bool=False,
                 default:any=None, domain:Union["Domains", None]=None, meta_summary:str=None) -> None:
        super().__init__(name)

        self.field_type = field_type
        self.precision = precision
        self.scale = scale
        self.length = length
        self.alias = alias if alias is not None else name
        self.nullable = nullable
        self.required = required
        self.default = default
        self.domain = domain
        self.meta_summary = meta_summary


    @property
    def dataset(self) -> Datasets:
        """Dataset to which this field belongs."""
        return self._dataset


    def _register_dataset(self, dataset):
        """Internal registration of the owning dataset."""
        if self._dataset is not None:
            raise AttributeError("Can only set the dataset once.")

        if not validation.is_structure_instance(dataset, "Dataset"):
            raise TypeError("Expecting an instance of the Dataset class.")

        self._dataset = dataset


    @property
    def field_type(self) -> str:
        """Type of data this field contains. Valid values found in Field.FIELD_TYPES."""
        return self._field_type


    @field_type.setter
    def field_type(self, value:str):
        self._field_type = validation.string(value, f"field type for field {self.name}", enum=Field.FIELD_TYPES)


    @property
    def precision(self) -> Union[int, None]:
        """Number of digits to be stored in a numeric field."""
        return self._precision


    @precision.setter
    def precision(self, value:Union[int, None]):
        if self.field_type not in ["SHORT", "LONG", "FLOAT", "DOUBLE"] and value is not None:
            raise ValueError(f"Value for {self.name} field's precision can only be None as the field is not numeric.")

        self._precision = validation.integer_or_none(value, f"{self.name} field's precision")


    @property
    def scale(self) -> int:
        """Number of decimal places stored in a float or double field."""
        return self._scale


    @scale.setter
    def scale(self, value:Union[int, None]):
        if self.field_type not in ["FLOAT", "DOUBLE"] and value is not None:
            #pylint: disable-next=line-too-long
            raise ValueError(f"Value for {self.name} field's scale can only be None as the field is neither a float nor double.")

        self._scale = validation.integer_or_none(value, f"{self.name} field's scale")


    @property
    def length(self) -> Union[int, None]:
        """Length of a text field."""
        return self._length


    @length.setter
    def length(self, value:Union[int, None]):
        if not self.field_type == "TEXT" and value is not None:
            raise ValueError(f"Value for {self.name} field's length can only be None as the field is not text.")

        length = value
        if self.field_type == "TEXT" and value is None:
            length = 255

        self._length = validation.integer_or_none(length, f"{self.name} field's length")


    @property
    def alias(self) -> str:
        """Alternative name for the dataset used for labelling."""
        return self._alias


    @alias.setter
    def alias(self, value:str):
        self._alias = validation.string(value, f"{self.name} field's alias", min_len=3, max_len=100)


    @property
    def nullable(self) -> bool:
        """Whether the field can contain null values."""
        return self._nullable


    @nullable.setter
    def nullable(self, value:bool):
        self._nullable = validation.boolean(value, f"{self.name} field's nullability")


    @property
    def required(self) -> bool:
        """Whether the field is required by ArcGIS."""
        return self._required


    @required.setter
    def required(self, value:bool):
        self._required = validation.boolean(value, f"{self.name} field's requirement")


    @property
    def default(self) -> any:
        """Default value for the field."""
        return self._default


    @default.setter
    def default(self, value:any):
        if value is None:
            self._default = None
        else:
            converted = validation.by_field_type(value, self.field_type, f"{self.name} field's default value")
            if self.domain and self.domain.test_value(converted) is False:
                raise ValueError("Default value not valid in the domain.")

            self._default = converted


    @property
    def domain(self) -> Union["Domains", None]:
        """Domain that constrains values for this field."""
        return self._domain


    @domain.setter
    def domain(self, value:Union["Domains", None]):
        if value is not None:
            if not validation.is_structure_instance(value, "Domain"):
                raise TypeError("Value for domain must be a Domain object or None.")

            if not self.field_type == value.field_type:
                raise TypeError("The domain has a different field type than the field to which its being added.")

            if self.default is not None:
                if value.test_value(self.default) is False:
                    raise ValueError("Default value is not valid is new domain.")

            value._register_field(self) #pylint: disable=protected-access

        self._domain = value


    @property
    def meta_summary(self) -> str:
        """Dataset's metadata summary."""
        return self._meta_summary


    @meta_summary.setter
    def meta_summary(self, value:str):
        validation.string_or_none(value, label="dataset's metadata summary")
        self._meta_summary = value