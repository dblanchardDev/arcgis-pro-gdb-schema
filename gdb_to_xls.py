"""
Read the schema of an ArcGIS Geodatabase and copy it into an XLS spreadsheet. Will include feature datasets, feature classes, tables, domains, and relationship classes. Meant to be used within ArcGIS Pro to replicate some of the features of X-Ray in ArcMap.

Author: David Blanchard

Version: 0.1
"""

import arcpy

from gdb_to_xls_comps import utils
from gdb_to_xls_comps.document_datasets import DocumentDatasets
from gdb_to_xls_comps.document_domains import DocumentDomains
from gdb_to_xls_comps.document_relationships import DocumentRelationships


# ====== TOOL PARAMETERS ======
# fill these out when debugging or otherwise running this tool directly.

PARAMS = {
    # The path to the geodatabase
    "GDB_PATH": r"",

    # The path to the output directory where the XLS files will be written
    "OUTPUT_DIRECTORY": r"",

    # Whether to include an index sheet for each worksheet
    "INCLUDE_INDEX": True,

    # Whether to include base fields like OBJECTID, and SHAPE in the output
    "INCLUDE_BASE_FIELDS": False,
}

##################


def document_gdb(gdb_path:str, output_directory:str, include_index:bool=True, include_base_fields:bool=False)->tuple:
    """Document the geodatabase, its feature classes, tables, domains, and relationship classes; writing the output to an Excel worksheet.

    Args:
        gdb_path (str): Path to the geodatabase to be documented.
        output_directory (str): Path to the directory where the worksheets will be written.
        include_index (bool, optional): Whether to include an index sheets and cross-sheet links. Defaults to True.
        include_base_fields (bool, optional): Whether to include base fields like OBJECTID and SHAPE. Defaults to False.

    Returns:
        tuple: Path to worksheets (datasets, domains, relationships)
    """

    # Retrieve descriptions from database
    arcpy.SetProgressor("default", "Generating geodatabase description")
    gdb_describe = arcpy.Describe(gdb_path)

    # Initialize the documentation classes
    all_docs = utils.AllDocuments([
        DocumentDatasets(gdb_describe, output_directory, include_index, include_base_fields),
        DocumentDomains(gdb_describe, output_directory, include_index, include_base_fields),
        DocumentRelationships(gdb_describe, output_directory, include_index, include_base_fields),
    ])

    # Populate the item information
    for doc in all_docs:
        doc.populate_item_info(all_docs)

    # Finilize the documents and return the worksheet paths
    arcpy.SetProgressor("default", "Finalizing and saving worksheets")
    worksheet_paths = []
    for doc in all_docs:
        doc.finish()
        worksheet_paths.append(doc.workbook.full_path)

    return tuple(worksheet_paths)


# When run directly for debugging, use the PARAMS to run the code
if __name__ == "__main__":
    print(document_gdb(
        PARAMS["GDB_PATH"],
        PARAMS["OUTPUT_DIRECTORY"],
        PARAMS["INCLUDE_INDEX"],
        PARAMS["INCLUDE_BASE_FIELDS"]
    ))