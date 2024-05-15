# Geodatabase Schema Tools

ArcGIS Pro tool for working with the schema of ArcGIS geodatabases. Will convert a geodatabase's schema to and from an Excel workbook, produce markdown, and update metadata. Meant as a replacement of X-Ray tools for ArcMap.

> **ArcGIS Pro – Generate Schema Report Tool**  
> ArcGIS Pro now has a built-in tool which provides some of the same functionality: [Generate Schema Report](https://pro.arcgis.com/en/pro-app/latest/help/data/geodatabases/overview/schema-report.htm).
>
> | This Custom Tool | ArcGIS Pro Built-In Tool |
> |------------------|--------------------------|
> | Support for metadata summary describing the purpose of: datasets, fields, subtypes, domains, and domain codes. | No support for metadata. |
> | Supports a limited subset of geodatabase elements: feature datasets, feature classes, tables, relationship classes, subtypes, and domains. | Supports all features of the geodatabase. |
> | Produces 3 Excel workbooks (datasets, domains, relationship classes). | Produces 1 Excel workbook. |
> | Update metadata for geodatabase objects that already exist. | No support for metadata. |
> | Produce markdown files for development docs or wikis. | No support for markdown. |
>
> This tool is therefore useful for those who need support metadata or markdown, or just want a simpler Excel output.

## Tools

### Geodatabase to Excel

The Geodatabase to Excel tool reads the schema and metadata of a geodatabase and outputs 3 Excel workbooks:

- **Datasets:** List of all feature classes and tables in the geodatabase along with their basic properties, fields, and subtypes.
- **Domains:** List of all domains in the geodatabase and their properties.
- **Relationships:** List of all relationship classes in the geodatabase along with their basic properties, rules, and fields.

### Excel to Geodatabase

The Excel to Geodatabase tool reads the schema and metadata from the same 3 Excel workbooks that are produced by the _Geodatabase to Excel_ tool and create the corresponding datasets, domains, and relationship classes in a geodatabase.

This tool will only create new elements. If an element with the same name already exists in the Geodatabase, an error will occur.

#### Creating/Modifying the Excel Workbooks

If you want to create a schema from scratch using the Excel workbooks, run the _Geodatabase to Excel_ workbook on an empty geodatabase to get templates. If you wish to start off with an existing schema, do the same but use the geodatabase with the existing schema as your input to _Geodatabase to Excel_.

For existing elements, simply modify the data in the corresponding spreadsheet. New rows can be added for fields and subtypes. To create new elements, simply duplicate the _\_template\__ worksheet. If a cell is highlighted in red, the data entered is invalid or missing.

##### Geodatabase Information

The metadata summary for the geodatabase will be updated using the _Summary_ from the dataset's \_INFO\_ sheet.

##### Datasets

When setting the dataset type to _Table_, the following rows can be deleted from the sheet:

- Geometry Type
- Horizontal Spatial Ref.
- Vertical Spatial Ref.
- Has M-Values
- Has Z-Values

##### Domains

When creating a range domain, you may delete all rows related to coded values. When creating a coded value domain, you may delete all rows related to range values.

##### Relationship Class

The value for the origin and destination table must be the name of the feature class or table; it cannot be the alias.

If the relationship class is **not** attributed, you may delete the fields table as it will be ignored.

##### Fields

The OBJECTID and SHAPE fields will be created when appropriate regardless of whether they are specified. If their alias is set in the sheet, it will be updated in the table.

The order column is ignored. Fields will be added from top to bottom. If you have changed the order field, make sure to sort the table.

##### Subtypes

If you are not using subtypes, you can delete all rows related to subtypes.

The default subtype value is set by setting a default value in the fields table for the subtype field.

##### Relationship Classes and Domain Users

The Relationship Classes table in the dataset sheets, and the Domain Users table in the domain sheets are ignored by this tool.

### Excel to Markdown

Convert the schema defined in Excel spreadsheets into markdown files. Useful for inclusion in developer documentation (e.g. a README), in wikis (e.g. in Azure DevOps), and in end-user documentation (e.g. Docsify and Docusaurus).

Excel file requirements are the same as those for the [Excel to Geodatabase](#excel-to-geodatabase) tool.

### Geodatabase to Markdown

Convert the schema found in a geodatabase to markdown files. Useful for inclusion in developer documentation (e.g. a README), in wikis (e.g. in Azure DevOps), and in end-user documentation (e.g. Docsify and Docusaurus).

### Update Metadata

Use the summaries and description defined schemas in Excel spreadsheets to update objects that already exist in the geodatabase.

This will update the metadata and description for:

- Geodatabase
- Feature Classes
- Tables
- Relationship Classes
- Domains
- Fields
- Subtypes

If an object defined in the spreadsheets does not exist in the geodatabase, it will be skipped with a warning.

---

## How to use

This tool is provided as a Python toolbox and is compatible with ArcGIS Pro 3.0 and later.

### Use as a toolbox in ArcGIS Pro

> ❗ **Important**
> All the files and folders in the zip file must remain together in order for the tools to work.

1. Download the latest [release](https://github.com/dblanchardDev/arcgis-pro-gdb-schema/releases).
1. Extract the content of the zip file.
1. [Add an existing toolbox](https://pro.arcgis.com/en/pro-app/latest/help/projects/connect-to-a-toolbox.htm) in ArcGIS Pro, pointing to the _Geodatabase Schema Tools.pyt_ file that was in the zip file.
1. Access the tools from the toolbox as you would with any other geoprocessing tool.

> ❔ **Help**
> Each parameter is documented from within the toolbox. Simply hover your mouse over the ℹ to get an explanation.

### Use from Python

You can use the tools directly in Python using one of the 2 methods below.

> 🛠 **Packages**  
> You will need to use the Python installation that comes with ArcGIS Pro or ArcGIS Server as the _arcpy_ package is required. All other packages required by these tools are already included in the ArcGIS instance of Python.

#### Import Toolbox

Use Arcpy's [Import Toolbox](https://pro.arcgis.com/en/pro-app/latest/arcpy/functions/importtoolbox.htm) method to import the entire toolbox.

```python
arcpy.ImportToolbox(r"C:\Files\schematools\Geodatabase Schema Tools.pyt")
arcpy.GeodatabaseSchemaTools.XLSToMD(
    datasets_spreadsheet=r"C:\Files\new_schema_datasets.xlsx",
    domains_spreadsheet=r"C:\Files\new_schema_domains.xlsx",
    relationships_spreadsheet=r"C:\Files\new_schema_relationships.xlsx",
    output_directory=r"C:\Files\Markdown_Output",
)
```

#### Direct Access to Classes

You may import the classes from these tools and call their methods directly.

```python
from gdbschematools.interfaces import ExcelInterface, GeodatabaseInterface, MarkdownInterface

# From GDB to Excel
gdb_structure = GeodatabaseInterface.read(path_to_gdb)
(datasets_path, domains_path, relationships_path) = ExcelInterface.write(
    gdb_structure,
    output_directory,
    template_visible=True,
    skip_unchanged_fields=True,
)

# From Excel to GDB
gdb_structure = ExcelInterface.read(
    datasets_path,
    domains_path,
    relationships_paths
)
GeodatabaseInterface.write(gdb_structure, path_to_new_gdb)

# From Excel to Markdown
gdb_structure = ExcelInterface.read(
    datasets_path,
    domains_path,
    relationships_paths
)
MarkdownInterface.write(gdb_structure, output_directory)

# Update Metadata from Excel
gdb_structure = ExcelInterface.read(
    datasets_path,
    domains_path,
    relationships_paths
)
GeodatabaseInterface.update_metadata(gdb_structure, path_to_existing_gdb)

# Update Metadata from Another Geodatabase
gdb_structure = GeodatabaseInterface.read(path_to_gdb_with_new_metadata)
GeodatabaseInterface.update_metadata(gdb_structure, path_to_gdb_to_update)
```

---

## Limitations

As previously stated, this tools does not support all features of a geodatabase.

Supported elements include:

- Geodatabase Metadata Summary
- Core properties, fields, subtypes, and feature datasets for:
  - Feature classes
  - Tables
  - Relationship classes
- Domains (range or coded value)

The following dataset properties are **not** supported:

- Versioning (supported in the _Geodatabase to Excel_ and _Geodatabase to Markdown_ output only)
- Editor Tracking
- Attribute Rules
- Contingent Values
- Indexes

---

## Support

This tool is distributed "AS IS" and is not supported nor certified by Esri Inc. or any of its international distributors. No guarantees are made regarding the functionality and proper functioning of this tool.

### Issues

Feel free to submit issues and enhancement requests. Please note however that this is a side project and I have very little time to address issues or enhancement requests.

---

## Contributions

Thank you to Roya Shourouni for her contributions to this tool, including the Excel Reader, the Geodatabase Writer, and the Markdown Writer components.

If you wish to contributor to this project, please contact David Blanchard in advance.

---

## License

Copyright 2023 - 2024 Esri Canada

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the [GNU General Public License](/LICENSE) for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
