"""
Reader File and Enterprise Geodatabases from ArcGIS.

Author: Roya Shourouni
"""

import os
import warnings
from typing import TYPE_CHECKING
import arcpy
from . import gdb_metadata
if TYPE_CHECKING:
    from ...structures import Geodatabase, Domains, FeatureDataset, Dataset
    from ...structures import FeatureClass, Table, Relationship, Field
    from ...structures.dataset import Subtype
    from ...structures.accessors.subtype_accessor import SubtypeProperties, SubtypeFieldProperties


def convert_date_values(field_type:str, value:any) -> any:
    """Convert DATE, DATEONLY, and TIMEONLY to a full date: YYYY-MM-DD HH:mm:ss
    e.g. "2024-02-06 14:44:26" and keep the other data types intact.

    Args:
        field_type (str): The object type of a variable
        value (any): the value of a variable

    Returns:
        any:
    """
    if field_type in ["DATE", "DATEONLY", "TIMEONLY"]:
        return value.strftime('%Y-%m-%d %H:%M:%S')

    return value

def write_full_geodatabase(path_to_gdb:str, gdb_struct:"Geodatabase"):
    """Write the full geodatabase structure to a file or enterprise geodatabase from an existing geodatabase structure.

    Args:
        path_to_gdb (str): Path to the file or enterprise geodatabase. Should be empty.
        gdb_struct (Geodatabase): Geodatabase structure instance from which the gdb is to be populated.
    """

    arcpy.SetProgressor("default", "Updating Geodatabase Metadata.")

    if gdb_struct.meta_summary is not None:
        gdb_metadata.update_metadata(path_to_gdb, gdb_struct.meta_summary)

    # Create domains, featuredatasets and datasets in geodatabase
    arcpy.SetProgressor("default", "Creating domains in geodatabase.")
    create_domains(path_to_gdb, gdb_struct)

    arcpy.SetProgressor("default", "Creating feature datasets in geodatabase.")
    create_featuredatasets(path_to_gdb, gdb_struct)

    arcpy.SetProgressor("default", "Creating datasets in geodatabase.")
    create_datasets(path_to_gdb, gdb_struct)

def create_domains(path_to_gdb:str, gdb_struct:"Geodatabase"):
    """Read all domains from Geodatabase structure and write them to a geodatabase.

    Args:
        path_to_gdb (str): Path to the file or enterprise geodatabase.
        gdb_struct (Geodatabase): Geodatabase structure from which domains will be read.
    """
    domains : list["Domains"] = gdb_struct.domains #Sequence of domains, behaves like a sequence.
    for domain in domains:
        try:
            domain_name = domain.name
            domain_description = domain.description
            field_type = domain.field_type
            domain_type = domain.domain_type
            split_policy = domain.split_policy
            merge_policy = domain.merge_policy

            arcpy.management.CreateDomain(path_to_gdb, domain_name, domain_description, field_type, domain_type,
                                        split_policy, merge_policy)

            if domain_type == "CODED":
                for code , props in domain.codes.items():
                    code = convert_date_values(domain.field_type, code)
                    arcpy.management.AddCodedValueToDomain(path_to_gdb, domain_name, code, props.description)

            elif domain_type == "RANGE":
                min_value = convert_date_values(domain.field_type, domain.minimum)
                max_value = convert_date_values(domain.field_type, domain.maximum)
                arcpy.management.SetValueForRangeDomain(path_to_gdb, domain_name, min_value, max_value)
                if domain.field_type in ["DATE", "DATEONLY", "TIMEONLY"]:
                    arcpy.management.SetValueForRangeDomain(path_to_gdb, domain_name, min_value, max_value)
        except Exception as exc:
            #pylint: disable-next=broad-exception-raised
            raise Exception(f"Failure while creating {domain.name} domain.") from exc

def create_featuredatasets(path_to_gdb:str, gdb_struct:"Geodatabase"):
    """Create feature datasets that match the feature datasets described in the ingested geodatabase structure.

    Args:
        path_to_gdb (str): Path to the file or enterprise geodatabase.
        gdb_struct (Geodatabase): Geodatabase structure from which feature datasets will be read.
    """
    feature_datasets : list["FeatureDataset"] = gdb_struct.feature_datasets

    for feature_dataset in feature_datasets:
        spatial_reference = None
        try:
            if feature_dataset.datasets is not None:
                for dataset in feature_dataset.datasets:
                    if dataset.dataset_type == "FeatureClass":
                        spatial_reference = dataset.spatial_ref
                        break
            arcpy.management.CreateFeatureDataset(path_to_gdb, feature_dataset.name, spatial_reference)
            # Assign the Metadata summary to the feature dataset
            if feature_dataset.meta_summary is not None:
                path_to_fds = os.path.join(path_to_gdb, feature_dataset.name)
                gdb_metadata.update_metadata(path_to_fds, feature_dataset.meta_summary)
        except Exception as exc:
            #pylint: disable-next=broad-exception-raised
            raise Exception(f"Failure while creating {feature_dataset.name} feature dataset.") from exc

