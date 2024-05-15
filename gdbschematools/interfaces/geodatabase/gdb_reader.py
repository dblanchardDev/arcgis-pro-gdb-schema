"""
Reader File and Enterprise Geodatabases from ArcGIS.

Author: David Blanchard
"""

import warnings
from typing import TYPE_CHECKING, Union

import arcpy

from . import gdb_metadata
from .gdb_converter import ap2st
from ...structures import Geodatabase

if TYPE_CHECKING:
    from ...structures import Datasets, Domains, FeatureDataset


def _is_archived(dts_desc) -> bool:
    """Check whether a dataset is archived.

    Args:
        dts_desc (arcpy describe): description of the dataset.

    Returns:
        bool: Whether it is archived.
    """
    is_archived = False
    try:
        is_archived = dts_desc.isArchived
    except AttributeError:
        pass

    return is_archived


def _get_key(keys:tuple[str, str], role:str) -> str:
    """Get the relationship key that matches the role.

    Args:
        keys (tuple[str, str]): Set of keys|roles.
        role (str): Role to be matched.

    Returns:
        str: The key that matches the role.
    """
    name = None
    if keys is not None:
        matches = [e[0] for e in keys if e[1] == role]

        if len(matches) == 1:
            name = matches[0]

    return name


def _split_dataset_name(geodatabase:"Geodatabase", dataset_desc) -> tuple[str, Union[str, None]]:
    """Split a dataset name into its schema and dataset name components, dropping the database name.

    Args:
        geodatabase (Geodatabase): Geodatabase object in which the dataset is to be contained.
        dataset_desc (arcpy description): Description of the dataset whose name needs to be split.

    Returns:
        tuple[str, Union[str, None]]: (dataset name, dataset schema)
    """
    name = dataset_desc.name
    schema = None

    if geodatabase.workspace_type == "REMOTE_DATABASE" and len(name.split(".")) == 3:
        parts = name.split(".")
        name = parts[2]
        schema = parts[1]

    return (name, schema)


def parse_full_geodatabase(source:str) -> None:
    """Parse the entire geodatabase into a Geodatabase structure.

    Args:
        source (str): Path to the file geodatabase or enterprise geodatabase connection file.
    """
    arcpy.SetProgressor("default", "Reading geodatabase information.")
    gdb_desc = arcpy.Describe(source)

    geodatabase = parse_geodatabase(gdb_desc)
    parse_domains(geodatabase, gdb_desc)
    walk_gdb(geodatabase, gdb_desc)

    return geodatabase


def parse_geodatabase(gdb_desc) -> "Geodatabase":
    """Read the geodatabase level data from Arcpy and create a Geodatabase structure with it.

    Args:
        gdb_desc (arcpy describe): Description of the geodatabase.

    Returns:
        Geodatabase: Geodatabase structure
    """
    arcpy.SetProgressorLabel("Reading geodatabase information.")
    workspace_type = ap2st.workspace_types[gdb_desc.workspaceType]
    name = gdb_desc.baseName
    server = None

    if workspace_type == "REMOTE_DATABASE":
        name = gdb_desc.connectionProperties.database
        server = gdb_desc.connectionProperties.server

    return Geodatabase(
        name=name,
        server=server,
        meta_summary=gdb_metadata.get_geodatabase_summary(gdb_desc),
        workspace_type=workspace_type,
    )


def parse_domains(geodatabase:"Geodatabase", gdb_desc):
    """Read all domains in a geodatabase and them to Geodatabase structure.

    Args:
        geodatabase (Geodatabase): Geodatabase structure in which domains will be added.
        gdb_desc (arcpy describe): Description of the geodatabase.
    """
    arcpy.SetProgressorLabel("Reading domain information.")
    domains_desc = arcpy.da.ListDomains(gdb_desc.catalogPath)

    for dm_desc in domains_desc:
        try:
            domain:"Domains" = geodatabase.domains.new(
                name=dm_desc.name,
                description=dm_desc.description,
                field_type=ap2st.domain_field_types[dm_desc.type],
                domain_type=ap2st.domain_types[dm_desc.domainType],
                split_policy=ap2st.split_policies[dm_desc.splitPolicy],
                merge_policy=ap2st.merge_policies[dm_desc.mergePolicy],
                value_range=dm_desc.range,
                schema=str(dm_desc.owner) or None,
            )

            if dm_desc.domainType == "CodedValue":
                for code, value in dm_desc.codedValues.items():
                    domain.codes.new(code, value)
        except Exception as exc:
            #pylint: disable-next=broad-exception-raised
            raise Exception(f"Failure while reading domain {dm_desc.name}.") from exc


