# Geodatabase Structure Classes

The geodatabase structure is used as the middle-man between a reader and a writer, storing the complete geodatabase structure in a standard format.

Interface readers must create a geodatabase structure instance from their source, and interface writers must read from a geodatabase structure to produce their output.

All classes, methods, and properties are documented with Python docstrings. The organization of the classes is documented below to provide an overview.

> ℹ **Note regarding editability**
> The structure was primarily created to allow creation of a Geodatabase instance from a known structure. Editing the properties or the structure of an existing Geodatabase instance isn't fully supported.

```mermaid
classDiagram
    direction LR

    class Geodatabase{
        VALID_NAME_REGEX*
        WORKSPACE_TYPES*

        name
        meta_summary
        server
        workspace_type
    }
    Geodatabase ..* Domain : domains
    Geodatabase ..* FeatureDataset : feature_datasets
    Geodatabase ..* Dataset : datasets
    Geodatabase ..* Table : datasets.tables
    Geodatabase ..* FeatureClass : datasets.feature_classes
    Geodatabase ..* Relationship : datasets.relationship_classes


    class Domain {
        VALID_NAME_REGEX*
        FIELD_TYPES*
        DOMAIN_TYPES*
        SPLIT_POLICIES*
        MERGE_POLICIES*

        name
        schema
        description
        field_type
        domain_type
        split_policy
        merge_policy
    }
    Domain ..> Geodatabase : geodatabase
    Domain ..* Field : fields

    class RangeDomain {
        minimum
        maximum
        test_value(value)
    }
    Domain <|-- RangeDomain

    class CodedDomain {
        test_value(value)
        convert_value(value)
    }
    Domain <|-- CodedDomain
    CodedDomain ..o CodeDescription : codes


    class FeatureDataset {
        VALID_NAME_REGEX*

        name
        schema
        meta_summary
    }
    FeatureDataset ..> Geodatabase : geodatabase
    FeatureDataset ..* Dataset : datasets


    class Dataset {
        VALID_NAME_REGEX*
        DATASET_TYPES*
        FIELD_TYPE_EXCLUSIONS*

        dataset_type
        schema
        is_archived
        is_versioned
        dsid
        meta_summary
        oid_is_64
    }
    Dataset ..> Geodatabase : geodatabase
    Dataset ..> FeatureDataset : feature_dataset
    Dataset ..* Field : fields
    Dataset ..> Subtype : subtype

    class Table {
        alias
    }
    Dataset <|-- Table
    Table ..* Relationship : relationship_classes

    class FeatureClass {
        GEOMETRY_TYPES*
       *
        geometry_type
        spatial_ref
        has_m
        has_z
    }
    Table <|-- FeatureClass

    class Relationship {
        RELATIONSHIP_TYPES*
        NOTIFICATIONS*
        CARDINALITIES*

        forward_label
        backward_label
        cardinality
        notification
        relationship_type
        attributed
    }
    Dataset <|-- Relationship
    Relationship ..> RelationshipMember : origin
    Relationship ..> RelationshipMember : destination

    class RelationshipMember {
        primary_key
        foreign_key
    }
    RelationshipMember ..> Table : table


    class Field {
        VALID_NAME_REGEX*
        FIELD_TYPES*

        name
        field_type
        precision
        scale
        length
        alias
        nullable
        required
        default
        meta_summary
    }
    Field ..> Domain : domain
    Field ..> Dataset : dataset


    class Subtype {
        default
    }
    Subtype ..> Dataset : dataset
    Subtype ..o SubtypeProperties : codes

    class SubtypeProperties {
        description
        meta_summary
    }
    SubtypeProperties ..* SubtypeFieldProperties : field_props

    
    class SubtypeFieldProperties {
        name
        default
    }
    SubtypeFieldProperties ..> Field : field
    SubtypeFieldProperties ..> Domain : domain

```

---

## Legend

```mermaid
classDiagram
    direction LR
    class Source {
        CLASS_CONSTANT*
        property
        method(parameter)
    }

    class Inheritor ["The class inherits the properties and methods of the source."]
    <<Inheritance>> Inheritor
    Source <|-- Inheritor

    class Property ["Property in source which provides access\nto a single instance of another class."]
    <<Property>> Property
    Source ..> Property : property_name

    class SequenceAccessor ["Property which provides access to multiple classes. Behaves like a list but\nwith 2 additions: a new() method to create a new member; and the ability to\naccess members by name like one would with a dictionary."]
    <<Sequence_Accessor>> SequenceAccessor
    SequenceAccessor : new(...) create a new instance within the accessor
    Source ..* SequenceAccessor : property_name

    class DictionaryAccessor ["Property which provides access to multiple classes. Behaves like a dictionary but\nwith 1 additions: a new() method to create a new member."]
    <<Dictionary_Accessor>> DictionaryAccessor
    DictionaryAccessor : new(...) create a new instance within the accessor
    Source ..o DictionaryAccessor : property_name
```
