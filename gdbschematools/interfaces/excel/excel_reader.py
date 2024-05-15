"""
Reader to convert schemas from Excel workbooks to a Geodatabase structure.

Author: Roya Shourouni
"""

import re
from typing import TYPE_CHECKING

import arcpy

from ...structures import Geodatabase
from .excel_converter import xl2st
from .reader.excel_to_json import parse_workbook

if TYPE_CHECKING:
    from ...structures import Datasets, Domains, FeatureClass, Table, Relationship, FeatureDataset

def _is_true(boolean_field:str=None) -> bool:
    """Check whether a field is True or False.

    Args:
        boolean_field (str): The value of field which is yes or no.

    Returns:
        bool: Whether it is True.
    """
    if boolean_field == 'yes':
        return True
    else:
        return False

def get_or_default(obj:dict, key:str, default:any=None):
    """Checks the presence of a key in a dictionary. If the key exists and has a value it returns the value.
    If the key doesn't exist or its value is None, it returns a default value for the key.

    Args:
        object (dict): a dictionary object
        key (str): key in the dictionary
        default (any, optional): The default value of the field/key. Defaults to None.

    Returns:
        _type_: Returns either the value of the key or a default value if the key doesn't exist or its None
    """
    return obj.get(key,default) if obj.get(key,default) else default

def ingest_excel(datasets_source:str, domains_source:str=None, relationships_source:str=None) -> Geodatabase:
    """Read a set of Excel workbooks into an internal Geodatabase structure.

    Args:
        datasets_source (str): Path to the workbook containing dataset schemas.
        domains_source (str, optional): Path to the workbook containing domain schemas. If not provided, datasets and relationships cannot use domains. Defaults to None.
        relationships_source (str, optional): Path to the workbook containing relationship class schemas. If not provided, datasets cannot participate in relationships. Defaults to None.

    Returns:
        Geodatabase: Geodatabase structure resulting from reading the workbooks.
    """ #pylint: disable=line-too-long

    arcpy.SetProgressor("default", "Reading Excel workbooks.")
    (gdb_info_datasets, datasets_data) = parse_workbook(datasets_source)
    (gdb_info_domains, domains_data) = parse_workbook(domains_source)
    (gdb_info_relationships, relationships_data) = parse_workbook(relationships_source)
    del gdb_info_domains, gdb_info_relationships

    # 1. Create a geodatabase structure and set its properties
    arcpy.SetProgressorLabel("Parsing geodatabase information.")
    gdb = Geodatabase(
        name = gdb_info_datasets.get('Database Name', None) ,
        server = gdb_info_datasets.get('Remote Server', None),
        meta_summary = gdb_info_datasets.get('Summary', None),
        workspace_type = xl2st.workspace_types.get(gdb_info_datasets.get('Workspace Type', None), None)
    )


    # 2. Call a function to parse the domains
    arcpy.SetProgressorLabel("Parsing domain information.")
    parse_domains(gdb, domains_data)

    # 3. Call a function to parse the datasets (and then the fields and subtypes)
    arcpy.SetProgressorLabel("Parsing dataset information.")
    walk_gdb(gdb, datasets_data)

    # 4. Call a function to parse the relationship classes (and then the fields and subtypes)
    arcpy.SetProgressorLabel("Parsing relationship class information.")
    walk_gdb(gdb, relationships_data)

    return gdb

