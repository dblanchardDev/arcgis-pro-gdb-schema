"""
Writer for the Excel spreadsheet output.

Author: David Blanchard
"""

import datetime
import os

from typing import TYPE_CHECKING, Union

import arcpy

from .excel_converter import st2xl, value_to_cell
from .writer import DatasetsWriter, DomainsWriter, RelationshipsWriter

if TYPE_CHECKING:
    from arcpy import SpatialReference
    from ...structures import Datasets, Domains, Field, Geodatabase, Relationship
    from ...structures.accessors.code_accessor import CodesTypes, Code
    from ...structures.accessors.subtype_accessor import SubtypeProperties, SubtypeFieldProperties
    from .writer.gdb_writer import GDBWriterWithFields


def _generate_spatial_ref_label(spatial_ref:Union["SpatialReference", "SpatialReference.VCS"]) -> str:
    """Produce a label from a spatial reference object.

    Args:
        spatial_ref (Union[SpatialReference, SpatialReference.VCS]): Spatial reference from which to generate a label.

    Returns:
        str: Label to be written to Excel.
    """
    label = None
    if spatial_ref:
        name = spatial_ref.name.replace("_", " ")
        wkid = spatial_ref.factoryCode
        label = f"{wkid} ({name})"

    return label


def _derive_workbook_paths(output_dir:str, gdb_name:str) -> tuple[str]:
    """Create file paths for all workbooks with the same timestamp and location.

    Args:
        output_dir (str): Directory to which all 3 workbooks will be written.
        gdb_name (str): Name of the geodatabase from which these are being derived.

    Returns:
        tuple[str]: All 3 paths (datasets, domains, relationships).
    """
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M")
    os.makedirs(output_dir, exist_ok=True)
    return (
        os.path.join(output_dir, f"{gdb_name}_{timestamp}_datasets.xlsx"),
        os.path.join(output_dir, f"{gdb_name}_{timestamp}_domains.xlsx"),
        os.path.join(output_dir, f"{gdb_name}_{timestamp}_relationships.xlsx"),
    )


def output_excel(gdb:"Geodatabase", output_dir:str, template_visible:bool=False,
                 skip_unchanged_fields:bool=True) -> tuple[str]:
    """Write all 3 spreadsheets (datasets, domains, relationships) from a geodatabase structure.

    Args:
        gdb (Geodatabase): Geodatabase structure from which the data output is to be produced.
        output_dir (str): Directory in which the spreadsheets are to be written.
        template_visible (bool, optional): Whether the template sheets (used to create new datasets/domains from
          scratch) are visible.
        skip_unchanged_fields (bool, optional): Whether to skip fields in the subtype that don't have a domain or
          default value set for the subtype.

    Returns:
        tuple(str): The 3 paths to which the spreadsheets were written (datasets, domains, relationships).
    """
    arcpy.SetProgressor("default", "Preparing spreadsheets.")

    # Get paths
    (datasets_path, domains_path, relationships_path) = _derive_workbook_paths(output_dir, gdb.name)

    # Create all the workbooks
    database_name = gdb.name
    workspace_type = st2xl.workspace_types[gdb.workspace_type]
    remote_server = gdb.server
    summary = gdb.meta_summary

    datasets_writer = DatasetsWriter(datasets_path, database_name, workspace_type, remote_server, summary,
                                     template_visible)
    dataset:"Datasets" = None
    for dataset in gdb.datasets.tables_and_feature_classes:
        datasets_writer.prepare_sheet(dataset.name, dataset.alias)

    domains_writer = DomainsWriter(domains_path, database_name, workspace_type, remote_server, summary,
                                   template_visible)
    domain:"Domains" = None
    for domain in gdb.domains:
        domains_writer.prepare_sheet(domain.name)

    relationships_writer = RelationshipsWriter(relationships_path, database_name, workspace_type, remote_server,
                                                   summary, template_visible)
    relationship:"Relationship" = None
    for relationship in gdb.datasets.relationship_classes:
        relationships_writer.prepare_sheet(relationship.name)

    # Register cross-workbook lookups
    registrations = {
        "datasets_path": datasets_writer.workbook_path,
        "datasets_lookup": datasets_writer.cw_lookup,
        "domains_path": domains_writer.workbook_path,
        "domains_lookup": domains_writer.cw_lookup,
        "relationships_path": relationships_writer.workbook_path,
        "relationships_lookup": relationships_writer.cw_lookup,
    }

    datasets_writer.register_cross_book_lookups(**registrations)
    domains_writer.register_cross_book_lookups(**registrations)
    relationships_writer.register_cross_book_lookups(**registrations)

    # Populate sheets with data
    _populate_datasets_workbook(datasets_writer, gdb, skip_unchanged_fields)
    _populate_domains_workbook(domains_writer, gdb)
    _populate_relationships_workbook(relationships_writer, gdb, skip_unchanged_fields)

    # Return paths
    return (datasets_path, domains_path, relationships_path)


