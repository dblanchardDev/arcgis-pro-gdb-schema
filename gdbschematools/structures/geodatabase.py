"""
Structure for the overall geodatabase.

Author: David Blanchard
"""

from typing import TYPE_CHECKING, Union

from . import validation
from .accessors.dataset_accessor import DatasetAccessor
from .accessors.domain_accessor import DomainsAccessor
from .accessors.feature_dataset_accessor import FeatureDatasetAccessor
from .gdb_element import GDBElement

if TYPE_CHECKING:
    from .feature_class import FeatureClass
    from .relationship import Relationship
    from .table import Table


# Alias for the various dataset types
Datasets = Union["FeatureClass", "Table", "Relationship"]


class Geodatabase(GDBElement):
    """Structure for an entire Geodatabase.

    Args:
        name (str): Name of the geodatabase.
        server (str, optional): Database server's hostname or IP. Defaults to None.
        meta_summary (str, optional): Metadata summary for the geodatabase. Defaults to None.
        workspace_type (str, optional): Type of workspace as described by ArcPy. Valid types found in
            Geodatabase.WORKSPACE_TYPES. Defaults to None.

    Attributes:
        WORKSPACE_TYPES (tuple[str]): Valid values for geodatabase workspace types.
    """

    # Regular expression which validate the name
    VALID_NAME_REGEX = "^[A-z][A-z0-9 ;_.-]{1,97}[A-z0-9]$"

    # Valid values for geodatabase workspace types
    WORKSPACE_TYPES = [
        "LOCAL_DATABASE",
        "REMOTE_DATABASE",
    ]


    # Geodatabase Instance Properties
    _feature_datasets:FeatureDatasetAccessor = None
    _domains:DomainsAccessor = None
    _datasets:DatasetAccessor = None

    _server:str = None
    _meta_summary:str = None
    _workspace_type:str = None


    def __init__(self, name:str, server:str=None, meta_summary:str=None, workspace_type:str=None) -> None:
        super().__init__(name)

        self._feature_datasets = FeatureDatasetAccessor(self)
        self._domains = DomainsAccessor(self)
        self._datasets = DatasetAccessor(self)

        self.meta_summary = meta_summary
        self.server = server
        self.workspace_type = workspace_type


    @property
    def meta_summary(self) -> str:
        """Geodatabase's metadata summary."""
        return self._meta_summary


    @meta_summary.setter
    def meta_summary(self, value:str):
        validation.string_or_none(value, label="geodatabase metadata summary")
        self._meta_summary = value


    @property
    def server(self) -> str:
        """Database server's hostname or IP."""
        return self._server


    @server.setter
    def server(self, value:str):
        validation.string_or_none(value, label="geodatabase server")
        self._server = value


    @property
    def workspace_type(self) -> str:
        """Whether the workspace is a local or remote database. Valid values in Geodatabase.WORKSPACE_TYPES."""
        return self._workspace_type


    @workspace_type.setter
    def workspace_type(self, value:str):
        validation.string_or_none(value, label="geodatabase workspace type", enum=Geodatabase.WORKSPACE_TYPES)
        self._workspace_type = value


    @property
    def domains(self) -> DomainsAccessor:
        """Accessor for the domains owned by the geodatabase, behaves like a sequence."""
        return self._domains


    @property
    def feature_datasets(self) -> FeatureDatasetAccessor:
        """Accessor for the feature datasets owned by the geodatabase, behaves like a sequence."""
        return self._feature_datasets


    @property
    def datasets(self) -> DatasetAccessor:
        """Accessor for the datasets (feature classes, tables, and relationship classes) owned by the geodatabase, behaves like a sequence.""" #pylint: disable=line-too-long
        return self._datasets