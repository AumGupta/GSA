# Routing router for the Green Spaces Accessibility API
# This module defines endpoints related to routing, such as finding the closest park and calculating walking distance 
# to it using pgRouting. 

# importing necessary libraries
from fastapi import APIRouter
from API.db import get_connection

# Creating the router for routing endpoints
router = APIRouter(prefix="/routing", tags=["Routing"])

# Endpoint to calculate walking distance to the closest park using pgRouting
@router.get("/closest-park")
def closest_park_route(lat: float, lon: float):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM ways_vertices_pgr
        ORDER BY the_geom <-> ST_SetSRID(ST_Point(%s, %s), 4326)
        LIMIT 1;
    """, (lon, lat))

    start_node = cur.fetchone()[0]

    query = f"""
    WITH start AS (
        SELECT {start_node} AS id
    ),
    park_vertices AS (
        SELECT
            g.gid,
            v.id AS vertex_id
        FROM green_areas g
        JOIN ways_vertices_pgr v
        ON ST_DWithin(v.the_geom, ST_Centroid(g.geom), 50)
        LIMIT 20
    ),
    route AS (
        SELECT *
        FROM pgr_dijkstra(
            'SELECT gid as id, source, target, length as cost FROM ways',
            (SELECT id FROM start),
            ARRAY(SELECT vertex_id FROM park_vertices),
            directed := false
        )
    )
    SELECT
        SUM(w.length) AS distance_m
    FROM route r
    JOIN ways w ON r.edge = w.gid;
    """

    cur.execute(query)
    distance = cur.fetchone()[0]

    cur.close()
    conn.close()

    return {
        "walking_distance_m": distance
    }

"""
    Run this in the database to create the necessary indexes for pgRouting performance:
    CREATE INDEX ways_geom_idx ON ways USING GIST(the_geom);
    CREATE INDEX vertices_geom_idx ON ways_vertices_pgr USING GIST(the_geom);
"""
