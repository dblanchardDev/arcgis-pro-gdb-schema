"""
Utilities to assist in extracting the schema from geodatabases.

Author: David Blanchard

Version: 0.1
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Union

if TYPE_CHECKING:
    from gdb_to_xls_comps.document_base import DocumentBase


class AllDocuments:
    """Handler for all document class instances to allow easy lookup accross documents.

    Args:
        documents (list[DocumentBase]): List of all document instances. Must not include duplicate data types.
    """

    _documents:Dict[str, DocumentBase] = {}

    def __init__(self, documents:list[DocumentBase])->None:
        # Store documents by type
        for doc in documents:
            self._documents[doc.data_type] = doc
        return


    def __iter__(self):
        return self._documents.values().__iter__()


    def get_document(self, data_type:str)->DocumentBase:
        """Get a document from the data type it stores.

        Args:
            data_type (str): Data type to get.

        Returns:
            DocumentBase: Document class instance.
        """

        return self._documents.get(data_type)


    def get_workbook_info(self, data_type:str)->Union[str, None]:
        """Get the name of the workbook for a particular data type.

        Args:
            data_type (str): The data type whose workbook needs to be accessed.

        Returns:
            Union[str, None]: name of the workbook.
        """

        data = None
        if data_type in self._documents:
            data = self._documents[data_type].workbook.file_name

        return data


    def get_sheet_info(self, data_type:str, item_name:str)->Union[tuple[str], tuple[None]]:
        """Get the name of the workbook and the name of the sheet.

        Args:
            data_type (str): The data type whose workbook needs to be accessed.
            item_name (str): The name of the item whose sheet is to be accessed.

        Returns:
            Union[tuple[str], tuple[None]]: (name of the workbook, name of the sheet)
        """

        data = (None, None)
        if data_type in self._documents:
            doc = self._documents[data_type]

            if item_name in doc.sheet_names:
                data = (doc.workbook.file_name, doc.sheet_names[item_name])

        return data


class ItemAndDataset:
    """Hold an items ArcPy describe and its dataset name.

    Args:
        describe (object): ArcPy describe for feature class or table.
        dataset_name (str, optional): Dataset name if any. Defaults to None.
    """

    _describe:object = None
    _dataset_name:str = None

    def __init__(self, describe:object, dataset_name:str=None) -> None:
        self._describe = describe
        self._dataset_name = dataset_name
        return


    @property
    def describe(self)->object:
        """Item's ArcPy Describe Object."""
        return self._describe


    @property
    def dataset_name(self)->str:
        """Item's dataset name or None."""
        return self._dataset_name



class GetItems:
    """Helper methods to retrieve all items of a particular type from a geodatabase description."""

    @staticmethod
    def _get_all_items_from_gdb(gdb_describe:object, data_types:list[str], cur_dataset:str=None)->list[ItemAndDataset]:
        """Get the ArcPy describe of all specified items types from an ArcPy Geodatabase describe.

        Args:
            gdb_describe (object): ArcPy describe object of a geodatabase.
            data_types (list[str]): List of all data types to extract.

        Returns:
            list[ItemAndDataset]: Flat list of ItemAndDataset object (.describe/.dataset_name).
        """
        all_items = []

        for child in gdb_describe.children:
            if child.dataType == "FeatureDataset":
                grand_children = GetItems._get_all_items_from_gdb(child, data_types, child.baseName)
                all_items.extend(grand_children)

            elif child.dataType in data_types:
                all_items.append(ItemAndDataset(child, cur_dataset))

        return all_items


    @staticmethod
    def all_fcs_and_tables(gdb_describe:object)->list[ItemAndDataset]:
        """Get the ArcPy describe of all feature classes and tables from an ArcPy Geodatabase describe.

        Args:
            gdb_describe (object): ArcPy describe object of a geodatabase.

        Returns:
            list[ItemAndDataset]: Flat list of ItemAndDataset object (.describe/.dataset_name).
        """

        return GetItems._get_all_items_from_gdb(gdb_describe, ["FeatureClass", "Table"])


    @staticmethod
    def all_rel_classes(gdb_describe:object)->list[ItemAndDataset]:
        """Get the ArcPy describe of all relationship classes from an ArcPy Geodatabase describe.

        Args:
            gdb_describe (object): ArcPy describe object of a geodatabase.

        Returns:
            list[ItemAndDataset]: Flat list of ItemAndDataset object (.describe/.dataset_name).
        """

        return GetItems._get_all_items_from_gdb(gdb_describe, ["RelationshipClass"])


class Standardize:
    """Helper methods to standardize data before outputting them to the workbook."""

    @staticmethod
    def to_string(data:any)->str:
        """Return a string representation of the data, using "null", "true", and "false" where appropriate. Lists and tuples will be joined into a coma-separated string.

        Args:
            data (any): Value to be standardized.

        Returns:
            str: The string representation.
        """

        standardized = data
        if isinstance(standardized, list):
            parts = [Standardize.to_string(e) for e in standardized]
            standardized = ", ".join(parts)

        else:
            standardized = Standardize.null(standardized)

            if isinstance(standardized, bool):
                return "true" if standardized else "false"

        return str(standardized)


    @staticmethod
    def null(data:any)->any:
        """Return the data as is, or "null" if the data is None or an empty string.

        Args:
            data (any): The data to be standardized.

        Returns:
            any: The standardized data.
        """

        if data is None or (isinstance(data, str) and data == ""):
            return "null"

        return data


    @staticmethod
    def null_or_negative(data:any)->any:
        """Return the data as is, or "null" if the data is None, an empty string, or -1.

        Args:
            data (any): The data to be standardized.

        Returns:
            any: The standardized data.
        """

        standardized = Standardize.null(data)
        if standardized == -1:
            standardized = "null"

        return standardized


class Retrieve:
    """Helper methods to retrieve more complex values from an ArcGIS Describe object."""

    @staticmethod
    def check_archived(item:object)->Union[bool, None]:
        """Return whether a dataset is archived or null if not available.

        Args:
            item (object): ArcPy describe object.

        Returns:
            Union[bool, None]: true, false, or None
        """

        is_archived = None

        try:
            is_archived = item.isArchived
        except AttributeError:
            pass

        return is_archived


    @staticmethod
    def spatial_reference(item:object)->Union[str, None]:
        """Return the dataset's spatial reference (if any).

        Args:
            item (object): ArcPy Describe Object.

        Returns:
            Union[str, None]: spatial reference description
        """

        label = item.spatialReference.name.replace("_", " ")

        if item.spatialReference.abbreviation:
            label = item.spatialReference.abbreviation.replace("_", " ")

        return f"{label} (WKID: {item.spatialReference.factoryCode})"