def parse_domains(geodatabase:"Geodatabase", domains_data:list):
    """Read domains info from a list resulting from reading the workbooks and add them to Geodatabase structure.

    Args:
        geodatabase (Geodatabase): Geodatabase structure in which domains will be added.
        domains_data (list): List of domains to be parsed.
    """

    for dm_data in domains_data:
        dm_desc = dm_data["key_value_pairs"]
        try:
            domain:"Domains" = geodatabase.domains.new(
                name=dm_desc["Name"],
                description=get_or_default(dm_desc, "Description", ''),
                field_type=xl2st.domain_field_types[dm_desc["Field Type"]],
                domain_type=xl2st.domain_types[dm_desc["Domain Type"]],
                split_policy=xl2st.split_policies[get_or_default(dm_desc, "Split Policy", "Default Value")],
                merge_policy=xl2st.merge_policies[get_or_default(dm_desc, "Merge Policy", "Default Value")],
                schema=dm_desc.get("Schema", None),
                value_range=(dm_desc["Minimum"],dm_desc["Maximum"]) if dm_desc["Domain Type"] == "Range" else None
            )

            if dm_desc["Domain Type"] == "Coded Value":
                dm_codes = dm_data["tables"]["Coded Values"]
                for coded_val in dm_codes:
                    domain.codes.new(coded_val['Code'], coded_val['Description'], coded_val.get("Summary", None))
        except Exception as exc:
            #pylint: disable-next=broad-exception-raised
            raise Exception(f"Failure while reading domain {dm_desc['Name']}.") from exc

def walk_gdb(geodatabase:"Geodatabase", datasets_data:list):
    """Walk through all feature datasets and datasets list and add them to the geodatabase structure.

    Args:
        geodatabase (Geodatabase): Geodatabase structure in which datasets will be added.
        datasets_data (list): List of datasets resulting from reading the workbooks.
    """
    for dataset_data in datasets_data:
        ds_desc = dataset_data["key_value_pairs"]
        if ds_desc.get("Feature Dataset", None) is not None:
            parse_feature_dataset(geodatabase, dataset_data)
        else:
            parse_datasets(geodatabase, dataset_data)

def parse_feature_dataset(geodatabase:"Geodatabase", dataset_data:dict):
    """Read a feature dataset's info and add it to the geodatabase structure.

    Args:
        geodatabase (Geodatabase): Geodatabase structure in which datasets will be added.
        dataset_data (dict): Feature dataset description.
    """
    datasets_desc = dataset_data["key_value_pairs"]
    fds_name = datasets_desc["Feature Dataset"]
    fds_schema = datasets_desc.get("Schema", None)
    #meta_summary = datasets_desc["Summary"] or None
    if not fds_name in geodatabase.feature_datasets:
        feature_dataset = geodatabase.feature_datasets.new(fds_name, fds_schema)
    else:
        feature_dataset = geodatabase.feature_datasets[fds_name]
    parse_datasets(geodatabase, dataset_data, feature_dataset)

def parse_datasets(geodatabase:"Geodatabase", dataset_data:dict, feature_dataset:"FeatureDataset"=None):
    """Read datasets info from a dataset list and add them to Geodatabase structure.

    Args:
        gdb (Geodatabase): Geodatabase structure in which datasets will be added.
        dataset_data (dict): Details of dataset resulting from reading the workbooks.
        feature_dataset (FeatureDataset, optional): Feature dataset to which the datasets belong. Defaults to None.
    """
    ds_desc = dataset_data["key_value_pairs"]
    try:
        if "Dataset Type" in ds_desc and ds_desc["Dataset Type"] == "Table":
            parse_table(geodatabase, dataset_data, feature_dataset)
        elif "Dataset Type" in ds_desc and ds_desc["Dataset Type"] == "Feature Class":
            parse_feature_class(geodatabase, dataset_data, feature_dataset)
        elif "Dataset Type" not in ds_desc and "Relationship Type" in ds_desc:
            parse_relationship_class(geodatabase, dataset_data, feature_dataset)
    except Exception as exc:
            #pylint: disable-next=broad-exception-raised
        raise Exception(f"Failure while reading dataset {ds_desc['Name']}.") from exc

def parse_table(geodatabase:"Geodatabase", table_data:dict, feature_dataset:"FeatureDataset"=None):
    """Read a table info from a table list resulting from reading the workbook and add it to a geodatabase structure.

    Args:
        geodatabase (Geodatabase): Geodatabase structure in which datasets will be added.
        table_data (dict): Description of table to be parsed.
        feature_dataset (FeatureDataset, optional): Feature dataset to which the table belongs. Defaults to None.
    """
    table_desc = table_data['key_value_pairs']
    table:"Table" = geodatabase.datasets.tables.new(
        name=table_desc["Name"],
        alias=table_desc.get("Alias", None),
        schema=table_desc.get("Schema", None),
        is_archived=_is_true(table_desc.get("Is Archived",False)),
        is_versioned=_is_true(table_desc.get("Is Versioned", False)),
        oid_is_64=_is_true(table_desc.get("64-bit OID", False)),
        dsid=table_desc.get("DSID", None),
        meta_summary=table_desc.get("Summary", None),
        feature_dataset=feature_dataset,
    )

    parse_dataset_fields(table, table_data)
    if "Subtype Details" in table_data["tables"]:
        parse_dataset_subtypes(table, table_data)

