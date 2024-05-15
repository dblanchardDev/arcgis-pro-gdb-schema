# Domains

> **Source Information**
>
> - **Database Name**: GDBSchemaTool
> - **Workspace Type**: Local Database
> - **Remote Server**:
> - **Summary**: This is a geodatabase to test the GDB Schema Tools.

[Buidling - General](#buidling---general)  
[Building - Commercial](#building---commercial)  
[Building - Government](#building---government)  
[Building - Industrial](#building---industrial)  
[Lake River Flow](#lake-river-flow)  
[Office Hours](#office-hours)  
[Street Types](#street-types)  
[Tree Diameter](#tree-diameter)  
[Tree Height](#tree-height)  
[Valid Speed Limits](#valid-speed-limits)  

---

## Buidling - General

- **Name**: Buidling - General
- **Schema**:
- **Description**: General Types of Buildings
- **Field Type**: Text
- **Domain Type**: Coded Value
- **Split Policy**: Default Value
- **Merge Policy**: Default Value

### Coded Values (Buidling - General)

| Code | Description | Summary |
|------|-------------|---------|
| OTH | Other |  |
| MTU | Multi-Use |  |
| REZ | Residential |  |

### Domain Users (Buidling - General)

- [Buildings](./GDBSchemaTool_date_time_datasets.approved.md#buildings)

---

## Building - Commercial

- **Name**: Building - Commercial
- **Schema**:
- **Description**: Types of commercial buildings.
- **Field Type**: Text
- **Domain Type**: Coded Value
- **Split Policy**: Default Value
- **Merge Policy**: Default Value

### Coded Values (Building - Commercial)

| Code | Description | Summary |
|------|-------------|---------|
| OFF | Office |  |
| RET | Retail |  |
| ENT | Entertainment |  |
| RES | Restaurant |  |

### Domain Users (Building - Commercial)

- [Buildings](./GDBSchemaTool_date_time_datasets.approved.md#buildings)

---

## Building - Government

- **Name**: Building - Government
- **Schema**:
- **Description**: Types of government buildings.
- **Field Type**: Text
- **Domain Type**: Coded Value
- **Split Policy**: Default Value
- **Merge Policy**: Default Value

### Coded Values (Building - Government)

| Code | Description | Summary |
|------|-------------|---------|
| GOV | Government Office |  |
| EDU | Educational |  |
| HSP | Hospital |  |
| REC | Recreational |  |

### Domain Users (Building - Government)

- [Buildings](./GDBSchemaTool_date_time_datasets.approved.md#buildings)

---

## Building - Industrial

- **Name**: Building - Industrial
- **Schema**:
- **Description**: Types of industrial buildings.
- **Field Type**: Text
- **Domain Type**: Coded Value
- **Split Policy**: Default Value
- **Merge Policy**: Default Value

### Coded Values (Building - Industrial)

| Code | Description | Summary |
|------|-------------|---------|
| FAC | Factory |  |
| WHR | Warehouse |  |
| SHP | Shipping |  |
| MNT | Maintenance |  |

### Domain Users (Building - Industrial)

- [Buildings](./GDBSchemaTool_date_time_datasets.approved.md#buildings)

---

## Lake River Flow

- **Name**: Lake River Flow
- **Schema**:
- **Description**: Which direction does a river flow into/out of a lake.
- **Field Type**: Text
- **Domain Type**: Coded Value
- **Split Policy**: Default Value
- **Merge Policy**: Default Value

### Coded Values (Lake River Flow)

| Code | Description | Summary |
|------|-------------|---------|
| IN | River flow into lake | The river is exclusively an input to the lake. |
| OUT | River flows out of lake | The river is exclusively an output from the lake. |
| BOTH | River flow into and out of lake | The lake is part of the river, with the river flowing into the lake, then out of the lake to continue. |

### Domain Users (Lake River Flow)

- [Rivers_and_Lakes](./GDBSchemaTool_date_time_relationships.approved.md#rivers_and_lakes)

---

## Office Hours

- **Name**: Office Hours
- **Schema**:
- **Description**: List of valid hours for opening and closings.
- **Field Type**: Time Only
- **Domain Type**: Range
- **Split Policy**: Default Value
- **Merge Policy**: Default Value

### Range Values (Office Hours)

- **Minimum**: 07:00:00
- **Maximum**: 22:00:00

### Domain Users (Office Hours)

- [Buildings](./GDBSchemaTool_date_time_datasets.approved.md#buildings)

---

## Street Types

- **Name**: Street Types
- **Schema**:
- **Description**: List of valid street types to choose from.
- **Field Type**: Text
- **Domain Type**: Coded Value
- **Split Policy**: Duplicate
- **Merge Policy**: Default Value

### Coded Values (Street Types)

| Code | Description | Summary |
|------|-------------|---------|
| AVE | Avenue |  |
| BLVD | Boulevard |  |
| CIR | Circle |  |
| CRES | Crescent |  |
| DR | Drive |  |
| EXPY | Expressway |  |
| HWY | Highway |  |
| LANE | Lane |  |
| PKY | Parkway |  |
| PL | Place |  |
| PROM | Promenade |  |
| RAMP | Ramp |  |
| RD | Road |  |
| RTE | Route |  |
| ST | Street |  |
| WAY | Way |  |

### Domain Users (Street Types)

- [StreetCentreline](./GDBSchemaTool_date_time_datasets.approved.md#streetcentreline)

---

## Tree Diameter

- **Name**: Tree Diameter
- **Schema**:
- **Description**: Valid tree diameters.
- **Field Type**: Double
- **Domain Type**: Range
- **Split Policy**: Default Value
- **Merge Policy**: Default Value

### Range Values (Tree Diameter)

- **Minimum**: 0.05
- **Maximum**: 10.0

### Domain Users (Tree Diameter)

- [Trees](./GDBSchemaTool_date_time_datasets.approved.md#trees)

---

## Tree Height

- **Name**: Tree Height
- **Schema**:
- **Description**: Range of valid tree heights.
- **Field Type**: Float
- **Domain Type**: Range
- **Split Policy**: Geometry Ratio
- **Merge Policy**: Sum Values

### Range Values (Tree Height)

- **Minimum**: 0.25
- **Maximum**: 30.0

### Domain Users (Tree Height)

- [Trees](./GDBSchemaTool_date_time_datasets.approved.md#trees)

---

## Valid Speed Limits

- **Name**: Valid Speed Limits
- **Schema**:
- **Description**: Range of valid speed limits for streets.
- **Field Type**: Short Integer
- **Domain Type**: Range
- **Split Policy**: Default Value
- **Merge Policy**: Default Value

### Range Values (Valid Speed Limits)

- **Minimum**: 5
- **Maximum**: 110

### Domain Users (Valid Speed Limits)

- [StreetCentreline](./GDBSchemaTool_date_time_datasets.approved.md#streetcentreline)
