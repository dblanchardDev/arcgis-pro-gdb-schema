# Geodatabase Schema Tools

ArcGIS Pro tools for working with the schema of ArcGIS geodatabases. Meant as a partial replacement of X-Ray tools.

## Tools

### Inspect Geodatabase Schema (gdb_to_xls.py)

The Inspect Geodatabase Schema tool reads the schema and metadata of a geodatabase and outputs 3 Excel spreadsheets:

- **Datasets:** List of all feature classes and tables in the geodatabase along with their basic properties, fields, and subtypes.
- **Domains:** List of all domains in the geodatabase and their properties.
- **Relationships:** List of all relationship classes in the geodatabase along with their basic properties, rules, and fields.

This tools will only list feature classes, tables, and relationship classes. Other dataset types such as rasters, views, and network datasets will be skipped.

---

## How to use

This tool is provided as a Python toolbox and is compatible with ArcGIS Pro 3.0 and later.

### Use as a toolbox in ArcGIS Pro

1. Download the latest [release](/release).
1. Extract the content of the zip file.
1. [Add an existing toolbox](https://pro.arcgis.com/en/pro-app/latest/help/projects/connect-to-a-toolbox.htm) in ArcGIS Pro, pointing to the _Geodatabase Schema Tools.pyt_ file that was in the zip file.
1. Access the tools from the toolbox as you would with any other geoprocessing tool.

> ❗ **Important**
> All the files and folders in the zip file must remain together in order for the tools to work.

### Use from Python

1. Download the latest [release](/release).
1. Extract the content of the zip file.
1. Import the _gdb\_to\_xls_ file.
1. Call the _document_gdb_ function with the following arguments:

| Parameter           | Type | Description
|---------------------|------|-------------
| gdb_path            | str  | Path to the geodatabase to be documented.
| output_directory    | str  | Path to the directory where the worksheets will be written.
| include_index       | bool | Whether to include index sheets and cross-sheet links. Defaults to `True`.
| include_base_fields | bool | Whether to include base fields like _OBJECTID_ and _SHAPE_. Default to `False`.

---

## Support

This tool is distributed "AS IS" and is not supported nor certified by Esri Inc. or any of its international distributors. No guarantees are made regarding the functionality and proper functioning of this tool.

### Issues

Feel free to submit issues and enhancement requests. Please note however that this is a side project and I have very little time to address issues or enhancement requests.

---

## License

Copyright 2023 Esri Canada

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the [GNU General Public License](/LICENSE) for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
