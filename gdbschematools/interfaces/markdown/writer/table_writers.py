"""
Markdown writer components for making tables within a markdown block (e.g. fields, subtypes, relationships).

Author: Roya Shourouni, David Blanchard
"""

import re
from typing import Callable, Union

CellValues = Union[str, float, int]

def make_table_name(base_name:str, prefix:str) -> str:
    """Make a name that can be used in a markdown block.

    Args:
        base_name (str): Name of element to which the table belongs.
        prefix (str): prefix to describe the table.

    Returns:
        str: A table name safe for use in Markdown.
    """

    # Combine with the suffix
    return f"### {prefix} ({base_name})"

class TableWriter:

    """Write entries into a table to a particular dataset.

    Args:
        base_name (str): Element name to which the table is added.
        get_cross_markdown_name (Callable): Function to get the name of another markdown file.
        markdown (str): markdown string to which the table will be written.
    """
    get_cross_markdown_name:Callable = None

    # To be overridden by children
    _heading:str = ''
    _table_headers:str = ''
    _table_name_prefix:str = ''

    def __init__(self, base_name:str, get_cross_markdown_name:Callable, markdown:str=None):
        self.base_name = base_name
        self.get_cross_markdown_name = get_cross_markdown_name
        self.markdown = markdown

    def __enter__(self) -> "TableWriter":
        self.start_table()
        return self


    def __exit__(self, exc_type, exc_value, exc_traceback):
        if not exc_type:
            return self


    def start_table(self):
        """Output heading and table headers."""
        self._heading = make_table_name(self.base_name, self._table_name_prefix)
        self.markdown =f"\n{self._heading}\n" + re.sub("    ","",self._table_headers)

    def reference_md_element(self, element:str, element_name:str) -> str:
        """ Finds te path and label of an element in another markdown file.

        Args:
            element (str): The element type which could be Domain, Dataset or relationshipClass.
            element_name (str): Name of element.

        Returns:
            str: A markdown block which refers to the name and path of an element in another markdown file.
        """
        element_block = ''
        if element_name:
            element_label = re.sub(r"\s+","-",element_name).lower()
            element_path = "./"+ self.get_cross_markdown_name(element)
            element_block = f"[{element_name}]({element_path}#{element_label})"
        return element_block


class FieldWriter(TableWriter):
    """Write fields to a particular markdown block.

    Args:
        base_name (str): Base name of the relationship class to which the fields will be written.
        get_cross_markdown_name (Callable): Function to get the name of another markdown file.
        markdown (str): markdown string to which the table will be written.
    """

    _table_headers:str = '''
    | Field Name | Field Type | Summary | Alias Name | Domain Name | Default Value | Is Nullable | Length | Precision | Scale |
    |------------|------------|---------|------------|-------------|---------------|-------------|--------|-----------|-------|
    '''
    _table_name_prefix:str = "Fields"

    def __enter__(self) -> "FieldWriter":
        # To override the return type
        return super().__enter__()

    #pylint: disable-next=arguments-differ,too-many-arguments
    def add_entry(self, field_name:str, field_type:str='', summary:str='', alias:str='', domain_name:str=None,
                default_value:str='', is_nullable:str='no',
                length:str='', precision:str='', scale:str=''):
        """Add a new field to the field table.

        Args:
            field_name (str): Base name given to the field
            field_type (str, optional): Type of field. Defaults to None.
            summary (str, optional): Metadata summary for the field. Defaults to None.
            alias (str, optional): Alternate name for the field. Defaults to None.
            domain_name (str, optional): Name of the domain assigned to the field if any. Defaults to None.
            default_value (Union[str, int, float], optional): Default value assigned to the field. Defaults to None.
            is_nullable (str, optional): Whether field is nullable. Defaults to None.
            length (int, optional): Length of the field for text. Defaults to None.
            precision (int, optional): Precision of the field for numbers. Defaults to None.
            scale (int, optional): Scale of the field for floats and doubles. Defaults to None.
        """ #pylint: disable=line-too-long
        if field_name is not None:
            domain_info = self.reference_md_element("domains", domain_name)
            field_block = f"| {field_name} | {field_type} | {summary} | {alias} | {domain_info} " + \
            f"| {default_value} | {is_nullable} | {length} | {precision} | {scale} |\n"
            self.markdown += field_block

