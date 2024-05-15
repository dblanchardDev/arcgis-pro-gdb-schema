"""
Markdown writer for the domains.

Author: Roya Shourouni, David Blanchard
"""

import re
from typing import Union
from .gdb_writer import GDBWriter
from .table_writers import DomainCodesWriter, DomainUsersWriter


CellValues = Union[str, float, int]


class DomainsWriter(GDBWriter):
    """Markdown writer component used specifically for the domains.

    Args:
        markdown_path (str): Path where the XLSX file will be written, including the extension.
        database_name (str): Name of the geodatabase.
        workspace_type (str, optional): Type of workspace (local or remote). Defaults to None.
        remote_server (str, optional): Address/name of the geodatabase if any. Defaults to None.
        summary (str, optional): Metadata summary about the geodatabase. Defaults to None.
    """

    element_type = "Domains"

    def populate_base_info(self, domain_name:str, schema:str='', description:str='', field_type:str='',
                           domain_type:str='', split_policy:str='', merge_policy:str=''):
        """Populate the base information about the domain.

        Args:
            domain_name (str): Domain's base name.
            schema (str, optional): Schema to which the domain belongs. Defaults to None.
            description (str, optional): Summary describing the purpose of the domain. Defaults to ''.
            field_type (str, optional): Type of data for the field to which the domain belongs. Defaults to ''.
            domain_type (str, optional): Whether the domain is range or coded value. Defaults to ''.
            split_policy (str, optional): Strategy used when splitting a record that uses this domain. Defaults to ''.
            merge_policy (str, optional): Strategy used when merging two records that use this domain. Defaults to ''.
        """

        domain_block = f'''\n---\n
            ## {domain_name}

            - **Name**: {domain_name}
            - **Schema**: {schema}
            - **Description**: {description}
            - **Field Type**: {field_type}
            - **Domain Type**: {domain_type}
            - **Split Policy**: {split_policy}
            - **Merge Policy**: {merge_policy}
            '''
        domain_block = re.sub("    ", "", domain_block)
        domain_block = re.sub(" \n", "\n", domain_block)
        self.markdown_str += domain_block


    def populate_range_info(self, domain_name:str, minimum:CellValues=None, maximum:CellValues=None):
        """Populate the minimum and maximum of a range domain.

        Args:
            domain_name (str): Domain's base name.
            minimum (Union[str, int, float], optional): Minimum value in the range. Defaults to None.
            maximum (Union[str, int, float], optional): Maximum value in the range. Defaults to None.
        """
        # Minimum and Maximum
        range_block = f'''
        ### Range Values ({domain_name})

        - **Minimum**: {str(minimum)}
        - **Maximum**: {str(maximum)}
        '''
        self.markdown_str += re.sub("    ","",range_block)


    def code_adder(self, base_name:str) -> DomainCodesWriter:
        """Returns an instance of DomainCodesWriter initialized for a particular sheet.

        Args:
            base_name (str): Base name of the domain to which codes are to be added.

        Returns:
            DomainCodesWriter: Domain Codes Writer initialized for that domain.
        """

        return DomainCodesWriter(
            base_name=base_name,
            get_cross_markdown_name=self.get_cross_markdown_name,
            markdown=''
        )

    def domain_user_adder(self, base_name:str) -> DomainUsersWriter:
        """Returns an instance of DomainUserWriter initialized for a particular domain.

        Args:
            base_name (str): Base name of the domain.

        Returns:
            DomainUsersWriter: Domain User writer initialized for that domain.
        """
        return DomainUsersWriter(
            base_name=base_name,
            get_cross_markdown_name=self.get_cross_markdown_name,
            markdown=''
        )