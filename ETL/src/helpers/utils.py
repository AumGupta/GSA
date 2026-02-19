from time import time


def get_super_type(tags):
    osm_type = tags.get("leisure") or tags.get("landuse") or tags.get("natural") or "unknown"
    mapping = {
        'park': 'park', 'garden': 'park', 'grass': 'park', 
        'village_green': 'park', 'playground': 'park', 'recreation_ground': 'park',
        'forest': 'forest', 'wood': 'forest', 'scrub': 'forest', 'nature_reserve': 'forest',
        'grassland': 'grassland', 'heath': 'grassland', 'fell': 'grassland'
    }
    return mapping.get(osm_type, osm_type)

def build_routing_query(bbox):
    south, west, north, east = bbox
    query = f"""[out:json][timeout:180];
    (
      way["highway"~"^(motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|secondary_link|tertiary|tertiary_link|unclassified|residential|living_street|service|road|track|bus_guideway|escape|raceway|footway|bridleway|steps|corridor|path|cycleway|pedestrian)$"]({south},{west},{north},{east});
    );
    out geom;
    """
    return query

def build_overpass_query(bbox):
    south, west, north, east = bbox
    
    query = f"""[out:json][timeout:180];
    (
    /* Leisure green spaces */
    way["leisure"~"^(park|garden|playground|nature_reserve|recreation_ground|dog_park)$"]({south},{west},{north},{east});
    relation["leisure"~"^(park|garden|playground|nature_reserve|recreation_ground|dog_park)$"]({south},{west},{north},{east});

    /* Landuse vegetation */
    way["landuse"~"^(forest|grass|village_green|allotments|recreation_ground)$"]({south},{west},{north},{east});
    relation["landuse"~"^(forest|grass|village_green|allotments|recreation_ground)$"]({south},{west},{north},{east});

    /* Natural vegetation */
    way["natural"~"^(wood|grassland|scrub|heath|fell)$"]({south},{west},{north},{east});
    relation["natural"~"^(wood|grassland|scrub|heath|fell)$"]({south},{west},{north},{east});
    );
    out geom;
    """

    return query

def time_this_function(func, **kwargs) -> str:
    """ Times function `func`

        Args:
            func (function): the function we want to time

        Returns:
            a string with the execution time
    """
    t0 = time()
    result = func(**kwargs)
    t1 = time()
    t = t1 - t0
    msg = f"DONE: '{func.__name__}' EXECUTED IN {t:.3f} SECONDS"
    return result, t, msg