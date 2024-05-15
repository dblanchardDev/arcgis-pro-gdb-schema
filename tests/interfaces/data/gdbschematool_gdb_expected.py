#pylint: disable=too-many-lines
"""Expected results when reading the GDBSchemaTool sample geodatabase."""

import datetime

import pytest


# Properties of the test geodatabase
GEODATABASE = {
    "name": "GDBSchemaTool",
    "meta_summary": "This is a geodatabase to test the GDB Schema Tools.",
    "workspace_type": "LOCAL_DATABASE",
}


# Domains that are in the test Geodatabase
DOMAINS = {
    "Building - Commercial": {
        "description": "Types of commercial buildings.",
        "field_type": "TEXT",
        "domain_type": "CODED",
        "split_policy": "DEFAULT",
        "merge_policy": "DEFAULT",
        "schema": None,
        "codes": {
            "OFF": {
                "description": "Office",
                "meta_summary": None,
            },
            "RET": {
                "description": "Retail",
                "meta_summary": None,
            },
            "ENT": {
                "description": "Entertainment",
                "meta_summary": None,
            },
            "RES": {
                "description": "Restaurant",
                "meta_summary": None,
            },
        },
    },
    "Buidling - General": {
        "description": "General Types of Buildings",
        "field_type": "TEXT",
        "domain_type": "CODED",
        "split_policy": "DEFAULT",
        "merge_policy": "DEFAULT",
        "schema": None,
        "codes": {
            "OTH": {
                "description": "Other",
                "meta_summary": None,
            },
            "MTU": {
                "description": "Multi-Use",
                "meta_summary": None,
            },
            "REZ": {
                "description": "Residential",
                "meta_summary": None,
            },
        },
    },
    "Building - Government": {
        "description": "Types of government buildings.",
        "field_type": "TEXT",
        "domain_type": "CODED",
        "split_policy": "DEFAULT",
        "merge_policy": "DEFAULT",
        "schema": None,
        "codes": {
            "GOV": {
                "description": "Government Office",
                "meta_summary": None,
            },
            "EDU": {
                "description": "Educational",
                "meta_summary": None,
            },
            "HSP": {
                "description": "Hospital",
                "meta_summary": None,
            },
            "REC": {
                "description": "Recreational",
                "meta_summary": None,
            },
        },
    },
    "Building - Industrial": {
        "description": "Types of industrial buildings.",
        "field_type": "TEXT",
        "domain_type": "CODED",
        "split_policy": "DEFAULT",
        "merge_policy": "DEFAULT",
        "schema": None,
        "codes": {
            "FAC": {
                "description": "Factory",
                "meta_summary": None,
            },
            "WHR": {
                "description": "Warehouse",
                "meta_summary": None,
            },
            "SHP": {
                "description": "Shipping",
                "meta_summary": None,
            },
            "MNT": {
                "description": "Maintenance",
                "meta_summary": None,
            },
        },
    },
    "Lake River Flow": {
        "description": "Which direction does a river flow into/out of a lake.",
        "field_type": "TEXT",
        "domain_type": "CODED",
        "split_policy": "DEFAULT",
        "merge_policy": "DEFAULT",
        "schema": None,
        "codes": {
            "IN": {
                "description": "River flow into lake",
                "meta_summary": "The river is exclusively an input to the lake.",
            },
            "OUT": {
                "description": "River flows out of lake",
                "meta_summary": "The river is exclusively an output from the lake.",
            },
            "BOTH": {
                "description": "River flow into and out of lake",
                "meta_summary": "The lake is part of the river, with the river flowing into the lake, then out of the lake to continue.", #pylint: disable=line-too-long
            },
        },
    },
    "Office Hours": {
        "description": "List of valid hours for opening and closings.",
        "field_type": "TIMEONLY",
        "domain_type": "RANGE",
        "split_policy": "DEFAULT",
        "merge_policy": "DEFAULT",
        "schema": None,
        "minimum": datetime.time(7, 0),
        "maximum": datetime.time(22, 0),
    },
    "Street Types": {
        "description": "List of valid street types to choose from.",
        "field_type": "TEXT",
        "domain_type": "CODED",
        "split_policy": "DUPLICATE",
        "merge_policy": "DEFAULT",
        "schema": None,
        "codes": {
            "AVE": {
                "description": "Avenue",
                "meta_summary": None,
            },
            "BLVD": {
                "description": "Boulevard",
                "meta_summary": None,
            },
            "CIR": {
                "description": "Circle",
                "meta_summary": None,
            },
            "CRES": {
                "description": "Crescent",
                "meta_summary": None,
            },
            "DR": {
                "description": "Drive",
                "meta_summary": None,
            },
            "EXPY": {
                "description": "Expressway",
                "meta_summary": None,
            },
            "HWY": {
                "description": "Highway",
                "meta_summary": None,
            },
            "LANE": {
                "description": "Lane",
                "meta_summary": None,
            },
            "PKY": {
                "description": "Parkway",
                "meta_summary": None,
            },
            "PL": {
                "description": "Place",
                "meta_summary": None,
            },
            "PROM": {
                "description": "Promenade",
                "meta_summary": None,
            },
            "RAMP": {
                "description": "Ramp",
                "meta_summary": None,
            },
            "RD": {
                "description": "Road",
                "meta_summary": None,
            },
            "RTE": {
                "description": "Route",
                "meta_summary": None,
            },
            "ST": {
                "description": "Street",
                "meta_summary": None,
            },
            "WAY": {
                "description": "Way",
                "meta_summary": None,
            },
        },
    },
    "Tree Diameter": {
        "description": "Valid tree diameters.",
        "field_type": "DOUBLE",
        "domain_type": "RANGE",
        "split_policy": "DEFAULT",
        "merge_policy": "DEFAULT",
        "schema": None,
        "minimum": 0.05,
        "maximum": 10,
    },
    "Tree Height": {
        "description": "Range of valid tree heights.",
        "field_type": "FLOAT",
        "domain_type": "RANGE",
        "split_policy": "GEOMETRY_RATIO",
        "merge_policy": "SUM_VALUES",
        "schema": None,
        "minimum": 0.25,
        "maximum": 30,
    },
    "Valid Speed Limits": {
        "description": "Range of valid speed limits for streets.",
        "field_type": "SHORT",
        "domain_type": "RANGE",
        "split_policy": "DEFAULT",
        "merge_policy": "DEFAULT",
        "schema": None,
        "minimum": 5,
        "maximum": 110,
    },
}


