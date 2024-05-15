# Relationship Classes

> **Source Information**
>
> - **Database Name**: GDBSchemaTool
> - **Workspace Type**: Local Database
> - **Remote Server**:
> - **Summary**: This is a geodatabase to test the GDB Schema Tools.

[Building_Inspections](#building_inspections)  
[Rivers_and_Lakes](#rivers_and_lakes)  

---

## Building_Inspections

- **Name**: Building_Inspections
- **Schema**:
- **Feature Dataset**:
- **Summary**: Links buildings to their inspections.
- **Relationship Type**: Composite
- **Origin Table**: [Buildings](./GDBSchemaTool_date_time_datasets.approved.md#buildings)
- **Destination Table**: [Inspections](./GDBSchemaTool_date_time_datasets.approved.md#inspections)
- **Forward Label**: Inspections
- **Backward Label**: Building
- **Origin Primary Key**: UUID
- **Origin Foreign Key**: BuildingUUID
- **Destination Primary Key**:
- **Destination Foreign Key**:
- **Notifications**: Forward
- **Cardinality**: One To Many
- **Is Attributed**: no
- **64-bit OID**: no
- **Is Archived**: no
- **Is Versioned**: no

---

## Rivers_and_Lakes

- **Name**: Rivers_and_Lakes
- **Schema**:
- **Feature Dataset**: Water
- **Summary**: Connection between rivers and lakes that flow into each other.
- **Relationship Type**: Simple
- **Origin Table**: [Rivers](./GDBSchemaTool_date_time_datasets.approved.md#rivers)
- **Destination Table**: [Lakes](./GDBSchemaTool_date_time_datasets.approved.md#lakes)
- **Forward Label**: Lakes Along
- **Backward Label**: River Connection
- **Origin Primary Key**: RiverID
- **Origin Foreign Key**: RiverID
- **Destination Primary Key**: RiverID
- **Destination Foreign Key**: LakesRiverID
- **Notifications**: None
- **Cardinality**: One To Many
- **Is Attributed**: yes
- **64-bit OID**: no
- **Is Archived**: no
- **Is Versioned**: no

### Fields (Rivers_and_Lakes)

| Field Name | Field Type | Summary | Alias Name | Domain Name | Default Value | Is Nullable | Length | Precision | Scale |
|------------|------------|---------|------------|-------------|---------------|-------------|--------|-----------|-------|
| RiverID | Long Integer |  | RiverID |  |  | yes |  | 0 |  |
| LakesRiverID | Long Integer |  | LakesRiverID |  |  | yes |  | 0 |  |
| RID | OBJECTID |  | RID |  |  | no |  |  |  |
| FlowDirection | Text | Whether the river flows into or out of the lake (or both). | Flow Direction | [Lake River Flow](./GDBSchemaTool_date_time_domains.approved.md#lake-river-flow) |  | yes | 4 |  |  |
