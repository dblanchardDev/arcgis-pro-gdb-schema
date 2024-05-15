"""
Excel writer for the relationships workbook.

Author: David Blanchard
"""

from .. import cellar
from ..excel_converter import xl2st
from .gdb_writer import GDBWriterWithFields


class RelationshipsWriter(GDBWriterWithFields):
    """Excel writer component used specifically for the relationships workbook.

    Args:
        workbook_path (str): Path where the XLSX file will be written, including the extension.
        database_name (str): Name of the geodatabase.
        workspace_type (str, optional): Type of workspace (local or remote). Defaults to None.
        remote_server (str, optional): Address/name of the geodatabase if any. Defaults to None.
        summary (str, optional): Metadata summary about the geodatabase. Defaults to None.
        template_visible (bool, optional): Whether the template sheets (used to create new datasets/domains from
          scratch) are visible.
    """

    element_type = "relationship class"
    _dropdown_relationship_type:cellar.CellDropdown = None
    _dropdown_notifications:cellar.CellDropdown = None
    _dropdown_cardinality:cellar.CellDropdown = None
    _dropdown_boolean:cellar.CellDropdown = None
    _column_widths:list[int] = [25,15,80,25,22,15,12,11,11,11,10]


    def _prepare_dropdowns(self):
        """Create the dropdowns for re-use throughout the workbook."""

        self._dropdown_relationship_type = cellar.CellDropdown(
            workbook=self.workbook,
            values=xl2st.relationship_types.keys(),
            label="relationship type",
        )

        self._dropdown_notifications = cellar.CellDropdown(
            workbook=self.workbook,
            values=xl2st.notifications.keys(),
            label="notifications",
        )

        self._dropdown_cardinality = cellar.CellDropdown(
            workbook=self.workbook,
            values=xl2st.cardinalities.keys(),
            label="cardinality",
        )

        self._dropdown_boolean = cellar.get_dropdown_boolean(self.workbook)


    def _create_template(self, visible:bool=False):
        super()._create_template(visible)

        # Populate with empty data
        self.populate_core_info(self.TEMPLATE_TITLE)

        field_writer = self.field_adder(self.TEMPLATE_TITLE)
        with field_writer:
            for idx in range(10):
                del idx
                field_writer.add_entry(None)

        subtype_writer = self.subtype_adder(self.TEMPLATE_TITLE, None,
                                            fields_table_coordinates=field_writer.coordinates)
        with subtype_writer:
            for idx in range(5):
                del idx
                subtype_writer.add_entry(None, None)


    #pylint: disable=too-many-arguments,too-many-locals
    def populate_core_info(self, relationship_name:str, schema:str=None, feature_dataset_name:str=None,
                           summary:str=None, relationship_type:str=None, origin_table_name:str=None,
                           destination_table_name:str=None, forward_label:str=None, backward_label:str=None,
                           origin_primary_key:str=None, origin_foreign_key:str=None, destination_primary_key:str=None,
                           destination_foreign_key:str=None, notifications:str=None, cardinality:str=None,
                           attributed:str=None, oid_is_64:str=None, is_archived:str=None, is_versioned:str=None,
                           dsid:int=None):
        """Populate the core information about the relationship.

        Args:
            relationship_name (str): Name of the relationship class.
            schema (str, optional): Schema to which the relationship class belongs. Defaults to None.
            feature_dataset_name (str, optional): Name of the feature dataset in which the relationship is contained. Defaults to None.
            summary (str, optional): Metadata summary describing the relationship class. Defaults to None.
            relationship_type (str, optional): Whether simple or composite. Defaults to None.
            origin_table_name (str, optional): Name of the origin table. Defaults to None.
            destination_table_name (str, optional): Name of the destination table. Defaults to None.
            forward_label (str, optional): Label for origin to destination. Defaults to None.
            backward_label (str, optional): Label for destination to origin. Defaults to None.
            origin_primary_key (str, optional): Field in origin table used for relationship ID. Defaults to None.
            origin_foreign_key (str, optional): Field in intermediate table or destination table used for relationship ID. Defaults to None.
            destination_primary_key (str, optional): Field in destination table used for relationship ID in an attributed or many to many relationship. Defaults to None.
            destination_foreign_key (str, optional): Field in intermediate table for destination used in an attributed or many to many relationship. Defaults to None.
            notifications (str, optional): Message/edit propagation. Defaults to None.
            cardinality (str, optional): Whether one-to-one, one-to-many, or many-to-many. Defaults to None.
            attributed (str, optional): Whether the relationship class has attributes. Defaults to None.
            oid_is_64 (str, optional): Whether FID field uses 64-bits. Defaults to None.
            is_archived (str, optional): Whether archiving is enabled. Defaults to None.
            is_versioned (str, optional): Whether versioning is enabled. Defaults to None.
            dsid (int, optional): Dataset's unique ID. Defaults to None.
        """ #pylint: disable=line-too-long

        cw = self.cw_lookup[relationship_name]

        skip_links = False
        if relationship_name == self.TEMPLATE_TITLE:
            relationship_name = None
            skip_links = True

        coordinates = cw.write_block(value_block=[
            [
                # empty row
            ], [
                "Name",
                (relationship_name, cellar.CELL_RULE_TEXT_MIN_3),
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Schema",
                schema,
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

        origin_table_options = None
        destination_table_options = None

        if not skip_links:
            origin_table_options = cellar.make_link_options(
                workbook_name=self.get_cross_workbook_name("datasets"),
                sheet_name=self.get_cross_workbook_sheet_name("datasets", origin_table_name),
            )

            destination_table_options = cellar.make_link_options(
                workbook_name=self.get_cross_workbook_name("datasets"),
                sheet_name=self.get_cross_workbook_sheet_name("datasets", destination_table_name),
            )

        # Rule for Destination keys being filled if attributed or many-to-many
        row_with_cardinality = coordinates[1][0] + 11
        row_with_attributed = coordinates[1][0] + 12
        rule_empty_if_attributed_or_many = cellar.CellRule(
            formula=f'AND(ISBLANK(<coordinate>), OR(B{row_with_cardinality} = "Many to Many", B{row_with_attributed} = "yes"))'
        )
        rule_filled_if_not_attributed_or_many = cellar.CellRule(
            formula=f'AND(ISBLANK(<coordinate>) = FALSE, B{row_with_cardinality} <> "Many to Many", B{row_with_attributed} <> "yes")'
        )

        cw.write_block(start_col=1, value_block=[
            [
                "Relationship Type",
                (relationship_type, cellar.CELL_RULE_NOT_BLANK, self._dropdown_relationship_type),
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Origin Table",
                (origin_table_name, origin_table_options, cellar.CELL_RULE_NOT_BLANK),
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Destination Table",
                (destination_table_name, destination_table_options, cellar.CELL_RULE_NOT_BLANK),
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Forward Label",
                (forward_label, cellar.CELL_RULE_NOT_BLANK),
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Backward Label",
                (backward_label, cellar.CELL_RULE_NOT_BLANK),
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Origin Primary Key",
                (origin_primary_key, cellar.CELL_RULE_NOT_BLANK),
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Origin Foreign Key",
                (origin_foreign_key, cellar.CELL_RULE_NOT_BLANK),
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Destination Primary Key",
                (destination_primary_key, rule_empty_if_attributed_or_many, rule_filled_if_not_attributed_or_many),
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Destination Foreign Key",
                (destination_foreign_key, rule_empty_if_attributed_or_many, rule_filled_if_not_attributed_or_many),
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Notifications",
                (notifications, self._dropdown_notifications),
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Cardinality",
                (cardinality, self._dropdown_cardinality),
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
                "Is Attributed",
                (attributed, self._dropdown_boolean),
                cellar.MERGE_CELL_WITH_LEFT,
            ], [
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