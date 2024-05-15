"""
Writer for the Markdown files output.

Author: Roya Shourouni, David Blanchard
"""

import datetime
import os

from typing import TYPE_CHECKING, Union

import arcpy

from .md_converter import value_to_cell, st2md
from .writer import DatasetsWriter, DomainsWriter, RelationshipsWriter

if TYPE_CHECKING:
    from arcpy import SpatialReference
    from ...structures import Datasets, Domains, Field, Geodatabase, Relationship
    from ...structures.accessors.code_accessor import CodesTypes, Code
    from ...structures.accessors.subtype_accessor import SubtypeProperties, SubtypeFieldProperties

def _generate_spatial_ref_label(spatial_ref:Union["SpatialReference", "SpatialReference.VCS"]) -> str:
    """Produce a label from a spatial reference object.

    Args:
        spatial_ref (Union[SpatialReference, SpatialReference.VCS]): Spatial reference from which to generate a label.

    Returns:
        str: Label to be written to markdown.
    """
    label = ''
    if spatial_ref:
        name = spatial_ref.name.replace("_", " ")
        wkid = spatial_ref.factoryCode
        label = f"{wkid} ({name})"

    return label

def _derive_markdown_file_paths(output_dir:str, gdb_name:str) -> tuple[str]:
    """Create file paths for all markdown files with the same timestamp and location.

    Args:
        output_dir (str): Directory to which all 3 files will be written.
        gdb_name (str): Name of the geodatabase from which these are being derived.

    Returns:
        tuple[str]: All 3 paths (datasets, domains, relationships).
    """
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M")
    os.makedirs(output_dir, exist_ok=True)
    return (
        os.path.join(output_dir, f"{gdb_name}_{timestamp}_datasets.md"),
        os.path.join(output_dir, f"{gdb_name}_{timestamp}_domains.md"),
        os.path.join(output_dir, f"{gdb_name}_{timestamp}_relationships.md"),
    )

def output_markdown(gdb:"Geodatabase", output_dir:str) -> tuple[str]:
    """Write all 3 markdown files (datasets, domains, relationships) from a geodatabase structure.

    Args:
        gdb (Geodatabase): Geodatabase structure from which the data output is to be produced.
        output_dir (str): Directory in which the markdown files are to be written.

    Returns:
        tuple(str): The 3 paths to which the markdown files were written (datasets, domains, relationships).
    """
    arcpy.SetProgressor("default", "Preparing markdowns.")

    # Get paths
    (datasets_path, domains_path, relationships_path) = _derive_markdown_file_paths(output_dir, gdb.name)

    # Create all the markdown files
    database_name = gdb.name
    workspace_type = st2md.workspace_types[gdb.workspace_type]
    remote_server = gdb.server or ''
    summary = gdb.meta_summary or ''

    # Populate dataset markdown
    datasets_writer = DatasetsWriter(datasets_path, database_name, workspace_type, remote_server, summary)

    dataset:"Datasets" = None
    for dataset in gdb.datasets.tables_and_feature_classes:
        datasets_writer.populate_index_info(dataset.name, dataset.alias)

    # Populate domains markdown
    domains_writer = DomainsWriter(domains_path, database_name, workspace_type, remote_server, summary)

    domain:"Domains" = None
    for domain in gdb.domains:
        domains_writer.populate_index_info(domain.name)

    # Populate relationships markdown
    relationships_writer = RelationshipsWriter(relationships_path, database_name,
                                               workspace_type, remote_server, summary)

    relation:"Relationship" = None
    for relation in gdb.datasets.relationship_classes:
        relationships_writer.populate_index_info(relation.name)


     # Register cross-workbook lookups
    registrations = {
        "datasets_path": datasets_writer.markdown_path,
        "domains_path": domains_writer.markdown_path,
        "relationships_path": relationships_writer.markdown_path,
    }

    datasets_writer.register_cross_book_lookups(**registrations)
    domains_writer.register_cross_book_lookups(**registrations)
    relationships_writer.register_cross_book_lookups(**registrations)

    _populate_datasets_md(datasets_writer, gdb)
    _populate_domains_md(domains_writer, gdb)
    _populate_relationships_md(relationships_writer, gdb)


    return (datasets_path, domains_path, relationships_path)

