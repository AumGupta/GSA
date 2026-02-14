"""
Module responsible for extracting green area data from Overpass API.
"""
from src.helpers import build_overpass_query, build_routing_query, die, info
from src.pipeline import OVERPASS_URL, CITY_BBOX

import requests
import time
from requests.exceptions import HTTPError, Timeout, ConnectionError

def extract_green_areas_data(max_retries=3):

    query = build_overpass_query(CITY_BBOX)
    info("EXTRACT: Built Overpass query for green areas data")
    
    for attempt in range(1, max_retries + 1):
        info(f"EXTRACT: Attempt {attempt} to extract green areas data...")
        try:
            response = requests.post(OVERPASS_URL, data={"data": query}, timeout=180)
            response.raise_for_status()
            
            info("EXTRACT: Green areas data extracted successfully")
            return response.json()

        except (HTTPError, Timeout, ConnectionError) as e:
            if attempt == max_retries:
                die(f"Extraction failed after {max_retries} attempts: {e}")
            time.sleep(attempt * 5)
            
def extract_routing_data(max_retries=3):
    query = build_routing_query(CITY_BBOX)
    info("EXTRACT: Built Overpass query for green areas data")
    
    for attempt in range(1, max_retries + 1):
        info(f"EXTRACT: Attempt {attempt} to extract routing data...")
        try:
            response = requests.post(OVERPASS_URL, data={"data": query}, timeout=180)

            info("EXTRACT: Routing data extracted successfully")
            response.raise_for_status()
            return response.json()

        except (HTTPError, Timeout, ConnectionError) as e:
            if attempt == max_retries:
                die(f"Extraction failed after {max_retries} attempts: {e}")
            time.sleep(attempt * 5)