def _populate_datasets_workbook(writer:DatasetsWriter, gdb:"Geodatabase", skip_unchanged_fields:bool=True):
    """Populate the datasets workbook with dataset base info, fields, subtypes, and relationship classes participation.

    Args:
        writer (DatasetsWriter): The GDB Writer for the datasets.
        gdb (Geodatabase): Geodatabase structure from which the datasets will be read.
        skip_unchanged_fields (bool, optional): Whether to skip fields in the subtype that don't have a domain or
          default value set for the subtype.
    """
    arcpy.SetProgressorLabel("Writing datasets spreadsheet.")

    with writer:
        for ds in gdb.datasets.tables_and_feature_classes:
            is_feature_class = ds.dataset_type == "FeatureClass"

            try:
                # Populate the base info
                writer.populate_base_info(
                    dataset_name=ds.name,
                    schema=ds.schema,
                    alias=ds.alias,
                    feature_dataset_name=ds.feature_dataset.name if ds.feature_dataset else None,
                    summary=ds.meta_summary,
                    dataset_type=st2xl.dataset_types[ds.dataset_type],
                    oid_is_64=st2xl.boolean[ds.oid_is_64],
                    is_archived=st2xl.boolean[ds.is_archived],
                    is_versioned=st2xl.boolean[ds.is_versioned],
                    dsid=ds.dsid,
                    geometry_type=st2xl.geometry_types[ds.geometry_type] if is_feature_class else None,
                    horizontal_spatial_ref=_generate_spatial_ref_label(ds.spatial_ref) if is_feature_class else None,
                    vertical_spatial_ref=_generate_spatial_ref_label(ds.spatial_ref.VCS) if is_feature_class else None,
                    has_m=st2xl.boolean[ds.has_m] if is_feature_class else None,
                    has_z=st2xl.boolean[ds.has_z] if is_feature_class else None,
                )

                # Populate the fields and subtypes
                fields_table_coordinates = _populate_fields(writer, ds)
                _populate_subtype(writer, ds, fields_table_coordinates, skip_unchanged_fields)

                # Populate the list of relationship classes
                if len(ds.relationship_classes) > 0:
                    with writer.in_relationships_adder(ds.name) as in_relationships_writer:
                        rs:"Relationship" = None
                        for rs in ds.relationship_classes:
                            in_relationships_writer.add_entry(rs.name)
            except Exception as exc:
                #pylint: disable-next=broad-exception-raised
                raise Exception(f"Failure while writing dataset {ds.name} to excel spreadsheet.") from exc


def _populate_domains_workbook(writer:DomainsWriter, gdb:"Geodatabase"):
    """Populate the domains workbook with domain base info, ranges, coded values, and users.

    Args:
        writer (DomainsWriter): The GDB Writer for the domains.
        gdb (Geodatabase): Geodatabase structure from which the datasets will be read.
    """
    arcpy.SetProgressorLabel("Writing domains spreadsheet.")

    with writer:
        domain:"Domains" = None
        for domain in gdb.domains:
            try:
                # Populate the base info
                writer.populate_base_info(
                    domain_name=domain.name,
                    schema=domain.schema,
                    description=domain.description,
                    field_type=st2xl.domain_field_types[domain.field_type],
                    domain_type=st2xl.domain_types[domain.domain_type],
                    split_policy=st2xl.split_policies[domain.split_policy],
                    merge_policy=st2xl.merge_policies[domain.merge_policy],
                )

                # Populate range min/max or coded values table
                if domain.domain_type == "RANGE":
                    writer.populate_range_info(
                        domain_name=domain.name,
                        minimum=value_to_cell(domain.minimum, domain.field_type),
                        maximum=value_to_cell(domain.maximum, domain.field_type),
                    )

                elif domain.domain_type == "CODED":
                    with writer.code_adder(domain.name) as code_writer:
                        code:"CodesTypes" = None
                        for code in domain.codes:
                            code_info:"Code" = domain.codes[code]

                            code_writer.add_entry(
                                code=value_to_cell(code, domain.field_type),
                                description=code_info.description,
                                summary=code_info.meta_summary,
                            )

                # Populate list of domain users
                all_datasets:list["Datasets"] = []
                field:"Field" = None
                for field in domain.fields:
                    if field.dataset not in all_datasets:
                        all_datasets.append(field.dataset)
                all_datasets.sort()

                with writer.domain_user_adder(domain.name) as user_writer:
                    for dataset in all_datasets:
                        user_writer.add_entry(base_name=dataset.name)
            except Exception as exc:
                #pylint: disable-next=broad-exception-raised
                raise Exception(f"Failure while writing domain {domain.name} to excel spreadsheet.") from exc