def walk_gdb(geodatabase:"Geodatabase", gdb_desc):
    """Walk through all feature datasets and datasets in the geodatabase and add them to the geodatabase structure.

    Args:
        geodatabase (Geodatabase): Geodatabase structure in which datasets will be added.
        gdb_desc (arcpy describe): Description of the geodatabase.
    """
    arcpy.SetProgressorLabel("Reading dataset and relationship class information.")
    root_descs = []

    for child_desc in gdb_desc.children:
        if child_desc.dataType == "FeatureDataset":
            parse_feature_dataset(geodatabase, child_desc)
        else:
            root_descs.append(child_desc)

    walk_datasets(geodatabase, root_descs)


def parse_feature_dataset(geodatabase:"Geodatabase", feat_dts_desc):
    """Read a feature dataset's info and add it to the geodatabase structure.

    Args:
        geodatabase (Geodatabase): Geodatabase structure in which datasets will be added.
        feat_dts_desc (arcpy describe): Feature dataset to be added.
    """
    name, schema = _split_dataset_name(geodatabase, feat_dts_desc)
    meta_summary = gdb_metadata.get_dataset_summary(feat_dts_desc)
    feature_dataset = geodatabase.feature_datasets.new(name, schema, meta_summary)

    walk_datasets(geodatabase, feat_dts_desc.children, feature_dataset)


def walk_datasets(geodatabase:"Geodatabase", dts_descs, feature_dataset:"FeatureDataset"=None):
    """Walk through the datasets, adding each to the geodatabase structure.

    Args:
        geodatabase (Geodatabase): Geodatabase structure in which datasets will be added.
        dts_descrips (lst[arcpy describe]): Datasets to be added.
        feature_dataset (FeatureDataset, optional): Feature dataset to which the datasets belong. Defaults to None.
    """
    relationships = []

    for dts_desc in dts_descs:
        if dts_desc.dataType == "RelationshipClass":
            relationships.append(dts_desc)

        elif dts_desc.dataType == "Table":
            parse_table(geodatabase, dts_desc, feature_dataset)

        elif dts_desc.dataType == "FeatureClass":
            parse_feature_class(geodatabase, dts_desc, feature_dataset)

        else:
            warnings.warn(f"Encountered a {dts_desc.dataType} dataset which are not supported.")


    for rel_cl_desc in relationships:
        parse_relationship_class(geodatabase, rel_cl_desc, feature_dataset)


def parse_table(geodatabase:"Geodatabase", table_desc, feature_dataset:"FeatureDataset"=None):
    """Read a table from a geodatabase adding it to a geodatabase structure.

    Args:
        geodatabase (Geodatabase): Geodatabase structure in which datasets will be added.
        table_desc (arcpy describe): Table to be parsed.
        feature_dataset (arcpy describe, optional): Feature dataset to which the table belongs. Defaults to None.
    """

    name, schema = _split_dataset_name(geodatabase, table_desc)

    try:
        table = geodatabase.datasets.tables.new(
            name=name,
            alias=table_desc.aliasName or None,
            schema=schema,
            is_archived=_is_archived(table_desc),
            is_versioned=table_desc.isVersioned,
            oid_is_64=getattr(table_desc, "hasOID64", None),
            dsid=table_desc.DSID,
            meta_summary=gdb_metadata.get_dataset_summary(table_desc),
            feature_dataset=feature_dataset,
        )
        parse_dataset_fields(table, table_desc)
        parse_dataset_subtypes(table, table_desc)

    except Exception as exc:
        #pylint: disable-next=broad-exception-raised
        raise Exception(f"Failure while reading table {name}.") from exc


