"""
Classes that simplify children element access.

Author: David Blanchard
"""

from typing import Iterator, TYPE_CHECKING, Union

from .base import AccessorWithGDB, SubAccessor
from ..feature_class import FeatureClass
from ..relationship import Relationship
from ..table import Table

if TYPE_CHECKING:
    from arcpy import SpatialReference

    from ..feature_dataset import FeatureDataset
    from ..geodatabase import Geodatabase


# Alias for the various dataset types
Datasets = Union[FeatureClass, Table, Relationship]


class _TableAccessor(SubAccessor):

    def __init__(self, geodatabase:"Geodatabase", accessor:AccessorWithGDB) -> None:
        super().__init__(geodatabase, accessor, "Table")


    #pylint: disable-next=too-many-arguments
    def new(self, name:str, alias:str=None, schema:Union[str, None]=None, is_archived:bool=False,
                  is_versioned:bool=False, oid_is_64:bool=None, dsid:int=None, meta_summary:str=None,
                  feature_dataset:"FeatureDataset"=None) -> Table:
        """Create a table in the geodatabase.

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

        Returns:
            Table: The newly created table.
        """ #pylint: disable=line-too-long

        if name in self._accessor:
            raise ValueError(f"A dataset with the '{name}' name already exists.")

        table = Table(name, alias, schema, is_archived, is_versioned, oid_is_64, dsid, meta_summary,
                      feature_dataset)

        if self._geodatabase:
            table._register_geodatabase(self._geodatabase) #pylint: disable=protected-access

        self._append(table)
        return table


class _FeatureClassAccessor(SubAccessor):

    def __init__(self, geodatabase:"Geodatabase", accessor:AccessorWithGDB) -> None:
        super().__init__(geodatabase, accessor, "FeatureClass")


    #pylint: disable-next=too-many-arguments
    def new(self, name:str, geometry_type:str, spatial_ref:"SpatialReference"=None, has_m:bool=False,
                          has_z:bool=False, alias:str=None, schema:Union[str, None]=None, is_archived:bool=False,
                          is_versioned:bool=False, oid_is_64:bool=None, dsid:int=None, meta_summary:str=None,
                          feature_dataset:"FeatureDataset"=None) -> FeatureClass:
        """Create a feature class in the geodatabase.

        Args:
            name (str): Name given to the dataset.
            geometry_type (str): Geometry type of the feature class. Valid values in FeatureClass.GEOMETRY_TYPES.
            spatial_ref (arcpy.SpatialReference): The horizontal and vertical (optional) spatial reference of the geometry.
            has_m (bool, optional): Whether the feature class has linear measurement values. Defaults to False.
            has_z (bool, optional): Whether the feature class has elevation values. Defaults to False.
            alias (str, optional): Alias to the name used as a label. Defaults to the name.
            schema (str, optional): Enterprise geodatabase owning schema. Default to None.
            is_archived (bool, optional): Whether archiving is enabled on the dataset. Defaults to False.
            is_versioned (bool, optional): Whether versioning is enabled on the dataset. Defaults to False.
            oid_is_64 (bool, optional): Whether the OBJECTID field is a 64-bit integer. Defaults to None.
            dsid (int, optional): Dataset's identifier in enterprise geodatabases. Defaults to None.
            meta_summary (str, optional): Metadata summary for the geodatabase. Defaults to None.
            feature_dataset (FeatureDataset, optional): Feature dataset that contains this feature class. Defaults to None.

        Returns:
            FeatureClass: The newly created feature class.
        """ #pylint: disable=line-too-long

        if name in self._accessor:
            raise ValueError(f"A dataset with the '{name}' name already exists.")

        feat_cl = FeatureClass(name, geometry_type, spatial_ref, has_m, has_z, alias, schema, is_archived,
                               is_versioned, oid_is_64, dsid, meta_summary, feature_dataset)

        if self._geodatabase:
            feat_cl._register_geodatabase(self._geodatabase) #pylint: disable=protected-access

        self._append(feat_cl)
        return feat_cl


