"""
Structure for geodatabase tables, feature classes, and relationship classes.

Author: David Blanchard
"""

import warnings
from typing import TYPE_CHECKING, Union

from . import validation
from .accessors.field_accessor import FieldAccessor
from .accessors.subtype_accessor import SubtypeCodeAccessor
from .gdb_element import GDBElementWithParent

if TYPE_CHECKING:
    from .feature_dataset import FeatureDataset
    from .field import Field


class Subtype():
    """Description of the subtypes applied to a dataset.

    Args:
        dataset (Dataset): Dataset to which the subtype is applied.
        field (Field): Field in which the subtype is stored.
    """

    _dataset:"Dataset" = None
    _codes:SubtypeCodeAccessor = None
    _field:"Field" = None


    def __init__(self, dataset:"Dataset", field:"Field") -> None:
        self._dataset = dataset
        self._codes = SubtypeCodeAccessor(self._dataset.fields)

        # Validate and set field
        if not validation.is_structure_instance(field, "Field"):
            raise TypeError("Field for subtype must be instance of Structure.Field.")

        if field.field_type not in ["BIGINTEGER", "SHORT", "LONG"]:
            raise TypeError("Field for subtype must be an integer (big, short, or long).")


        if not field.dataset == dataset:
            raise ValueError("Field provided for subtype is not a member of the dataset.")

        self._field = field


    @property
    def dataset(self) -> "Dataset":
        """Dataset to which this subtype belongs."""
        return self._dataset


    @property
    def field(self) -> "Field":
        """Field in which the subtype value is stored."""
        return self._field


    @property
    def default(self) -> int:
        """Default code for the subtype field."""
        if self.field.default is not None and self.field.default not in self._codes:
            raise ValueError("The default values for the subtype field is not a value in the subtype codes.")
        return self._field.default


    @property
    def codes(self) -> SubtypeCodeAccessor:
        """Dictionary like accessor for the subtype codes."""
        return self._codes


