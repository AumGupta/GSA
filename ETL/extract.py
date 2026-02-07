"""
Module responsible for extracting green area data from Overpass API.
"""

import requests
import time
from requests.exceptions import HTTPError, Timeout, ConnectionError
from config import OVERPASS_URL, CITY_BBOX


def build_overpass_query(bbox):
    south, west, north, east = bbox

    # query = f"""[out:json][timeout:180];
    # (
    #   way["leisure"~"park|garden|playground|nature_reserve|recreation_ground"]({south},{west},{north},{east});
    #   relation["leisure"~"park|garden|playground|nature_reserve|recreation_ground"]({south},{west},{north},{east});

    #   way["landuse"~"forest|grass|meadow|village_green"]({south},{west},{north},{east});
    #   relation["landuse"~"forest|grass|meadow|village_green"]({south},{west},{north},{east});

    #   way["natural"~"wood|grassland|scrub|heath"]({south},{west},{north},{east});
    #   relation["natural"~"wood|grassland|scrub|heath"]({south},{west},{north},{east});
    # );
    # out geom;
    # """

    # Exhaustive query - includes more tags but also more noise
    # query = f"""
    # [out:json][timeout:180];
    # (
    #   way["leisure"~"park|garden|playground|nature_reserve|recreation_ground|dog_park|miniature_golf|nature_reserve|pitch"]({south},{west},{north},{east});
    #   relation["leisure"~"park|garden|playground|nature_reserve|recreation_ground|dog_park|miniature_golf|nature_reserve|pitch"]({south},{west},{north},{east});

    #   way["landuse"~"forest|grass|meadow|village_green|fairground|allotments|farmland|animal_keeping|flowerbed|greenhouse_horticulture|orchard|plant_nursery|vineyard|cemetery|recreation_ground|greenery"]({south},{west},{north},{east});
    #   relation["landuse"~"forest|grass|meadow|village_green|fairground|allotments|farmland|animal_keeping|flowerbed|greenhouse_horticulture|orchard|plant_nursery|vineyard|cemetery|recreation_ground|greenery"]({south},{west},{north},{east});

    #   way["natural"~"wood|grassland|scrub|heath|fell|scrub|shrubbery|tree|tree_row|tundra|wood"]({south},{west},{north},{east});
    #   relation["natural"~"wood|grassland|scrub|heath|fell|scrub|shrubbery|tree|tree_row|tundra|wood"]({south},{west},{north},{east});
    # );
    # out geom;
    # """

    # refined
    query = f"""[out:json][timeout:180];
    (
    /* Leisure green spaces */
    way["leisure"~"park|garden|playground|nature_reserve|recreation_ground|dog_park"]({south},{west},{north},{east});
    relation["leisure"~"park|garden|playground|nature_reserve|recreation_ground|dog_park"]({south},{west},{north},{east});

    /* Landuse vegetation */
    way["landuse"~"forest|grass|meadow|village_green|allotments|cemetery|recreation_ground"]({south},{west},{north},{east});
    relation["landuse"~"forest|grass|meadow|village_green|allotments|cemetery|recreation_ground"]({south},{west},{north},{east});

    /* Natural vegetation */
    way["natural"~"wood|grassland|scrub|heath|fell"]({south},{west},{north},{east});
    relation["natural"~"wood|grassland|scrub|heath|fell"]({south},{west},{north},{east});
    );
    out geom;
    """

    return query


def extract_green_spaces(max_retries=3):

    query = build_overpass_query(CITY_BBOX)

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                OVERPASS_URL,
                data={"data": query},
                timeout=180
            )

            response.raise_for_status()
            return response.json()

        except (HTTPError, Timeout, ConnectionError) as e:
            if attempt == max_retries:
                raise Exception(f"Extraction failed after retries: {e}")
            time.sleep(attempt * 5)
