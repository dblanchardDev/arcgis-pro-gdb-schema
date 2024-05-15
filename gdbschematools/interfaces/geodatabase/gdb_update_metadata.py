"""
Utility to update the metadata of an existing Geodatabase from a structure.

Author: Roya Shourouni
"""

import warnings
from typing import TYPE_CHECKING
import arcpy
from . import gdb_metadata
if TYPE_CHECKING:
    from ...structures import Geodatabase, Domains, FeatureDataset, Dataset, Relationship
    from ...structures import Field, CodedDomain, SubtypeProperties


def gdb_update_metadata(path_to_gdb:str, gdb_struct:"Geodatabase"):
    """Update an existing geodatabase and its objects with the metadata from another entity.

    Args:
        path_to_gdb (str): Path to the file or enterprise geodatabase for which the gdb metadata is to be updated.
        gdb_struct (Geodatabase): Geodatabase structure instance from which the gdb metadata is retrieved.
    """#pylint: disable=line-too-long

    gdb_desc = arcpy.Describe(path_to_gdb)

    # Assign the Metadata summary to the gdb
    if gdb_struct.meta_summary is not None:
        gdb_metadata.update_metadata(path_to_gdb, gdb_struct.meta_summary)

    # Assign the Metadata summary to the domains
    domain_update_metadata(gdb_struct, gdb_desc)

    # Assign the Metadata summary to the feature datasets
    fds_update_metadata(gdb_struct, gdb_desc)

    # Assign the Metadata summary to the datasets
    ds_update_metadata(gdb_struct, gdb_desc)

def domain_update_metadata(gdb_struct:"Geodatabase", gdb_desc):
    """Update existing domains with the metadata from another entity.

    Args:
        gdb_struct (Geodatabase): Geodatabase instance from which the domains metadata summary is retrieved.
        gdb_desc (arcpy describe): Description of the geodatabase.
    """
    domains : list["Domains"] = gdb_struct.domains
    domains_desc = arcpy.da.ListDomains(gdb_desc.catalogPath)

    for domain in domains:
        domain_desc = next((desc for desc in domains_desc if desc.name == domain.name), None)
        if domain_desc:
            if domain_desc.description != domain.description:
                arcpy.management.AlterDomain(gdb_desc.catalogPath, domain.name,
                                            new_domain_description=domain.description)
            if domain.domain_type == 'CODED':
                for code, desc in domain.codes.items():
                    if code not in domain_desc.codedValues:
                        warnings.warn(f"{code} domain code doesn't exist in '{domain.name}' domain.")
        else:
            warnings.warn(f"{domain.name} domain doesn't exist in {gdb_desc.name}.")

def fds_update_metadata(gdb_struct:"Geodatabase", gdb_desc):
    """Update existing feature datasets with the metadata from another entity.

    Args:
        gdb_struct (Geodatabase): Geodatabase instance from which the featuredataset metadata summary is retrieved.
        gdb_desc (arcpy describe): Description of the geodatabase for which the featuredataset metadata is to be updated.
    """#pylint: disable=line-too-long
    feature_datasets : list["FeatureDataset"] = gdb_struct.feature_datasets
    feat_dts_desc = []

    for child_desc in gdb_desc.children:
        if child_desc.dataType == "FeatureDataset":
            feat_dts_desc.append(child_desc)

    for feature_dataset in feature_datasets:
        fds_desc = next((desc for desc in feat_dts_desc if desc.name == feature_dataset.name), None)
        if fds_desc:
            fds_desc_meta_summary = gdb_metadata.get_dataset_summary(fds_desc)
            if feature_dataset.meta_summary != fds_desc_meta_summary:
                gdb_metadata.update_metadata(fds_desc.catalogPath, feature_dataset.meta_summary)
        else:
            warnings.warn(f"{feature_dataset.name} feature_dataset doesn't exist in {gdb_desc.name}.")

def ds_update_metadata(gdb_struct:"Geodatabase", gdb_desc):
    """Update existing datasets with the metadata from another entity.

    Args:
        gdb_struct (Geodatabase): Geodatabase instance from which the dataset metadata summary is retrieved.
        gdb_desc (arcpy describe): Description of the geodatabase for which the dataset metadata is to be updated.
    """#pylint: disable=line-too-long
    datasets : list["Dataset"] = gdb_struct.datasets
    dts_descs = []

    for child_desc in gdb_desc.children:
        if child_desc.dataType == "FeatureDataset":
            for child_child_desc in child_desc.children:
                dts_descs.append(child_child_desc)
        else:
            dts_descs.append(child_desc)

    for dataset in datasets:
        dt_desc = next((desc for desc in dts_descs if desc.name == dataset.name), None)
        if dt_desc:
            dt_desc_meta_summary = gdb_metadata.get_dataset_summary(dt_desc)
            if dataset.meta_summary != dt_desc_meta_summary:
                gdb_metadata.update_metadata(dt_desc.catalogPath, dataset.meta_summary)

            #Update metadata summary of fields and subtypes
            field_update_metadata(dataset, dt_desc)
            subtype_update_metadata(dataset, dt_desc)
        else:
            warnings.warn(f"{dataset.name} dataset doesn't exist in {gdb_desc.name}.")