def create_datasets(path_to_gdb:str, gdb_struct:"Geodatabase"):
    """Create datasets that match the datasets described in the ingested geodatabase structure.

    Args:
        path_to_gdb (str): Path to the file or enterprise geodatabase.
        gdb_struct (Geodatabase): Geodatabase structure from which datasets will be read.
    """
    datasets : list["Dataset"] = gdb_struct.datasets

    # Create tables and Feature classes
    arcpy.SetProgressor("default", "Creating datasets in geodatabase.")
    is_enterprise = arcpy.Describe(path_to_gdb).workspaceType == "RemoteDatabase"

    for dataset in datasets:
        out_path = os.path.join(path_to_gdb, dataset.feature_dataset.name) if dataset.feature_dataset \
            else path_to_gdb
        path_to_dataset = os.path.join(out_path, dataset.name)
        # Create dataset
        if dataset.dataset_type == "FeatureClass":
            create_feature_class (out_path, dataset)
        elif dataset.dataset_type == "Table":
            create_table(out_path, dataset)

        # Enable Archiving if it's an enterprise geodatabases and archiving is enabled for a dataset.
        if is_enterprise and dataset.is_archived:
            arcpy.EnableArchiving_management(path_to_dataset)
        elif not is_enterprise and dataset.is_archived:
            warnings.warn("Archiving is only supported on enterprise GDB.File GDB do not support archiving.")
        # Warning if dataset versioning is enabled
        if dataset.is_versioned:
            warnings.warn("The GDB Schema tool does not support enabling editor tracking.")

    # Create relationship classes once tables and feature classes created
    arcpy.SetProgressor("default", "Creating relationship classes in geodatabase.")
    for dataset in datasets.relationship_classes:
        out_path = os.path.join(path_to_gdb, dataset.feature_dataset.name) if dataset.feature_dataset else path_to_gdb
        create_relationship_class (out_path, dataset)
        # Enable Archiving if it is not already enabled.
        if is_enterprise and dataset.is_archived:
            arcpy.EnableArchiving_management(path_to_dataset)
        elif not is_enterprise and dataset.is_archived:
            warnings.warn("Archiving is only supported on enterprise GDB.File GDB do not support archiving.")

        # Warning if dataset versioning is enabled
        if dataset.is_versioned:
            warnings.warn("The GDB Schema tool does not support enabling editor tracking.")

def create_feature_class(out_path:str, dataset:"FeatureClass"):
    """Create feature class in the geodatabase that match the geodatabase structure.

    Args:
        out_path (str): Path to the feature dataset or gdb in which the output feature class will be created.
        dataset (FeatureClass): A new feature class to be created.
    """
    try:
        name = dataset.name
        geometry_type = dataset.geometry_type
        has_m = "ENABLED" if dataset.has_m else "DISABLED"
        has_z = "ENABLED" if dataset.has_z else "DISABLED"
        spatial_reference = dataset.spatial_ref
        alias = dataset.alias
        oid_type="64_BIT" if dataset.oid_is_64 else "32_BIT"

        # Create the feature class
        arcpy.management.CreateFeatureclass(out_path, name, geometry_type, None, has_m, has_z,
                                        spatial_reference, out_alias=alias, oid_type=oid_type)
        # Assign the Metadata summary to the feature class
        if dataset.meta_summary is not None:
            path_to_ds = os.path.join(out_path, dataset.name)
            gdb_metadata.update_metadata(path_to_ds, dataset.meta_summary)

        # Add Fields
        for field in dataset.fields:
            add_field(os.path.join(out_path, name), field)

        #Add Subtypes
        if dataset.subtype:
            add_subtype(os.path.join(out_path, dataset.name), dataset.subtype)

    except Exception as exc:
        #pylint: disable-next=broad-exception-raised
        raise Exception(f"Failure while creating {dataset.name} featureclass.") from exc

def create_table(out_path:str, dataset:"Table"):
    """Create table in the geodatabase that match the geodatabase structure.

    Args:
        out_path (str): Path to the feature dataset or gdb in which the output table will be created.
        dataset (Table): A new table to be created.
    """
    oid_type="64_BIT" if dataset.oid_is_64 else "32_BIT"
    try:
        arcpy.management.CreateTable(out_path, dataset.name, template=None, out_alias=dataset.alias, oid_type=oid_type)

        # Assign the Metadata summary to the table
        if dataset.meta_summary is not None:
            path_to_ds = os.path.join(out_path, dataset.name)
            gdb_metadata.update_metadata(path_to_ds, dataset.meta_summary)
        # Add fields
        for field in dataset.fields:
            add_field(os.path.join(out_path, dataset.name), field)

        if dataset.subtype:
            add_subtype(os.path.join(out_path, dataset.name), dataset.subtype)
    except Exception as exc:
        #pylint: disable-next=broad-exception-raised
        raise Exception(f"Failure while creating {dataset.name} featureclass.") from exc