def parse_feature_class(geodatabase:"Geodatabase", fc_data:dict, feature_dataset:"FeatureDataset"=None):
    """Read a feature class info from a list resulting from reading the workbook and add it to a geodatabase structure.

    Args:
        geodatabase (Geodatabase): Geodatabase structure in which datasets will be added.
        fc_data (dict): Description of feature class to be parsed.
        feature_dataset (FeatureDataset, optional): Feature dataset to which the feature class belongs. Defaults to None.
    """ #pylint: disable=line-too-long
    fc_desc = fc_data["key_value_pairs"]
    hcs = fc_desc.get("Horizontal Spatial Ref.", None)
    hcs_wkid = int(re.findall(r'\d+',hcs)[0]) if hcs else None
    vcs = fc_desc.get("Vertical Spatial Ref.", None)
    vcs_wkid = int(re.findall(r'\d+',vcs)[0]) if vcs else None

    feature_class:"FeatureClass" = geodatabase.datasets.feature_classes.new(
        name=fc_desc["Name"],
        geometry_type=xl2st.geometry_types[fc_desc["Geometry Type"]],
        spatial_ref=arcpy.SpatialReference(hcs_wkid, vcs_wkid),
        alias=fc_desc.get("Alias", None),
        schema=fc_desc.get("Schema", None),
        has_m=_is_true(fc_desc.get("Has M-Values", False)),
        has_z=_is_true(fc_desc.get("Has Z-Values", False)),
        is_archived=_is_true(fc_desc.get("Is Archived",False)),
        is_versioned=_is_true(fc_desc.get("Is Versioned", False)),
        oid_is_64=_is_true(fc_desc.get("64-bit OID", False)),
        dsid=fc_desc.get("DSID", None),
        meta_summary=fc_desc.get("Summary", None),
        feature_dataset=feature_dataset,
    )

    parse_dataset_fields(feature_class, fc_data)
    if "Subtype Details" in fc_data["tables"]:
        parse_dataset_subtypes(feature_class, fc_data)

def parse_relationship_class(geodatabase:"Geodatabase", rel_cl_data:dict, feature_dataset:"FeatureDataset"=None):
    """Read all relationships info from a list resulting from reading the workbooks and add them to GDB structure.
    Must be done after the related tables and feature classes have been added.

    Args:
        geodatabase (Geodatabase): Geodatabase structure in which relationships will be added.
        relationships_data (dict): relationship class to be parsed resulting from reading the workbooks.
        feature_dataset (FeatureDataset, optional): Feature dataset to which the relationship class belongs. Defaults
            to None.
    """

    rel_cl_desc = rel_cl_data["key_value_pairs"]

    origin_table_name = rel_cl_desc["Origin Table"]
    destin_table_name = rel_cl_desc["Destination Table"]

    relationship:"Relationship" = geodatabase.datasets.relationship_classes.new(
        name=rel_cl_desc["Name"],
        origin_table=geodatabase.datasets[origin_table_name],
        destination_table=geodatabase.datasets[destin_table_name],
        relationship_type=xl2st.relationship_types[rel_cl_desc["Relationship Type"]],
        forward_label=rel_cl_desc["Forward Label"],
        backward_label=rel_cl_desc["Backward Label"],
        notification=xl2st.notifications[rel_cl_desc["Notifications"]],
        cardinality=xl2st.cardinalities[rel_cl_desc["Cardinality"]],
        origin_primary_key=rel_cl_desc["Origin Primary Key"],
        origin_foreign_key=rel_cl_desc["Origin Foreign Key"],
        destination_primary_key=rel_cl_desc.get("Destination Primary Key", None),
        destination_foreign_key=rel_cl_desc.get("Destination Foreign Key", None),
        schema=rel_cl_desc.get("Schema", None),
        attributed=_is_true(rel_cl_desc.get("Is Attributed", False)),
        is_archived=_is_true(rel_cl_desc.get("Is Archived",False)),
        is_versioned=_is_true(rel_cl_desc.get("Is Versioned", False)),
        oid_is_64=_is_true(rel_cl_desc.get("64-bit OID", False)),
        dsid=rel_cl_desc.get("DSID", None),
        meta_summary=rel_cl_desc.get("Summary", None),
        feature_dataset=feature_dataset,
    )

    if rel_cl_desc["Is Attributed"] and rel_cl_desc["Is Attributed"]=='yes':
        parse_dataset_fields(relationship, rel_cl_data)
    if "Subtype Details" in rel_cl_data["tables"]:
        parse_dataset_subtypes(relationship, rel_cl_data)

