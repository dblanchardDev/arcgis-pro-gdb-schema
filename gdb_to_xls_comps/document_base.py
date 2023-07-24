"""
Base class and utilities for the documenting of geodatabase parts.

Author: David Blanchard

Version: 0.1
"""

from typing import Union

import arcpy

from gdb_to_xls_comps import metadata, utils, xls_handler


_WORKSPACE_TYPES = {
    "esriDataSourcesGDB.AccessWorkspaceFactory": "Personal geodatabase",
    "esriDataSourcesGDB.FileGDBWorkspaceFactory": "File geodatabase",
    "esriDataSourcesGDB.InMemoryWorkspaceFactory": "In-memory workspace",
    "esriDataSourcesGDB.MemoryWorkspaceFactory": "Memory workspace",
    "esriDataSourcesGDB.SdeWorkspaceFactory": "Enterprise geodatabase",
    "esriDataSourcesGDB.SqliteWorkspaceFactory": "Mobile geodatabase",
    "esriDataSourcesGDB.AccessWorkspaceFactory.1": "Personal geodatabase",
    "esriDataSourcesGDB.FileGDBWorkspaceFactory.1": "File geodatabase",
    "esriDataSourcesGDB.InMemoryWorkspaceFactory.1": "In-memory workspace",
    "esriDataSourcesGDB.MemoryWorkspaceFactory.1": "Memory workspace",
    "esriDataSourcesGDB.SdeWorkspaceFactory.1": "Enterprise geodatabase",
    "esriDataSourcesGDB.SqliteWorkspaceFactory.1": "Mobile geodatabase",
    "": "Unknown",
}


class DocumentBase:
    """Base for the various item documentation classes.

        Args:
            gdb_describe (object): ArcPy Describe object of the geodatabase.
            output_diretory (str): Path to the directory where worksheets will be written.
            include_index (bool, optional): Whether to include an index page and links between sheets. Defaults to True.
            include_base_fields (bool, optional): Whether to include base fields like OBJECTID and SHAPE. Defaults to False.
    """

    data_type:str = "Base"
    item_sheet_max_widths:list[Union[int, None]] = []

    gdb_describe:object = None
    include_index:bool = True
    include_base_fields:bool = False

    workbook:xls_handler.Workbook = None
    all_items:list[object] = []
    sheet_names:dict = {}
    info_sheet:xls_handler.Sheet = None


    def __init__(self, gdb_describe:object, output_diretory:str, include_index:bool=True, include_base_fields:bool=False) -> None:

        arcpy.SetProgressor("default", f"Preparing information for {self.data_type.lower()}.")

        # Store
        self.gdb_describe = gdb_describe
        self.include_index = include_index
        self.include_base_fields = include_base_fields

        # Create new workbook
        workbook_base_name = f"{self.gdb_describe.baseName}_{self.data_type}"
        self.workbook = xls_handler.Workbook(output_diretory, workbook_base_name)

        # Create list of all items
        self._populate_all_items()

        # Generate sheet names
        for item in self.all_items:
            name = self._extract_item_name(item)
            sheet_name = self.workbook.make_valid_sheet_name(name)
            self.sheet_names[name] = sheet_name

        # Generate the gdb info/index sheet
        self.info_sheet = self.workbook.add_sheet("_INFO_", [28, None])
        self._generate_gdb_info()

        if include_index:
            self._generate_index()

        return


    def _populate_all_items(self)->None:
        """Populate the self.all_items list with a listing of all items to be documented.

        Raises:
            NotImplementedError: Must be overriden by the inheritor.
        """
        raise NotImplementedError("The inherited class must override the _populate_all_items method.")


    def _extract_item_name(self, item:object)->str:
        """Extract the name from a single item.

        Args:
            item (object): the item needing a name.

        Raises:
            NotImplementedError: Must be overriden by the inheritor.

        Returns:
            str: the item's name.
        """
        raise NotImplementedError("The inherited class must override the _extract_item_name method.")


    def _generate_gdb_info(self)->None:
        """Populate the info sheet with the geodatabase information."""
        sheet = self.info_sheet
        gdb_d = self.gdb_describe

        sheet.write_row(["Source Information"], ["heading"])
        workspace_type = _WORKSPACE_TYPES.get(self.gdb_describe.workspaceFactoryProgID)

        if workspace_type in ["Personal geodatabase", "File geodatabase"]:
            sheet.write_row_listing("Geodatabase Name", gdb_d.baseName)
            sheet.write_row_listing("Catalog Path", gdb_d.catalogPath)

        elif workspace_type == "Enterprise geodatabase":
            sheet.write_row_listing("Database Name", gdb_d.connectionProperties.database)
            sheet.write_row_listing("Instance Details", gdb_d.connectionProperties.instance)
            sheet.write_row_listing("Is Geodatabase", gdb_d.connectionProperties.is_geodatabase)
            sheet.write_row_listing("Connected User", gdb_d.connectionProperties.user)
            sheet.write_row_listing("Version", gdb_d.connectionProperties.version)

        sheet.write_row_listing("Workspace Type", workspace_type)
        sheet.write_row_listing("Geodatabase Release", gdb_d.release)
        sheet.write_row_listing("Description", utils.Standardize.null(metadata.get_description(gdb_d)))
        sheet.write_row_listing("Generated On", self.workbook.timestamp)

        return


    def _generate_index(self):
        """Populate the info sheet with the item index."""
        self.info_sheet.write_row([""])
        self.info_sheet.write_row(["Index"], ["heading"])

        for item in self.all_items:
            name = self._extract_item_name(item)
            sheet = self.sheet_names[name]
            link = xls_handler.make_hyperlink(sheet, name)

            self.info_sheet.write_row([link], ["hyperlink"])

        return


    def populate_item_info(self, all_documents:utils.AllDocuments=None)->None:
        """Populate the workbook with sheets detailing each item's information.

        Args:
            all_documents (dict, optional): Reference to other documents being build {datasets, domains}. Defaults to None.
        """
        arcpy.SetProgressor("step", f"Documenting {self.data_type.lower()}", 0, len(self.all_items))

        for item in self.all_items:
            # Create sheet
            item_name = self._extract_item_name(item)
            sheet = self.workbook.add_sheet(self.sheet_names[item_name], self.item_sheet_max_widths)
            self._add_return_to_index_link(sheet)

            # Populate the item's data
            self._populate_single_item(sheet, item, all_documents)

            arcpy.SetProgressorPosition()

        return


    def _populate_single_item(self, sheet:xls_handler.Sheet, item:any, all_documents:utils.AllDocuments=None)->None:
        """Populate a sheet with a single item's information.

        Args:
            sheet (xls_handler.Sheet): The sheet into which to write the data.
            item (any): The item's ArcPy describe object or ItemAndDaset object.
            all_documents (dict, optional): Reference to other documents being build {datasets, domains}. Defaults to None.

        Raises:
            NotImplementedError: Must be overriden by the inheritor.
        """
        raise NotImplementedError("The inherited class must override the _populate_single_item method.")


    def _add_return_to_index_link(self, sheet:xls_handler.Sheet)->None:
        """Add a link to return to the index/info sheet. Will only be added if include_index is true.

        Args:
            sheet (xls_handler.Sheet): The sheet to which to add the link.
        """
        if self.include_index:
            link = xls_handler.make_hyperlink(self.info_sheet.name, "Go to Index")
            sheet.write_row([link], ["hyperlink"])
            sheet.write_row([""])
        return


    def finish(self):
        """Complete writing the documentation and save it to file."""
        # Add indicator if no items of this type in database
        if len(self.all_items) == 0:
            self.info_sheet.write_row([""])
            self.info_sheet.write_row([f"Geodatabase had no {self.data_type.lower()}."], ["bold"])

        self.workbook.save()
        return


