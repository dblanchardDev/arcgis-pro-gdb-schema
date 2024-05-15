"""
Excel writer for the datasets workbook.

Author: David Blanchard
"""

from .. import cellar
from ..excel_converter import xl2st
from .gdb_writer import GDBWriterWithFields
from .table_writers import InRelationshipsWriter


class DatasetsWriter(GDBWriterWithFields):
    """Excel writer component used specifically for the datasets workbook.

    Args:
        workbook_path (str): Path where the XLSX file will be written, including the extension.
        database_name (str): Name of the geodatabase.
        workspace_type (str, optional): Type of workspace (local or remote). Defaults to None.
        remote_server (str, optional): Address/name of the geodatabase if any. Defaults to None.
        summary (str, optional): Metadata summary about the geodatabase. Defaults to None.
        template_visible (bool, optional): Whether the template sheets (used to create new datasets/domains from
          scratch) are visible.
    """

    element_type:str = "dataset"
    _dropdown_dataset_type:cellar.CellDropdown = None
    _dropdown_geometry_type:cellar.CellDropdown = None
    _dropdown_horizontal_sr:cellar.CellDropdown = None
    _dropdown_boolean:cellar.CellDropdown = None
    _column_widths:list[int] = [25, 15, 80, 25, 22, 15, 12, 11, 11, 11, 10]


    def _prepare_dropdowns(self):
        """Create the dropdowns for re-use throughout the workbook."""

        self._dropdown_dataset_type = cellar.CellDropdown(
            workbook=self.workbook,
            values=[
                "Feature Class",
                "Table",
            ],
            label="dataset type"
        )

        self._dropdown_geometry_type = cellar.CellDropdown(
            workbook=self.workbook,
            values=xl2st.geometry_types.keys(),
            label="geometry type",
        )

        self._dropdown_horizontal_sr = cellar.CellDropdown(
            workbook=self.workbook,
            values=[
                "3857 (WGS 1984 Web Mercator Auxiliary Sphere)",
                "4326 (GCS WGS 1984)",
            ],
            label="spatial reference",
            user_fill_in=True,
            message="A user-defined value has been entered for the spatial reference. The format is the numeric WKID followed by an optional text label.", #pylint: disable=line-too-long
        )

        self._dropdown_boolean = cellar.get_dropdown_boolean(self.workbook)


    def _create_template(self, visible: bool = False):
        super()._create_template(visible)

        # Populate with empty data
        self.populate_base_info(dataset_name=self.TEMPLATE_TITLE)

        field_writer = self.field_adder(self.TEMPLATE_TITLE)
        with field_writer:
            for idx in range(50):
                del idx
                field_writer.add_entry(None)

        subtype_writer = self.subtype_adder(self.TEMPLATE_TITLE, None,
                                            fields_table_coordinates=field_writer.coordinates)
        with subtype_writer:
            for idx in range(20):
                del idx
                subtype_writer.add_entry(None, None)

        relationship_writer = self.in_relationships_adder(self.TEMPLATE_TITLE)
        with relationship_writer:
            for idx in range(2):
                del idx
                relationship_writer.add_entry(None)


    #pylint: disable=too-many-locals,too-many-arguments
    def populate_base_info(self, dataset_name:str, schema:str=None, alias:str=None, feature_dataset_name:str=None,
                           summary:str=None, dataset_type:str=None, oid_is_64:str=None, is_archived:str=None,
                           is_versioned:str=None, dsid:str=None, geometry_type:str=None,
                           horizontal_spatial_ref:str=None, vertical_spatial_ref:str=None, has_m:str=None,
                           has_z:str=None):
        """Populate the base information about the dataset.

        Args:
            dataset_name (str): Dataset's base name.
            schema (str, optional): Schema in which the dataset participates. Defaults to None.
            alias (str, optional): Alternate name. Defaults to None.
            feature_dataset_name (str, optional): Name of the feature dataset in which the dataset participates. Defaults to None.
            summary (str, optional): Metadata summary description. Defaults to None.
            dataset_type (str, optional): Type of dataset (e.g. Feature Class, Table). Defaults to None.
            oid_is_64 (str, optional): Whether dataset used 64-bit object IDs. Defaults to None.
            is_archived (str, optional): Whether archival is enabled. Defaults to None.
            is_versioned (str, optional): Whether versioning is enabled. Defaults to None.
            dsid (str, optional): Dataset's unique ID. Defaults to None.
            geometry_type (str, optional): Type of geometry (e.g. Point). Only applies to feature classes. Defaults to None.
            horizontal_spatial_ref (str, optional): Description of the horizontal spatial reference. Only applies to feature classes. Defaults to None.
            vertical_spatial_ref (str, optional): Description of the vertical spatial reference. Only applies to feature classes. Defaults to None.
            has_m (str, optional): Whether m-values are enabled. Defaults to None.
            has_z (str, optional): Whether vertical values are enabled. Defaults to None.
        """ #pylint: disable=line-too-long

        cw = self.cw_lookup[dataset_name]

        force_feature_class_attributes = False
        if dataset_name == self.TEMPLATE_TITLE:
            dataset_name = None
            force_feature_class_attributes = True

        coordinates = cw.write_block(value_block=[
            [
                #empty row
            ], [
                "Name",
                (dataset_name, cellar.CELL_RULE_TEXT_MIN_3),
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Schema",
                schema,
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Alias",
                alias,
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Feature Dataset",
                feature_dataset_name,
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Summary",
                (summary, cellar.CELL_OPTS_WRAP),
                cellar.MERGE_CELL_WITH_LEFT,
            ],
        ], default_cell_options=[
            cellar.CELL_OPTS_KEY,
            cellar.CELL_OPTS_TEXT,
        ])

        row_with_summary = coordinates[1][0]
        cw.increase_basic_height(row_with_summary, factor=2)

        coordinates = cw.write_block(value_block=[
            [
                "Dataset Type",
                (dataset_type, cellar.CELL_RULE_NOT_BLANK, self._dropdown_dataset_type),
                cellar.MERGE_CELL_WITH_LEFT,
            ],
        ], default_cell_options=[
            cellar.CELL_OPTS_KEY,
            cellar.CELL_OPTS_TEXT,
        ])

        if geometry_type or force_feature_class_attributes:

            # Spatial reference starts with a number for the WKID
            spatial_ref_valid = cellar.CellRule(
                formula="AND(ISBLANK(<coordinate>) = FALSE, ISNUMBER(VALUE(LEFT(<coordinate>, 4))) = FALSE)"
            )
            # Horizontal spatial reference shouldn't be empty if vertical coordinate system specified
            rule_hsr_not_empty_if_vcs = cellar.CellRule(
                formula="AND(ISBLANK(OFFSET(<coordinate>, 1, 0)) = FALSE, ISBLANK(<coordinate>))"
            )

            cw.write_block(value_block=[
                [
                    "Geometry Type",
                    (geometry_type, cellar.CELL_RULE_NOT_BLANK, self._dropdown_geometry_type),
                    cellar.MERGE_CELL_WITH_LEFT,
                ], [
                    "Horizontal Spatial Ref.",
                    (horizontal_spatial_ref, spatial_ref_valid, rule_hsr_not_empty_if_vcs,
                     self._dropdown_horizontal_sr),
                    cellar.MERGE_CELL_WITH_LEFT,
                ], [
                    "Vertical Spatial Ref.",
                    (vertical_spatial_ref, spatial_ref_valid),
                    cellar.MERGE_CELL_WITH_LEFT,
                ], [
                    "Has M-Values",
                    (has_m, self._dropdown_boolean),
                    cellar.MERGE_CELL_WITH_LEFT,
                ], [
                    "Has Z-Values",
                    (has_z, self._dropdown_boolean),
                    cellar.MERGE_CELL_WITH_LEFT,
                ],
            ], default_cell_options=[
                cellar.CELL_OPTS_KEY,
                cellar.CELL_OPTS_TEXT,
            ])

        cw.write_block(value_block=[
            [
                "64-bit OID",
                (oid_is_64, self._dropdown_boolean),
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Is Archived",
                (is_archived, self._dropdown_boolean),
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Is Versioned",
                (is_versioned, self._dropdown_boolean),
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "DSID",
                (dsid, cellar.CELL_OPTS_INTEGER_LEFT),
                cellar.MERGE_CELL_WITH_LEFT,
            ],
        ], default_cell_options=[
            cellar.CELL_OPTS_KEY,
            cellar.CELL_OPTS_TEXT,
        ])


    def in_relationships_adder(self, base_name:str) -> InRelationshipsWriter:
        """Returns an instance of InRelationshipsWriter initialized for a particular dataset.

        Args:
            base_name (str): Base name of the feature class, table, or relationship class.

        Returns:
            InRelationshipsWriter: In-Relationships writer initialized for that dataset.
        """
        return InRelationshipsWriter(
            workbook=self.workbook,
            cw=self.cw_lookup[base_name],
            get_cross_workbook_name=self.get_cross_workbook_name,
            get_cross_workbook_sheet_name=self.get_cross_workbook_sheet_name,
        )