def _populate_relationships_workbook(writer:RelationshipsWriter, gdb:"Geodatabase", skip_unchanged_fields:bool=True):
    """Populate the relationships workbook with relationship classes base info, fields, and subtypes.

    Args:
        writer (RelationshipsWriter): The GDB Writer for the relationship classes.
        gdb (Geodatabase): Geodatabase structure from which the datasets will be read.
        skip_unchanged_fields (bool, optional): Whether to skip fields in the subtype that don't have a domain or
          default value set for the subtype.
    """
    arcpy.SetProgressorLabel("Writing relationships spreadsheet.")

    with writer:
        rel:"Relationship" = None
        for rel in gdb.datasets.relationship_classes:
            try:
                # Populate the base info
                writer.populate_core_info(
                    relationship_name=rel.name,
                    schema=rel.schema,
                    feature_dataset_name=rel.feature_dataset.name if rel.feature_dataset else None,
                    summary=rel.meta_summary,
                    relationship_type=st2xl.relationship_types[rel.relationship_type],
                    origin_table_name=rel.origin.table.name,
                    destination_table_name=rel.destination.table.name,
                    forward_label=rel.forward_label,
                    backward_label=rel.backward_label,
                    origin_primary_key=rel.origin.primary_key,
                    origin_foreign_key=rel.origin.foreign_key,
                    destination_primary_key=rel.destination.primary_key,
                    destination_foreign_key=rel.destination.foreign_key,
                    notifications=st2xl.notifications[rel.notification],
                    cardinality=st2xl.cardinalities[rel.cardinality],
                    attributed=st2xl.boolean[rel.attributed],
                    oid_is_64=None if rel.oid_is_64 is None else st2xl.boolean[rel.oid_is_64],
                    is_archived=st2xl.boolean[rel.is_archived],
                    is_versioned=st2xl.boolean[rel.is_versioned],
                    dsid=rel.dsid,
                )

                # Populate the fields and subtypes
                if rel.attributed:
                    fields_table_coordinates = _populate_fields(writer, rel)
                    _populate_subtype(writer, rel, fields_table_coordinates, skip_unchanged_fields)
            except Exception as exc:
                #pylint: disable-next=broad-exception-raised
                raise Exception(f"Failure while writing relationship {rel.name} to excel spreadsheet.") from exc


def _populate_fields(writer:"GDBWriterWithFields", ds:"Datasets") -> list[list[int]]:
    """Populate the fields for a dataset.

    Args:
        writer (GDBWriter): The GDB Writer for the feature class, table, or relationship class.
        ds (Datasets): Structure for the feature class, table, or relationship class.

    Returns:
        list[list[int]]: Coordinates for the fields table.
    """
    with writer.field_adder(ds.name) as field_writer:
        field:"Field" = None
        for field in ds.fields:
            default_type = str
            try:
                if field.field_type in ["SHORT", "LONG", "BIGINTEGER"]:
                    default_type = int
                elif field.field_type in ["FLOAT", "DOUBLE"]:
                    default_type = float

                field_writer.add_entry(
                    field_name=field.name,
                    field_type=st2xl.field_types[field.field_type],
                    summary=field.meta_summary,
                    alias=field.alias,
                    domain_name=field.domain.name if field.domain else None,
                    default_value=value_to_cell(field.default, field.field_type),
                    is_nullable=st2xl.boolean[field.nullable],
                    length=field.length,
                    precision=field.precision,
                    scale=field.scale,
                    default_type=default_type,
                )
            except Exception as exc:
                #pylint: disable-next=broad-exception-raised
                raise Exception(f"Failure while writing {ds.name}.{field.name} field to excel spreadsheet.") from exc

    return field_writer.coordinates


def _populate_subtype(writer:"GDBWriterWithFields", ds:"Datasets", fields_table_coordinate:list[list[int]]=None,
                      skip_unchanged_fields:bool=True):
    """Populate the subtypes for a dataset.

    Args:
        writer (GDBWriterWithFields): The GDB Writer fot the feature class, table, or relationship class.
        ds (Datasets): Structure for the feature class, table, or relationship class.
        fields_table_coordinate (list[list[int]], optional): Coordinates for the fields table allowing for cross-validation. If not provided, cross-validation will not be applied.
        skip_unchanged_fields (bool, optional): Whether to skip fields that don't have a domain or default value set for the subtype.
    """ #pylint: disable=line-too-long

    if ds.subtype:
        with writer.subtype_adder(ds.name, ds.subtype.field.name, fields_table_coordinate) as subtype_writer:

            # Loop through each code
            for code in ds.subtype.codes:
                try:
                    subtype_code_printed = False
                    code_details:"SubtypeProperties" = ds.subtype.codes[code]

                    # Loop through each field
                    field_props:"SubtypeFieldProperties" = None
                    for field_props in code_details.field_props:

                        # Skip fields with no changes
                        if skip_unchanged_fields and field_props.domain is None and field_props.default is None:
                            continue

                        subtype_writer.add_entry(
                            subtype_name=code_details.description,
                            subtype_code=code,
                            summary=code_details.meta_summary,
                            field_name=field_props.field.name,
                            domain_name=field_props.domain.name if field_props.domain else None,
                            default_value=value_to_cell(field_props.default, field_props.field.field_type),
                        )

                        subtype_code_printed = True

                    # If subtype code not printed (no fields with default or domain), then print standalone
                    if not subtype_code_printed:
                        subtype_writer.add_entry(
                            subtype_name=code_details.description,
                            subtype_code=code,
                            summary=code_details.meta_summary,
                        )
                except Exception as exc:
                    #pylint: disable-next=broad-exception-raised
                    raise Exception(f"Failure while writing subtype {ds.name}.{code} to excel spreadsheet.") from exc