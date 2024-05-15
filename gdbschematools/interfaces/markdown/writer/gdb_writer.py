"""
Markdown writer component that is used as the base for all other geodatabase element writers.

Author: Roya Shourouni, David Blanchard
"""

import os
import re

class GDBWriter:
    """Markdown writer component that is used as the base for all other geodatabase element writers.

    Args:
        markdown_path (str): Path where the markdown file will be written, including the extension.
        database_name (str): Name of the geodatabase.
        workspace_type (str, optional): Type of workspace (local or remote). Defaults to None.
        remote_server (str, optional): Address/name of the geodatabase if any. Defaults to None.
        summary (str, optional): Metadata summary about the geodatabase. Defaults to None.
    """

    source_info:str = None
    element_type:str = None
    info_block:str = None
    markdown_str:str=''
    cross_markdown_paths:dict[str, str] = None

    def __init__(self, markdown_path:str, database_name:str, workspace_type:str=None,
                remote_server:str=None, summary:str=None) -> None:
        self.markdown_path=markdown_path

        # Initialize info-block
        self.populate_source_info(self.element_type, database_name,
                                    workspace_type, remote_server, summary)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def close(self):
        """Close and save the markdown file. Further edits cannot be saved."""
        if os.path.exists(self.markdown_path):
            raise FileExistsError(f"Failed to close and save markdown as a file already exists: {self.markdown_path}.")

        with open(self.markdown_path, 'w+', encoding='utf-8') as markdown_file:
            markdown_file.write(self.markdown_str)

    def populate_source_info(self, element_type:str, database_name:str, workspace_type:str='', remote_server:str='',
                              summary:str=''):
        """Populate the information about the source geodatabase.

        Args:
            element_type (str): element type
            database_name (str): Name of the geodatabase.
            workspace_type (str, optional): Type of workspace (local or remote). Defaults to ''.
            remote_server (str, optional): Address/name of the geodatabase if any. Defaults to ''.
            summary (str, optional): Metadata summary about the geodatabase. Defaults to ''.
        """

        info_block= f'''# {element_type}\n
            > **Source Information**
            >
            > - **Database Name**: {database_name}
            > - **Workspace Type**: {workspace_type}
            > - **Remote Server**: {remote_server}
            > - **Summary**: {summary}\n
            '''
        info_block = re.sub(" \n","\n",info_block)
        self.markdown_str += re.sub("    ","",info_block)


    def populate_index_info(self, base_name:str, alias:str=None):
        """Prepare a geodatabase element block.

        Args:
            base_name (str): Base name by which the element is uniquely known.
            alias (str, optional): Human readable name by which this element is known. Defaults to None.
        """
        label = base_name or alias

        # Derive a name for the sheet, ensuring no duplicates
        block_name = re.sub(r"\s+", "-", label).lower()
        # Create the block
        block:str = f'[{label}](#{block_name})  \n'
        self.markdown_str += block


    def register_cross_book_lookups(self, datasets_path:str, domains_path:str, relationships_path:str):
        """Set the cross-markdown lookups. Must be set after preparing index block, but before populating them in order for cross-markdown links to work.

        Args:
            datasets_path (str): Path to the datasets worksheet.
            domains_path (str): Path to the domains worksheet.
            relationships_path (str): Path to the relationships worksheet.
        """ #pylint: disable=line-too-long

        self.cross_markdown_paths = {
            "datasets": datasets_path,
            "domains": domains_path,
            "relationships": relationships_path,
        }


    def get_cross_markdown_name(self, markdown_type:str) -> str:
        """Use the cross-markdown lookups to get the name of another markdown.

        Args:
            markdown_type (str): Type of data this other markdown contains ("datasets", "domains", "relationships").

        Returns:
            str: Name of the markdown including the extension.
        """
        return os.path.basename(self.cross_markdown_paths[markdown_type])