# Coded domains that are expected to be in the test GDB
CODED_DOMAINS = {k:v for k, v in DOMAINS.items() if v["domain_type"] == "CODED"}


# Name of feature datasets that are expected to be in the test GDB
FEATURE_DATASETS = {
    "Water": {
        "schema": None,
        "meta_summary": "Grouping of tables that relate to natural water features.",
    },
}


# Structure of tables that are expected to be in the test GDB
TABLES = {
    "Inspections": {
        "alias": "Inspections",
        "is_archived": False,
        "is_versioned": False,
        "oid_is_64": False,
        "dsid": 21,
        "meta_summary": None,
        "feature_dataset": None,
        "fields": {
            "OBJECTID": {
                "field_type": "OBJECTID",
                "precision": None,
                "scale": None,
                "length": None,
                "alias": "OBJECTID",
                "nullable": False,
                "required": True,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "BuildingUUID": {
                "field_type": "GUID",
                "precision": None,
                "scale": None,
                "length": None,
                "alias": "Building Unique ID",
                "nullable": False,
                "required": False,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "InspectedOn": {
                "field_type": "DATE",
                "precision": None,
                "scale": None,
                "length": None,
                "alias": "Inspected On",
                "nullable": False,
                "required": False,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "InspectedBy": {
                "field_type": "TEXT",
                "precision": None,
                "scale": None,
                "length": 50,
                "alias": "Inspected By",
                "nullable": False,
                "required": False,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
        },
        "subtypes": None,
    },
}


# Structure of feature classes that are expected to be in the test GDB
FEAT_CLS = {
    "Lakes": {
        "geometry_type": "POLYGON",
        "spatial_reference": (3857, None),
        "has_m": False,
        "has_z": True,
        "alias": "Lakes",
        "is_archived": False,
        "is_versioned": False,
        "oid_is_64": False,
        "dsid": 17,
        "meta_summary": None,
        "feature_dataset": "Water",
        "fields": {
            "OBJECTID": {
                "field_type": "OBJECTID",
                "precision": None,
                "scale": None,
                "length": None,
                "alias": "OBJECTID",
                "nullable": False,
                "required": True,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "Shape": {
                "field_type": "SHAPE",
                "precision": None,
                "scale": None,
                "length": None,
                "alias": "SHAPE",
                "nullable": True,
                "required": True,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "Name": {
                "field_type": "TEXT",
                "precision": None,
                "scale": None,
                "length": 100,
                "alias": "Name",
                "nullable": True,
                "required": False,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "RiverID": {
                "field_type": "LONG",
                "precision": 0,
                "scale": None,
                "length": None,
                "alias": "River ID",
                "nullable": True,
                "required": False,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
        },
        "subtypes": None,
    },
    "Rivers": {
        "geometry_type": "POLYLINE",
        "spatial_reference": (3857, None),
        "has_m": False,
        "has_z": True,
        "alias": "Rivers",
        "is_archived": False,
        "is_versioned": False,
        "oid_is_64": False,
        "dsid": 18,
        "meta_summary": None,
        "feature_dataset": "Water",
        "fields": {
            "OBJECTID": {
                "field_type": "OBJECTID",
                "precision": None,
                "scale": None,
                "length": None,
                "alias": "OBJECTID",
                "nullable": False,
                "required": True,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "Shape": {
                "field_type": "SHAPE",
                "precision": None,
                "scale": None,
                "length": None,
                "alias": "SHAPE",
                "nullable": True,
                "required": True,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "RiverID": {
                "field_type": "LONG",
                "precision": 0,
                "scale": None,
                "length": None,
                "alias": "River ID",
                "nullable": True,
                "required": False,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "Name": {
                "field_type": "TEXT",
                "precision": None,
                "scale": None,
                "length": 100,
                "alias": "Name",
                "nullable": True,
                "required": False,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
        },
        "subtypes": None,
    },
    "Buildings": {
        "geometry_type": "POLYGON",
        "spatial_reference": (54030, None),
        "has_m": False,
        "has_z": False,
        "alias": "Buildings",
        "is_archived": False,
        "is_versioned": False,
        "oid_is_64": False,
        "dsid": 7,
        "meta_summary": None,
        "feature_dataset": None,
        "fields": {
            "OBJECTID": {
                "field_type": "OBJECTID",
                "precision": None,
                "scale": None,
                "length": None,
                "alias": "OBJECTID",
                "nullable": False,
                "required": True,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "Shape": {
                "field_type": "SHAPE",
                "precision": None,
                "scale": None,
                "length": None,
                "alias": "SHAPE",
                "nullable": True,
                "required": True,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "Classification": {
                "field_type": "SHORT",
                "precision": 0,
                "scale": None,
                "length": None,
                "alias": "Classification",
                "nullable": False,
                "required": False,
                "default": 0,
                "domain": None,
                "meta_summary": None,
            },
            "Type": {
                "field_type": "TEXT",
                "precision": None,
                "scale": None,
                "length": 3,
                "alias": "Type",
                "nullable": False,
                "required": False,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "Name": {
                "field_type": "TEXT",
                "precision": None,
                "scale": None,
                "length": 100,
                "alias": "Name",
                "nullable": True,
                "required": False,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "Built": {
                "field_type": "DATEONLY",
                "precision": None,
                "scale": None,
                "length": None,
                "alias": "Build Date",
                "nullable": True,
                "required": False,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "UUID": {
                "field_type": "GUID",
                "precision": None,
                "scale": None,
                "length": None,
                "alias": "Building Unique ID",
                "nullable": False,
                "required": False,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "OpeningHour": {
                "field_type": "TIMEONLY",
                "precision": None,
                "scale": None,
                "length": None,
                "alias": "Opening Hour",
                "nullable": True,
                "required": False,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "ClosingHour": {
                "field_type": "TIMEONLY",
                "precision": None,
                "scale": None,
                "length": None,
                "alias": "Closing Hour",
                "nullable": True,
                "required": False,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
        },
        "subtypes": {
            "field": "Classification",
            "default": 0,
            "codes": {
                0: {
                    "description": "General",
                    "meta_summary": "Residential, multi-use, or otherwise unclassified buildings.",
                    "fields": {
                        "OBJECTID": {
                            "default": None,
                            "domain": None,
                        },
                        "Shape": {
                            "default": None,
                            "domain": None,
                        },
                        "Classification": {
                            "default": None,
                            "domain": None,
                        },
                        "Type": {
                            "default": "OTH",
                            "domain": "Buidling - General",
                        },
                        "Name": {
                            "default": None,
                            "domain": None,
                        },
                        "Built": {
                            "default": None,
                            "domain": None,
                        },
                        "UUID": {
                            "default": None,
                            "domain": None,
                        },
                        "OpeningHour": {
                            "default": None,
                            "domain": None,
                        },
                        "ClosingHour": {
                            "default": None,
                            "domain": None,
                        },
                    },
                },
                1: {
                    "description": "Commercial",
                    "meta_summary": "Buildings from which a non-industrial business operates such as offices, retail, restaurants, and entertainment venues.", #pylint: disable=line-too-long
                    "fields": {
                        "OBJECTID": {
                            "default": None,
                            "domain": None,
                        },
                        "Shape": {
                            "default": None,
                            "domain": None,
                        },
                        "Classification": {
                            "default": None,
                            "domain": None,
                        },
                        "Type": {
                            "default": None,
                            "domain": "Building - Commercial",
                        },
                        "Name": {
                            "default": None,
                            "domain": None,
                        },
                        "Built": {
                            "default": None,
                            "domain": None,
                        },
                        "UUID": {
                            "default": None,
                            "domain": None,
                        },
                        "OpeningHour": {
                            "default": None,
                            "domain": None,
                        },
                        "ClosingHour": {
                            "default": None,
                            "domain": None,
                        },
                    },
                },
                2: {
                    "description": "Industrial",
                    "meta_summary": "Manufacturing and warehousing facilities.",
                    "fields": {
                        "OBJECTID": {
                            "default": None,
                            "domain": None,
                        },
                        "Shape": {
                            "default": None,
                            "domain": None,
                        },
                        "Classification": {
                            "default": None,
                            "domain": None,
                        },
                        "Type": {
                            "default": None,
                            "domain": "Building - Industrial",
                        },
                        "Name": {
                            "default": None,
                            "domain": None,
                        },
                        "Built": {
                            "default": None,
                            "domain": None,
                        },
                        "UUID": {
                            "default": None,
                            "domain": None,
                        },
                        "OpeningHour": {
                            "default": None,
                            "domain": None,
                        },
                        "ClosingHour": {
                            "default": None,
                            "domain": None,
                        },
                    },
                },
                3: {
                    "description": "Government",
                    "meta_summary": None,
                    "fields": {
                        "OBJECTID": {
                            "default": None,
                            "domain": None,
                        },
                        "Shape": {
                            "default": None,
                            "domain": None,
                        },
                        "Classification": {
                            "default": None,
                            "domain": None,
                        },
                        "Type": {
                            "default": None,
                            "domain": "Building - Government",
                        },
                        "Name": {
                            "default": None,
                            "domain": None,
                        },
                        "Built": {
                            "default": None,
                            "domain": None,
                        },
                        "UUID": {
                            "default": None,
                            "domain": None,
                        },
                        "OpeningHour": {
                            "default": datetime.time(8,30,0),
                            "domain": "Office Hours",
                        },
                        "ClosingHour": {
                            "default": datetime.time(16,30,0),
                            "domain": "Office Hours",
                        },
                    },
                },
            },
        },
    },
    "StreetCentreline": {
        "geometry_type": "POLYLINE",
        "spatial_reference": (3857, None),
        "has_m": True,
        "has_z": True,
        "alias": "Street Centreline",
        "is_archived": False,
        "is_versioned": False,
        "oid_is_64": False,
        "dsid": 3,
        "meta_summary": "This is a description of the street centrelines that are contained within this feature class.", #pylint: disable=line-too-long
        "feature_dataset": None,
        "fields": {
            "OBJECTID": {
                "field_type": "OBJECTID",
                "precision": None,
                "scale": None,
                "length": None,
                "alias": "OBJECTID",
                "nullable": False,
                "required": True,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "Shape": {
                "field_type": "SHAPE",
                "precision": None,
                "scale": None,
                "length": None,
                "alias": "SHAPE",
                "nullable": True,
                "required": True,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "GlobalID": {
                "field_type": "GLOBALID",
                "precision": None,
                "scale": None,
                "length": None,
                "alias": "GlobalID",
                "nullable": False,
                "required": True,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "StreetName": {
                "field_type": "TEXT",
                "precision": None,
                "scale": None,
                "length": 100,
                "alias": "Street Name",
                "nullable": False,
                "required": False,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "StreetType": {
                "field_type": "TEXT",
                "precision": None,
                "scale": None,
                "length": 4,
                "alias": "Street Type",
                "nullable": False,
                "required": False,
                "default": None,
                "domain": "Street Types",
                "meta_summary": None,
            },
            "Municipality": {
                "field_type": "TEXT",
                "precision": None,
                "scale": None,
                "length": 50,
                "alias": "Municipality",
                "nullable": True,
                "required": False,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "Speed": {
                "field_type": "SHORT",
                "precision": 0,
                "scale": None,
                "length": None,
                "alias": "Speed Limit",
                "nullable": True,
                "required": False,
                "default": None,
                "domain": "Valid Speed Limits",
                "meta_summary": None,
            },
        },
        "subtypes": None,
    },
    "Trees": {
        "geometry_type": "POINT",
        "spatial_reference": (3857, None),
        "has_m": False,
        "has_z": False,
        "alias": "Trees",
        "is_archived": False,
        "is_versioned": False,
        "oid_is_64": False,
        "dsid": 13,
        "meta_summary": "A summary about the tree feature class. This is a points feature class.",
        "feature_dataset": None,
        "fields": {
            "OBJECTID": {
                "field_type": "OBJECTID",
                "precision": None,
                "scale": None,
                "length": None,
                "alias": "OBJECTID",
                "nullable": False,
                "required": True,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "Shape": {
                "field_type": "SHAPE",
                "precision": None,
                "scale": None,
                "length": None,
                "alias": "SHAPE",
                "nullable": True,
                "required": True,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "Height": {
                "field_type": "FLOAT",
                "precision": 0,
                "scale": 0,
                "length": None,
                "alias": "Height",
                "nullable": True,
                "required": False,
                "default": pytest.approx(0.65),
                "domain": "Tree Height",
                "meta_summary": "Height of the tree in meters.",
            },
            "Diameter": {
                "field_type": "DOUBLE",
                "precision": 0,
                "scale": 0,
                "length": None,
                "alias": "Diameter",
                "nullable": True,
                "required": False,
                "default": None,
                "domain": "Tree Diameter",
                "meta_summary": "The diameter of the tree's crown.",
            },
        },
        "subtypes": None,
    },
}


REL_CLS = {
    "Building_Inspections": {
        "origin_table": "Buildings",
        "destination_table": "Inspections",
        "forward_label": "Inspections",
        "backward_label": "Building",
        "cardinality": "ONE_TO_MANY",
        "notification": "FORWARD",
        "relationship_type": "COMPOSITE",
        "attributed": False,
        "origin_primary_key": "UUID",
        "destination_primary_key": None,
        "origin_foreign_key": "BuildingUUID",
        "destination_foreign_key": None,
        "schema": None,
        "is_archived": False,
        "is_versioned": False,
        "oid_is_64": False,
        "dsid": None,
        "meta_summary": "Links buildings to their inspections.",
        "feature_dataset": None,
        "fields": {},
        "subtypes": None,
    },
    "Rivers_and_Lakes": {
        "origin_table": "Rivers",
        "destination_table": "Lakes",
        "forward_label": "Lakes Along",
        "backward_label": "River Connection",
        "cardinality": "ONE_TO_MANY",
        "notification": "NONE",
        "relationship_type": "SIMPLE",
        "attributed": True,
        "origin_primary_key": "RiverID",
        "destination_primary_key": "RiverID",
        "origin_foreign_key": "RiverID",
        "destination_foreign_key": "LakesRiverID",
        "schema": None,
        "is_archived": False,
        "is_versioned": False,
        "oid_is_64": False,
        "dsid": 19,
        "meta_summary": "Connection between rivers and lakes that flow into each other.",
        "feature_dataset": "Water",
        "fields": {
            "RiverID": {
                "field_type": "LONG",
                "precision": 0,
                "scale": None,
                "length": None,
                "alias": "RiverID",
                "nullable": True,
                "required": False,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "LakesRiverID": {
                "field_type": "LONG",
                "precision": 0,
                "scale": None,
                "length": None,
                "alias": "LakesRiverID",
                "nullable": True,
                "required": False,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "RID": {
                "field_type": "OBJECTID",
                "precision": None,
                "scale": None,
                "length": None,
                "alias": "RID",
                "nullable": False,
                "required": True,
                "default": None,
                "domain": None,
                "meta_summary": None,
            },
            "FlowDirection": {
                "field_type": "TEXT",
                "precision": None,
                "scale": None,
                "length": 4,
                "alias": "Flow Direction",
                "nullable": True,
                "required": False,
                "default": None,
                "domain": "Lake River Flow",
                "meta_summary": "Whether the river flows into or out of the lake (or both).",
            },
        },
        "subtypes": None,
    },
}


# Dictionary of all datasets combined together
DATASETS = {**TABLES, **FEAT_CLS, **REL_CLS}


# List of fields combined with the dataset [[dataset_1, field_1], [dataset_1, field_2], [dataset_2, field_1]]
FIELDS_WITH_DATASET:list[list[str, str]] = []
for dts_name, dts_props in DATASETS.items():
    for fld_name, fld_props in dts_props["fields"].items():
        FIELDS_WITH_DATASET.append([dts_name, fld_name])


# Dictionary of datasets with subtypes
DATASETS_WITH_SUBTYPES = {k:v for k, v in DATASETS.items() if v["subtypes"]}


# List of datasets combined with subtypes code [[dataset_1, code_1], [dataset_1, code_2], [dataset_2, code_1]]
DATASETS_WITH_SUBTYPE_CODES:list[list[str, str]] = []
for dts_name, dts_props in DATASETS.items():
    if dts_props["subtypes"]:
        for code, sub_props in dts_props["subtypes"]["codes"].items():
            DATASETS_WITH_SUBTYPE_CODES.append([dts_name, code])