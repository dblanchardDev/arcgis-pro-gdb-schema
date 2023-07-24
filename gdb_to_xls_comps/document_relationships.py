"""
Document Relationship Classes from Geodatabases.

Author: David Blanchard

Version: 0.1
"""

import types

import arcpy

from gdb_to_xls_comps import metadata, utils, xls_handler
from gdb_to_xls_comps.document_base import DocumentBaseDatasets


class RetrieverFxns:
    """Helper methods to retrieve data from the describe."""

    @staticmethod
    def relationship_type(describe:object)->str:
        """Get the Relationship Type (simple or composite).

        Args:
            describe (object): ArcPy Describe object of the relationship class.

        Returns:
            str: the value.
        """

        return "Composite" if describe.isComposite else "Simple"


    @staticmethod
    def origin_primary_key(describe:object)->str:
        """Get the origin primary key.

        Args:
            describe (object): ArcPy Describe object of the relationship class.

        Returns:
            str: the value.
        """

        data = None
        if len(describe.originClassKeys) > 0:
            data = describe.originClassKeys[0][0]

        return utils.Standardize.null(data)


    @staticmethod
    def origin_foreign_key(describe:object)->str:
        """Get the origin foreign key.

        Args:
            describe (object): ArcPy Describe object of the relationship class.

        Returns:
            str: the value.
        """

        data = None
        if len(describe.originClassKeys) > 1:
            data = describe.originClassKeys[1][0]

        return utils.Standardize.null(data)


    @staticmethod
    def destination_primary_key(describe:object)->str:
        """Get the destination primary key.

        Args:
            describe (object): ArcPy Describe object of the relationship class.

        Returns:
            str: the value.
        """

        data = None
        if len(describe.destinationClassKeys) > 0:
            data = describe.destinationClassKeys[0][0]

        return utils.Standardize.null(data)


    @staticmethod
    def destination_foreign_key(describe:object)->str:
        """Get the destination foreign key.

        Args:
            describe (object): ArcPy Describe object of the relationship class.

        Returns:
            str: the value.
        """

        data = None
        if len(describe.destinationClassKeys) > 1:
            data = describe.destinationClassKeys[1][0]

        return utils.Standardize.null(data)


_RETRIEVERS_RC = {
        "Description": metadata.get_description,
        "Relationship Type": RetrieverFxns.relationship_type,
        "Forward Label": "forwardPathLabel",
        "Backward Label": "backwardPathLabel",
        "Message Direction": "notification",
        "Cardinality": "cardinality",
        "Attributed": "isAttributed",
        "Origin Primary Key": RetrieverFxns.origin_primary_key,
        "Origin Foreign Key": RetrieverFxns.origin_foreign_key,
        "Destination Primary Key": RetrieverFxns.destination_primary_key,
        "Destination Foreign Key": RetrieverFxns.destination_foreign_key,
        "Is Change Tracked": "changeTracked",
        "Is Archived": utils.Retrieve.check_archived,
}


