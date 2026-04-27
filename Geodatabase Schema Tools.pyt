# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods, invalid-name

"""
ArcGIS Pro Python Toolbox to access the Geodatabase Schema Tools.

Author: David Blanchard, Roya Shourouni

Version: 2.0
"""

import warnings
import arcpy
from gdbschematools.interfaces import ExcelInterface, GeodatabaseInterface, MarkdownInterface


class Toolbox:
    """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""

    def __init__(self):

        self.label = "Geodatabase Schema Tools"
        self.alias = "GeodatabaseSchemaTools"

        # List of tool classes associated with this toolbox
        self.tools = [GDBToXLS, XLSToGDB, GDBToMD, XLSToMD, UpdateMetadata, CompareGDB, CompareExcels, CompareGDBToExcel]


class GDBToXLS:
    """Define the tool (tool name is the name of the class)."""

    def __init__(self):
        self.label = "Geodatabase to Excel"
        self.description = "Inspect the schema of a geodatabase and output the schema as an Excel spreadsheet."


    def getParameterInfo(self):
        """Define the tool parameters."""

        gdb_path = arcpy.Parameter(
            displayName="Geodatabase",
            name="gdb_path",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input",
        )
        gdb_path.filter.list = ["Local Database", "Remote Database"]

        output_directory = arcpy.Parameter(
            displayName="Output Directory",
            name="output_directory",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )

        all_fields_in_subtypes = arcpy.Parameter(
            displayName="Include All Fields in Subtypes",
            name="include_all_field_in_subtypes",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input"
        )
        all_fields_in_subtypes.value = False

        hide_template = arcpy.Parameter(
            displayName="Hide Template Worksheet",
            name="hide_template",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input"
        )
        hide_template.value = False

        datasets_spreadsheet = arcpy.Parameter(
            displayName="Datasets Spreadsheet",
            name="datasets_spreadsheet",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output"
        )

        domains_spreadsheet = arcpy.Parameter(
            displayName="Domains Spreadsheet",
            name="domains_spreadsheet",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output"
        )

        relationships_spreadsheet = arcpy.Parameter(
            displayName="Relationship Classes Spreadsheet",
            name="relationships_spreadsheet",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output"
        )

        return [gdb_path, output_directory, all_fields_in_subtypes, hide_template, datasets_spreadsheet,
                domains_spreadsheet, relationships_spreadsheet]


    def execute(self, parameters, messages):
        """Run the tool, completing operations and returning results."""
        del messages

        # Read parameters
        gdb_path = parameters[0].valueAsText
        output_directory = parameters[1].valueAsText
        all_fields_in_subtypes =  parameters[2].value
        hide_template = parameters[3].value
        datasets_spreadsheet_index = 4
        domains_spreadsheet_index = 5
        relationships_spreadsheet_index = 6

        # Execute conversion
        with warnings.catch_warnings(record=True) as warns:
            warnings.simplefilter("always")
            gdb_structure = GeodatabaseInterface.read(gdb_path)
            for w in warns:
                arcpy.AddWarning(f"{w.message}")

        (datasets_path, domains_path, relationships_path) = ExcelInterface.write(
            gdb=gdb_structure,
            output_dir=output_directory,
            template_visible=not(hide_template),
            skip_unchanged_fields=not(all_fields_in_subtypes),
        )

        # Set output parameters
        parameters[datasets_spreadsheet_index].value = datasets_path
        parameters[domains_spreadsheet_index].value = domains_path
        parameters[relationships_spreadsheet_index].value = relationships_path

        arcpy.AddMessage("Completed successfully, see Parameters tab for links to the resulting spreadsheets.")


class XLSToGDB:
    """Define the tool (tool name is the name of the class)."""

    def __init__(self):
        self.label = "Excel to Geodatabase"
        self.description = "Apply the schema defined in an Excel file to a geodatabase."


    def getParameterInfo(self):
        """Define the tool parameters."""

        datasets_spreadsheet = arcpy.Parameter(
            displayName="Datasets Workbook",
            name="datasets_spreadsheet",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        datasets_spreadsheet.filter.list = ["xlsx"]

        domains_spreadsheet = arcpy.Parameter(
            displayName="Domains Workbook",
            name="domains_spreadsheet",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        domains_spreadsheet.filter.list = ["xlsx"]

        relationships_spreadsheet = arcpy.Parameter(
            displayName="Relationships Workbook",
            name="relationships_spreadsheet",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        relationships_spreadsheet.filter.list = ["xlsx"]

        gdb_path = arcpy.Parameter(
            displayName="Geodatabase",
            name="gdb_path",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input",
        )
        gdb_path.filter.list = ["Local Database", "Remote Database"]

        return [datasets_spreadsheet, domains_spreadsheet, relationships_spreadsheet, gdb_path]


    def execute(self, parameters, messages):
        """Run the tool, completing operations and returning results."""
        del messages

        # Read parameters
        datasets_spreadsheet = parameters[0].valueAsText
        domains_spreadsheet = parameters[1].valueAsText
        relationships_spreadsheet = parameters[2].valueAsText
        gdb_path = parameters[3].valueAsText

        # Execute conversion
        gdb_structure = ExcelInterface.read(datasets_spreadsheet, domains_spreadsheet, relationships_spreadsheet)
        with warnings.catch_warnings(record=True) as warns:
            warnings.simplefilter("always")
            GeodatabaseInterface.write(gdb_structure, gdb_path)
            for w in warns:
                arcpy.AddWarning(f"{w.message}")

        arcpy.AddMessage(f"Completed successfully, changes applied to database at {gdb_path}.")


class GDBToMD:
    """Define the tool (tool name is the name of the class)."""

    def __init__(self):
        self.label = "Geodatabase to Markdown"
        self.description = "Inspect the schema of a geodatabase and output the schema as Markdown files."


    def getParameterInfo(self):
        """Define the tool parameters."""

        gdb_path = arcpy.Parameter(
            displayName="Geodatabase",
            name="gdb_path",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input",
        )
        gdb_path.filter.list = ["Local Database", "Remote Database"]

        output_directory = arcpy.Parameter(
            displayName="Output Directory",
            name="output_directory",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )

        datasets_markdown = arcpy.Parameter(
            displayName="Datasets Markdown",
            name="datasets_markdown",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output"
        )

        domains_markdown = arcpy.Parameter(
            displayName="Domains Markdown",
            name="domains_markdown",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output"
        )

        relationships_markdown = arcpy.Parameter(
            displayName="Relationship Classes Markdown",
            name="relationships_markdown",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output"
        )

        return [gdb_path, output_directory, datasets_markdown, domains_markdown, relationships_markdown]


    def execute(self, parameters, messages):
        """Run the tool, completing operations and returning results."""
        del messages

        # Read parameters
        gdb_path = parameters[0].valueAsText
        output_directory = parameters[1].valueAsText
        datasets_markdown_index = 2
        domains_markdown_index = 3
        relationships_markdown_index = 4

        # Execute conversion
        gdb_structure = GeodatabaseInterface.read(gdb_path)
        (datasets_path, domains_path, relationships_path) = MarkdownInterface.write(
            gdb=gdb_structure,
            output_dir=output_directory
        )

        # Set output parameters
        parameters[datasets_markdown_index].value = datasets_path
        parameters[domains_markdown_index].value = domains_path
        parameters[relationships_markdown_index].value = relationships_path

        arcpy.AddMessage("Completed successfully, see Parameters tab for links to the resulting markdown files.")


class XLSToMD:
    """Define the tool (tool name is the name of the class)."""

    def __init__(self):
        self.label = "Excel to Markdown"
        self.description = "Inspect the schema defined in a Excel spreadsheets and output the schema as Markdown files."


    def getParameterInfo(self):
        """Define the tool parameters."""

        datasets_spreadsheet = arcpy.Parameter(
            displayName="Datasets Workbook",
            name="datasets_spreadsheet",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        datasets_spreadsheet.filter.list = ["xlsx"]

        domains_spreadsheet = arcpy.Parameter(
            displayName="Domains Workbook",
            name="domains_spreadsheet",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        domains_spreadsheet.filter.list = ["xlsx"]

        relationships_spreadsheet = arcpy.Parameter(
            displayName="Relationships Workbook",
            name="relationships_spreadsheet",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        relationships_spreadsheet.filter.list = ["xlsx"]

        output_directory = arcpy.Parameter(
            displayName="Output Directory",
            name="output_directory",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )

        datasets_markdown = arcpy.Parameter(
            displayName="Datasets Markdown",
            name="datasets_markdown",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output"
        )

        domains_markdown = arcpy.Parameter(
            displayName="Domains Markdown",
            name="domains_markdown",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output"
        )

        relationships_markdown = arcpy.Parameter(
            displayName="Relationships Markdown",
            name="relationships_markdown",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output"
        )

        return [datasets_spreadsheet, domains_spreadsheet, relationships_spreadsheet, output_directory, \
                datasets_markdown, domains_markdown, relationships_markdown]


    def execute(self, parameters, messages):
        """Run the tool, completing operations and returning results."""
        del messages

        # Read parameters
        datasets_spreadsheet = parameters[0].valueAsText
        domains_spreadsheet = parameters[1].valueAsText
        relationships_spreadsheet = parameters[2].valueAsText
        output_directory = parameters[3].valueAsText
        datasets_markdown_index = 4
        domains_markdown_index = 5
        relationships_markdown_index = 6

        # Execute conversion
        gdb_structure = ExcelInterface.read(datasets_spreadsheet, domains_spreadsheet, relationships_spreadsheet)
        (datasets_path, domains_path, relationships_path) = MarkdownInterface.write(
            gdb=gdb_structure,
            output_dir=output_directory
        )

        # Set output parameters
        parameters[datasets_markdown_index].value = datasets_path
        parameters[domains_markdown_index].value = domains_path
        parameters[relationships_markdown_index].value = relationships_path

        arcpy.AddMessage("Completed successfully, see Parameters tab for links to the resulting markdown files.")


class UpdateMetadata:
    """Define the tool (tool name is the name of the class)."""

    def __init__(self):
        self.label = "Update Metadata from Excel"
        self.description = "Update the metadata in a geodatabase with the summaries \
        and descriptions found in a Excel workbooks."

    def getParameterInfo(self):
        """Define the tool parameters."""

        datasets_spreadsheet = arcpy.Parameter(
            displayName="Datasets Workbook",
            name="datasets_spreadsheet",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        datasets_spreadsheet.filter.list = ["xlsx"]

        domains_spreadsheet = arcpy.Parameter(
            displayName="Domains Workbook",
            name="domains_spreadsheet",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        domains_spreadsheet.filter.list = ["xlsx"]

        relationships_spreadsheet = arcpy.Parameter(
            displayName="Relationships Workbook",
            name="relationships_spreadsheet",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        relationships_spreadsheet.filter.list = ["xlsx"]

        gdb_path = arcpy.Parameter(
            displayName="Geodatabase",
            name="gdb_path",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input",
        )
        gdb_path.filter.list = ["Local Database", "Remote Database"]

        return [datasets_spreadsheet, domains_spreadsheet, relationships_spreadsheet, gdb_path]

    def execute(self, parameters, messages):
        """Run the tool, completing operations and returning results."""
        del messages

        # Read parameters
        datasets_spreadsheet = parameters[0].valueAsText
        domains_spreadsheet = parameters[1].valueAsText
        relationships_spreadsheet = parameters[2].valueAsText
        path_to_gdb = parameters[3].valueAsText


        # Execute conversion
        gdb_structure = ExcelInterface.read(datasets_spreadsheet, domains_spreadsheet, relationships_spreadsheet)

        with warnings.catch_warnings(record=True) as warns:
            warnings.simplefilter("always")
            GeodatabaseInterface.update_metadata(gdb_structure, path_to_gdb)
            for w in warns:
                arcpy.AddWarning(f"{w.message}")

        arcpy.AddMessage("The metadata of Geodatabase and its objects updated successfully.")


class CompareGDB:
    """Define the tool (tool name is the name of the class)."""

    def __init__(self):
        self.label = "Compare two Geodatabases"
        self.description = "Compare the schema of two geodatabase and output the differences as a Text file."
        self.category = "Compare"


    def getParameterInfo(self):
        """Define the tool parameters."""

        origin_gdb_path = arcpy.Parameter(
            displayName="Origin Geodatabase",
            name="origin_gdb_path",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input",
        )
        origin_gdb_path.filter.list = ["Local Database", "Remote Database"]

        other_gdb_path = arcpy.Parameter(
            displayName="Other Geodatabase",
            name="other_gdb_path",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input",
        )
        other_gdb_path.filter.list = ["Local Database", "Remote Database"]

        output_directory = arcpy.Parameter(
            displayName="Output Directory",
            name="output_directory",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )

        output_text_file = arcpy.Parameter(
            displayName="Output Text file",
            name="output_text_file",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output"
        )

        return [origin_gdb_path, other_gdb_path, output_directory, output_text_file]


    def execute(self, parameters, messages):
        """Run the tool, completing operations and returning results."""
        del messages

        # Read parameters
        origin_gdb_path = parameters[0].valueAsText
        other_gdb_path = parameters[1].valueAsText
        output_directory = parameters[2].valueAsText
        text_file_index = 3

        # Execute conversion
        origin_gdb_structure = GeodatabaseInterface.read(origin_gdb_path)
        other_gdb_structure = GeodatabaseInterface.read(other_gdb_path)
        diff_path = GeodatabaseInterface.compare(origin_gdb_structure, other_gdb_structure,
                                                output_dir=output_directory)

        # Set output parameters
        parameters[text_file_index].value = diff_path

        # Set output parameters

        arcpy.AddMessage("Completed successfully, see Parameters tab for links to the resulting markdown files.")


class CompareExcels:
    """Define the tool (tool name is the name of the class)."""
    def __init__(self):
        self.label = "Compare two Excel Schemas"
        self.description = "Compare the schema of two Excel files and output the differences as a Text file."
        self.category = "Compare"


    def getParameterInfo(self):
        """Define the tool parameters."""

        origin_datasets_spreadsheet = arcpy.Parameter(
            displayName="Origin Datasets Workbook",
            name="origin_datasets_spreadsheet",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        origin_datasets_spreadsheet.filter.list = ["xlsx"]

        origin_domains_spreadsheet = arcpy.Parameter(
            displayName="Origin Domains Workbook",
            name="origin_domains_spreadsheet",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        origin_domains_spreadsheet.filter.list = ["xlsx"]

        origin_relationships_spreadsheet = arcpy.Parameter(
            displayName="Origin Relationships Workbook",
            name="origin_relationships_spreadsheet",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        origin_relationships_spreadsheet.filter.list = ["xlsx"]

        other_datasets_spreadsheet = arcpy.Parameter(
            displayName="Other Datasets Workbook",
            name="other_datasets_spreadsheet",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        other_datasets_spreadsheet.filter.list = ["xlsx"]

        other_domains_spreadsheet = arcpy.Parameter(
            displayName="Other Domains Workbook",
            name="other_domains_spreadsheet",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        other_domains_spreadsheet.filter.list = ["xlsx"]

        other_relationships_spreadsheet = arcpy.Parameter(
            displayName="Other Relationships Workbook",
            name="other_relationships_spreadsheet",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        other_relationships_spreadsheet.filter.list = ["xlsx"]


        output_directory = arcpy.Parameter(
            displayName="Output Directory",
            name="output_directory",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )

        output_text_file = arcpy.Parameter(
            displayName="Output Text file",
            name="output_text_file",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output"
        )

        return [origin_datasets_spreadsheet, origin_domains_spreadsheet, origin_relationships_spreadsheet, other_datasets_spreadsheet, other_domains_spreadsheet, other_relationships_spreadsheet, output_directory, output_text_file]


    def execute(self, parameters, messages):
        """Run the tool, completing operations and returning results."""
        del messages

        # Read parameters
        origin_datasets_spreadsheet = parameters[0].valueAsText
        origin_domains_spreadsheet = parameters[1].valueAsText
        origin_relationships_spreadsheet = parameters[2].valueAsText
        other_datasets_spreadsheet = parameters[3].valueAsText
        other_domains_spreadsheet = parameters[4].valueAsText
        other_relationships_spreadsheet = parameters[5].valueAsText
        output_directory = parameters[6].valueAsText
        text_file_index = 7

        # Execute conversion
        origin_gdb_structure = ExcelInterface.read(origin_datasets_spreadsheet, origin_domains_spreadsheet, origin_relationships_spreadsheet)
        other_gdb_structure = ExcelInterface.read(other_datasets_spreadsheet, other_domains_spreadsheet, other_relationships_spreadsheet)
        diff_path = GeodatabaseInterface.compare(origin_gdb_structure, other_gdb_structure,
                                                output_dir=output_directory)

        # Set output parameters
        parameters[text_file_index].value = diff_path

        # Set output parameters

        arcpy.AddMessage("Completed successfully, see Parameters tab for links to the resulting markdown files.")


class CompareGDBToExcel:
    """Define the tool (tool name is the name of the class)."""
    def __init__(self):
        self.label = "Compare Geodatabase to Excel Schema"
        self.description = "Compare the schema of a geodatabase and an Excel file and output the differences as a Text file."
        self.category = "Compare"


    def getParameterInfo(self):
        """Define the tool parameters."""

        origin_gdb_path = arcpy.Parameter(
            displayName="Origin Geodatabase",
            name="origin_gdb_path",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input",
        )
        origin_gdb_path.filter.list = ["Local Database", "Remote Database"]


        other_datasets_spreadsheet = arcpy.Parameter(
            displayName="Other Datasets Workbook",
            name="other_datasets_spreadsheet",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        other_datasets_spreadsheet.filter.list = ["xlsx"]

        other_domains_spreadsheet = arcpy.Parameter(
            displayName="Other Domains Workbook",
            name="other_domains_spreadsheet",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        other_domains_spreadsheet.filter.list = ["xlsx"]

        other_relationships_spreadsheet = arcpy.Parameter(
            displayName="Other Relationships Workbook",
            name="other_relationships_spreadsheet",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        other_relationships_spreadsheet.filter.list = ["xlsx"]


        output_directory = arcpy.Parameter(
            displayName="Output Directory",
            name="output_directory",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )

        output_text_file = arcpy.Parameter(
            displayName="Output Text file",
            name="output_text_file",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output"
        )

        return [origin_gdb_path, other_datasets_spreadsheet, other_domains_spreadsheet, other_relationships_spreadsheet, output_directory, output_text_file]


    def execute(self, parameters, messages):
        """Run the tool, completing operations and returning results."""
        del messages

        # Read parameters
        origin_gdb_path = parameters[0].valueAsText
        other_datasets_spreadsheet = parameters[1].valueAsText
        other_domains_spreadsheet = parameters[2].valueAsText
        other_relationships_spreadsheet = parameters[3].valueAsText
        output_directory = parameters[4].valueAsText
        text_file_index = 5

        # Execute conversion
        origin_gdb_structure = GeodatabaseInterface.read(origin_gdb_path)
        other_gdb_structure = ExcelInterface.read(other_datasets_spreadsheet, other_domains_spreadsheet, other_relationships_spreadsheet)
        diff_path = GeodatabaseInterface.compare(origin_gdb_structure, other_gdb_structure,
                                                output_dir=output_directory)

        # Set output parameters
        parameters[text_file_index].value = diff_path

        # Set output parameters

        arcpy.AddMessage("Completed successfully, see Parameters tab for links to the resulting markdown files.")
