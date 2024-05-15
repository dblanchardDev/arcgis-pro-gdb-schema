"""
Markdown writer for the datasets.

Author: Roya Shourouni, David Blanchard
"""
import re
from .gdb_writer import GDBWriter
from .table_writers import FieldWriter, SubtypeWriter, InRelationshipsWriter

class DatasetsWriter(GDBWriter):
    """Markdown writer component used specifically for the datasets.

    Args:
        markdown_path (str): Path where the XLSX file will be written, including the extension.
        database_name (str): Name of the geodatabase.
        workspace_type (str, optional): Type of workspace (local or remote). Defaults to None.
        remote_server (str, optional): Address/name of the geodatabase if any. Defaults to None.
        summary (str, optional): Metadata summary about the geodatabase. Defaults to None.
    """

    element_type:str = "Datasets"

    #pylint: disable=too-many-locals,too-many-arguments
    def populate_base_info(self, dataset_name:str, schema:str='', alias:str='', feature_dataset_name:str='',
                           summary:str='', dataset_type:str='', oid_is_64:str='no', is_archived:str='no',
                           is_versioned:str='no',  geometry_type:str='',
                           horizontal_spatial_ref:str='', vertical_spatial_ref:str='', has_m:str='no',
                           has_z:str='no'):
        """Populate the base information about the dataset.

        Args:
            dataset_name (str): Dataset's base name.
            schema (str, optional): Schema in which the dataset participates. Defaults to None.
            alias (str, optional): Alternate name. Defaults to None.
            feature_dataset_name (str, optional): Name of the feature dataset in which the dataset participates. Defaults to None.
            summary (str, optional): Metadata summary description. Defaults to None.
            dataset_type (str, optional): Type of dataset (e.g. Feature Class, Table). Defaults to None.
            oid_is_64 (str, optional): Whether dataset used 64-bit object IDs. Defaults to 'no'.
            is_archived (str, optional): Whether archival is enabled. Defaults to 'no'.
            is_versioned (str, optional): Whether versioning is enabled. Defaults to 'no'.
            geometry_type (str, optional): Type of geometry (e.g. Point). Only applies to feature classes. Defaults to None.
            horizontal_spatial_ref (str, optional): Description of the horizontal spatial reference. Only applies to feature classes. Defaults to no.
            vertical_spatial_ref (str, optional): Description of the vertical spatial reference. Only applies to feature classes. Defaults to None.
            has_m (str, optional): Whether m-values are enabled. Defaults to 'no'.
            has_z (str, optional): Whether vertical values are enabled. Defaults to 'no'.
        """ #pylint: disable=line-too-long

        dataset_block = f'''\n---\n
            ## {dataset_name}

            - **Name**: {dataset_name}
            - **Schema**: {schema}
            - **Alias**: {alias}
            - **Feature Dataset**: {feature_dataset_name}
            - **Summary**: {summary}
            - **Dataset Type**: {dataset_type}
            '''

        if geometry_type:
            dataset_block += f'''- **Geometry Type**: {geometry_type}
            - **Horizontal Spatial Ref.**: {horizontal_spatial_ref}
            - **Vertical Spatial Ref.**: {vertical_spatial_ref}
            - **Has M-Values**: {has_m}
            - **Has Z-Values**: {has_z}
            '''
        dataset_block += f'''- **64-bit OID**: {oid_is_64}
            - **Is Archived**: {is_archived}
            - **Is Versioned**: {is_versioned}
            '''
        dataset_block = re.sub("    ","", dataset_block)
        dataset_block = re.sub(" \n","\n", dataset_block)
        self.markdown_str += dataset_block

    def field_adder(self, base_name:str) -> FieldWriter:
        """Returns an instance of FieldWriter initialized for a particular dataset.

        Args:
            base_name (str): Base name of the feature class, table, or relationship class.

        Returns:
            FieldWriter: Field writer initialized for that dataset.
        """

        # Derive a name for the table, ensuring no duplicates
        # Create a name with only alpha-numeric characters and underscores
        return FieldWriter(base_name=base_name,
                        get_cross_markdown_name=self.get_cross_markdown_name,
                        markdown='')

    def subtype_adder(self, base_name:str, subtype_field_name:str) -> SubtypeWriter:
        """Returns an instance of SubtypeWriter initialized for a particular dataset.

        Args:
            base_name (str): Base name of the feature class, table, or relationship class.
            subtype_field_name (str): Name of the field to which the subtype is applied.

        Returns:
            SubtypeWriter: Subtype writer initialized for that dataset.
        """

        return SubtypeWriter(
                    base_name=base_name,
                    get_cross_markdown_name=self.get_cross_markdown_name,
                    subtype_field_name=subtype_field_name
        )

    def in_relationships_adder(self, base_name:str) -> InRelationshipsWriter:
        """Returns an instance of InRelationshipsWriter initialized for a particular dataset.

        Args:
            base_name (str): Base name of the feature class, table, or relationship class.

        Returns:
            InRelationshipsWriter: In-Relationships writer initialized for that dataset.
        """
        return InRelationshipsWriter(
                base_name=base_name,
                get_cross_markdown_name=self.get_cross_markdown_name,
                markdown='',
        )