class DocumentRelationships(DocumentBaseDatasets):
    """Document relationship classes from geodatabases into worksheets.

    Args:
        gdb_describe (object): ArcPy Describe object of the geodatabase.
        output_diretory (str): Path to the directory where worksheets will be written.
        include_index (bool, optional): Whether to include an index page and links between sheets. Defaults to True.
        include_base_fields (bool, optional): Whether to include base fields like OBJECTID and SHAPE. Defaults to False.
    """

    data_type:str = "Relationship Classes"
    item_sheet_max_widths = [55, 14, None, 55]


    def _populate_all_items(self) -> None:
        arcpy.SetProgressor("default", "Generating relationship class descriptions")
        self.all_items = utils.GetItems.all_rel_classes(self.gdb_describe)
        self.all_items.sort(key=self._extract_item_name)
        return


    def _populate_single_item(self, sheet:xls_handler.Sheet, item:any, all_documents:utils.AllDocuments = None) -> None:
        self._populate_base_info(sheet, item, all_documents)
        self._populate_rules(sheet, item)
        self._populate_fields(sheet, item, all_documents)

        return


    def _populate_base_info(self, sheet:xls_handler.Sheet, item:utils.ItemAndDataset, all_documents:utils.AllDocuments = None)->None:
        """Populate the base information for a relationship class.

        Args:
            sheet (xls_handler.Sheet): The sheet to which to write the info.
            item (utils.ItemAndDataset): The feature classe's or table's info.
            all_documents (dict, optional): Reference to other documents being build {datasets, domains}. Defaults to None.
        """

        # Get basic info
        sheet.write_row_listing("Relationship Class Name", self._extract_item_name(item))
        sheet.write_row_listing("Dataset", utils.Standardize.null(item.dataset_name))

        # Get origin and destination
        origin_value = self._convert_full_name_to_simple(item.describe.originClassNames[0])
        destin_value = self._convert_full_name_to_simple(item.describe.destinationClassNames[0])

        if self.include_index and all_documents:
            origin_workbook, origin_sheet = all_documents.get_sheet_info("Datasets", origin_value)
            origin_link = xls_handler.make_hyperlink(origin_sheet, origin_value, origin_workbook)
            sheet.write_row(["Origin Table", origin_link], ["bold", "hyperlink"])

            destin_workbook, destin_sheet = all_documents.get_sheet_info("Datasets", destin_value)
            destin_link = xls_handler.make_hyperlink(destin_sheet, destin_value, destin_workbook)
            sheet.write_row(["Destination Table", destin_link], ["bold", "hyperlink"])
        else:
            sheet.write_row_listing("Origin Table", origin_value)
            sheet.write_row_listing("Destination Table", destin_value)

        # Retrieve remaining fields
        for label, retriever in _RETRIEVERS_RC.items():
            data = "null"

            if isinstance(retriever, str):
                data = getattr(item.describe, retriever)

            elif isinstance(retriever, types.FunctionType):
                data = retriever(item.describe)

            data = utils.Standardize.to_string(data)
            sheet.write_row_listing(label, data)

        sheet.write_row_listing("DSID", utils.Standardize.null_or_negative(item.describe.dsid))

        return


    def _populate_rules(self, sheet:xls_handler.Sheet, item:utils.ItemAndDataset)->None:
        """Populate the info for the relationship class rules.

        Args:
            sheet (xls_handler.Sheet): The sheet to which to write the info.
            item (utils.ItemAndDataset): The feature classe's or table's info.
        """

        all_rules = item.describe.relationshipRules

        # Skip if no rules
        if len(all_rules) == 0:
            return

        sheet.write_row([""])
        sheet.write_row(["Relationship Rules"], ["heading"])

        headers = ["Rule ID", "Origin Subtype", "Origin Min", "Origin Max", "Destin. Subtype", "Destin. Min", "Destin. Max"]
        sheet.write_row(headers, ["bold"] * len(headers))

        for rule in all_rules:
            sheet.write_row([
                rule.ruleID,
                utils.Standardize.to_string(rule.originSubtypeCode),
                utils.Standardize.null(rule.originMinimumCardinality),
                utils.Standardize.null(rule.originMaximumCardinality),
                utils.Standardize.to_string(rule.destinationSubtypeCode),
                utils.Standardize.null(rule.destinationMinimumCardinality),
                utils.Standardize.null(rule.originMaximumCardinality),
            ])

        return


    def _populate_fields(self, sheet:xls_handler.Sheet, item:utils.ItemAndDataset, all_documents:dict = None)->None:
        """Populate the field information for an attributed or many-to-many relationship class.

        Args:
            sheet (xls_handler.Sheet): The sheet to which to write the info.
            item (utils.ItemAndDataset): The feature classe's or table's info.
            all_documents (dict, optional): Reference to other documents being build {datasets, domains}. Defaults to None.
        """

        # skip this section as there are no fields
        if len(item.describe.fields) == 0:
            return

        self._populate_all_fields(sheet, item, item.describe.fields, all_documents)

        return