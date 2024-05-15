"""
Structure for geodatabase feature dataset groupings.

Author: David Blanchard
"""

from typing import TYPE_CHECKING, Union

from . import validation
from .accessors.dataset_accessor import ReadOnlyDatasetAccessor
from .gdb_element import GDBElementWithParent

if TYPE_CHECKING:
    from .feature_class import FeatureClass
    from .relationship import Relationship
    from .table import Table


# Alias for the various dataset types
Datasets = Union["FeatureClass", "Table", "Relationship"]


class FeatureDataset(GDBElementWithParent):
    """A geodatabase feature dataset, which groups datasets together.

    Args:
        name (str): Name of the feature dataset.
        schema (str, optional): Enterprise geodatabase owning schema. Default to None.
        meta_summary (str, optional): Metadata summary for the feature dataset. Defaults to None.
    """

    # Regular expression which validate the name
    VALID_NAME_REGEX = "^[A-z][A-z0-9_]{1,97}[A-z0-9]$"

    _schema:str = None
    _datasets:ReadOnlyDatasetAccessor = None
    _meta_summary:str = None


    def __init__(self, name:str, schema:str=None, meta_summary:str=None) -> None:
        super().__init__(name)
        self.schema = schema
        self.meta_summary = meta_summary
        self._datasets = ReadOnlyDatasetAccessor(self._geodatabase)


    @property
    def schema(self) -> Union[str, None]:
        """Enterprise database schema."""
        return self._schema


    @schema.setter
    def schema(self, value:Union[str, None]):
        self._schema = validation.string_or_none(value, "dataset schema", min_len=1, max_len=100)


    @property
    def meta_summary(self) -> str:
        """Feature dataset's metadata summary."""
        return self._meta_summary


    @meta_summary.setter
    def meta_summary(self, value:str):
        validation.string_or_none(value, label="feature dataset's metadata summary")
        self._meta_summary = value


    @property
    def datasets(self) -> ReadOnlyDatasetAccessor:
        """Accessor for the datasets (feature classes, tables, and relationship classes) contained within the feature dataset, behaves like a sequence.""" #pylint: disable=line-too-long
        return self._datasets


    def _register_dataset(self, dataset:Datasets):
        """Internal mechanic to register a dataset as being contained by this feature dataset.

        Args:
            dataset (Datasets): Reference to dataset object.
        """
        if not validation.is_structure_instance(dataset, "Dataset"):
            raise TypeError("Feature dataset members must be an instance of Dataset.")

        self._datasets._append(dataset) #pylint: disable=protected-access