def field_update_metadata(dataset:"Dataset", dataset_desc):
    """Update existing datasets with the metadata from another entity.

    Args:
        dataset (Dataset): Dataset from which the field metadata is retrieved.
        dataset_desc (arcpy describe):  Description of the dataset for which the field metadata is to be updated.
    """#pylint: disable=line-too-long
    path_to_ds = dataset_desc.catalogPath

    if dataset.dataset_type == "RelationshipClass":
        relationship : "Relationship" = dataset
        if not relationship.attributed:
            return

    fields : list ["Field"] = dataset.fields
    for field in fields:
        field_desc = next((desc for desc in dataset_desc.fields if desc.name == field.name), None)
        if field_desc:
            field_desc_meta_summary = gdb_metadata.get_field_summary(dataset_desc, field.name)
            if field.meta_summary != field_desc_meta_summary:
                gdb_metadata.update_field_metadata(path_to_ds, field.name, field.meta_summary, field.alias)

            #Assign metadata to coded domains
            domain = dataset.geodatabase.domains[field.domain.name] if field.domain else None
            if domain and domain.domain_type == "CODED":
                coded_domain_update_metadata(domain, dataset_desc, field_desc.name)
        else:
            warnings.warn(f"{field.name} field doesn't exist in in {dataset_desc.name}.")

def coded_domain_update_metadata(domain:"Domains", dataset_desc, field_name:str):
    """Update existing coded value domain summary with the metadata from another entity.

    Args:
        domain (Domains): Domain structure from which field metadata summary is retrieved.
        dataset_desc (object): ArcPy Describe object for the dataset that contains the field with the domain.
        field_name (str): Name of the field to which the domain metadata is to be updated.
    """

    field_desc = next((desc for desc in dataset_desc.fields if desc.name == field_name), None)

    if field_desc and field_desc.domain == domain.name:
        enum_values = gdb_metadata.get_enumerated_domain_values(dataset_desc, field_name)
        domain_codes : list["CodedDomain"] = domain.codes
        for code in domain_codes:
            converted_code = domain.convert_value(code)
            if domain.test_value(converted_code):
                domain_desc_meta_summary = enum_values.get(str(code))
                domain_meta_summary = domain.codes[converted_code].meta_summary
                if domain_meta_summary != domain_desc_meta_summary:
                    gdb_metadata.update_edomain_metadata(dataset_desc.catalogPath, field_name, domain, code,
                                                        domain_meta_summary)
    else:
        warnings.warn(f"{domain.name} domain doesn't exist in {dataset_desc.name}.{field_name} field.")

def subtype_update_metadata(dataset:"Dataset", dataset_desc):
    """Update existing datasets with the metadata from another entity.

    Args:
        dataset (Dataset): Dataset from which the field metadata is retrieved.
        dataset_desc (arcpy describe):  Description of the dataset for which the metadata of subtype field is to be updated.
    """#pylint: disable=line-too-long
    path_to_ds = dataset_desc.catalogPath
    subtypes_desc = None

    try:
        subtypes_desc = arcpy.da.ListSubtypes(dataset_desc.catalogPath)
    except SystemError as exc:
        if dataset.dataset_type == "RelationshipClass":
            return # happens on some non-attributed rel-classes
        raise exc
    subtypes_field_name = next(iter(subtypes_desc.values()))['SubtypeField']

    if len(subtypes_field_name) > 0:
        enum_values = gdb_metadata.get_enumerated_domain_values(dataset_desc, subtypes_field_name)
        dataset_subtypes : list["SubtypeProperties"] = dataset.subtype.codes
        for code in dataset_subtypes:
            if code in subtypes_desc:
                # Add metadata summary for codes
                code_desc_meta_summary = enum_values.get(str(code))
                if dataset_subtypes[code].meta_summary != code_desc_meta_summary:
                    gdb_metadata.update_edomain_metadata(path_to_ds, subtypes_field_name, dataset.subtype, code,
                                                        dataset_subtypes[code].meta_summary)
            else:
                warnings.warn(f"{code} subtype code doesn't exist in in {dataset_desc.name}.{subtypes_field_name}.")
