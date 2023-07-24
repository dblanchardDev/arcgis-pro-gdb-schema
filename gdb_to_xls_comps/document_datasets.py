"""
Document Feature Classes and Tables from Geodatabases.

Author: David Blanchard

Version: 0.1
"""

import types

import arcpy

from gdb_to_xls_comps import metadata, utils, xls_handler
from gdb_to_xls_comps.document_base import DocumentBaseDatasets

_RETRIEVERS_FC = {
    "Description": metadata.get_description,
    "Dataset Type": "dataType",
    "Shape Type": "shapeType",
    "Feature Type": "featureType",
    "Alias Name": "aliasName",
    "Spatial Reference": utils.Retrieve.spatial_reference,
    "Has M": "hasM",
    "Has Z": "hasZ",
    "Is Change Tracked": "changeTracked",
    "Is Archived": utils.Retrieve.check_archived,
    "Subtype Field Name": "subtypeFieldName",
}

_RETRIEVERS_TABLE = {
    "Description": metadata.get_description,
    "DatasetType": "dataType",
    "AliasName": "aliasName",
    "Is Change Tracked": "changeTracked",
    "Is Archived": utils.Retrieve.check_archived,
    "SubtypeFieldName": "subtypeFieldName",
}


class DocumentDatasets(DocumentBaseDatasets):
    """Document feature classes and tables from geodatabases into worksheets.

    Args:
        gdb_describe (object): ArcPy Describe object of the geodatabase.
        output_diretory (str): Path to the directory where worksheets will be written.
        include_index (bool, optional): Whether to include an index page and links between sheets. Defaults to True.
        include_base_fields (bool, optional): Whether to include base fields like OBJECTID and SHAPE. Defaults to False.
    """

    data_type:str = "Datasets"
    item_sheet_max_widths = [55, 14, None, 55]


    def _populate_all_items(self) -> None:
        arcpy.SetProgressor("default", "Generating dataset descriptions")
        self.all_items = utils.GetItems.all_fcs_and_tables(self.gdb_describe)
        self.all_items.sort(key=self._extract_item_name)
        return


    def _populate_single_item(self, sheet:xls_handler.Sheet, item:any, all_documents:utils.AllDocuments = None) -> None:
        self._populate_base_info(sheet, item)
        self._populate_fields(sheet, item, all_documents)
        self._populate_subtypes(sheet, item, all_documents)
        self._populate_relationship_classes(sheet, item, all_documents)

        return


    def _populate_base_info(self, sheet:xls_handler.Sheet, item:utils.ItemAndDataset)->None:
        """Populate the base information for a feature class or table.

        Args:
            sheet (xls_handler.Sheet): The sheet to which to write the info.
            item (utils.ItemAndDataset): The feature classe's or table's info.
        """
        describe = item.describe
        prop_retrievers = None

        if describe.dataType == "FeatureClass":
            sheet.write_row_listing("Feature Class Name", self._extract_item_name(item))
            sheet.write_row_listing("Dataset", utils.Standardize.null(item.dataset_name))
            prop_retrievers = _RETRIEVERS_FC

        else:
            sheet.write_row_listing("Table Name", self._extract_item_name(item))
            prop_retrievers = _RETRIEVERS_TABLE

        for label, retriever in prop_retrievers.items():
            data = "null"

            if isinstance(retriever, str):
                data = getattr(describe, retriever)

            elif isinstance(retriever, types.FunctionType):
                data = retriever(describe)

            data = utils.Standardize.to_string(data)
            sheet.write_row_listing(label, data)

        # Add numeric data
        def_subtype = describe.defaultSubtypeCode
        if def_subtype == -1:
            def_subtype = ""

        sheet.write_row_listing("Default Subtype", def_subtype)
        sheet.write_row_listing("DSID", describe.dsid)

        return


    def _populate_fields(self, sheet:xls_handler.Sheet, item:utils.ItemAndDataset, all_documents:utils.AllDocuments)->None:
        """Populate the field listing for a feature class or table.

        Args:
            sheet (xls_handler.Sheet): The sheet to which to write the info.
            item (utils.ItemAndDataset): The item whose fields are to be populated.
            all_documents (utils.AllDocuments, optional): Reference to other documents being build {datasets, domains}. Defaults to None.
        """

        return self._populate_all_fields(sheet, item, item.describe.fields, all_documents)


    def _populate_subtypes(self, sheet:xls_handler.Sheet, item:utils.ItemAndDataset, all_documents:utils.AllDocuments)->None:
        """Populate the subtype listing for a feature class or table.

        Args:
            sheet (xls_handler.Sheet): The sheet to which to write the info.
            item (object): The ArcPy describe object for the item to document.
            all_documents (utils.AllDocuments, optional): Reference to other documents being build {datasets, domains}. Defaults to None
        """

        # Skip if no subtype defined
        if len(item.describe.subtypeFieldName) == 0:
            return

        # pylint: disable-next=no-member
        subtypes = arcpy.da.ListSubtypes(item.describe.catalogPath)

        # Write list header
        sheet.write_row([""])
        sheet.write_row(["Subtypes"], ["heading"])
        sheet.write_row(["SubtypeName", "SubtypeCode"], ["bold", "bold"])

        # Write Subtypes List
        for code, details in subtypes.items():
            sheet.write_row([
                details["Name"],
                code,
            ])

        # Write subtype info headers
        sheet.write_row([""])
        sheet.write_row(["Subtype Field Info"], ["heading"])
        sheet.write_row(["SubtypeName", "SubtypeCode", "FieldName", "DomainName", "DefaultValue"], ["bold"] * 5)

        domains_doc = all_documents.get_document("Domains")

        # Write subtype info
        for code, details in subtypes.items():
            name = details["Name"]

            for field, (default, domain) in details["FieldValues"].items():
                if domain is not None:
                    domain_value = domain.name
                    if self.include_index:
                        dom_workbook, dom_sheet = all_documents.get_sheet_info("Domains", domain.name)
                        domain_value = xls_handler.make_hyperlink(dom_sheet, domain.name, dom_workbook)

                    if domains_doc:
                        item_name = self._extract_item_name(item)
                        domains_doc.register_dataset_with_domain(domain.name, item_name)

                    data = [
                        name,
                        code,
                        field,
                        domain_value,
                        utils.Standardize.null(default),
                    ]

                    styles = [None] * len(data)
                    if self.include_index:
                        styles[3] = "hyperlink"

                    sheet.write_row(data, styles)

        return


    def _populate_relationship_classes(self, sheet:xls_handler.Sheet, item:utils.ItemAndDataset, all_documents:utils.AllDocuments)->None:
        """Populate the subtype listing for a feature class or table.

        Args:
            sheet (xls_handler.Sheet): The sheet to which to write the info.
            item (object): The ArcPy describe object for the item to document.
            all_documents (utils.AllDocuments, optional): Reference to other documents being build {datasets, domains}. Defaults to None
        """

        rc_names = item.describe.relationshipClassNames

        # Skip if no relationship classes
        if len(rc_names) == 0:
            return

        # Write list header
        sheet.write_row([""])
        sheet.write_row(["Relationship Classes"], ["heading"])

        for full_name in rc_names:
            name = self._convert_full_name_to_simple(full_name)
            if self.include_index and all_documents:
                workbook, sheet_name = all_documents.get_sheet_info("Relationship Classes", name)
                value = xls_handler.make_hyperlink(sheet_name, name, workbook)
                sheet.write_row([value], ["hyperlink"])
            else:
                sheet.write_row([name])

        return