def parse_dataset_fields(dataset:"Datasets", dataset_data:dict):
    """Read the fields and add them to a dataset structure.

    Args:
        dataset (Datasets): dataset structure to which the fields are to be added.
        dataset_data (dict): description of dataset.
    """

    fields_desc = dataset_data["tables"]["Fields"]
    for field_desc in fields_desc:
        try:
            # Get size fields according to type
            precision = field_desc.get("Precision", None)
            scale = field_desc.get("Scale", None)
            length = field_desc.get("Length", None)

            if field_desc["Field Type"] not in ["Text"]:
                length = None
            if field_desc["Field Type"] not in ["Long Integer", "Integer", "Short Integer", "Single",
                                                "Double", "Float"]:
                precision = None
            if field_desc["Field Type"] not in ["Single", "Double", "Float"]:
                scale = None

            domain = None
            if field_desc.get("Domain Name",None):
                domain = dataset.geodatabase.domains[field_desc["Domain Name"]]

        # Create new field
            dataset.fields.new(
                name=field_desc["Field Name"],
                field_type=xl2st.field_types[field_desc["Field Type"]],
                meta_summary=field_desc.get("Summary", None),
                alias=field_desc.get("Alias Name", None),
                domain=domain,
                default=field_desc.get("Default Value", None),
                nullable=_is_true(field_desc.get("Is Nullable", True)),
                required=True if field_desc["Field Type"] in ["OBJECTID", "Geometry", "Global ID"] else False,
                precision=precision,
                scale=scale,
                length=length
            )
        except Exception as exc:
            #pylint: disable-next=broad-exception-raised
            raise Exception(f"Failure while reading field {field_desc['Field Name']}.") from exc

def parse_dataset_subtypes(dataset:"Datasets",  dataset_data:dict):
    """Read the subtypes and add them to a dataset structure.

    Args:
        dataset (Datasets): dataset structure to which the subtypes are to be added.
        dataset_data (dict): Description of dataset.
    """
    subtypes_desc = dataset_data["tables"]["Subtype Details"]
    subtype_field_name = dataset_data["key_value_pairs"]["Subtype Field Name"]
    try:
        if len(subtype_field_name) > 0:
            subtypes = dataset.set_subtype(dataset.fields[subtype_field_name])

        for subtype_code in subtypes_desc:
            code = subtype_code["Code"]
            code_desc = subtype_code["Subtype Name"]
            meta_summary = subtype_code["Description"]

            if code in subtypes.codes:
                code_props = subtypes.codes[code]
            else:
                code_props = subtypes.codes.new(code, code_desc, meta_summary)
            subfield_props = code_props.field_props[subtype_code["Field Name"]]
            subfield_props.default = subtype_code["Default Value"]
            subfield_props.domain = None
            if subtype_code["Domain Name"]:
                subfield_props.domain = dataset.geodatabase.domains[subtype_code["Domain Name"]]

    except Exception as exc:
        #pylint: disable-next=broad-exception-raised
        raise Exception(f"Failure while reading subtype {subtype_field_name}.") from exc