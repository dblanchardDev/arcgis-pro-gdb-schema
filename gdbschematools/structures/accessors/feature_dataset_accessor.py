"""
Classes that simplify children feature datasets.

Author: David Blanchard
"""

from .base import AccessorWithGDB
from ..feature_dataset import FeatureDataset


class FeatureDatasetAccessor(AccessorWithGDB):
    """Sequence of feature datasets, behaves like a sequence."""


    def new(self, name:str, schema:str=None, meta_summary:str=None) -> FeatureDataset:
        """Create a geodatabase feature dataset, which groups datasets together.

        Args:
            name (str): Name of the feature dataset.
            schema (str, optional): Enterprise geodatabase owning schema. Default to None.
            meta_summary (str, optional): Metadata summary for the feature dataset. Defaults to None.

        Returns:
            FeatureDataset: The newly created feature dataset.
        """ #pylint: disable=line-too-long

        if name in self:
            raise ValueError(f"A feature dataset with the '{name}' name already exists.")

        feat_dts = FeatureDataset(name, schema, meta_summary)

        if self._geodatabase:
            feat_dts._register_geodatabase(self._geodatabase) #pylint: disable=protected-access

        self._elements.append(feat_dts)
        self._elements.sort()

        return feat_dts