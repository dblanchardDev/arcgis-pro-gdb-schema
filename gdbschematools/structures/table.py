"""
Structure for geodatabase tables.

Author: David Blanchard
"""

from typing import TYPE_CHECKING, Union

from . import validation
from .accessors.base import Accessor
from .dataset import Dataset

if TYPE_CHECKING:
    from .feature_dataset import FeatureDataset
    from .relationship import Relationship


class Table(Dataset):
    """Tables without geometry in a geodatabase (see FeatureClass for tables with geometry).

    Args:
        name (str): Name given to the dataset.
        alias (str, optional): Alias to the name used as a label. Default to the name.
        schema (str, optional): Enterprise geodatabase owning schema. Default to None.
        is_archived (bool, optional): Whether archiving is enabled on the dataset. Defaults to False.
        is_versioned (bool, optional): Whether versioning is enabled on the dataset. Defaults to False.
        oid_is_64 (bool, optional): Whether the OBJECTID field is a 64-bit integer. Defaults to None.
        dsid (int, optional): Dataset's identifier in enterprise geodatabases. Defaults to None.
        meta_summary (str, optional): Metadata summary for the geodatabase. Defaults to None.
        feature_dataset (FeatureDataset, optional): Feature dataset that contains this table. Defaults to None.
    """

    _relationship_classes:Accessor = None
    _subtype_field_name:str = None
    _subtype_default_code:str = None


    #pylint: disable=too-many-arguments
    def __init__(self, name:str, alias:str=None, schema:Union[str, None]=None, is_archived:bool=False,
                 is_versioned:bool=False, oid_is_64:bool=None, dsid:int=None, meta_summary:str=None,
                 feature_dataset:"FeatureDataset"=None) -> None:

        if self.dataset_type is None:
            self.dataset_type = "Table"

        super().__init__(name, schema, is_archived, is_versioned, oid_is_64, dsid, meta_summary, feature_dataset)

        self.alias = alias if alias is not None else name
        self._relationship_classes = Accessor()


    @property
    def alias(self) -> str:
        """Alternative name for the dataset used for labelling."""
        return self._alias


    @alias.setter
    def alias(self, value:str):
        self._alias = validation.string(value, "dataset alias", min_len=3, max_len=100)


    @property
    def relationship_classes(self) -> Accessor:
        """Relationship classes in which this table participates."""
        return self._relationship_classes


    def _register_relationship_classes(self, relationship_class:"Relationship"):
        """Register a table as participating in a relationship class.

        Args:
            relationship_class (Relationship): Instance of Relationship class.
        """
        if not validation.is_structure_instance(relationship_class, "Relationship"):
            raise TypeError("Table's relationship class must be an instance of Relationship class.")
        self._relationship_classes._append(relationship_class) #pylint: disable=protected-access