"""
Structure for geodatabase domains.

Author: David Blanchard
"""

import datetime
from typing import TYPE_CHECKING, Union

from . import validation
from .accessors.base import Accessor
from .accessors.code_accessor import CodeAccessor
from .gdb_element import GDBElementWithParent
from . import utility

if TYPE_CHECKING:
    from .field import Field


class Domain(GDBElementWithParent):  # pylint: disable=too-many-instance-attributes
    """A base class for geodatabase domains. Use the RangeDomain and CodedDomain classes to instantiate a Domain.

    Args:
        name (str): Name of the domain.
        description (str): Description of the domain, value displayed in queries.
        field_type (str): Field type that matches the data type of the field to which the attribute domain will be
            assigned. Valid values found in Domain.FIELD_TYPES.
        split_policy (str): Behavior of an attribute's values when a feature that is split. Valid values found
            in Domain.SPLIT_POLICIES.
        merge_policy (str): Behavior of an attribute's values when two feature are merged. Valid values found in
            Domain.MERGE_POLICIES.
        schema (str, optional): Enterprise geodatabase owning schema. Default to None.

    Attributes:
        FIELD_TYPES (tuple[str]): Valid field types for domains.
        DOMAIN_TYPES (tuple[str]): Valid domain types for domains.
        SPLIT_POLICIES (tuple[str]): Valid split policies for domains.
        MERGE_POLICIES (tuple[str]): Valid merge policies for domains.
    """

    # Valid field types for domains
    FIELD_TYPES = (
        "SHORT",
        "LONG",
        "BIGINTEGER",
        "FLOAT",
        "DOUBLE",
        "TEXT",
        "DATE",
        "DATEONLY",
        "TIMEONLY",
    )

    # Valid domain types
    DOMAIN_TYPES = (
        "CODED",
        "RANGE",
    )

    # Valid split policies for domains
    SPLIT_POLICIES = (
        "DEFAULT",
        "DUPLICATE",
        "GEOMETRY_RATIO",
    )

    # Valid merge policies for domains
    MERGE_POLICIES = (
        "DEFAULT",
        "SUM_VALUES",
        "AREA_WEIGHTED",
    )

    # Instance Properties
    _fields: Accessor = None
    _description: str = None
    _field_type: str = None
    _domain_type: str = None
    _split_policy: str = None
    _merge_policy: str = None
    _schema: str = None

    def __init__(
        self, name: str, description: str, field_type: str, split_policy: str, merge_policy: str, schema: str = None
    ):
        super().__init__(name)
        self._fields = Accessor()
        self.description = description
        self.field_type = field_type
        self.split_policy = split_policy
        self.merge_policy = merge_policy
        self.schema = schema

    @property
    def description(self) -> str:
        """Description of the domain."""
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = validation.string(value, label="domain description")

    @property
    def field_type(self) -> str:
        """Field type that matches the data type of the field to which the attribute domain will be assigned.
        Valid values in DOMAIN.FIELD_TYPES."""
        return self._field_type

    @field_type.setter
    def field_type(self, value: str):
        self._field_type = validation.string(value, label="domain field type", enum=Domain.FIELD_TYPES)

    @property
    def domain_type(self) -> str:
        """Domain type, either coded or range. Valid values in Domain.DOMAIN_TYPES."""
        return self._domain_type

    @domain_type.setter
    def domain_type(self, value: str):
        self._domain_type = validation.string(value, label="domain type", enum=Domain.DOMAIN_TYPES)

    @property
    def split_policy(self) -> str:
        """Behavior of an attribute's values when a feature that is split. Valid values in Domain.SPLIT_POLICIES."""
        return self._split_policy

    @split_policy.setter
    def split_policy(self, value: str):
        self._split_policy = validation.string(value, label="domain split policy", enum=Domain.SPLIT_POLICIES)

    @property
    def merge_policy(self) -> str:
        """Behavior of an attribute's values when two feature are merged. Valid values in Domain.MERGE_POLICIES."""
        return self._merge_policy

    @merge_policy.setter
    def merge_policy(self, value: str):
        self._merge_policy = validation.string(value, label="domain merge policy", enum=Domain.MERGE_POLICIES)

    @property
    def fields(self) -> Accessor:
        """Fields that use this domain."""
        return self._fields

    def _register_field(self, field: "Field"):
        """Register a field as a user of this domain.

        Args:
            field (Field): Instance of field class.
        """
        if not validation.is_structure_instance(field, "Field"):
            raise TypeError("Domain field must be an instance of Field class.")
        self.fields._append(field)  # pylint: disable=protected-access

    @property
    def schema(self) -> str:
        """Owning schema of the domain."""
        return self._schema

    @schema.setter
    def schema(self, value: str):
        self._schema = validation.string_or_none(value, label="domain schema")

    def test_value(self, value) -> bool:
        """Test whether a value is valid in the domain.

        Args:
            value (any): Value to be tested.

        Returns:
            bool: Whether it is valid.
        """
        raise NotImplementedError("Must be implemented by subclasses.")

    def diff(self, other_domain: "Domain") -> list:
        """It compares the properties of two domains.

        Args:
            other_domain (Domain): Other domain to compare with

        Returns:
            list: a list of differences between two domains
        """

        properties = ["name", "schema", "description", "field_type", "domain_type", "split_policy", "merge_policy"]
        diff_results = utility.diff(self, other_domain, "domain", properties)
        return diff_results