class _RelationshipClassAccessor(SubAccessor):

    def __init__(self, geodatabase:"Geodatabase", accessor:AccessorWithGDB) -> None:
        super().__init__(geodatabase, accessor, "RelationshipClass")


    #pylint: disable-next=too-many-arguments,too-many-locals
    def new(self, name:str, origin_table:"Table", destination_table:str, relationship_type:str, forward_label:str,
            backward_label:str, notification:str, cardinality:str, attributed:str, origin_primary_key:str,
            origin_foreign_key:str, destination_primary_key:Union[str, None]=None,
            destination_foreign_key:Union[str, None]=None, schema:Union[str, None]=None, is_archived:str=False,
            is_versioned:bool=False, oid_is_64:bool=None, dsid:int=None, meta_summary:str=None,
            feature_dataset:"FeatureDataset"=None) -> Relationship:
        """Create a new relationship class linking two tables together.

        Args:
            name (str): Name of the relationship class.
            origin_table (Table): Originating table for the relationship.
            destination_table (str): Destination table for the relationship.
            relationship_type (str): Whether the relationship is simple or composite (each destination record must be related to an origin record). Valid values in Relationship.RELATIONSHIP_TYPES.
            forward_label (str): Label used to identify origin to destination.
            backward_label (str): Label used to identify destination to origin.
            notification (str): Whether changes to one table are propagated to the other table. Valid values in Relationship.NOTIFICATIONS.
            cardinality (str): Number of related values in destination relative to origin. Valid values in Relationship.CARDINALITIES.
            attributed (str): Whether the relationship class has attributes other than the keys.
            origin_primary_key (str): Primary key field name for the origin table.
            origin_foreign_key (str): Foreign key field name for the intermediate table or the destination table depending on the relationship type.
            destination_primary_key (Union[str, None], optional): Primary key field name for the destination table. Required for many to many relationships or attributed relationships. Defaults to None.
            destination_foreign_key (Union[str, None], optional): Foreign key field name for the destination table. Required for many to many relationships or attributed relationships. Defaults to None.
            schema (str, optional): Enterprise geodatabase owning schema. Default to None.
            is_archived (bool, optional): Whether archiving is enabled on the dataset. Defaults to False.
            is_versioned (bool, optional): Whether versioning is enabled on the dataset. Defaults to False.
            oid_is_64 (bool, optional): Whether the OBJECTID field is a 64-bit integer. Defaults to None.
            dsid (int, optional): Dataset's identifier in enterprise geodatabases. Defaults to None.
            meta_summary (str, optional): Metadata summary for the geodatabase. Defaults to None.
            feature_dataset (FeatureDataset, optional): Feature dataset that contains this relationship class. Defaults to None.

        Returns:
            Relationship: The newly created relationship class.
        """ #pylint: disable=line-too-long

        if name in self._accessor:
            raise ValueError(f"A dataset with the '{name}' name already exists.")

        rel_cl = Relationship(name, origin_table, destination_table, relationship_type, forward_label, backward_label,
                              notification, cardinality, attributed, origin_primary_key, origin_foreign_key,
                              destination_primary_key, destination_foreign_key, schema, is_archived, is_versioned,
                              oid_is_64, dsid, meta_summary, feature_dataset)

        if self._geodatabase:
            rel_cl._register_geodatabase(self._geodatabase) #pylint: disable=protected-access

        self._append(rel_cl)
        return rel_cl


class ReadOnlyDatasetAccessor(AccessorWithGDB):
    """Sequence of datasets (tables, feature classes, and relationship classes), behaves like a sequence.

        Args:
            geodatabase (Geodatabase): Reference to the geodatabase object that will own the datasets.
        """

    _tables:_TableAccessor = None
    _feature_classes:_FeatureClassAccessor = None
    _relationship_classes:_RelationshipClassAccessor = None


    def __init__(self, geodatabase:"Geodatabase") -> None:
        super().__init__(geodatabase)
        self._tables = SubAccessor(accessor=self, geodatabase=geodatabase, dataset_type="Table")
        self._feature_classes = SubAccessor(accessor=self, geodatabase=geodatabase, dataset_type="FeatureClass")
        self._relationship_classes = SubAccessor(accessor=self, geodatabase=geodatabase,
                                                 dataset_type="RelationshipClass")


    @property
    def tables(self) -> SubAccessor:
        """Filtered iterable of datasets of the table type."""
        return self._tables


    @property
    def feature_classes(self) -> SubAccessor:
        """Filtered iterable of datasets of the feature class type."""
        return self._feature_classes


    @property
    def relationship_classes(self) -> SubAccessor:
        """Filtered iterable of datasets of the relationship class type."""
        return self._relationship_classes


    @property
    def tables_and_feature_classes(self) -> list[Datasets]:
        """Filtered list of tables and feature classes."""
        combined = list(self.tables) + list(self.feature_classes)
        combined.sort()
        return combined


    def walk(self) -> Iterator[tuple["FeatureDataset", tuple["FeatureClass"], tuple["Table"], tuple["Relationship"]]]:
        """Walk through all the datasets, grouped by their participation in feature datasets.

        Returns:
            IteratorIterator[tuple["FeatureDataset", tuple("FeatureClass"), tuple("Table"), tuple("Relationship")]]: The feature dataset (or none for datasets not participating in one), followed by a sequence of feature classes, a sequence of tables, and a sequence of relationships.
        """ #pylint: disable=line-too-long

        all_feat_dts = []
        top_level_feat_cls = []
        top_level_tables = []
        top_level_rel_cls = []

        for dataset in self._elements:
            if dataset.feature_dataset is not None:
                if dataset.feature_dataset not in all_feat_dts:
                    all_feat_dts.append(dataset.feature_dataset)

            elif dataset.dataset_type == "FeatureClass":
                top_level_feat_cls.append(dataset)
            elif dataset.dataset_type == "Table":
                top_level_tables.append(dataset)
            elif dataset.dataset_type == "RelationshipClass":
                top_level_rel_cls.append(dataset)

        all_feat_dts.sort()
        top_level_feat_cls.sort()
        top_level_tables.sort()
        top_level_rel_cls.sort()

        for feat_dts in all_feat_dts:
            dts = feat_dts.datasets
            yield (feat_dts, tuple(dts.feature_classes), tuple(dts.tables), tuple(dts.relationship_classes))

        yield (None, tuple(top_level_feat_cls), tuple(top_level_tables), tuple(top_level_rel_cls))


class DatasetAccessor(ReadOnlyDatasetAccessor):
    """Sequence of datasets (tables, feature classes, and relationship classes), behaves like a sequence. Sub-accessors include 'new' method to create new datasets within.

    Args:
        geodatabase (Geodatabase): Reference to the geodatabase object that will own the datasets.
    """ #pylint: disable=line-too-long

    _tables:_TableAccessor = None
    _feature_classes:_FeatureClassAccessor = None
    _relationship_classes:_RelationshipClassAccessor = None


    def __init__(self, geodatabase:"Geodatabase") -> None:
        super().__init__(geodatabase)
        self._tables = _TableAccessor(accessor=self, geodatabase=geodatabase)
        self._feature_classes = _FeatureClassAccessor(accessor=self, geodatabase=geodatabase)
        self._relationship_classes = _RelationshipClassAccessor(accessor=self, geodatabase=geodatabase)