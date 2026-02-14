from src.helpers import parse_way, parse_relation, ensure_multipolygon, get_super_type, die, info

import pandas as pd
import geopandas as gpd
from shapely import LineString, Point
from collections import Counter


def transform_green_areas_data(json):
    elements = json.get("elements", [])
    records = []

    for el in elements:
        geom = parse_way(el) if el["type"] == "way" else parse_relation(el)
        if geom is None:
            continue

        tags = el.get("tags", {})
        name = tags.get("name", "Unnamed")
        raw_type = (
            tags.get("leisure")
            or tags.get("landuse")
            or tags.get("natural")
            or "unknown"
        )
        final_type = get_super_type(tags) if name == "Unnamed" else raw_type

        records.append(
            {
                "osm_id": el["id"],
                "name": name,
                "type": final_type.capitalize().replace("_", " "),
                "geometry": geom,
            }
        )
    info(f"TRANSFORM: Parsed {len(records)} green area records from raw data")
    
    if not records:
        return gpd.GeoDataFrame()

    ga_gdf = gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:4326").to_crs(
        "EPSG:3857"
    )
    ga_gdf = ga_gdf[ga_gdf.is_valid].copy()

    # 1. PRIORITY & COOKIE-CUTTER
    ga_gdf["area"] = ga_gdf.geometry.area
    ga_gdf["is_named"] = ga_gdf["name"] != "Unnamed"
    ga_gdf = ga_gdf.sort_values(
        by=["is_named", "area"], ascending=[False, True]
    ).reset_index(drop=True)

    geoms = ga_gdf.geometry.values.copy()
    sindex = ga_gdf.sindex
    for i in range(len(ga_gdf)):
        curr = geoms[i]
        if curr is None or curr.is_empty:
            continue
        for j in list(sindex.intersection(curr.bounds)):
            if j > i and geoms[j] is not None and curr.intersects(geoms[j]):
                try:
                    geoms[j] = geoms[j].difference(curr)
                except:
                    geoms[j] = geoms[j].buffer(0).difference(curr.buffer(0))

    ga_gdf["geometry"] = geoms
    ga_gdf = ga_gdf[~ga_gdf.geometry.is_empty].copy()
    info(f"TRANSFORM: Applied cookie-cutter logic to resolve overlaps, resulting in {len(ga_gdf)} non-overlapping green areas")

    # 2. LOCALISED SEMANTIC MERGE
    GAP_TOLERANCE = 3.0
    original_state = ga_gdf.copy()
    ga_gdf["geometry"] = ga_gdf.geometry.buffer(GAP_TOLERANCE)
    ga_gdf = ga_gdf.dissolve(
        by=["name", "type"], as_index=False, aggfunc={"osm_id": "first"}
    )

    ga_gdf["geometry"] = ga_gdf.geometry.buffer(-GAP_TOLERANCE)
    ga_gdf = pd.concat([ga_gdf, original_state], ignore_index=True)
    ga_gdf = ga_gdf.dissolve(
        by=["name", "type"], as_index=False, aggfunc={"osm_id": "first"}
    )
    info(f"TRANSFORM: Performed localized semantic merge, resulting in {len(ga_gdf)} green areas after merging close features")

    # 3. FINAL CLEANUP
    ga_gdf = ga_gdf.explode(index_parts=False).reset_index(drop=True)
    ga_gdf["geometry"] = ga_gdf.geometry.apply(ensure_multipolygon)
    ga_gdf = ga_gdf[ga_gdf.geometry.notnull() & ~ga_gdf.geometry.is_empty].copy()
    
    info(f"TRANSFORM: Cleaned and merged green areas, resulting in {len(ga_gdf)} final records")

    # types table df
    types_df = ga_gdf[["type"]].drop_duplicates().reset_index(drop=True)
    types_df.insert(0, "id", types_df.index + 1)
    info(f"TRANSFROM: Created `types` dataframe with {len(types_df)} unique types")

    ga_gdf = ga_gdf.merge(types_df[["id", "type"]], on=["type"], how="left")
    ga_gdf.rename(columns={"id": "type_id"}, inplace=True)
    info("TRANSFORM: Merged `types` dataframe back into green areas dataframe to assign type_id")
    
    ga_gdf = ga_gdf.reset_index(drop=True)
    ga_gdf.insert(0, "id", ga_gdf.index + 1)

    # NOTE: Order of returning is important for loading: types_df must be loaded before ga_gdf due to FK constraint
    return (
        types_df,
        ga_gdf.to_crs("EPSG:4326")[["id", "osm_id", "name", "type_id", "geometry"]],
    )


