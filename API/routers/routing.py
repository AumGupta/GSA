# Routing router for the Green Spaces Accessibility API
# This module defines endpoints related to routing, such as finding the closest park and calculating walking distance 
# to it using pgRouting. 

# importing necessary libraries
from fastapi import APIRouter, HTTPException
from API.db import get_connection
import json

# Creating the router for routing endpoints
router = APIRouter(prefix="/routing", tags=["Routing"])


# Endpoint to calculate the route to the nearest park
@router.get("/to-nearest-park")
def route_to_nearest_park(lat: float, lon: float):
    """
    Computes a walking route from the user location
    to the nearest green area using pgRouting.
    """

    conn = get_connection()
    cur = conn.cursor()

    query = """
        WITH user_loc AS (
            SELECT ST_SetSRID(ST_Point(%s, %s), 4326) AS geom
        ),
        nearest_park AS (
            SELECT id, name, geometry 
            FROM green_areas 
            ORDER BY geometry <-> (SELECT geom FROM user_loc) 
            LIMIT 1
        ),
        nodes AS (
            SELECT 
                (SELECT v.id FROM vertices v 
                    ORDER BY v.geometry <-> (SELECT geom FROM user_loc) 
                    LIMIT 1) as start_id,

                (SELECT v.id FROM vertices v 
                    ORDER BY v.geometry <-> ST_Centroid((SELECT geometry FROM nearest_park)) 
                    LIMIT 1) as end_id
        ),
        route_calc AS (
            SELECT path.seq, w.geometry, w.length_m
            FROM pgr_dijkstra(
                'SELECT id, source, target, cost, reverse_cost FROM ways',
                (SELECT start_id FROM nodes), 
                (SELECT end_id FROM nodes), 
                directed := false
            ) AS path
            JOIN ways AS w ON path.edge = w.id
        )
        SELECT 
            COALESCE(
                (SELECT ST_AsGeoJSON(ST_LineMerge(ST_Union(geometry))) FROM route_calc),
                ST_AsGeoJSON(ST_MakeLine(
                    (SELECT geometry FROM vertices WHERE id = (SELECT start_id FROM nodes)),
                    (SELECT geometry FROM vertices WHERE id = (SELECT end_id FROM nodes))
                ))
            ) as route_geojson,
            COALESCE((SELECT SUM(length_m) FROM route_calc), 0) as total_distance_m,
            CASE 
                WHEN (SELECT COUNT(*) FROM route_calc) > 0 THEN 'CONNECTED' 
                ELSE 'DISCONNECTED' 
            END as status,
            (SELECT name FROM nearest_park) as destination_park
        LIMIT 1;
    """

    # IMPORTANT: PostGIS expects (lon, lat)
    cur.execute(query, (lon, lat))
    result = cur.fetchone()

    cur.close()
    conn.close()

    if result is None:
        raise HTTPException(status_code=404, detail="No route found")

    # Convert GeoJSON string from Postgres into Python dict
    route_geometry = json.loads(result[0])

    return {
        "type": "Feature",
        "geometry": route_geometry,
        "properties": {
            "distance_m": round(result[1], 2),
            "status": result[2],
            "destination_park": result[3]
        }
    }


