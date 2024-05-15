"""
Structure for geodatabase relationship classes.

Author: David Blanchard
"""

from typing import TYPE_CHECKING, Union

from . import validation
from .dataset import Dataset

if TYPE_CHECKING:
    from .accessors.field_accessor import FieldAccessor
    from .feature_dataset import FeatureDataset
    from .table import Table


class RelationshipMember():
    """A table that is a member of a relationship class, either as an origin or destination table.

    Args:
        table (Table): The table (or feature class) that is a member of the relationship.
        primary_key (str): Name of the field that is the primary key.
        foreign_key (str): Name of the field that is the foreign key.
    """

    # Instance Properties
    _table:"Table" = None
    _primary_key:str = None
    _foreign_key:str = None


    def __init__(self, table:"Table", primary_key:str, foreign_key:str) -> None:
        self.table = table
        self.primary_key = primary_key
        self.foreign_key = foreign_key


    def __repr__(self) -> str:
        return f"<structures.RelationshipMember table='{self.table.name}'>"


    @property
    def table(self) -> "Table":
        """Table that is a member of this relationship."""
        return self._table


    @table.setter
    def table(self, value:"Table"):
        if not validation.is_structure_instance(value, "Table"):
            raise TypeError("Relationship Class members must be an instance of Table.")
        self._table = value


    @property
    def primary_key(self) -> str:
        """Relationship member's primary key field name."""
        return self._primary_key


    @primary_key.setter
    def primary_key(self, value:str):
        self._primary_key = validation.string_or_none(value, f"primary key {value}", min_len=3,
                                                      max_len=100, allow_numbers=False)


    @property
    def foreign_key(self) -> str:
        """Relationship member's foreign key field name."""
        return self._foreign_key


    @foreign_key.setter
    def foreign_key(self, value:str):
        self._foreign_key = validation.string_or_none(value, f"foreign key {value}", min_len=3,
                                              max_len=100, allow_numbers=False)


    @staticmethod
    def confirm_key_in_table(table:"Table", key:str):
        """Confirm that a key is a member of a table. If not, raises an exception.

        Args:
            table (Table): Table in which the key should be a field.
            key (str): Name of the field that serves as a primary or foreign key.

        Raises:
            ValueError: Key is not a field in the table.
        """
        matches = [f for f in table.fields if f.name == key]
        if len(matches) == 0:
            raise ValueError(f"Key {key} is not a field in the relationship class member table.")


