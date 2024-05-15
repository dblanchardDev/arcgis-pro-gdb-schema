"""
Conversion of properties between the expected value for arcpy and the structure.

Author: David Blanchard
"""

#pylint: disable=too-few-public-methods
class _GDBConverter():
    _WORKSPACE_TYPES = {
        "LocalDatabase": "LOCAL_DATABASE",
        "RemoteDatabase": "REMOTE_DATABASE",
    }

    workspace_types:dict[str, str] = None


    _RELATIONSHIP_TYPES = {
        "Simple": "SIMPLE",
        "Composite": "COMPOSITE",
    }

    relationship_types:dict[str, str] = None


    _NOTIFICATIONS = {
        "None": "NONE",
        "Forward": "FORWARD",
        "Backward": "BACKWARD",
        "Both": "BOTH",
    }

    notifications:dict[str, str] = None


    _CARDINALITIES = {
        "OneToOne": "ONE_TO_ONE",
        "OneToMany": "ONE_TO_MANY",
        "ManyToMany": "MANY_TO_MANY",
    }

    cardinalities:dict[str, str] = None


    _GEOMETRY_TYPES = {
        "Polygon": "POLYGON",
        "Polyline": "POLYLINE",
        "Point": "POINT",
        "Multipoint": "MULTIPOINT",
        "Multipatch": "MULTIPATCH",
    }

    geometry_types:dict[str, str] = None


    _FIELD_TYPES = {
        "Blob": "BLOB",
        "BigInteger": "BIGINTEGER",
        "Date": "DATE",
        "DateOnly": "DATEONLY",
        "Double": "DOUBLE",
        "Geometry": "SHAPE",
        "GlobalID": "GLOBALID",
        "Guid": "GUID",
        "Integer": "LONG",
        "OID": "OBJECTID",
        "Raster": "RASTER",
        "Single": "FLOAT",
        "SmallInteger": "SHORT",
        "String": "TEXT",
        "TimeOnly": "TIMEONLY",
        "TimestampOffset": "TIMESTAMPOFFSET",
    }

    field_types:dict[str, str] = None


    _DOMAIN_TYPES = {
        "CodedValue": "CODED",
        "Range": "RANGE",
    }

    domain_types:dict[str, str] = None


    _DOMAIN_FIELD_TYPES = {
        "BigInteger": "BIGINTEGER",
        "Date": "DATE",
        "DateOnly": "DATEONLY",
        "Double": "DOUBLE",
        "Long": "LONG",
        "Float": "FLOAT",
        "Short": "SHORT",
        "Text": "TEXT",
        "TimeOnly": "TIMEONLY",
        "TimestampOffset": "TIMESTAMPOFFSET",
    }

    domain_field_types:dict[str, str] = None


    _SPLIT_POLICIES = {
        "DefaultValue": "DEFAULT",
        "Duplicate": "DUPLICATE",
        "GeometryRatio": "GEOMETRY_RATIO",
    }

    split_policies:dict[str, str] = None


    MERGE_POLICIES = {
        "DefaultValue": "DEFAULT",
        "SumValues": "SUM_VALUES",
        "AreaWeighted": "AREA_WEIGHTED",
    }

    merge_policies:dict[str, str] = None


    def __init__(self, gdb_to_struct:bool=True) -> None:
        """Convert values from those in arcpy and those in the structure and vice-versa.

        Args:
            gdb_to_struct (bool, optional): Whether to convert from arcpy GDB to structure. Will convert the other way if False. Defaults to True.
        """ #pylint: disable=line-too-long
        flip = not gdb_to_struct

        self.workspace_types = self._flip(_GDBConverter._WORKSPACE_TYPES, flip)
        self.relationship_types = self._flip(_GDBConverter._RELATIONSHIP_TYPES, flip)
        self.notifications = self._flip(_GDBConverter._NOTIFICATIONS, flip)
        self.cardinalities = self._flip(_GDBConverter._CARDINALITIES, flip)
        self.field_types = self._flip(_GDBConverter._FIELD_TYPES, flip)
        self.geometry_types = self._flip(_GDBConverter._GEOMETRY_TYPES, flip)
        self.domain_types = self._flip(_GDBConverter._DOMAIN_TYPES, flip)
        self.domain_field_types = self._flip(_GDBConverter._DOMAIN_FIELD_TYPES, flip)
        self.split_policies = self._flip(_GDBConverter._SPLIT_POLICIES, flip)
        self.merge_policies = self._flip(_GDBConverter.MERGE_POLICIES, flip)



    def _flip(self, dictionary:dict, flip:bool) -> dict:
        """Will swap the keys and values in a dictionary if flip is true.

        Args:
            dictionary (dict): Dictionary that might need to be flipped.
            flip (bool): Whether to flip the dictionary.

        Returns:
            dict: The dictionary either flipped or not.
        """
        if flip:
            return {v:k for k, v in dictionary.items()}

        return dictionary


# Arcpy to Structure
ap2st = _GDBConverter(gdb_to_struct=True)


# Structure to Arcpy
st2ap = _GDBConverter(gdb_to_struct=False)