# Alias for the various values valid for a Range Domain
Range = Union[int, float, complex, datetime.datetime.date, datetime.time]


class RangeDomain(Domain):
    """A geodatabase range domain.

    Args:
        name (str): Name of the domain.
        description (str): Description of the domain, value displayed in queries.
        field_type (str): Field type that matches the data type of the field to which the attribute domain will be
            assigned. Valid values: "SHORT", "LONG", "BIGINTEGER", "FLOAT", "DOUBLE", "TEXT", "DATE", "DATEONLY",
            "TIMEONLY".
        split_policy (str): Behavior of an attribute's values when a feature that is split. Valid values: "DEFAULT",
            "DUPLICATE", "GEOMETRY_RATIO".
        merge_policy (str): Behavior of an attribute's values when two feature are merged. Valid values: "DEFAULT",
            "SUM_VALUES", "AREA_WEIGHTED".
        value_range (tuple[Range, Range]): Domain's minimum and maximum values in that order.
        schema (str, optional): Enterprise geodatabase owning schema. Default to None.
    """

    _minimum: Range = None
    _maximum: Range = None

    def __init__(
        self,
        name: str,
        description: str,
        field_type: str,
        split_policy: str,
        merge_policy: str,
        value_range: tuple[Range, Range],
        schema: str = None,
    ):
        super().__init__(name, description, field_type, split_policy, merge_policy, schema)

        self.domain_type = "RANGE"

        if field_type == "TEXT":
            raise ValueError("Range Domains cannot be used with a TEXT field.")

        if value_range is None:
            raise ValueError("Value range must be specified when creating a RangeDomain.")

        if not isinstance(value_range, (tuple, list)):
            raise TypeError("Value range must be specified as a tuple.")

        if not len(value_range) == 2:
            raise ValueError("Value range in a range domain must contain 2 values.")

        self.minimum = value_range[0]
        self.maximum = value_range[1]

    @property
    def minimum(self) -> Range:
        """Minimum value for the range domain."""
        return self._minimum

    @minimum.setter
    def minimum(self, value: Range):
        self._minimum = validation.by_field_type(value, self.field_type, f"{self.name} domain minimum")

    @property
    def maximum(self) -> Range:
        """Maximum value for the range domain."""
        return self._maximum

    @maximum.setter
    def maximum(self, value: Range):
        updated = validation.by_field_type(value, self.field_type, f"{self.name} domain maximum")

        if updated < self._minimum:
            raise ValueError(f"Maximum value {value} for range domain {self.name} is smaller than minimum value.")

        self._maximum = updated

    def test_value(self, value) -> bool:
        return (value >= self.minimum) and (value <= self.maximum)  # pylint: disable=chained-comparison

    def diff(self, other_domain: "RangeDomain"):
        """Compares minimum and maximum of two range domains

        Args:
            other_domain (RangeDomain): the other range domain to compare with

        Returns:
            list: A list of differences
        """
        diff_results = super().diff(other_domain)
        if self.minimum != other_domain.minimum:
            diff_results.append(
                f"minimum of {self.name} range domain {self.minimum} in the origin gdb and {other_domain.minimum} in the other gdb."
            )
        if self.maximum != other_domain.maximum:
            diff_results.append(
                f"maximum of {self.name} range domain is {self.maximum} in the origin gdb and {other_domain.maximum} in the other gdb."
            )
        return diff_results


