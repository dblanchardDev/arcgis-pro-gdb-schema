"""
Compare two Geodatabase structures

Author: Roya Shourouni
"""

import os
from typing import TYPE_CHECKING
import arcpy
if TYPE_CHECKING:
    from ...structures import Geodatabase

def compare_two_geodatabases(origin_gdb_struct:"Geodatabase", other_gdb_struct:"Geodatabase", output_dir:str) -> str:
    """_summary_

    Args:
        origin_gdb_struct (Geodatabase): _description_
        other_gdb_struct (Geodatabase): _description_
        output_dir (str): Directory in which the diff file will be written.

    Returns:
        The path to which the diff text file is written.
    """
    arcpy.SetProgressor("default", "Comparing two geodatabases.")

    diff_results = origin_gdb_struct.diff(other_gdb_struct)
    if diff_results:
        diff_file_path = os.path.join(output_dir, f"{origin_gdb_struct.name}_{other_gdb_struct.name}_comparison.txt")
        if os.path.exists(diff_file_path):
            raise FileExistsError(f"Failed to save diff results as a file already exists: {diff_file_path}.")

        with open(diff_file_path, 'w', encoding='utf-8') as diff_file:
            diff_file.write('\n'.join(str(i) for i in diff_results))


    return diff_file_path