class SubtypeWriter(TableWriter):
    """Write fields to a particular sheet.

    Args:
        base_name (str): The base name of dataset to which the table will be written.
        get_cross_markdown_name (Callable): Function to get the name of another markdown file.
        subtype_field_name (str): Name of the field to which the subtype is applied.
    """ #pylint: disable=line-too-long
    _table_headers:str = '''\n| Subtype Name | Code | Description | Field Name | Domain Name | Default Value |
            |--------------|------|-------------|------------|-------------|---------------|
            '''
    _table_name_prefix:str = "Subtype"

    def __init__(self, base_name:str, get_cross_markdown_name:str, subtype_field_name:str):
        super().__init__(base_name, get_cross_markdown_name)

        subtype_field_row = f"\n- **Subtype Field Name**: {subtype_field_name}\n"
        self._table_headers = subtype_field_row + self._table_headers
        self._subtype_field_name=subtype_field_name
        self._subtype_summary_printed = []
        self.summary_printout = None

    def __enter__(self) -> "SubtypeWriter":
        # To override the return type
        return super().__enter__()


    #pylint: disable-next=arguments-differ
    def add_entry(self, subtype_name:str, subtype_code:int, summary:str='', field_name:str=None,
                  domain_name:str=None, default_value:str=''):
        """Add an entry to the subtype table.

        Args:
            subtype_name (str): Name of the subtype being added.
            subtype_code (int): Code corresponding to the subtype.
            summary (str, optional): Metadata summary for the subtype. Only printed the first time. Defaults to ''.
            field_name (str, optional): Name of the field being modified, if any. Defaults to None.
            domain_name (str, optional): Name of the domain applied to the field. Defaults to None.
            default_value (str, optional): Default value being applied to the field. Defaults to ''.
        """
        summary_printout = ''
        if subtype_code is not None and subtype_code not in self._subtype_summary_printed:
            summary_printout = summary
            self._subtype_summary_printed.append(subtype_code)

        domain_info = self.reference_md_element("domains", domain_name)
        subtype_block = f"| {subtype_name} | {subtype_code} | {summary_printout} | {field_name} |" +\
            f" {domain_info} | {default_value} |\n"
        self.markdown += subtype_block

class InRelationshipsWriter(TableWriter):
    """Write the relationship classes in which a dataset participates to a particular sheet.

    Args:
        base_name (str): Base name of the relationship class to which the fields will be written.
        get_cross_markdown_name (Callable): Function to get the name of another markdown file.
        markdown (str): markdown string to which the relationship classes will be written.
    """

    _table_name_prefix:str = "Relationship Classes"

    def __enter__(self) -> "InRelationshipsWriter":
        # To override the return type
        return super().__enter__()


    #pylint: disable-next=arguments-differ,too-many-arguments
    def add_entry(self, base_name:str):
        """Add a new row to the relationships table.

        Args:
            relationship_name (str): Base name for the relationship class.
        """
        relationship_info = self.reference_md_element("relationships", base_name)
        relationship_block = f'''\n- {relationship_info}\n'''
        self.markdown += relationship_block

class DomainCodesWriter(TableWriter):
    """Write the coded values that are part of a coded value domain.

    Args:
        base_name (str): Base name of the relationship class to which the fields will be written.
        get_cross_markdown_name (Callable): Function to get the name of another markdown file.
        markdown (str): markdown string to which the Domain Codes will be written.
    """

    _table_headers:str = '''
        | Code | Description | Summary |
        |------|-------------|---------|
        '''
    _table_name_prefix:str = "Coded Values"

    def __enter__(self) -> "DomainCodesWriter":
        # To override the return type
        return super().__enter__()

    #pylint: disable-next=arguments-differ
    def add_entry(self, code:CellValues, description:str=None, summary:str=None):
        """Add a coded value to the codes table.

        Args:
            code (Union[int, str, None]): The coded value.
            description (str, optional): The description of the coded value. Defaults to None.
            summary (str, optional): Metadata summary for the coded value. Defaults to None.
        """
        domain_code_block = f'''| {code} | {description} | {summary} |\n'''
        self.markdown += domain_code_block

class DomainUsersWriter(TableWriter):
    """Write the feature classes, tables, and relationship classes to which a domain is assigned.

    Args:
        base_name (str): Cell writer to which the fields will be written.
        get_cross_markdown_name (Callable): Function to get the name of another markdown.
        markdown (str): markdown string to which the Domain Users table will be written.
    """

    _table_name_prefix:str = "Domain Users"

    def __enter__(self) -> "DomainUsersWriter":
        # To override the return type
        return super().__enter__()


    #pylint: disable-next=arguments-differ,too-many-arguments
    def add_entry(self, element_name:str, element_type:str):
        """Add a new field to the field table.

        Args:
            base_name (str): Base name for the feature class, table, or relationship class.
        """
        if element_type == 'RelationshipClass':
            md_info = self.reference_md_element("relationships", element_name)
        else:
            md_info = self.reference_md_element("datasets", element_name)
        domain_user_block = f'''\n- {md_info}\n'''
        self.markdown += domain_user_block