def parse_feature_class(geodatabase:"Geodatabase", fc_desc, feature_dataset:"FeatureDataset"=None):
    """Read a feature class from arcpy and add it to a geodatabase structure.

    Args:
        geodatabase (Geodatabase): Geodatabase structure in which datasets will be added.
        fc_desc (arcpy describe): Feature class to be parsed.
        feature_dataset (arcpy describe, optional): Feature dataset to which the feature class belongs. Defaults to None.
    """ #pylint: disable=line-too-long

    name, schema = _split_dataset_name(geodatabase, fc_desc)

    try:
        feature_class = geodatabase.datasets.feature_classes.new(
            name=name,
            geometry_type=ap2st.geometry_types[fc_desc.shapeType],
            spatial_ref=arcpy.SpatialReference(text=fc_desc.SpatialReference.exportToString()),
            has_m=fc_desc.hasM,
            has_z=fc_desc.hasZ,
            alias=fc_desc.aliasName or None,
            schema=schema,
            is_archived=_is_archived(fc_desc),
            is_versioned=fc_desc.isVersioned,
            oid_is_64=getattr(fc_desc, "hasOID64", None),
            dsid=fc_desc.DSID,
            meta_summary=gdb_metadata.get_dataset_summary(fc_desc),
            feature_dataset=feature_dataset,
        )
        parse_dataset_fields(feature_class, fc_desc)
        parse_dataset_subtypes(feature_class, fc_desc)
    except Exception as exc:
        #pylint: disable-next=broad-exception-raised
        raise Exception(f"Failure while reading featureclass {name}.") from exc

def parse_relationship_class(geodatabase:"Geodatabase", rel_cl_desc, feature_dataset:"FeatureDataset"=None):
    """Read a relationship class and add it to a geodatabase structure. Must be done after the related tables and feature classes have been added.

    Args:
        geodatabase (Geodatabase): Geodatabase structure in which datasets will be added.
        table_desc (arcpy describe): Table to be parsed.
        feature_dataset (arcpy describe, optional): Feature dataset to which the table belongs. Defaults to None.
    """ #pylint: disable=line-too-long

    name, schema = _split_dataset_name(geodatabase, rel_cl_desc)

    try:
        origin_table_name = rel_cl_desc.originClassNames[0]
        destin_table_name = rel_cl_desc.destinationClassNames[0]
        origin_primary = _get_key(rel_cl_desc.originClassKeys, "OriginPrimary")
        destin_primary = _get_key(rel_cl_desc.destinationClassKeys, "DestinationPrimary")
        origin_foreign = _get_key(rel_cl_desc.originClassKeys, "OriginForeign")
        destin_foreign = _get_key(rel_cl_desc.destinationClassKeys, "DestinationForeign")

        relationship = geodatabase.datasets.relationship_classes.new(
            name=name,
            origin_table=geodatabase.datasets[origin_table_name],
            destination_table=geodatabase.datasets[destin_table_name],
            relationship_type="COMPOSITE" if rel_cl_desc.isComposite else "SIMPLE",
            forward_label=rel_cl_desc.forwardPathLabel,
            backward_label=rel_cl_desc.backwardPathLabel,
            notification=ap2st.notifications[rel_cl_desc.notification],
            cardinality=ap2st.cardinalities[rel_cl_desc.cardinality],
            attributed=rel_cl_desc.isAttributed,
            origin_primary_key=origin_primary,
            origin_foreign_key=origin_foreign,
            destination_primary_key=destin_primary,
            destination_foreign_key=destin_foreign,
            schema=schema,
            is_archived=_is_archived(rel_cl_desc),
            is_versioned=rel_cl_desc.isVersioned,
            oid_is_64=getattr(rel_cl_desc, "hasOID64", False),
            dsid=None if rel_cl_desc.DSID == -1 else rel_cl_desc.DSID,
            meta_summary=gdb_metadata.get_dataset_summary(rel_cl_desc),
            feature_dataset=feature_dataset,
        )

        parse_dataset_fields(relationship, rel_cl_desc)
        parse_dataset_subtypes(relationship, rel_cl_desc)
    except Exception as exc:
        #pylint: disable-next=broad-exception-raised
        raise Exception(f"Failure while reading relationship {name}.") from exc