def _populate_datasets_md(writer:DatasetsWriter, gdb:"Geodatabase"):
    """Populate the datasets markdown with dataset base info, fields, subtypes, and relationship classes participation.

    Args:
        writer (DatasetsWriter): The GDB Writer for the datasets.
        gdb (Geodatabase): Geodatabase structure from which the datasets will be read.
    """
    arcpy.SetProgressorLabel("Writing datasets markdown.")

    with writer:
        for ds in gdb.datasets.tables_and_feature_classes:
            try:
                is_feature_class = ds.dataset_type == "FeatureClass"

                # Populate the base info
                writer.populate_base_info(
                    dataset_name=ds.name,
                    schema=ds.schema or '',
                    alias=ds.alias or '',
                    feature_dataset_name=ds.feature_dataset.name if ds.feature_dataset else '',
                    summary=ds.meta_summary or '',
                    dataset_type=st2md.dataset_types[ds.dataset_type],
                    oid_is_64=st2md.boolean[ds.oid_is_64],
                    is_archived=st2md.boolean[ds.is_archived],
                    is_versioned=st2md.boolean[ds.is_versioned],
                    geometry_type=st2md.geometry_types[ds.geometry_type] if is_feature_class else None,
                    horizontal_spatial_ref=_generate_spatial_ref_label(ds.spatial_ref) if is_feature_class else '',
                    vertical_spatial_ref=_generate_spatial_ref_label(ds.spatial_ref.VCS) if is_feature_class else '',
                    has_m=st2md.boolean[ds.has_m] if is_feature_class else 'no',
                    has_z=st2md.boolean[ds.has_z] if is_feature_class else 'no',
                )

                # Populate the fields and subtypes
                if ds.fields:
                    _populate_fields(writer, ds)
                if ds.subtype:
                    _populate_subtype(writer, ds)

                # Populate the list of relationship classes
                if len(ds.relationship_classes) > 0:
                    with writer.in_relationships_adder(ds.name) as in_relationships_writer:
                        rs:"Relationship" = None
                        for rs in ds.relationship_classes:
                            in_relationships_writer.add_entry(rs.name)
                        writer.markdown_str += in_relationships_writer.markdown
            except Exception as exc:
                #pylint: disable-next=broad-exception-raised
                raise Exception(f"Failure while writing markdown for {ds.name} dataset.") from exc

def _populate_domains_md(writer:DomainsWriter, gdb:"Geodatabase"):
    """Populate the domains markdown with domain base info, ranges, coded values, and users.

    Args:
        writer (DomainsWriter): The GDB Writer for the domains.
        gdb (Geodatabase): Geodatabase structure from which the datasets will be read.
    """
    arcpy.SetProgressorLabel("Writing domains markdown.")

    with writer:
        domain:"Domains" = None
        for domain in gdb.domains:
            try:
                # Populate the base info
                writer.populate_base_info(
                    domain_name=domain.name,
                    schema=domain.schema or '',
                    description=domain.description or '',
                    field_type=st2md.domain_field_types[domain.field_type],
                    domain_type=st2md.domain_types[domain.domain_type],
                    split_policy=st2md.split_policies[domain.split_policy],
                    merge_policy=st2md.merge_policies[domain.merge_policy],
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
                                description=code_info.description or '',
                                summary=code_info.meta_summary or '',
                            )
                        writer.markdown_str += code_writer.markdown

                # Populate list of domain users
                all_datasets:list["Datasets"] = []
                field:"Field" = None
                for field in domain.fields:
                    if field.dataset not in all_datasets:
                        all_datasets.append(field.dataset)
                all_datasets.sort()

                with writer.domain_user_adder(domain.name) as user_writer:
                    for dataset in all_datasets:
                        user_writer.add_entry(element_name=dataset.name, element_type=dataset.dataset_type)
                    writer.markdown_str += user_writer.markdown
            except Exception as exc:
                #pylint: disable-next=broad-exception-raised
                raise Exception(f"Failure while writing markdown for {domain.name} domain.") from exc

