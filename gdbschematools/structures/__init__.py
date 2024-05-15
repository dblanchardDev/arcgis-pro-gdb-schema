"""
Structure for geodatabases and the elements it can contain.

Author: David Blanchard
"""

from .dataset import Dataset
from .domain import Domain, Range, RangeDomain, CodedDomain, Domains
from .feature_class import FeatureClass
from .feature_dataset import FeatureDataset
from .field import Field
from .geodatabase import Datasets, Geodatabase
from .relationship import Relationship, RelationshipMember
from .table import Table