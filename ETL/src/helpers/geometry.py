from shapely import MultiPolygon, Polygon, make_valid, unary_union

def build_polygon(coords):
    if len(coords) < 3: return None
    if coords[0] != coords[-1]: coords = coords + [coords[0]]
    if len(coords) < 4: return None
    try:
        poly = Polygon(coords)
        if not poly.is_valid:
            poly = make_valid(poly)
            if poly.geom_type == 'GeometryCollection':
                polys = [g for g in poly.geoms if g.geom_type in ['Polygon', 'MultiPolygon']]
                if not polys: return None
                poly = unary_union(polys)
        return poly if not poly.is_empty else None
    except Exception: return None

def parse_way(element):
    if "geometry" not in element: return None
    coords = [(pt["lon"], pt["lat"]) for pt in element["geometry"]]
    return build_polygon(coords)

def parse_relation(element):
    polygons = []
    for member in element.get("members", []):
        if "geometry" not in member: continue
        coords = [(pt["lon"], pt["lat"]) for pt in member["geometry"]]
        poly = build_polygon(coords)
        if poly: polygons.append(poly)
    if not polygons: return None
    merged = unary_union(polygons)
    return ensure_multipolygon(merged)

def ensure_multipolygon(geom):
    if geom is None or geom.is_empty: return None
    if isinstance(geom, Polygon): return MultiPolygon([geom])
    if isinstance(geom, MultiPolygon): return geom
    if geom.geom_type == 'GeometryCollection':
        polys = [g for g in geom.geoms if isinstance(g, (Polygon, MultiPolygon))]
        flat = []
        for p in polys:
            if isinstance(p, Polygon): flat.append(p)
            else: flat.extend(list(p.geoms))
        return MultiPolygon(flat) if flat else None
    return None