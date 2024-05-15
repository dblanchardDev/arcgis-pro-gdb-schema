"""
Markdown writer for the relationships.

Author: Roya Shourouni, David Blanchard
"""
import re
from .dataset_writer import DatasetsWriter


class RelationshipsWriter(DatasetsWriter):
    """Markdown component used specifically for the relationships.

    Args:
        markdown_path (str): Path where the XLSX file will be written, including the extension.
        database_name (str): Name of the geodatabase.
        workspace_type (str, optional): Type of workspace (local or remote). Defaults to None.
        remote_server (str, optional): Address/name of the geodatabase if any. Defaults to None.
        summary (str, optional): Metadata summary about the geodatabase. Defaults to None.
    """

    element_type = "Relationship Classes"

    #pylint: disable=too-many-arguments,too-many-locals
    def populate_core_info(self, relationship_name:str, schema:str=None, feature_dataset_name:str=None,
                           summary:str=None, relationship_type:str=None, origin_table_name:str=None,
                           destination_table_name:str=None, forward_label:str=None, backward_label:str=None,
                           origin_primary_key:str=None, origin_foreign_key:str=None, destination_primary_key:str=None,
                           destination_foreign_key:str=None, notifications:str=None, cardinality:str=None,
                           attributed:str='no', oid_is_64:str='no', is_archived:str='no', is_versioned:str='no'):
        """Populate the core information about the relationship.

        Args:
            relationship_name (str): Name of the relationship class.
            schema (str, optional): Schema to which the relationship class belongs. Defaults to None.
            feature_dataset_name (str, optional): Name of the feature dataset in which the relationship is contained. Defaults to None.
            summary (str, optional): Metadata summary describing the relationship class. Defaults to None.
            relationship_type (str, optional): Whether simple or composite. Defaults to None.
            origin_table_name (str, optional): Name of the origin table. Defaults to None.
            destination_table_name (str, optional): Name of the destination table. Defaults to None.
            forward_label (str, optional): Label for origin to destination. Defaults to None.
            backward_label (str, optional): Label for destination to origin. Defaults to None.
            origin_primary_key (str, optional): Field in origin table used for relationship ID. Defaults to None.
            origin_foreign_key (str, optional): Field in intermediate table or destination table used for relationship ID. Defaults to None.
            destination_primary_key (str, optional): Field in destination table used for relationship ID in an attributed or many to many relationship. Defaults to None.
            destination_foreign_key (str, optional): Field in intermediate table for destination used in an attributed or many to many relationship. Defaults to None.
            notifications (str, optional): Message/edit propagation. Defaults to None.
            cardinality (str, optional): Whether one-to-one, one-to-many, or many-to-many. Defaults to None.
            attributed (str, optional): Whether the relationship class has attributes. Defaults to None.
            oid_is_64 (str, optional): Whether FID field uses 64-bits. Defaults to None.
            is_archived (str, optional): Whether archiving is enabled. Defaults to None.
            is_versioned (str, optional): Whether versioning is enabled. Defaults to None
        """ #pylint: disable=line-too-long

        relationship_block = f'''\n---\n
        ## {relationship_name}

        - **Name**: {relationship_name}
        - **Schema**: {schema}
        - **Feature Dataset**: {feature_dataset_name}
        - **Summary**: {summary}
        - **Relationship Type**: {relationship_type}
        - **Origin Table**: [{origin_table_name}](./{self.get_cross_markdown_name("datasets")}#{origin_table_name.lower()})
        - **Destination Table**: [{destination_table_name}](./{self.get_cross_markdown_name("datasets")}#{destination_table_name.lower()})
        - **Forward Label**: {forward_label}
        - **Backward Label**: {backward_label}
        - **Origin Primary Key**: {origin_primary_key}
        - **Origin Foreign Key**: {origin_foreign_key}
        - **Destination Primary Key**: {destination_primary_key}
        - **Destination Foreign Key**: {destination_foreign_key}
        - **Notifications**: {notifications}
        - **Cardinality**: {cardinality}
        - **Is Attributed**: {attributed}
        - **64-bit OID**: {oid_is_64}
        - **Is Archived**: {is_archived}
        - **Is Versioned**: {is_versioned}
        '''
        relationship_block = re.sub(" \n","\n",relationship_block)
        self.markdown_str += re.sub("    ", "", relationship_block)