def transform_routing_data(json):
    elements = json.get("elements", [])
    ways_data = [el for el in elements if el["type"] == "way"]
    info(f"TRANSFORM: Extracted {len(ways_data)} ways from routing data for further processing")
    
    # 1. Fast Node Counting
    node_counts = Counter()
    for way in ways_data:
        node_counts.update(way.get("nodes", []))
    info(f"TRANSFORM: Counted node occurrences across {len(ways_data)} ways for intersection detection")

    vertex_map = {}  # OSM_node_id -> Internal_integer_id
    next_vertex_id = 1
    vertices_records = []
    way_records = []

    # 2. Process Ways
    for way in ways_data:
        nodes = way.get("nodes", [])
        geometry_list = way.get("geometry", [])
        if not nodes or not geometry_list:
            continue

        # Pre-convert geometry_list to list of tuples for speed
        coords = [(pt["lon"], pt["lat"]) for pt in geometry_list]

        segment_coords = []
        current_start_node_osm = nodes[0]
        segment_coords.append(coords[0])

        for i in range(1, len(nodes)):
            node_osm_id = nodes[i]
            coord = coords[i]
            segment_coords.append(coord)

            # Intersection logic
            is_intersection = node_counts[node_osm_id] > 1
            is_endpoint = i == len(nodes) - 1

            if is_intersection or is_endpoint:
                # Handle Vertex Mapping without .index()
                for osm_id, c_idx in [
                    (
                        current_start_node_osm,
                        (
                            nodes.index(current_start_node_osm)
                            if is_endpoint and i == 1
                            else 0
                        ),
                    ),
                    (node_osm_id, i),
                ]:
                    # Small optimization: we only need the coordinate at index i or the start index
                    if osm_id not in vertex_map:
                        vertex_map[osm_id] = next_vertex_id
                        vertices_records.append(
                            {"id": next_vertex_id, "geometry": Point(coords[c_idx])}
                        )
                        next_vertex_id += 1

                # Add way record (Distance calculated later)
                way_records.append(
                    {
                        "osm_id": way["id"],
                        "source": vertex_map[current_start_node_osm],
                        "target": vertex_map[node_osm_id],
                        "geometry": LineString(segment_coords),
                    }
                )
                # Reset for next segment
                segment_coords = [coord]
                current_start_node_osm = node_osm_id
    info(f"TRANSFORM: Processed ways to identify {len(vertices_records)} vertices and {len(way_records)} way segments")

    # 3. Vectorized GeoPandas Operations (The Speed Boost)
    ways_gdf = gpd.GeoDataFrame(way_records, geometry="geometry", crs="EPSG:4326")
    info(f"TRANSFORM: Created GeoDataFrame for ways with {len(ways_gdf)} records")

    # Calculate all lengths at once (much faster than loop)
    ways_gdf["length_m"] = ways_gdf.to_crs(epsg=3857).geometry.length
    ways_gdf["cost"] = ways_gdf["length_m"]
    ways_gdf["reverse_cost"] = ways_gdf["length_m"]
    info("TRANSFORM: Calculated lengths and costs for all ways in a vectorized manner")

    vertices_gdf = gpd.GeoDataFrame(
        vertices_records, geometry="geometry", crs="EPSG:4326"
    )
    info(f"TRANSFORM: Created GeoDataFrame for vertices with {len(vertices_gdf)} records")

    return ways_gdf, vertices_gdf

