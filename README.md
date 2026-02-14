# <img src="docs/assets/favicon/logo.svg" style="width:24px;"/> [GSA: Green Space Accessibility](https://aumgupta.github.io/GSA/)

![GitHub License](https://img.shields.io/github/license/AumGupta/GSA)
![GitHub repo size](https://img.shields.io/github/repo-size/AumGupta/GSA)
![GitHub deployments](https://img.shields.io/github/deployments/AumGupta/GSA/github-pages)


This repository hosts the source code for the [**GSA**](https://aumgupta.github.io/GSA/) Project, a geospatial web application that evaluates urban green space accessibility by integrating OpenStreetMap data, spatial ETL processing, PostGIS analytics, and an interactive map-based frontend.

> [!note]
> This project is presented for the course "Group Project Seminar on Programming and Analysis".

### Application Architecture

The system follows a three-tier architecture: 
1. **External** data source: OSM OverPass API
2. **Backend** (ETL pipeline, PostGIS-enabled PostgreSQL database, and API)
3. **Frontend** web application

```mermaid
architecture-beta

    group datasource(internet)[External Data Source]
    group backend(cloud)[Backend]
    group etl(server)[ETL] in backend
    group frontend(internet)[Frontend]

    %% External
    service overpass(internet)[Overpass API] in datasource

    %% Backend - ETL
    service extract(cloud)[Extract] in etl
    service transform(server)[Transform] in etl
    service load(disk)[Load] in etl

    %% Backend - Database
    service postgres(database)[PostgreSQL] in backend
    service postgis(disk)[PostGIS] in backend

    %% Backend - API
    service api(server)[Backend API] in backend
    service scoring(server)[Proccessing] in backend

    %% Frontend
    service web(internet)[Web App] in frontend
    service map(server)[Interactive Map] in frontend


    %% Data Flow
    overpass:R --> L:extract

    extract:R --> L:transform
    transform:R --> L:load
    load:B --> T:postgres

    postgis:T --> B:postgres
    postgres:R --> L:api
    api:L --> R:postgres

    api:R <--> L:web


    api:B --> T:scoring
    scoring:T --> B:api
    map:T --> B:web
```


## Database Schema

* **`types`**: A lookup table for green area classifications.
* **`green_areas`**: Stores the polygonal geometry and metadata for parks and forests.
* **`vertices`**: The nodes (intersections) of the routing network.
* **`ways`**: The edges (streets/paths) of the network, including `cost` and `reverse_cost` for pgRouting calculations.

### ER Diagram

```mermaid
erDiagram
    types ||--o{ green_areas : "categorizes"
    vertices ||--o{ ways : "defines source"
    vertices ||--o{ ways : "defines target"

    types {
        INTEGER id PK
        VARCHAR type
    }

    green_areas {
        INTEGER id PK
        BIGINT osm_id
        TEXT name
        INTEGER type_id FK
        GEOMETRY(MultiPolygon) geometry
    }

    vertices {
        INTEGER id PK
        GEOMETRY(Point) geometry
    }

    ways {
        INTEGER id PK
        BIGINT osm_id
        FLOAT length_m
        INTEGER source FK
        INTEGER target FK
        FLOAT cost
        FLOAT reverse_cost
        GEOMETRY(LineString) geometry
    }

```

> [!IMPORTANT]
> The schema includes **GIST (Generalized Search Tree)** indices on all geometry columns to ensure high-performance spatial queries.

## Team
[**Om Gupta**](https://github.com/AumGupta) & [**Santiago José Lara**](https://github.com/SLara24)
