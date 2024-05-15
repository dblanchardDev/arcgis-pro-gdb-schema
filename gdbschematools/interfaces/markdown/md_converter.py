"""
Conversion of properties between the expected value for markdown text outputs and the structure.

Author: Roya Shourouni, David Blanchard
"""

def value_to_cell(value:any, field_type:str) -> str:
    """Convert a value to one ready for display in a cell. Mainly converts date/time to a string.

    Args:
        value (any): The value to be written to the cell.
        field_type (str): The type of field as defined in the structure.

    Returns:
        Union[str, int, float]: The value ready to be written to Excel.
    """
    out_value = value

    if value is None:
        out_value =''

    elif field_type in ["DATE"]:
        out_value = value.strftime("%Y-%m-%d %H:%M:%S")

    elif field_type == "DATEONLY":
        out_value = value.strftime("%Y-%m-%d")

    elif field_type == "TIMEONLY":
        out_value = value.strftime("%H:%M:%S")

    return str(out_value)


#pylint: disable=too-few-public-methods
class _GDBConverter():

    _BOOLEAN = {
        "yes": True,
        "no": False,
    }

    boolean:dict[any, any] = None


    _CARDINALITIES = {
        "One To One": "ONE_TO_ONE",
        "One To Many": "ONE_TO_MANY",
        "Many To Many": "MANY_TO_MANY",
    }

    cardinalities:dict[str, str] = None


    _DATASET_TYPES = {
        "Feature Class": "FeatureClass",
        "Table": "Table",
        "Relationship Class": "RelationshipClass",
        "Any": "Any",
        "Cadastral Fabric": "CadastralFabric",
        "Cad Drawing": "CadDrawing",
        "Container": "Container",
        "Diagram Dataset": "DiagramDataset",
        "Feature Dataset": "FeatureDataset",
        "Geometry Network": "Geo",
        "LAS Dataset": "LasDataset",
        "Locator": "Locator",
        "Mosaic Dataset": "MosaicDataset",
        "Network Dataset": "NetworkDataset",
        "Parcel Dataset": "ParcelDataset",
        "Planar Graph": "PlanarGraph",
        "Raster Band": "RasterBand",
        "Raster Dataset": "RasterDataset",
        "Schematic Dataset": "SchematicDataset",
        "Text": "Text",
        "TIN": "TIN",
        "Tool": "Tool",
        "Toolbox": "Toolbox",
        "Topology": "Topology",
        "Terrain": "Terrain",
        "Utility Network": "UtilityNetwork",
    }

    dataset_types:dict[str, str] = None


    _DOMAIN_FIELD_TYPES = {
        "Big Integer": "BIGINTEGER",
        "Date": "DATE",
        "Date Only": "DATEONLY",
        "Double": "DOUBLE",
        "Long Integer": "LONG",
        "Float": "FLOAT",
        "Short Integer": "SHORT",
        "Text": "TEXT",
        "Time Only": "TIMEONLY",
        "Timestamp Offset": "TIMESTAMPOFFSET",
    }

    domain_field_types:dict[str, str] = None


    _DOMAIN_TYPES = {
        "Coded Value": "CODED",
        "Range": "RANGE",
    }

    domain_types:dict[str, str] = None


    _FIELD_TYPES = {
        "Blob": "BLOB",
        "Big Integer": "BIGINTEGER",
        "Date": "DATE",
        "Date Only": "DATEONLY",
        "Double": "DOUBLE",
        "Geometry": "SHAPE",
        "Global ID": "GLOBALID",
        "GUID": "GUID",
        "Long Integer": "LONG",
        "OBJECTID": "OBJECTID",
        "Raster": "RASTER",
        "Float": "FLOAT",
        "Short Integer": "SHORT",
        "Text": "TEXT",
        "Time Only": "TIMEONLY",
        "Timestamp Offset": "TIMESTAMPOFFSET",
    }

    field_types:dict[str, str] = None


    _GEOMETRY_TYPES = {
        "Polygon": "POLYGON",
        "Polyline": "POLYLINE",
        "Point": "POINT",
        "Multipoint": "MULTIPOINT",
        "Multipatch": "MULTIPATCH",
    }

    geometry_types:dict[str, str] = None


    _MERGE_POLICIES = {
        "Default Value": "DEFAULT",
        "Sum Values": "SUM_VALUES",
        "Area Weighted": "AREA_WEIGHTED",
    }

    merge_policies:dict[str, str] = None


    _NOTIFICATIONS = {
        "None": "NONE",
        "Forward": "FORWARD",
        "Backward": "BACKWARD",
        "Both": "BOTH",
    }

    notifications:dict[str, str] = None


    _RELATIONSHIP_TYPES = {
        "Simple": "SIMPLE",
        "Composite": "COMPOSITE",
    }

    relationship_types:dict[str, str] = None


    _SPLIT_POLICIES = {
        "Default Value": "DEFAULT",
        "Duplicate": "DUPLICATE",
        "Geometry Ratio": "GEOMETRY_RATIO",
    }

    split_policies:dict[str, str] = None


    _WORKSPACE_TYPES = {
        "Local Database": "LOCAL_DATABASE",
        "Remote Database": "REMOTE_DATABASE",
    }

    workspace_types:dict[str, str] = None


    def __init__(self, md_to_struct:bool=True) -> None:
        """Convert values from those in Markdown and those in the structure and vice-versa.

        Args:
            xls_to_struct (bool, optional): Whether to convert from Excel text to structure. Will convert the other way if False. Defaults to True.
        """ #pylint: disable=line-too-long
        flip = not md_to_struct

        self.boolean = self._flip(_GDBConverter._BOOLEAN, flip)
        self.cardinalities = self._flip(_GDBConverter._CARDINALITIES, flip)
        self.dataset_types = self._flip(_GDBConverter._DATASET_TYPES, flip)
        self.domain_field_types = self._flip(_GDBConverter._DOMAIN_FIELD_TYPES, flip)
        self.domain_types = self._flip(_GDBConverter._DOMAIN_TYPES, flip)
        self.field_types = self._flip(_GDBConverter._FIELD_TYPES, flip)
        self.geometry_types = self._flip(_GDBConverter._GEOMETRY_TYPES, flip)
        self.merge_policies = self._flip(_GDBConverter._MERGE_POLICIES, flip)
        self.notifications = self._flip(_GDBConverter._NOTIFICATIONS, flip)
        self.relationship_types = self._flip(_GDBConverter._RELATIONSHIP_TYPES, flip)
        self.split_policies = self._flip(_GDBConverter._SPLIT_POLICIES, flip)
        self.workspace_types = self._flip(_GDBConverter._WORKSPACE_TYPES, flip)



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


# Excel to Structure
md2st = _GDBConverter(md_to_struct=True)


# Structure to Excel
st2md = _GDBConverter(md_to_struct=False)