class CodedDomain(Domain):
    """A geodatabase coded value domain.

    Args:
        name (str): Name of the domain.
        description (str): Description of the domain, value displayed in queries.
        field_type (str): Field type that matches the data type of the field to which the attribute domain will be
            assigned. Valid values: "SHORT", "LONG", "BIGINTEGER", "FLOAT", "DOUBLE", "TEXT", "DATE", "DATEONLY",
            "TIMEONLY".
        domain_type (str): Type of domain. Valid values: "CODED", "RANGE".
        split_policy (str): Behavior of an attribute's values when a feature that is split. Valid values: "DEFAULT",
            "DUPLICATE", "GEOMETRY_RATIO".
        merge_policy (str): Behavior of an attribute's values when two feature are merged. Valid values: "DEFAULT",
            "SUM_VALUES", "AREA_WEIGHTED".
        schema (str, optional): Enterprise geodatabase owning schema. Default to None.
    """

    _codes: CodeAccessor = None

    def __init__(
        self, name: str, description: str, field_type: str, split_policy: str, merge_policy: str, schema: str = None
    ):
        super().__init__(name, description, field_type, split_policy, merge_policy, schema)

        self.domain_type = "CODED"
        self._codes = CodeAccessor(self)

    @property
    def codes(self) -> CodeAccessor:
        """Read-only dictionary like object of the coded values. Use its new method to add a new code."""
        return self._codes

    def test_value(self, value: any) -> bool:
        return value in self.codes

    def convert_value(self, value: any) -> any:
        """Convert a text code value to one that matches the domain's codes.

        Args:
            value (any): Coded value to convert.

        Returns:
            any: Code as found in the domain.
        """
        return validation.by_field_type(value, self.field_type, f"{self.name} domain code conversion")

    def diff(self, other_domain: "CodedDomain"):
        """Compares the codes of two coded domains

        Args:
            other_domain (CodedDomain): other coded domain to compare with

        Returns:
            list: A list of differences
        """
        diff_results = super().diff(other_domain)

        origin_code_names = {self.convert_value(code) for code in self.codes.keys()}
        other_code_names = {other_domain.convert_value(code) for code in other_domain.codes.keys()}

        codes_missing_in_origin = other_code_names.difference(origin_code_names)
        if codes_missing_in_origin:
            diff_results.append(
                f"The following codes are in the {other_domain.name} domain in the other GDB but not in the origin GDB: {', '.join(map(str, codes_missing_in_origin))}."
            )

        codes_missing_in_other = origin_code_names.difference(other_code_names)
        if codes_missing_in_other:
            diff_results.append(
                f"The following codes are in the {self.name} domain in origin GDB but not in the other GDB: {', '.join(map(str, codes_missing_in_other))}."
            )

        for code in origin_code_names.intersection(other_code_names):
            origin_code = self.codes[code]
            other_code = other_domain.codes[code]
            if origin_code.meta_summary != other_code.meta_summary:
                diff_results.append(
                    f"meta_summary of {code} domain code for {self.name} domain is {origin_code.meta_summary} in the origin GDB and {other_code.meta_summary} in the other GDB."
                )
            if origin_code.description != other_code.description:
                diff_results.append(
                    f"description of {code} domain code for {other_domain.name} domain is {origin_code.description} in the origin GDB and {other_code.description} in the other GDB."
                )

        return diff_results


# Type combining Range Domains and Coded-Value Domains
Domains = Union[RangeDomain, CodedDomain]
