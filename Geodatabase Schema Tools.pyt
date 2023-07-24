# pylint: disable=missing-class-docstring, missing-function-docstring, too-few-public-methods, invalid-name

"""
ArcGIS Pro Python Toolbox to access the various Geodatabase Schema Tools.

Author: David Blanchard

Version: 0.1
"""

import arcpy
import gdb_to_xls


class Toolbox:
    def __init__(self):
        self.label = "Geodatabase Schema Tools"
        self.alias = "GeodatabaseSchemaTools"

        # List of tool classes associated with this toolbox
        self.tools = [Inspect_Geodatabase_Schema]


class Inspect_Geodatabase_Schema:
    def __init__(self):
        self.label = "Inspect Geodatabase Schema"
        self.description = "Read the schema of a geodatabase and write it out to spreadsheets."
        self.canRunInBackground = True


    def getParameterInfo(self):
        gdb_path = arcpy.Parameter(
            displayName="Geodatabase",
            name="gdb_path",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input"
        )
        gdb_path.filter.list = ["Local Database", "Remote Database"]

        output_directory = arcpy.Parameter(
            displayName="Output Directory",
            name="output_directory",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )

        include_index = arcpy.Parameter(
            displayName="Include Index",
            name="include_index",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input"
        )
        include_index.value = True

        include_base_fields = arcpy.Parameter(
            displayName="Include Base Fields",
            name="include_base_fields",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input"
        )
        include_base_fields.value = False

        dataset_spreadsheet = arcpy.Parameter(
            displayName="Dataset Spreadsheet",
            name="dataset_spreadsheet",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output"
        )

        domain_spreadsheet = arcpy.Parameter(
            displayName="Dataset Spreadsheet",
            name="dataset_spreadsheet",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output"
        )

        return [gdb_path, output_directory, include_index, include_base_fields, dataset_spreadsheet, domain_spreadsheet]


    def execute(self, parameters, messages):
        del messages

        # Get parameters and run tool
        gdb_path = parameters[0].valueAsText
        output_directory = parameters[1].valueAsText
        include_index = parameters[2].value
        include_base_fields = parameters[3].value

        spreadsheets = gdb_to_xls.document_gdb(gdb_path, output_directory, include_index, include_base_fields)

        # Set results
        parameters[4].value = spreadsheets[0]
        parameters[5].value = spreadsheets[1]
        arcpy.AddMessage("Completed successfully, see Parameters tab for links to the resulting spreadsheets.")

        return
