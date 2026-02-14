# Accessibility router for the Green Spaces Accessibility API
# This module defines endpoints related to calculating the accessibility score of green spaces based on various factors.

# importing necessary libraries
from fastapi import APIRouter
from API.db import get_connection
import math
from collections import Counter

# Creating the router for accessibility endpoints
router = APIRouter(prefix="/accessibility", tags=["Accessibility"])

# Endpoint to calculate the accessibility score for a given point
@router.get("/accessibility-score")
def accessibility_score(lat: float, lon: float, buffer_m: float = 500):
    """
    Green Accessibility Score based on:
    - Proximity
    - Quantity
    - Area
    - Diversity
    """

    conn = get_connection()
    cur = conn.cursor()

    # Spatial query
    query = """
    SELECT
        gid,
        name,
        type,
        ST_Area(ST_Transform(geometry, 3857)) AS area_m2,
        ST_Distance(
            ST_Transform(geometry, 3857),
            ST_Transform(
                ST_SetSRID(ST_Point(%s, %s), 4326),
                3857
            )
        ) AS distance_m,
        ST_AsGeoJSON(geometry) AS geometry
    FROM green_areas
    WHERE ST_DWithin(
        ST_Transform(geometry, 3857),
        ST_Transform(
            ST_SetSRID(ST_Point(%s, %s), 4326),
            3857
        ),
        %s
    )
    AND ST_Area(ST_Transform(geometry, 3857)) > 300;
    """

    cur.execute(query, (lon, lat, lon, lat, buffer_m))
    parks = cur.fetchall()

    cur.close()
    conn.close()

    # If no parks found, return 0 score
    if len(parks) == 0:
        return {
            "accessibility_score": 0.0,
            "scores": {
                "proximity": 0.0,
                "quantity": 0.0,
                "area": 0.0,
                "diversity": 0.0
            },
            "parks_found": 0
        }

    # Proximity score: based on distance to nearest park, with a decay function
    proximity_total = 0

    for park in parks:
        distance = park[4]  # distance_m
        contribution = 1 - (distance / buffer_m)

        if contribution < 0:
            contribution = 0

        proximity_total += contribution

    proximity_score = (proximity_total / len(parks))* 10

    # Quantity score: based on number of parks found
    n_parks = len(parks)
    quantity_score = (1 - math.exp(-n_parks / 5)) * 10

    # Area score: based on total area of parks found
    total_area = sum(park[3] for park in parks)  # area_m2
    area_score = min(1, total_area / 50000) * 10

    # Diversity score: based on variety of park types
    types = [park[2] for park in parks if park[2] is not None]

    if len(types) <= 1:
        diversity_score = 0
    else:
        counts = Counter(types)
        total = sum(counts.values())

        H = 0
        for c in counts.values():
            p = c / total
            H -= p * math.log(p)

        diversity_score = (H / math.log(len(counts))) * 10

    # Final accessibility score: weighted average of all components
    accessibility = (
        0.4 * proximity_score +
        0.3 * area_score +
        0.2 * quantity_score +
        0.1 * diversity_score
    )

    return {
        "accessibility_score": round(accessibility, 2),
        "scores": {
            "proximity": round(proximity_score, 2),
            "quantity": round(quantity_score, 2),
            "area": round(area_score, 2),
            "diversity": round(diversity_score, 2),
            "parks": [{"gid": p[0], "name": p[1],"type": p[2], "area": p[3], "distance": p[4], "geometry": p[5]} for p in parks],
        },
        "parks_found": n_parks,
        "buffer_m": buffer_m
    }