#pylint: disable-next=too-many-instance-attributes
class Dataset(GDBElementWithParent):
    """The base class for all Geodatabase datasets. You wouldn't normally use this class directly. Instead, use Table,
    FeatureClass, or RelationshipClass.

    Args:
        name (str): Name given to the dataset.
        schema (str, optional): Enterprise geodatabase owning schema. Default to None.
        is_archived (bool, optional): Whether archiving is enabled on the dataset. Defaults to False.
        is_versioned (bool, optional): Whether versioning is enabled on the dataset. Defaults to False.
        oid_is_64 (bool, optional): Whether the OBJECTID field is a 64-bit integer. Defaults to None.
        dsid (int, optional): Dataset's identifier in enterprise geodatabases. Defaults to None.
        meta_summary (str, optional): Metadata summary for the geodatabase. Defaults to None.
        feature_dataset (FeatureDataset, optional): Feature dataset that contains this dataset. Defaults to None.

    Attributes:
        DATASET_TYPES (tuples[str]): Dataset types that are supported by this class.
    """ #pylint: disable=line-too-long

    # Regular expression which validate the name
    VALID_NAME_REGEX = "^[A-z][A-z0-9_]{1,97}[A-z0-9]$"

    # Dataset types that are supported by this class
    DATASET_TYPES = (
        "FeatureClass",
        "Table",
        "RelationshipClass",
    )


    # Field types that are excluded from being added to this dataset type
    FIELD_TYPE_EXCLUSIONS = []


    # Instance Properties
    _feature_dataset:"FeatureDataset" = None
    _schema:str = None
    _dataset_type:str = None
    _is_archived:bool = None
    _is_versioned:bool = None
    _dsid:int = None
    _meta_summary:str = None
    _fields:FieldAccessor = None
    _oid_is_64:bool = None
    _subtype:Subtype = None


    #pylint: disable=too-many-arguments
    def __init__(self, name:str, schema:Union[str, None]=None, is_archived:bool=False, is_versioned:bool=False,
                 oid_is_64:bool=None, dsid:int=None, meta_summary:str=None,
                 feature_dataset:"FeatureDataset"=None) -> None:

        if self.dataset_type is None:
            #pylint: disable-next=line-too-long
            warnings.warn("The Dataset class should not be instantiated directly. Use the Table, FeatureClass, or RelationshipClass classes instead.")

        super().__init__(name)
        self._fields = FieldAccessor(self, self.__class__.FIELD_TYPE_EXCLUSIONS)
        self.schema = schema
        self.is_archived = is_archived
        self.is_versioned = is_versioned
        self.oid_is_64 = oid_is_64
        self.dsid = dsid
        self.meta_summary = meta_summary

        if feature_dataset is not None:
            if not validation.is_structure_instance(feature_dataset, "FeatureDataset"):
                raise TypeError("Value for feature_dataset must be a FeatureDataset.")

            self._feature_dataset = feature_dataset
            feature_dataset._register_dataset(self)


    @property
    def feature_dataset(self) -> Union["FeatureDataset", None]:
        """Feature dataset this dataset is a part of."""
        return self._feature_dataset


    @property
    def dataset_type(self) -> str:
        """Type of data contained within the dataset. Valid values in Dataset.DATASET_TYPE."""
        return self._dataset_type


    @dataset_type.setter
    def dataset_type(self, value:str):
        if self._dataset_type is not None:
            raise AttributeError("Cannot change the dataset type once set.")
        self._dataset_type = validation.string(value, "dataset type", enum=Dataset.DATASET_TYPES)


    @property
    def schema(self) -> Union[str, None]:
        """Enterprise database schema."""
        return self._schema


    @schema.setter
    def schema(self, value:Union[str, None]):
        self._schema = validation.string_or_none(value, "dataset schema", min_len=1, max_len=100)


    @property
    def is_archived(self) -> bool:
        """Whether dataset has been archived. Only for Enterprise geodatabases."""
        return self._is_archived


    @is_archived.setter
    def is_archived(self, value:bool):
        self._is_archived = validation.boolean(value, "dataset is archived")


    @property
    def is_versioned(self) -> bool:
        """Whether the dataset has versioning turned on."""
        return self._is_versioned


    @is_versioned.setter
    def is_versioned(self, value:bool):
        self._is_versioned = validation.boolean(value, "dataset is versioned")


    @property
    def dsid(self) -> Union[int, None]:
        """Dataset's unique identifier."""
        return self._dsid


    @dsid.setter
    def dsid(self, value:Union[int, None]):
        self._dsid = validation.integer_or_none(value, "dataset DSID")    #pylint: disable-next=too-many-arguments


    @property
    def meta_summary(self) -> str:
        """Dataset's metadata summary."""
        return self._meta_summary


    @meta_summary.setter
    def meta_summary(self, value:str):
        validation.string_or_none(value, label="dataset's metadata summary")
        self._meta_summary = value


    @property
    def fields(self) -> FieldAccessor:
        """Sequence like accessor for fields contained with the dataset."""
        return self._fields


    @property
    def oid_is_64(self) -> bool:
        """Whether the OBJECTID field is a 64-bit integer."""
        return self._oid_is_64


    @oid_is_64.setter
    def oid_is_64(self, value:bool):
        validation.boolean_or_none(value, label="dataset's objectid is 64-bit")
        self._oid_is_64 = value


    @property
    def subtype(self) -> Subtype:
        """The subtype description (or None if no subtype is set)."""
        return self._subtype


    def set_subtype(self, field:"Field") -> Subtype:
        """Set the subtype for a dataset (to be done after defining fields)."""
        if self._subtype is not None:
            raise AttributeError("Cannot change the subtype field once it is set.")

        self._subtype = Subtype(dataset=self, field=field)
        return self._subtype