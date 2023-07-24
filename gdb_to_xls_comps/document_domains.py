"""
Document Domains from Geodatabases.

Author: David Blanchard

Version: 0.1
"""

import arcpy

from gdb_to_xls_comps import utils, xls_handler
from gdb_to_xls_comps.document_base import DocumentBase


class DocumentDomains(DocumentBase):
    """Document domains from geodatabases into worksheets.

    Args:
        gdb_describe (object): ArcPy Describe object of the geodatabase.
        output_diretory (str): Path to the directory where worksheets will be written.
        include_index (bool, optional): Whether to include an index page and links between sheets. Defaults to True.
        include_base_fields (bool, optional): Whether to include base fields like OBJECTID and SHAPE. Defaults to False.
    """

    data_type:str = "Domains"
    item_sheet_max_widths = [55, None]
    dataset_registration:dict[str, list[str]] = {}


    def register_dataset_with_domain(self, domain_name:str, dataset_name:str)->None:
        """Register a dataset as using the domain. Must be called before the populate_item_info method.

        Args:
            domain_name (str): Name of the domain.
            dataset_name (str): Name of the dataset.
        """

        self.dataset_registration.setdefault(domain_name, [])

        if dataset_name not in self.dataset_registration[domain_name]:
            self.dataset_registration[domain_name].append(dataset_name)

        return


    def _populate_all_items(self) -> None:
        arcpy.SetProgressor("default", "Generating domain descriptions")
        # pylint: disable-next=no-member
        self.all_items = arcpy.da.ListDomains(self.gdb_describe.catalogPath)
        self.all_items.sort(key=self._extract_item_name)
        return


    def _extract_item_name(self, item: object):
        return item.name


    def _populate_single_item(self, sheet:xls_handler.Sheet, item:any, all_documents:utils.AllDocuments = None) -> None:

        self._populate_base_info(sheet, item)

        if item.domainType == "CodedValue":
            self._populate_coded_values(sheet, item)
        else:
            self._populate_range_domain(sheet, item)

        self._populate_domain_users(sheet, item, all_documents)

        return


    def _populate_base_info(self, sheet:xls_handler.Sheet, domain:object)->None:
        """Populate the base information for a domain.

        Args:
            sheet (xls_handler.Sheet): The sheet to which to write the info.
            domain (object): The ArcPy describe object for the domain to document.
        """

        sheet.write_row_listing("Domain Name", domain.name)
        sheet.write_row_listing("Domain Type", domain.domainType)
        sheet.write_row_listing("Field Type", domain.type)
        sheet.write_row_listing("Merge Policy", domain.mergePolicy)
        sheet.write_row_listing("SplitPolicy", domain.splitPolicy)
        sheet.write_row_listing("Description", domain.description)
        sheet.write_row_listing("Owner", domain.owner or "null")

        return


    def _populate_coded_values(self, sheet:xls_handler.Sheet, domain:object)->None:
        """Populate the code-value details for a domain.

        Args:
            sheet (xls_handler.Sheet): The sheet to which to write the info.
            domain (object): The ArcPy describe object for the domain to document.
        """

        # Add headers
        sheet.write_row([""])
        sheet.write_row(["Coded Values"], ["heading"])
        sheet.write_row(["Code", "Name"], ["bold", "bold"])

        # Run through each coded value
        for code, name in domain.codedValues.items():
            sheet.write_row([code, name])

        return


    def _populate_range_domain(self, sheet:xls_handler.Sheet, domain:object)->None:
        """Populate the code-value details for a domain.

        Args:
            sheet (xls_handler.Sheet): The sheet to which to write the info.
            domain (object): The ArcPy describe object for the domain to document.
        """

        # Add headers
        sheet.write_row([""])
        sheet.write_row(["Range"], ["heading"])
        sheet.write_row(["Min", "Max"], ["bold", "bold"])

        # Add values
        minimum = domain.range[0]
        maximum = domain.range[1]

        if domain.type in ["Short", "Long"]:
            minimum = round(minimum)
            maximum = round(maximum)

        elif domain.type == "Date":
            pass

        sheet.write_row([minimum, maximum])

        return


    def _populate_domain_users(self, sheet:xls_handler.Sheet, domain:object, all_documents:utils.AllDocuments)->None:
        """Populate a list of feature classes and tables that use the domain.

        Args:
            sheet (xls_handler.Sheet): The sheet to which to write the info.
            domain (object): The ArcPy describe object for the domain to document.
            all_documents (utils.AllDocuments, optional): Reference to other documents being build {datasets, domains}. Defaults to None
        """

        # Add headers
        sheet.write_row([""])
        sheet.write_row(["Domain Users"], ["heading"])

        domain_name = self._extract_item_name(domain)
        datasets = self.dataset_registration.get(domain_name, [])

        if datasets:
            for ds_name in datasets:
                if self.include_index:
                    workbook, sheet_name = all_documents.get_sheet_info("Datasets", ds_name)
                    link = xls_handler.make_hyperlink(sheet_name, ds_name, workbook)
                    sheet.write_row([link], ["hyperlink"])
                else:
                    sheet.write_row([ds_name])

        else:
            sheet.write_row(["<None>"])