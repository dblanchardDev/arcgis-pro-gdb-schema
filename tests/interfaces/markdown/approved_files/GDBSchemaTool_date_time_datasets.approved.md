# Datasets

> **Source Information**
>
> - **Database Name**: GDBSchemaTool
> - **Workspace Type**: Local Database
> - **Remote Server**:
> - **Summary**: This is a geodatabase to test the GDB Schema Tools.

[Buildings](#buildings)  
[Inspections](#inspections)  
[Lakes](#lakes)  
[Rivers](#rivers)  
[StreetCentreline](#streetcentreline)  
[Trees](#trees)  

---

## Buildings

- **Name**: Buildings
- **Schema**:
- **Alias**: Buildings
- **Feature Dataset**:
- **Summary**:
- **Dataset Type**: Feature Class
- **Geometry Type**: Polygon
- **Horizontal Spatial Ref.**: 54030 (World Robinson)
- **Vertical Spatial Ref.**:
- **Has M-Values**: no
- **Has Z-Values**: no
- **64-bit OID**: no
- **Is Archived**: no
- **Is Versioned**: no

### Fields (Buildings)

| Field Name | Field Type | Summary | Alias Name | Domain Name | Default Value | Is Nullable | Length | Precision | Scale |
|------------|------------|---------|------------|-------------|---------------|-------------|--------|-----------|-------|
| OBJECTID | OBJECTID |  | OBJECTID |  |  | no |  |  |  |
| Shape | Geometry |  | SHAPE |  |  | yes |  |  |  |
| Classification | Short Integer |  | Classification |  | 0 | no |  | 0 |  |
| Type | Text |  | Type |  |  | no | 3 |  |  |
| Name | Text |  | Name |  |  | yes | 100 |  |  |
| Built | Date Only |  | Build Date |  |  | yes |  |  |  |
| UUID | GUID |  | Building Unique ID |  |  | no |  |  |  |
| OpeningHour | Time Only |  | Opening Hour |  |  | yes |  |  |  |
| ClosingHour | Time Only |  | Closing Hour |  |  | yes |  |  |  |

### Subtype (Buildings)

- **Subtype Field Name**: Classification

| Subtype Name | Code | Description | Field Name | Domain Name | Default Value |
|--------------|------|-------------|------------|-------------|---------------|
| General | 0 | Residential, multi-use, or otherwise unclassified buildings. | Type | [Buidling - General](./GDBSchemaTool_date_time_domains.approved.md#buidling---general) | OTH |
| Commercial | 1 | Buildings from which a non-industrial business operates such as offices, retail, restaurants, and entertainment venues. | Type | [Building - Commercial](./GDBSchemaTool_date_time_domains.approved.md#building---commercial) |  |
| Industrial | 2 | Manufacturing and warehousing facilities. | Type | [Building - Industrial](./GDBSchemaTool_date_time_domains.approved.md#building---industrial) |  |
| Government | 3 |  | Type | [Building - Government](./GDBSchemaTool_date_time_domains.approved.md#building---government) |  |
| Government | 3 |  | OpeningHour | [Office Hours](./GDBSchemaTool_date_time_domains.approved.md#office-hours) | 08:30:00 |
| Government | 3 |  | ClosingHour | [Office Hours](./GDBSchemaTool_date_time_domains.approved.md#office-hours) | 16:30:00 |

### Relationship Classes (Buildings)

- [Building_Inspections](./GDBSchemaTool_date_time_relationships.approved.md#building_inspections)

---

## Inspections

- **Name**: Inspections
- **Schema**:
- **Alias**: Inspections
- **Feature Dataset**:
- **Summary**:
- **Dataset Type**: Table
- **64-bit OID**: no
- **Is Archived**: no
- **Is Versioned**: no

### Fields (Inspections)

| Field Name | Field Type | Summary | Alias Name | Domain Name | Default Value | Is Nullable | Length | Precision | Scale |
|------------|------------|---------|------------|-------------|---------------|-------------|--------|-----------|-------|
| OBJECTID | OBJECTID |  | OBJECTID |  |  | no |  |  |  |
| BuildingUUID | GUID |  | Building Unique ID |  |  | no |  |  |  |
| InspectedOn | Date |  | Inspected On |  |  | no |  |  |  |
| InspectedBy | Text |  | Inspected By |  |  | no | 50 |  |  |

### Relationship Classes (Inspections)

- [Building_Inspections](./GDBSchemaTool_date_time_relationships.approved.md#building_inspections)

---

## Lakes

- **Name**: Lakes
- **Schema**:
- **Alias**: Lakes
- **Feature Dataset**: Water
- **Summary**:
- **Dataset Type**: Feature Class
- **Geometry Type**: Polygon
- **Horizontal Spatial Ref.**: 3857 (WGS 1984 Web Mercator Auxiliary Sphere)
- **Vertical Spatial Ref.**:
- **Has M-Values**: no
- **Has Z-Values**: yes
- **64-bit OID**: no
- **Is Archived**: no
- **Is Versioned**: no

### Fields (Lakes)

| Field Name | Field Type | Summary | Alias Name | Domain Name | Default Value | Is Nullable | Length | Precision | Scale |
|------------|------------|---------|------------|-------------|---------------|-------------|--------|-----------|-------|
| OBJECTID | OBJECTID |  | OBJECTID |  |  | no |  |  |  |
| Shape | Geometry |  | SHAPE |  |  | yes |  |  |  |
| Name | Text |  | Name |  |  | yes | 100 |  |  |
| RiverID | Long Integer |  | River ID |  |  | yes |  | 0 |  |

### Relationship Classes (Lakes)

- [Rivers_and_Lakes](./GDBSchemaTool_date_time_relationships.approved.md#rivers_and_lakes)

---

## Rivers

- **Name**: Rivers
- **Schema**:
- **Alias**: Rivers
- **Feature Dataset**: Water
- **Summary**:
- **Dataset Type**: Feature Class
- **Geometry Type**: Polyline
- **Horizontal Spatial Ref.**: 3857 (WGS 1984 Web Mercator Auxiliary Sphere)
- **Vertical Spatial Ref.**:
- **Has M-Values**: no
- **Has Z-Values**: yes
- **64-bit OID**: no
- **Is Archived**: no
- **Is Versioned**: no

### Fields (Rivers)

| Field Name | Field Type | Summary | Alias Name | Domain Name | Default Value | Is Nullable | Length | Precision | Scale |
|------------|------------|---------|------------|-------------|---------------|-------------|--------|-----------|-------|
| OBJECTID | OBJECTID |  | OBJECTID |  |  | no |  |  |  |
| Shape | Geometry |  | SHAPE |  |  | yes |  |  |  |
| RiverID | Long Integer |  | River ID |  |  | yes |  | 0 |  |
| Name | Text |  | Name |  |  | yes | 100 |  |  |

### Relationship Classes (Rivers)

- [Rivers_and_Lakes](./GDBSchemaTool_date_time_relationships.approved.md#rivers_and_lakes)

---

## StreetCentreline

- **Name**: StreetCentreline
- **Schema**:
- **Alias**: Street Centreline
- **Feature Dataset**:
- **Summary**: This is a description of the street centrelines that are contained within this feature class.
- **Dataset Type**: Feature Class
- **Geometry Type**: Polyline
- **Horizontal Spatial Ref.**: 3857 (WGS 1984 Web Mercator Auxiliary Sphere)
- **Vertical Spatial Ref.**:
- **Has M-Values**: yes
- **Has Z-Values**: yes
- **64-bit OID**: no
- **Is Archived**: no
- **Is Versioned**: no

### Fields (StreetCentreline)

| Field Name | Field Type | Summary | Alias Name | Domain Name | Default Value | Is Nullable | Length | Precision | Scale |
|------------|------------|---------|------------|-------------|---------------|-------------|--------|-----------|-------|
| OBJECTID | OBJECTID |  | OBJECTID |  |  | no |  |  |  |
| Shape | Geometry |  | SHAPE |  |  | yes |  |  |  |
| GlobalID | Global ID |  | GlobalID |  |  | no |  |  |  |
| StreetName | Text |  | Street Name |  |  | no | 100 |  |  |
| StreetType | Text |  | Street Type | [Street Types](./GDBSchemaTool_date_time_domains.approved.md#street-types) |  | no | 4 |  |  |
| Municipality | Text |  | Municipality |  |  | yes | 50 |  |  |
| Speed | Short Integer |  | Speed Limit | [Valid Speed Limits](./GDBSchemaTool_date_time_domains.approved.md#valid-speed-limits) |  | yes |  | 0 |  |

---

## Trees

- **Name**: Trees
- **Schema**:
- **Alias**: Trees
- **Feature Dataset**:
- **Summary**: A summary about the tree feature class. This is a points feature class.
- **Dataset Type**: Feature Class
- **Geometry Type**: Point
- **Horizontal Spatial Ref.**: 3857 (WGS 1984 Web Mercator Auxiliary Sphere)
- **Vertical Spatial Ref.**:
- **Has M-Values**: no
- **Has Z-Values**: no
- **64-bit OID**: no
- **Is Archived**: no
- **Is Versioned**: no

### Fields (Trees)

| Field Name | Field Type | Summary | Alias Name | Domain Name | Default Value | Is Nullable | Length | Precision | Scale |
|------------|------------|---------|------------|-------------|---------------|-------------|--------|-----------|-------|
| OBJECTID | OBJECTID |  | OBJECTID |  |  | no |  |  |  |
| Shape | Geometry |  | SHAPE |  |  | yes |  |  |  |
| Height | Float | Height of the tree in meters. | Height | [Tree Height](./GDBSchemaTool_date_time_domains.approved.md#tree-height) | 0.6499999761581421 | yes |  | 0 | 0 |
| Diameter | Double | The diameter of the tree's crown. | Diameter | [Tree Diameter](./GDBSchemaTool_date_time_domains.approved.md#tree-diameter) |  | yes |  | 0 | 0 |
