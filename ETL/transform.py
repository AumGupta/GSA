#Module responsible for transforming raw Overpass JSON into a clean GeoDataFrame.


import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon

def parse_geometry(element):
    """Convert Overpass geometry to Shapely polygon.
    """
    if "geometry" not in element:
        return None

    coords = [(node["lon"], node["lat"]) for node in element["geometry"]]

    if len(coords) < 3:
        return None

    return Polygon(coords)


def transform_to_geodataframe(overpass_json):
    """Transform Overpass API JSON response into a GeoDataFrame.
    
    Parameters:
        overpass_json (dict): the JSON response from Overpass API query

    Returns:
        geopandas.GeoDataFrame: GeoDataFrame with parsed geometries and attributes
    """

    elements = overpass_json.get("elements", [])

    records = []

    for el in elements:
        geom = parse_geometry(el)

        if geom is None:
            continue

        record = {
            "gid": el["id"],
            "name": el.get("tags", {}).get("name", "Unnamed"),
            "type": el.get("tags", {}).get("leisure", "unknown"),
            "geometry": geom
        }

        records.append(record)

    gdf = gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:4326")

    # remove invalid geometries
    gdf = gdf[gdf.is_valid]

    return gdf