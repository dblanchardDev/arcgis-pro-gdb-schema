"""Series of tests that can be used to check whether the resulting structure matches the GDBSchemaTool file
geodatabase."""
#pylint: disable=missing-function-docstring

from typing import TYPE_CHECKING

import pytest

from tests.interfaces.data import gdbschematool_gdb_expected as exp

if TYPE_CHECKING:
    from gdbschematools.structures import Datasets, Domain, FeatureClass, Field, Geodatabase, Relationship, Table
    from gdbschematools.structures.accessors.subtype_accessor import SubtypeProperties


class StructureTests:
    """Series of tests that can be used to check whether the resulting structure matches the GDBSchemaTool file
       geodatabase. Simply replace the geodatabase fixture method to return the Geodatabase structure to be tested."""

    @pytest.fixture(scope="module")
    def geodatabase(self, tmpdir_factory) -> "Geodatabase": #pylint: disable=unused-argument
        """Fixture of the Geodatabase structure with all data from the GDBSchemaTool file geodatabase read into it."""
        msg = "Must implement the geodatabase fixture method to return the Geodatabase structure to be tested."
        raise NotImplementedError(msg)
    #region Domains

    @pytest.mark.parametrize("domain_name", list(exp.DOMAINS.keys()))
    def test_domain_exists(self, geodatabase:"Geodatabase", domain_name:str):
        assert geodatabase.domains[domain_name].name == domain_name


    def test_domains_no_extraneous(self, geodatabase:"Geodatabase"):
        unexpected = []
        for domain in geodatabase.domains:
            if domain.name not in exp.DOMAINS:
                unexpected.append(domain.name)

        if unexpected:
            pytest.fail(f"Unexpected domains found in geodatabase >> {unexpected}")


    @pytest.mark.parametrize("domain_name", list(exp.DOMAINS.keys()))
    def test_domain_properties(self, geodatabase:"Geodatabase", domain_name:str):
        props = exp.DOMAINS[domain_name]
        dom:"Domain" = geodatabase.domains[domain_name]

        assert dom.name == domain_name
        assert dom.description == props["description"]
        assert dom.field_type == props["field_type"]
        assert dom.domain_type == props["domain_type"]
        assert dom.split_policy == props["split_policy"]
        assert dom.merge_policy == props["merge_policy"]
        assert dom.schema == props["schema"]

        if dom.domain_type == "RANGE":
            assert dom.minimum == props["minimum"]
            assert dom.maximum == props["maximum"]


    @pytest.mark.parametrize("domain_name", list(exp.CODED_DOMAINS.keys()))
    def test_domain_codes(self, geodatabase:"Geodatabase", domain_name:str):
        expected = exp.CODED_DOMAINS[domain_name]["codes"]
        dom:"Domain" = geodatabase.domains[domain_name]

        assert len(list(dom.codes)) == len(expected)

        for code, props in expected.items():
            assert dom.codes[code].description == props["description"]
            assert dom.codes[code].meta_summary == props["meta_summary"]

    #endregion
    #region Feature Datasets

    def test_feature_datasets_exists(self, geodatabase:"Geodatabase"):
        expected = list(exp.FEATURE_DATASETS.keys())
        expected.sort()

        found = [e.name for e in list(geodatabase.feature_datasets)]
        found.sort()

        assert found == expected


    @pytest.mark.parametrize("feat_dts_name", exp.FEATURE_DATASETS.keys())
    def test_feature_dataset_properties(self, geodatabase:"Geodatabase", feat_dts_name:str):
        expected = exp.FEATURE_DATASETS[feat_dts_name]
        found = geodatabase.feature_datasets[feat_dts_name]

        assert found.schema == expected["schema"]
        #assert found.meta_summary == expected["meta_summary"]

    #endregion
    #region Datasets

    def test_dataset_count(self, geodatabase:"Geodatabase"):
        expected = len(exp.TABLES) + len(exp.FEAT_CLS) + len(exp.REL_CLS)
        assert len(geodatabase.datasets) == expected


    @pytest.mark.parametrize("table_name", list(exp.TABLES.keys()))
    def test_table_properties(self, geodatabase:"Geodatabase", table_name):
        expected = exp.TABLES[table_name]
        table:"Table" = geodatabase.datasets.tables[table_name]

        assert table.name == table_name
        assert table.alias == expected["alias"]
        assert table.is_archived == expected["is_archived"]
        assert table.is_versioned == expected["is_versioned"]
        assert table.oid_is_64 == expected["oid_is_64"]
        assert table.meta_summary == expected["meta_summary"]
        assert (table.feature_dataset is None and expected["feature_dataset"] is None
                or table.feature_dataset.name == expected["feature_dataset"])


    @pytest.mark.parametrize("feat_cl_name", list(exp.FEAT_CLS.keys()))
    def test_feature_class_properties(self, geodatabase:"Geodatabase", feat_cl_name):
        expected = exp.FEAT_CLS[feat_cl_name]
        feat_cl:"FeatureClass" = geodatabase.datasets.feature_classes[feat_cl_name]

        assert feat_cl.name == feat_cl_name
        assert feat_cl.geometry_type == expected["geometry_type"]
        assert feat_cl.spatial_ref.factoryCode == expected["spatial_reference"][0]
        assert (feat_cl.spatial_ref.VCS is None and expected["spatial_reference"][1] is None
                or feat_cl.spatial_ref.VCS.factoryCode == expected["spatial_reference"][1])
        assert feat_cl.has_m == expected["has_m"]
        assert feat_cl.has_z == expected["has_z"]
        assert feat_cl.alias == expected["alias"]
        assert feat_cl.is_archived == expected["is_archived"]
        assert feat_cl.is_versioned == expected["is_versioned"]
        assert feat_cl.oid_is_64 == expected["oid_is_64"]
        assert feat_cl.meta_summary == expected["meta_summary"]
        assert (feat_cl.feature_dataset is None and expected["feature_dataset"] is None
                or feat_cl.feature_dataset.name == expected["feature_dataset"])


    @pytest.mark.parametrize("rel_cl_name", list(exp.REL_CLS.keys()))
    def test_relationship_class_properties(self, geodatabase:"Geodatabase", rel_cl_name:str):
        expected = exp.REL_CLS[rel_cl_name]
        rel_cl:"Relationship" = geodatabase.datasets.relationship_classes[rel_cl_name]

        assert rel_cl.name == rel_cl_name
        assert rel_cl.origin.table.name == expected["origin_table"]
        assert rel_cl.destination.table.name == expected["destination_table"]
        assert rel_cl.forward_label == expected["forward_label"]
        assert rel_cl.backward_label == expected["backward_label"]
        assert rel_cl.cardinality == expected["cardinality"]
        assert rel_cl.notification == expected["notification"]
        assert rel_cl.relationship_type == expected["relationship_type"]
        assert rel_cl.attributed == expected["attributed"]
        assert rel_cl.origin.primary_key == expected["origin_primary_key"]
        assert rel_cl.destination.primary_key == expected["destination_primary_key"]
        assert rel_cl.origin.foreign_key == expected["origin_foreign_key"]
        assert rel_cl.destination.foreign_key == expected["destination_foreign_key"]
        assert rel_cl.schema == expected["schema"]
        assert rel_cl.is_archived == expected["is_archived"]
        assert rel_cl.is_versioned == expected["is_versioned"]
        assert rel_cl.oid_is_64 == expected["oid_is_64"]
        assert rel_cl.meta_summary == expected["meta_summary"]
        assert getattr(rel_cl.feature_dataset, "name", None) == expected["feature_dataset"]

    #endregion
    #region Fields


    def get_field_list(self, dataset:"Datasets") -> list[str]:
        found = []
        try:
            found = list(dataset.fields)
        except AttributeError as exc:
            if dataset.dataset_type == "RelationshipClass" and dataset.attributed is False:
                pass # Non-attributed relationships don't have fields
            else:
                raise exc

        return found


    @pytest.mark.parametrize("dts_name", exp.DATASETS.keys())
    def test_dataset_field_count(self, geodatabase:"Geodatabase", dts_name:str):
        expected = len(exp.DATASETS[dts_name]["fields"])
        dataset:"Datasets" = geodatabase.datasets[dts_name]
        found = len(self.get_field_list(dataset))

        assert found == expected


    @pytest.mark.parametrize("dts_name", exp.DATASETS.keys())
    def test_dataset_field_order(self, geodatabase:"Geodatabase", dts_name:str):
        expected = list(exp.DATASETS[dts_name]["fields"].keys())
        dataset:"Datasets" = geodatabase.datasets[dts_name]
        found = [f.name for f in self.get_field_list(dataset)]

        assert found == expected


    @pytest.mark.parametrize("dts_name, field_name", exp.FIELDS_WITH_DATASET)
    def test_dataset_field_properties(self, geodatabase:"Geodatabase", dts_name:str, field_name:str):
        expected = exp.DATASETS[dts_name]["fields"][field_name]
        found:"Field" = geodatabase.datasets[dts_name].fields[field_name]

        assert found.name == field_name
        assert found.field_type == expected["field_type"]
        assert found.precision == expected["precision"]
        assert found.scale == expected["scale"]
        assert found.length == expected["length"]
        assert found.alias == expected["alias"]
        assert found.nullable == expected["nullable"]
        assert found.required == expected["required"]
        assert found.default == expected["default"]
        assert getattr(found.domain, "name", None) == expected["domain"]
        assert found.meta_summary == expected["meta_summary"]

    #endregion
    #region Subtypes

    @pytest.mark.parametrize("dataset_name", exp.DATASETS_WITH_SUBTYPES.keys())
    def test_subtypes_properties(self, geodatabase:"Geodatabase", dataset_name:str):
        dataset:"Datasets" = geodatabase.datasets[dataset_name]
        expected = exp.DATASETS[dataset_name]["subtypes"]

        assert dataset.subtype.field.name == expected["field"]
        assert dataset.subtype.default == expected["default"]


    @pytest.mark.parametrize("dataset_name", exp.DATASETS_WITH_SUBTYPES.keys())
    def test_subtypes_code_list(self, geodatabase:"Geodatabase", dataset_name:str):
        dataset:"Datasets" = geodatabase.datasets[dataset_name]
        expected = exp.DATASETS[dataset_name]["subtypes"]
        assert list(dataset.subtype.codes) == list(expected["codes"].keys())


    @pytest.mark.parametrize("dataset_name,code", exp.DATASETS_WITH_SUBTYPE_CODES)
    def test_subtypes_code_properties(self, geodatabase:"Geodatabase", dataset_name:str, code:int):
        expected = exp.DATASETS_WITH_SUBTYPES[dataset_name]["subtypes"]["codes"][code]
        found:"SubtypeProperties" = geodatabase.datasets[dataset_name].subtype.codes[code]

        assert found.description == expected["description"]
        assert found.meta_summary == expected["meta_summary"]


    @pytest.mark.parametrize("dataset_name,code", exp.DATASETS_WITH_SUBTYPE_CODES)
    def test_subtypes_code_field_props(self, geodatabase:"Geodatabase", dataset_name:str, code:int):
        expected = exp.DATASETS_WITH_SUBTYPES[dataset_name]["subtypes"]["codes"][code]
        found:"SubtypeProperties" = geodatabase.datasets[dataset_name].subtype.codes[code]

        expected_field_names = list(expected["fields"].keys())
        expected_field_names.sort()

        found_field_names = [fp.field.name for fp in found.field_props]
        found_field_names.sort()

        assert expected_field_names == found_field_names

        for field_name, field_details in expected["fields"].items():
            subtype_field_props = found.field_props[field_name]

            assert subtype_field_props.default == field_details["default"]
            if subtype_field_props.domain:
                assert subtype_field_props.domain.name == field_details["domain"]
            else:
                assert field_details["domain"] is None

    #endregion