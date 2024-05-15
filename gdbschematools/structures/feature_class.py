"""
Structure for geodatabase feature classes.

Author: David Blanchard
"""

from typing import TYPE_CHECKING, Union

from arcpy import SpatialReference

from . import validation
from .table import Table

if TYPE_CHECKING:
    from .feature_dataset import FeatureDataset


class FeatureClass(Table):
    """Tables without geometry in a geodatabase (see FeatureClass for tables with geometry).

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

    Attributes:
        GEOMETRY_TYPES (tuple[str]): Valid geometry types for feature classes.
    """

    # Valid geometry types
    GEOMETRY_TYPES = (
        "POINT",
        "MULTIPOINT",
        "POLYGON",
        "POLYLINE",
        "MULTIPATCH",
    )


    # Instance Properties
    _geometry_type:str = None
    _spatial_ref:SpatialReference = None
    _has_z:bool = None
    _has_m:bool = None


    #pylint: disable-next=too-many-arguments
    def __init__(self, name:str, geometry_type:str, spatial_ref:SpatialReference=None, has_m:bool=False,
                 has_z:bool=False, alias:str=None, schema:Union[str, None]=None, is_archived:bool=False,
                 is_versioned:bool=False, oid_is_64:bool=None, dsid:int=None, meta_summary:str=None,
                 feature_dataset:"FeatureDataset"=None) -> None:

        if self.dataset_type is None:
            self.dataset_type = "FeatureClass"

        super().__init__(name, alias, schema, is_archived, is_versioned, oid_is_64, dsid, meta_summary,
                         feature_dataset)

        self.geometry_type = geometry_type
        self.spatial_ref = spatial_ref
        self.has_m = has_m
        self.has_z = has_z


    @property
    def geometry_type(self) -> str:
        """Geometry type of the feature class. Valid values in FeatureClass.GEOMETRY_TYPES."""
        return self._geometry_type


    @geometry_type.setter
    def geometry_type(self, value:str):
        self._geometry_type = validation.string(value, "geometry type", enum=FeatureClass.GEOMETRY_TYPES)


    @property
    def spatial_ref(self) -> SpatialReference:
        """The geometries spatial reference properties."""
        return self._spatial_ref


    @spatial_ref.setter
    def spatial_ref(self, value:SpatialReference):
        if not isinstance(value, SpatialReference):
            raise TypeError("Spatial Reference value must be an arcpy.SpatialReference object.")

        self._spatial_ref = value


    @property
    def has_m(self):
        """Whether the feature class has linear measurement values."""
        return self._has_m


    @has_m.setter
    def has_m(self, value:bool):
        self._has_m = validation.boolean(value, "has-m")


    @property
    def has_z(self):
        """Whether the feature class has elevation values."""
        return self._has_z


    @has_z.setter
    def has_z(self, value:bool):
        self._has_z = validation.boolean(value, "has-z")