# pylint: disable-next=abstract-method
class DocumentBaseDatasets(DocumentBase):
    """Extended base for the various geodatabase dataset items (feature classes, tables, relationship classes, etc.).

        Args:
            gdb_describe (object): ArcPy Describe object of the geodatabase.
            output_diretory (str): Path to the directory where worksheets will be written.
            include_index (bool, optional): Whether to include an index page and links between sheets. Defaults to True.
            include_base_fields (bool, optional): Whether to include base fields like OBJECTID and SHAPE. Defaults to False.
    """


    def _extract_item_name(self, item: object):
        return self._convert_full_name_to_simple(item.describe.name)


    def _convert_full_name_to_simple(self, full_name:str)->str:
        """Convert a fully qualified name into its simple base name.

        Args:
            full_name (str): fully qualified name

        Returns:
            str: base name
        """
        return full_name.split(".")[-1]


    def _populate_all_fields(self, sheet:xls_handler.Sheet, item:utils.ItemAndDataset, field_list:list[object], all_documents:utils.AllDocuments)->None:
        """Populate the field listing for each field in a list.

        Args:
            sheet (xls_handler.Sheet): The sheet to which to write the info.
            item (utils.ItemAndDataset): The item whose fields are to be populated.
            field_list (list[object]): The list of fields to document as arcpy describe objects.
            all_documents (utils.AllDocuments, optional): Reference to other documents being build {datasets, domains}. Defaults to None.
        """
        item_name = self._extract_item_name(item)

        # Heading
        sheet.write_row([""])
        sheet.write_row(["Fields"], ["heading"])

        headings = ["FieldName", "Type", "Length", "Description", "AliasName", "DomainName", "DefaultValue", "IsNullable", "Precision", "Scale", "Required"]
        self._adjust_for_rel_class(headings)
        sheet.write_row(headings, ["bold"] * len(headings))

        # Loop through each field
        domains_doc = all_documents.get_document("Domains")

        for field in field_list:
            if self.include_base_fields is False and field.required and field.type != "GlobalID":
                continue

            # Domain hyperlink
            domain = "null"
            if field.domain:
                domain = field.domain
                if self.include_index and all_documents:
                    dom_workbook, dom_sheet = all_documents.get_sheet_info("Domains", field.domain)
                    domain = xls_handler.make_hyperlink(dom_sheet, field.domain, dom_workbook)

                if domains_doc:
                    if self.data_type == "Datasets":
                        domains_doc.register_dataset_with_domain(field.domain, item_name)

            # Write data
            description = metadata.get_field_description(field, item.describe)

            data = [
                field.name,
                field.type,
                field.length,
                utils.Standardize.null(description),
                utils.Standardize.to_string(field.aliasName),
                domain,
                utils.Standardize.null(field.defaultValue),
                utils.Standardize.to_string(field.isNullable),
                field.precision,
                field.scale,
                utils.Standardize.to_string(field.required),
            ]

            self._adjust_for_rel_class(data)

            styles = [None] * len(data)
            if field.domain and self.include_index and all_documents and self.data_type != "Relationship Classes":
                styles[5] = "hyperlink"

            sheet.write_row(data, styles)

        return


    def _adjust_for_rel_class(self, data_list:list):
        """Adjust a list to remove the domain and default value position for relationship classes.

        Args:
            list (list): List of data related to fields.
        """

        if self.data_type == "Relationship Classes":
            data_list.pop(6)
            data_list.pop(5)

        return