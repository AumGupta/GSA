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

## API

The project exposes a RESTful API built with **FastAPI**.
The API acts as the communication layer between the PostgreSQL/PostGIS database and the frontend application, allowing spatial analysis, accessibility evaluation, routing, and user feedback storage.

The API is organized into three main components:

```
API/
│── routers/
│── db/
│── main.py
```

---

### 1. `main.py`

`main.py` is the application entry point.
It initializes the FastAPI application and registers all routers under the `/api/v1` prefix.

Its responsibilities include:

* Creating the FastAPI app instance
* Including all API routers
* Exposing the endpoints to the web server (Uvicorn)

---

### 2. `db/`

The `db` module manages the connection with the PostgreSQL database.

It provides:

* Database engine configuration
* Session management
* Dependency injection (`get_db`) used by the routers

All endpoints access the database through this module, ensuring that connections are opened and closed safely during each request.

---

### 3. `routers/`

The `routers` directory contains the API endpoints grouped by functionality.
Each router defines specific operations and queries executed on the PostGIS database.

#### a. `spatial` (GET)

Provides basic spatial queries.
It receives geographic coordinates (latitude and longitude) and retrieves nearby green areas from the database.

Main functionality:

* Query green areas
* Spatial filtering using PostGIS geometry operations

---

#### b. `accessibility` (GET)

Calculates the **green space accessibility index** for a given location.

The endpoint analyzes green areas within a specified buffer distance and computes multiple indicators:

* **Proximity score** – distance to the nearest green area
* **Quantity score** – number of green areas in range
* **Area score** – total surface of accessible green areas
* **Diversity score** – variation of green area types

This module performs spatial analysis directly in PostGIS and returns a structured JSON response with the computed indicators.

---

#### c. `routing` (GET)

Computes the walking route from a user location to the nearest green area.

The routing process uses **pgRouting** and the OpenStreetMap road network stored in the database.

Steps performed:

1. Snap the user coordinates to the closest network vertex
2. Identify the nearest green area
3. Snap the park centroid to the road network
4. Calculate the shortest path using Dijkstra’s algorithm
5. Return the route as GeoJSON

The endpoint returns:

* Destination park name
* Route distance (meters)
* Connectivity status
* Route geometry (GeoJSON LineString)

---

#### d. `feedback` (POST)

Stores user feedback and calculated accessibility results.

The endpoint receives a JSON payload from the frontend and inserts it into the database.
This allows the application to keep a record of user interactions and computed scores.

---

## Request/Response Format

All endpoints communicate using JSON.
Spatial outputs such as routes are returned in **GeoJSON format**, making them directly compatible with web mapping libraries such as Leaflet or Mapbox GL JS.

---

## Summary

The API integrates:

* **FastAPI** → request handling
* **PostgreSQL/PostGIS** → spatial database
* **pgRouting** → network analysis

It serves as the analytical backend of the application, providing spatial queries, accessibility evaluation, routing computation, and persistent user feedback storage.

## How to Run the Project Locally

This section explains how to set up and execute the Green Space Accessibility (GSA) API on a local machine.

---

### 1. Requirements

Install the following software before starting:

* **Miniconda** (Python environment manager)
* **PostgreSQL** (v14 or newer recommended)
* **PostGIS** extension
* **pgRouting** extension
* **Git**

You can verify installations:

```bash
python --version
psql --version
conda --version
```

---

### 2. Clone the Repository

```bash
git clone https://github.com/AumGupta/GSA.git
cd GSA
```

---

### 3. Create the Conda Environment

The project uses **Miniconda** to manage dependencies.

Create and activate the environment:

```bash
conda create -n gsa_env python=3.10
conda activate gsa_env
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file in the root directory of the project:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=green_accessibility
DB_USER=postgres
DB_PASSWORD=your_password
```

The API reads these values to connect to the PostgreSQL database.

---

### 5. Create and Prepare the Database

Open PostgreSQL (psql or PgAdmin) and create the database:

```sql
CREATE DATABASE green_accessibility;
\c green_accessibility;

CREATE EXTENSION postgis;
CREATE EXTENSION pgrouting;
```

---

### 6. Load Spatial Data

You must populate the database with OpenStreetMap data.

1. Download a `.osm.pbf` file (e.g., Portugal or Lisbon) from Geofabrik.
2. Import the road network using `osm2pgrouting` (creates `ways` and `vertices` tables).
3. Run the ETL scripts included in the repository to generate the `green_areas` table.

After loading data, create spatial indexes:

```sql
CREATE INDEX idx_green_geom ON green_areas USING GIST(geometry);
CREATE INDEX idx_vertices_geom ON vertices USING GIST(geometry);
CREATE INDEX idx_ways_geom ON ways USING GIST(geometry);
```

---

### 7. Run the API

Start the FastAPI server:

```bash
uvicorn API.main:app --reload
```

If successful, the terminal will display:

```
Uvicorn running on http://127.0.0.1:8000
```

---

### 8. API Documentation

FastAPI automatically provides interactive documentation:

* Swagger UI → http://127.0.0.1:8000/docs
* ReDoc → http://127.0.0.1:8000/redoc

You can test all endpoints directly from the browser.

---

### 9. Example Requests

**Nearest green areas**

```
http://127.0.0.1:8000/api/v1/spatial/green-area?lat=38.7385&lon=-9.1324
```

**Accessibility index**

```
http://127.0.0.1:8000/api/v1/accessibility/index?lat=38.7385&lon=-9.1324
```

**Route to nearest park**

```
http://127.0.0.1:8000/api/v1/routing/to-nearest-park?lat=38.7385&lon=-9.1324
```

**Send feedback (POST)**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/feedback \
     -H "Content-Type: application/json" \
     -d '{"user_id":"test","message":"example feedback"}'
```

---

### 10. Troubleshooting

**Error: `Could not import module "main"`**

* Make sure you are inside the project root directory
* Confirm the file path `API/main.py` exists

**Database connection error**

* Verify PostgreSQL is running
* Check credentials in `.env`

**Routing takes too long**

* Ensure `ways.cost` is measured in meters
* Confirm spatial indexes exist on geometries

---

### Summary

To run the project locally:

1. Create the Conda environment
2. Prepare the PostGIS + pgRouting database
3. Load OSM and green area data
4. Start the FastAPI server
5. Test endpoints using the browser documentation

The API will then be available at:

```
http://127.0.0.1:8000/api/v1/
```


## Team
[**Om Gupta**](https://github.com/AumGupta) & [**Santiago José Lara**](https://github.com/SLara24)
