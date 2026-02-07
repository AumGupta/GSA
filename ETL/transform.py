"""
Transform Overpass JSON into GeoDataFrame with proper multipolygon support.
"""

import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union


def build_polygon(coords):
    if len(coords) < 3:
        return None

    # ensure ring is closed
    if coords[0] != coords[-1]:
        coords.append(coords[0])

    poly = Polygon(coords)

    if not poly.is_valid:
        poly = poly.buffer(0)

    return poly if poly.is_valid else None


def parse_way(element):
    if "geometry" not in element:
        return None

    coords = [(pt["lon"], pt["lat"]) for pt in element["geometry"]]
    return build_polygon(coords)


def parse_relation(element):
    polygons = []

    for member in element.get("members", []):
        if "geometry" not in member:
            continue

        coords = [(pt["lon"], pt["lat"]) for pt in member["geometry"]]
        poly = build_polygon(coords)

        if poly:
            polygons.append(poly)

    if not polygons:
        return None

    merged = unary_union(polygons)

    if isinstance(merged, Polygon):
        return MultiPolygon([merged])

    if isinstance(merged, MultiPolygon):
        return merged

    return None


def get_green_type(tags):
    return (
        tags.get("leisure")
        or tags.get("landuse")
        or tags.get("natural")
        or "unknown"
    )


def transform_to_geodataframe(overpass_json):

    elements = overpass_json.get("elements", [])
    records = []

    for el in elements:

        if el["type"] == "way":
            geom = parse_way(el)

        elif el["type"] == "relation":
            geom = parse_relation(el)

        else:
            continue

        if geom is None:
            continue

        # force multipolygon
        if isinstance(geom, Polygon):
            geom = MultiPolygon([geom])

        record = {
            "gid": el["id"],
            "name": el.get("tags", {}).get("name", "Unnamed"),
            "type": get_green_type(el.get("tags", {})),
            "geometry": geom
        }

        records.append(record)

    gdf = gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:4326")

    # drop invalid
    gdf = gdf[gdf.is_valid]

    return gdf
