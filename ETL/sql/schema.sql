CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgrouting;

DROP TABLE IF EXISTS types CASCADE;
DROP TABLE IF EXISTS green_areas CASCADE;
DROP TABLE IF EXISTS vertices CASCADE;
DROP TABLE IF EXISTS ways CASCADE;

-- 1. Reference table
CREATE TABLE IF NOT EXISTS types (
    id INTEGER PRIMARY KEY,
    type VARCHAR(100) NOT NULL UNIQUE
);

-- 2. Green areas
CREATE TABLE IF NOT EXISTS green_areas (
    id INTEGER PRIMARY KEY,
    osm_id BIGINT,
    name TEXT,
    type_id INTEGER,
    geometry GEOMETRY(MultiPolygon, 4326),
    CONSTRAINT fk_type FOREIGN KEY (type_id) REFERENCES types(id)
);

-- 3. The vertices (Nodes)
-- We use 'id' to match the 'source' and 'target' in the ways table.
CREATE TABLE IF NOT EXISTS vertices (
    id INTEGER PRIMARY KEY,
    geometry GEOMETRY(Point, 4326)
);

-- 4. The ways (Edges)
CREATE TABLE IF NOT EXISTS ways (
    id SERIAL PRIMARY KEY,
    osm_id BIGINT,
    length_m FLOAT,
    source INTEGER, -- Refers to vertices.id
    target INTEGER, -- Refers to vertices.id
    cost FLOAT,
    reverse_cost FLOAT,
    geometry GEOMETRY(LineString, 4326)
);

-- 5. feedback Table
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    lat FLOAT,
    lon FLOAT,
    liked BOOLEAN,
    accessibility_score FLOAT,
    proximity_score FLOAT,
    quantity_score FLOAT,
    area_score FLOAT,
    diversity_score FLOAT,
    timestamp TIMESTAMP
);

-- 5. Critical Indices for Performance
CREATE INDEX IF NOT EXISTS idx_green_areas_geom ON green_areas USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_ways_geom ON ways USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_vertices_geom ON vertices USING GIST (geometry);