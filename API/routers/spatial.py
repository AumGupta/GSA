# Spatial router for the Green Spaces Accessibility API
# This module defines endpoints related to spatial queries, 
# such as checking if a point is within a green area or finding nearby green areas.

# importing necessary libraries
from fastapi import APIRouter
from API.db import get_connection

# Creating the router for spatial endpoints
router = APIRouter(tags=["Spatial"])

# Endpoint to check if a point is within a green area
@router.get("/green-area")
def get_green_area(lat: float, lon: float):

    conn = get_connection()
    cur = conn.cursor()

    query = """
    SELECT gid, name
    FROM green_areas
    WHERE ST_Contains(
        geometry,
        ST_SetSRID(ST_Point(%s, %s), 4326)
    )
    LIMIT 1;
    """

    cur.execute(query, (lon, lat))

    result = cur.fetchone()

    cur.close()
    conn.close()

    if result:
        return {
            "gid": result[0],
            "name": result[1],
            "inside_green_area": True
        }
    else:
        return {
            "inside_green_area": False
        }

# Endpoint to get green areas within a buffer around a point
@router.get("/green-area-buffer")
def get_green_areas_buffer(lat: float, lon: float, buffer_m: float = 500):
    conn = get_connection()
    cur = conn.cursor()

    query = """
    SELECT gid, name
    FROM green_areas
    WHERE ST_Intersects(
        geometry,
        ST_Transform(
            ST_Buffer(
                ST_Transform(
                    ST_SetSRID(ST_Point(%s, %s), 4326),
                    3857
                ),
                %s
            ),
            4326
        )
    );
    """

    cur.execute(query, (lon, lat, buffer_m))
    results = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {"gid": r[0], "name": r[1]} for r in results
    ]