def parse_dataset_fields(dataset:"Datasets", dataset_desc):
    """Read the fields and add them to a dataset structure.

    Args:
        dataset (Datasets): dataset structure to which the fields are to be added.
        dataset_desc (arcpy describe): arcpy description of dataset.
    """
    skip_fields = []
    if hasattr(dataset_desc, "lengthFieldName"):
        skip_fields.append(dataset_desc.lengthFieldName)
    if hasattr(dataset_desc, "areaFieldName"):
        skip_fields.append(dataset_desc.areaFieldName)

    for field_desc in dataset_desc.fields:
        try:
            # Skip automatic fields
            if field_desc.name in skip_fields:
                continue

            # Get size fields according to type
            precision = field_desc.precision
            scale = field_desc.scale
            length = field_desc.length

            if field_desc.type not in ["String"]:
                length = None
            if field_desc.type not in ["BigInteger", "Integer", "SmallInteger", "Single", "Double"]:
                precision = None
            if field_desc.type not in ["Single", "Double"]:
                scale = None

            domain = None if field_desc.domain == "" else dataset.geodatabase.domains[field_desc.domain]

            # Create new field
            dataset.fields.new(
                name=field_desc.name,
                field_type=ap2st.field_types[field_desc.type],
                precision=precision,
                scale=scale,
                length=length,
                alias=field_desc.aliasName,
                nullable=field_desc.isNullable,
                required=field_desc.required,
                default=field_desc.defaultValue,
                domain=domain,
                meta_summary=gdb_metadata.get_field_summary(dataset_desc, field_desc.name),
            )

            if domain and domain.domain_type == "CODED":
                parse_domain_metadata(domain, dataset_desc, field_desc.name)
        except Exception as exc:
            #pylint: disable-next=broad-exception-raised
            raise Exception(f"Failure while reading {dataset.name}.{field_desc.name} field.") from exc

def parse_domain_metadata(domain:"Domains", dataset_desc, field_name:str):
    """Update the coded value domain summary with the definitions pulled from the field metadata.

    Args:
        domain (Domains): Domain structure to be updated.
        dataset_desc (object): ArcPy Describe object for the dataset that contains the field with the domain.
        field_name (str): Name of the field to which the domain is assigned.
    """
    try:
        enum_values = gdb_metadata.get_enumerated_domain_values(dataset_desc, field_name)
        for code, summary in enum_values.items():
            converted_code = domain.convert_value(code)
            if domain.test_value(converted_code):
                domain.codes[converted_code].meta_summary = summary
    except Exception as exc:
            #pylint: disable-next=broad-exception-raised
        raise Exception(f"Failure while reading {dataset_desc.name}.{field_name} coded domains.") from exc


def parse_dataset_subtypes(dataset:"Datasets", dataset_desc):
    """Read the subtypes and add them to a dataset structure.

    Args:
        dataset (Datasets): dataset structure to which the subtypes are to be added.
        dataset_desc (arcpy describe): arcpy description of dataset.
    """
    subtypes_desc = None

    try:
        subtypes_desc = arcpy.da.ListSubtypes(dataset_desc.catalogPath)
    except SystemError as exc:
        if dataset.dataset_type == "RelationshipClass":
            return # happens on some non-attributed rel-classes
        raise exc
    subtypes_field_name = next(iter(subtypes_desc.values()))['SubtypeField']

    if len(subtypes_field_name) > 0:
        subtypes = dataset.set_subtype(dataset.fields[subtypes_field_name])
        enum_values = gdb_metadata.get_enumerated_domain_values(dataset_desc, subtypes_field_name)
        try:
            for code in subtypes_desc:
                code_desc = subtypes_desc[code]
                meta_summary = enum_values.get(str(code))
                code_props = subtypes.codes.new(code, code_desc["Name"], meta_summary)

                for field_name, (default_val, domain_desc) in code_desc["FieldValues"].items():
                    if default_val is not None or domain_desc is not None:
                        subfield_props = code_props.field_props[field_name]
                        subfield_props.default = default_val
                        subfield_props.domain = dataset.geodatabase.domains[domain_desc.name]
        except Exception as exc:
            #pylint: disable-next=broad-exception-raised
            raise Exception(f"Failure while reading {dataset_desc.name}.{code} subtype.") from exc