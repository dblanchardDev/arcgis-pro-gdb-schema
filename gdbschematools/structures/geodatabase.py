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
    from .domain import Domain
    from .feature_dataset import FeatureDataset
    from .dataset import Dataset
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
    VALID_NAME_REGEX = "^(?:[A-Za-z]|[A-Za-z][A-Za-z0-9 ;_.-]{0,97}[A-Za-z0-9])$"

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

    def diff(self, other_gdb:"GDBElement") -> list:
        """Compares the meta_summary and children of two geodatabases.

        Args:
            other_gdb (GDBElement): Other geodatabase to compare with

        Returns:
            list: a list of differences between two geodatabases
        """
        diff_results = []
        if self.meta_summary != other_gdb.meta_summary:
            diff_results.append(f"Meta_summary of {self.name} GDB is different than meta_summary of {other_gdb.name} GDB.")

        # Compare Domains
        origin_domain_names = {domain.name for domain in self.domains}
        other_domain_names = {domain.name for domain in other_gdb.domains}

        domains_missing_in_origin = other_domain_names.difference(origin_domain_names)
        if domains_missing_in_origin:
            diff_results.append(f"The following domains are in the other GDB but not in the origin GDB: {', '.join(domains_missing_in_origin)}.")

        domains_missing_in_other = origin_domain_names.difference(other_domain_names)
        if domains_missing_in_other:
            diff_results.append(f"The following domains are in the origin GDB but not in the other GDB: {', '.join(domains_missing_in_other)}.")

        for domain_name in origin_domain_names.intersection(other_domain_names):
            origin_domain:"Domain" = self.domains[domain_name]
            other_domain:"Domain" = other_gdb.domains[domain_name]
            domain_diff_results = origin_domain.diff(other_domain)
            diff_results.extend(domain_diff_results)

        # Compare Feature Datasets
        origin_fds_names = {fds.name for fds in self.feature_datasets}
        other_fds_names = {fds.name for fds in other_gdb.feature_datasets}

        fds_missing_in_origin = other_fds_names.difference(origin_fds_names)
        if fds_missing_in_origin:
            diff_results.append(f"The following feature datasets are in the other GDB but not in the origin GDB: {', '.join(fds_missing_in_origin)}.")

        fds_missing_in_other = origin_fds_names.difference(other_fds_names)
        if fds_missing_in_other:
            diff_results.append(f"The following feature datasets are in the origin GDB but not in the other GDB: {', '.join(fds_missing_in_other)}.")

        for fds_name in origin_fds_names.intersection(other_fds_names):
            origin_fds:"FeatureDataset" = self.feature_datasets[fds_name]
            other_fds:"FeatureDataset" = other_gdb.feature_datasets[fds_name]
            fds_diff_results = origin_fds.diff(other_fds)
            diff_results.extend(fds_diff_results)


        # Compare Datasets
        origin_datasets = self.datasets
        other_datasets = other_gdb.datasets
        origin_ds_names = {ds.name for ds in self.datasets}
        other_ds_names = {ds.name for ds in other_datasets}

        ds_missing_in_origin = other_ds_names.difference(origin_ds_names)
        if ds_missing_in_origin:
            diff_results.append(f"The following datasets are in the other GDB but not in the origin GDB: {', '.join(ds_missing_in_origin)}.")

        ds_missing_in_other = origin_ds_names.difference(other_ds_names)
        if ds_missing_in_other:
            diff_results.append(f"The following datasets are in the origin GDB but not in the other GDB: {', '.join(ds_missing_in_other)}.")

        for ds_name in origin_ds_names.intersection(other_ds_names):
            origin_ds:"Dataset" = origin_datasets[ds_name]
            other_ds:"Dataset" = other_datasets[ds_name]
            ds_diff_results = origin_ds.diff(other_ds)
            diff_results.extend(ds_diff_results)

        return diff_results