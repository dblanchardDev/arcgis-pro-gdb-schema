"""
Classes that simplify children domains.

Author: David Blanchard
"""

from .base import AccessorWithGDB
from ..domain import CodedDomain, Domain, Range, RangeDomain


class DomainsAccessor(AccessorWithGDB):
    """Sequence of domains, behaves like a sequence."""


    def new(self, name:str, description:str, field_type:str, domain_type:str, split_policy:str, merge_policy:str,
            value_range:tuple[Range, Range]=None, schema:str=None) -> Domain:
        """Create a geodatabase domains.

        Args:
            name (str): Name of the domain.
            description (str): Description of the domain (for metadata).
            field_type (str): Field type that matches the data type of the field to which the attribute domain will be  assigned. Valid values found in Domain.FIELD_TYPES.
            domain_type (str): Type of domain. Valid values found in Domain.DOMAIN_TYPES.
            split_policy (str): Behavior of an attribute's values when a feature that is split. Valid values found in Domain.SPLIT_POLICIES.
            merge_policy (str): Behavior of an attribute's values when two feature are merged. Valid values found in Domain.MERGE_POLICIES.
            value_range (tuple[Range, Range], optional): Domain's minimum and maximum values in that order. Only required for RANGE domains. Defaults to None.
            schema (str, optional): Enterprise geodatabase owning schema. Default to None.

        Returns:
            Domain: The newly created domain.
        """ #pylint: disable=line-too-long

        if name in self:
            raise ValueError(f"A domain with the '{name}' name already exists.")

        domain = None
        if domain_type == "RANGE":
            domain = RangeDomain(name, description, field_type, split_policy, merge_policy, value_range, schema)
        else:
            domain = CodedDomain(name, description, field_type, split_policy, merge_policy, schema)

        if self._geodatabase:
            domain._register_geodatabase(self._geodatabase) #pylint: disable=protected-access

        self._elements.append(domain)
        self._elements.sort()

        return domain