def _populate_relationships_md(writer:RelationshipsWriter, gdb:"Geodatabase"):
    """Populate the relationships markdown with relationship classes base info, fields, and subtypes.

    Args:
        writer (RelationshipsWriter): The GDB Writer for the relationship classes.
        gdb (Geodatabase): Geodatabase structure from which the datasets will be read.
    """
    arcpy.SetProgressorLabel("Writing relationships markdown.")

    with writer:
        rel:"Relationship" = None
        for rel in gdb.datasets.relationship_classes:
            try:
            # Populate the base info
                writer.populate_core_info(
                    relationship_name=rel.name,
                    schema=rel.schema or '',
                    feature_dataset_name=rel.feature_dataset.name if rel.feature_dataset else '',
                    summary=rel.meta_summary or '',
                    relationship_type=st2md.relationship_types[rel.relationship_type],
                    origin_table_name=rel.origin.table.name,
                    destination_table_name=rel.destination.table.name,
                    forward_label=rel.forward_label,
                    backward_label=rel.backward_label,
                    origin_primary_key=rel.origin.primary_key,
                    origin_foreign_key=rel.origin.foreign_key,
                    destination_primary_key=rel.destination.primary_key or '',
                    destination_foreign_key=rel.destination.foreign_key or '',
                    notifications=st2md.notifications[rel.notification],
                    cardinality=st2md.cardinalities[rel.cardinality],
                    attributed=st2md.boolean[rel.attributed] or 'no',
                    oid_is_64='no' if rel.oid_is_64 is None else st2md.boolean[rel.oid_is_64],
                    is_archived=st2md.boolean[rel.is_archived],
                    is_versioned=st2md.boolean[rel.is_versioned],
                )

                # Populate the fields and subtypes
                if rel.attributed:
                    _populate_fields(writer, rel)
                    _populate_subtype(writer, rel)
            except Exception as exc:
                #pylint: disable-next=broad-exception-raised
                raise Exception(f"Failure while writing markdown for {rel.name} relationship.") from exc


def _populate_fields(writer:"DatasetsWriter", ds:"Datasets"):
    """Populate the fields for a dataset.

    Args:
        writer (DatasetsWriter): The dataset Writer for the feature class, table, or relationship class.
        ds (Datasets): Structure for the feature class, table, or relationship class.
    """
    with writer.field_adder(ds.name) as field_writer:
        field:"Field" = None
        for field in ds.fields:
            try:
                field_writer.add_entry(
                    field_name=field.name,
                    field_type=st2md.field_types[field.field_type],
                    summary=field.meta_summary or '',
                    alias=field.alias or '',
                    domain_name=field.domain.name if field.domain else None,
                    default_value=value_to_cell(field.default, field.field_type) if field.default is not None else '',
                    is_nullable=st2md.boolean[field.nullable],
                    length=field.length or '',
                    precision=str(field.precision) if field.precision is not None else '',
                    scale=str(field.scale) if field.scale is not None else ''
                )
            except Exception as exc:
                #pylint: disable-next=broad-exception-raised
                raise Exception(f"Failure while writing markdown for {ds.name}.{field.name} field.") from exc

        writer.markdown_str += field_writer.markdown

def _populate_subtype(writer:DatasetsWriter, ds:"Datasets"):
    """Populate the subtypes for a dataset.

    Args:
        writer (GDBWriterWithFields): The GDB Writer fot the feature class, table, or relationship class.
        ds (Datasets): Structure for the feature class, table, or relationship class.
    """ #pylint: disable=line-too-long

    if ds.subtype:
        with writer.subtype_adder(ds.name, ds.subtype.field.name) as subtype_writer:
            # Loop through each code
            for code in ds.subtype.codes:
                try:
                    subtype_code_printed = False
                    code_details:"SubtypeProperties" = ds.subtype.codes[code]

                    # Loop through each field
                    field_props:"SubtypeFieldProperties" = None
                    for field_props in code_details.field_props:
                        # Skip fields with no changes
                        if field_props.domain is None and field_props.default is None:
                            continue
                        subtype_writer.add_entry(
                            subtype_name=code_details.description,
                            subtype_code=code,
                            summary=code_details.meta_summary or '',
                            field_name=field_props.field.name,
                            domain_name=field_props.domain.name if field_props.domain else '',
                            default_value=value_to_cell(field_props.default, field_props.field.field_type) or '',
                        )

                        subtype_code_printed = True

                    # If subtype code not printed (no fields with default or domain), then print standalone
                    if not subtype_code_printed:
                        subtype_writer.add_entry(
                            subtype_name=code_details.description,
                            subtype_code=code,
                            summary=code_details.meta_summary or '',
                        )
                except Exception as exc:
                    #pylint: disable-next=broad-exception-raised
                    raise Exception(f"Failure while writing markdown for {ds.name}.{code} subtype.") from exc
        writer.markdown_str += subtype_writer.markdown