#pylint: disable-next=too-many-instance-attributes
class Relationship(Dataset):
    """Structure for a geodatabase relationship class linking two tables together.

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

    Attributes:
        RELATIONSHIP_TYPES (tuple[str]): Values that are valid for relationship_type.
        NOTIFICATIONS (tuple[str]): Values that are valid for notification.
        CARDINALITIES (tuple[str]): Values that are valid for cardinality.
        FIELD_TYPES (tuple[str]): Field types that are valid in an attributed field class.
    """ #pylint: disable=line-too-long

    # Valid relationship types
    RELATIONSHIP_TYPES = (
        "SIMPLE",
        "COMPOSITE",
    )


    # Valid notification values
    NOTIFICATIONS = (
        "NONE",
        "FORWARD",
        "BACKWARD",
        "BOTH",
    )


    # Valid cardinality values
    CARDINALITIES = (
        "ONE_TO_ONE",
        "ONE_TO_MANY",
        "MANY_TO_MANY",
    )


    # Field types that are valid in an attributed field class.
    FIELD_TYPE_EXCLUSIONS = (
        "SHAPE",
    )


    # Instance Properties
    _origin:RelationshipMember = None
    _destination:RelationshipMember = None
    _forward_label:str = None
    _backward_label:str = None
    _cardinality:str = None
    _notification:str = None
    _relationship_type:str = None
    _attributed:bool = None


    #pylint: disable-next=too-many-arguments,too-many-locals
    def __init__(self, name:str, origin_table:"Table", destination_table:str, relationship_type:str, forward_label:str,
                 backward_label:str, notification:str, cardinality:str, attributed:str, origin_primary_key:str,
                 origin_foreign_key:str, destination_primary_key:Union[str, None]=None,
                 destination_foreign_key:Union[str, None]=None, schema:Union[str, None]=None, is_archived:str=False,
                 is_versioned:bool=False, oid_is_64:bool=None, dsid:int=None, meta_summary:str=None,
                 feature_dataset:"FeatureDataset"=None) -> None:

        if self.dataset_type is None:
            self.dataset_type = "RelationshipClass"

        super().__init__(name, schema, is_archived, is_versioned, oid_is_64, dsid, meta_summary, feature_dataset)

        # Members & key checks
        if origin_primary_key is None or origin_foreign_key is None:
            raise ValueError(f"Value for Origin Primary and Foreign key must be specified for relationship {name}.")

        if attributed or cardinality == "MANY_TO_MANY":
            # Complex keys with both origin and destination
            RelationshipMember.confirm_key_in_table(origin_table, origin_primary_key)
            RelationshipMember.confirm_key_in_table(destination_table, destination_primary_key)

        else:
            # Simple keys with only origin keys
            RelationshipMember.confirm_key_in_table(origin_table, origin_primary_key)
            RelationshipMember.confirm_key_in_table(destination_table, origin_foreign_key)

        self._origin = RelationshipMember(origin_table, origin_primary_key, origin_foreign_key)
        self._destination = RelationshipMember(destination_table, destination_primary_key, destination_foreign_key)
        origin_table._register_relationship_classes(self)
        destination_table._register_relationship_classes(self)

        # Properties
        self.forward_label = forward_label
        self.backward_label = backward_label
        self.cardinality = cardinality
        self.notification = notification
        self.relationship_type = relationship_type
        self.attributed = attributed


    @property
    def _foreign_keys_defined(self) -> bool:
        """Whether foreign keys are defined for both the origin and destination tables."""
        return self.origin.foreign_key is not None and self.destination.foreign_key is not None


    @property
    def origin(self) -> RelationshipMember:
        """Originating relationship member table or feature class."""
        return self._origin


    @property
    def destination(self) -> RelationshipMember:
        """Destination relationship member table or feature class."""
        return self._destination


    @property
    def forward_label(self) -> str:
        """Label used to identify origin to destination."""
        return self._forward_label


    @forward_label.setter
    def forward_label(self, value:str):
        self._forward_label = validation.string(value, "relationship class forward label", min_len=1, max_len=100)


    @property
    def backward_label(self) -> str:
        """Label used to identify destination to origin."""
        return self._backward_label


    @backward_label.setter
    def backward_label(self, value:str):
        self._backward_label = validation.string(value, "relationship class backward label", min_len=1, max_len=100)


    @property
    def cardinality(self) -> str:
        """Number of unique values in destination relative to origin. Valid values in Relationship.CARDINALITIES."""
        return self._cardinality


    @cardinality.setter
    def cardinality(self, value:str):
        validation.string(value, "relationship class cardinality", enum=Relationship.CARDINALITIES, allow_numbers=False)

        if value == "MANY_TO_MANY" and not self._foreign_keys_defined:
            raise ValueError("Cardinality of relationship class can only be set to MANY_TO_MANY if foreign keys defined.")

        self._cardinality = value


    @property
    def notification(self) -> str:
        """Whether changes to one table are propagated to the other table. Valid values in
        Relationship.NOTIFICATIONS."""
        return self._notification


    @notification.setter
    def notification(self, value:str):
        self._notification = validation.string(value, "relationship class notification type",
                                               enum=Relationship.NOTIFICATIONS)


    @property
    def relationship_type(self) -> str:
        """Whether the relationship is simple or composite (each destination record must be related to an
        origin record). Valid values in Relationship.RELATIONSHIP_TYPES."""
        return self._relationship_type


    @relationship_type.setter
    def relationship_type(self, value:str):
        self._relationship_type = validation.string(value, "relationship class type",
                                                    enum=Relationship.RELATIONSHIP_TYPES)


    @property
    def attributed(self) -> bool:
        """Whether the relationship class has attributes other than the keys."""
        return self._attributed


    @attributed.setter
    def attributed(self, value:bool):
        validation.boolean(value, "relationship class attributed", coerce=False)

        if value and not self._foreign_keys_defined:
            raise ValueError("Relationship Class can only be made attributed if foreign keys defined.")

        if value is False and len(list(self._fields)) > 0:
            raise ValueError("Cannot make the relationship class not attributed when fields exist.")

        self._attributed = value


    @property
    def fields(self) -> "FieldAccessor":
        """Sequence like accessor for fields contained with the dataset."""
        if not self.attributed:
            raise AttributeError("Fields are not available in a non-attributed relationship class.")

        return self._fields