def create_relationship_class (out_path:str, dataset:"Relationship"):
    """_summary_

    Args:
        out_path (str): Path to the feature dataset or gdb in which the output relation class will be created.
        dataset (Relationship): The new relationship class to be created.
    """
    try:
        d = dataset
        origin_table = os.path.join(out_path, d.origin.table.name)
        destination_table = os.path.join(out_path, d.destination.table.name)
        out_relationship_class = os.path.join(out_path, d.name)
        origin_primary_key = d.origin.primary_key
        origin_foreign_key = d.origin.foreign_key
        destination_primary_key = d.destination.primary_key
        destination_foreign_key = d.destination.foreign_key

        arcpy.management.CreateRelationshipClass(origin_table, destination_table, out_relationship_class,
                                                d.relationship_type, d.forward_label, d.backward_label, d.notification,
                                                d.cardinality, d.attributed, origin_primary_key, origin_foreign_key,
                                                destination_primary_key, destination_foreign_key)



        # Assign the Metadata summary to the relationship class
        if dataset.meta_summary is not None:
            path_to_ds = os.path.join(out_path, dataset.name)
            gdb_metadata.update_metadata(path_to_ds, dataset.meta_summary)

        # Add additional fields When a relationship class is attributed
        if dataset.attributed:
            for f in dataset.fields:
                if f.name not in [origin_primary_key, origin_foreign_key, destination_primary_key, \
                                  destination_foreign_key]:
                    add_field(out_relationship_class, f)
            if dataset.subtype:
                add_subtype(os.path.join(out_path, dataset.name), dataset.subtype)
    except Exception as exc:
        #pylint: disable-next=broad-exception-raised
        raise Exception(f"Failure while creating {dataset.name} relationship.") from exc

def add_field(out_path:str, field:"Field"):
    """Adds new fields to an existing dataset in geodatabases.

    Args:
        out_path (str): The path of dataset in geodatabase where the fields will be added.
        field (Field): A new field to be added to a dataset.
    """
    try:
        if field.field_type == "OBJECTID":
            field_name = arcpy.ListFields(out_path, field_type="OID")[0].name
            arcpy.management.AlterField(out_path, field_name, new_field_alias=field.alias)
        elif field.field_type == "SHAPE":
            field_name = arcpy.ListFields(out_path, field_type="GEOMETRY")[0].name
            arcpy.management.AlterField(out_path, field_name, new_field_alias=field.alias)
        else:
            field_name = field.name
            if field.domain is not None and field.domain.domain_type == "CODED":
                for code, props in field.domain.codes.items():
                    if props.meta_summary is not None:
                        gdb_metadata.update_edomain_metadata(out_path, field.name, field.domain, code,
                                                            field.meta_summary, field.alias)
            # Add field to dataset
            domain = field.domain.name if field.domain else None
            arcpy.management.AddField(out_path, field.name, field.field_type, field.precision, field.scale,
                                    field.length, field.alias, field.nullable, field.required, domain)
            # Assign default value to a field
            if field.default is not None:
                arcpy.management.AssignDefaultToField(out_path, field.name, field.default)

        # Update field metadata
        if field.meta_summary is not None:
            gdb_metadata.update_field_metadata(out_path, field_name, field.meta_summary, field.alias)
    except Exception as exc:
        #pylint: disable-next=broad-exception-raised
        raise Exception(f"Failure while creating {field_name} field.") from exc

def add_subtype (out_path:str, subtype:"Subtype"):
    """Adds a new subtype field to the input dataset.

    Args:
        out_path (str): The path of dataset in geodatabase where subtype field will be added.
        subtype (Subtype): A new subtype field to be added.
    """
    arcpy.SetSubtypeField_management(out_path, subtype.field.name)

    # Process: Add Subtype codes...
    subtype_dict : list["SubtypeProperties"] = subtype.codes
    for code in subtype_dict:
        try:
            arcpy.AddSubtype_management(out_path, code, subtype_dict[code].description)
            # Add domain and default values of other fields for each code
            fields : list["SubtypeFieldProperties"] = subtype_dict[code].field_props
            for field in fields:
                if field.domain is not None:
                    arcpy.management.AssignDomainToField(out_path, field.name, field.domain.name, code)
                if field.default is not None:
                    field_default = convert_date_values (field.field.field_type, field.default)
                    arcpy.management.AssignDefaultToField(out_path, field.name, field_default, code)

            # Add metadata summary for codes
            if subtype_dict[code].meta_summary:
                gdb_metadata.update_edomain_metadata(out_path, subtype.field.name, subtype, code,
                                                    subtype.field.meta_summary, subtype.field.alias)
            if subtype.default is not None:
                arcpy.SetDefaultSubtype_management (out_path, subtype.default)

        except Exception as exc:
            #pylint: disable-next=broad-exception-raised
            raise Exception(f"Failure while creating {subtype.dataset}.{code} subtype.") from exc