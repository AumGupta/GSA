"""
Module responsible for extracting green area data from Overpass API.

Includes:
- Extended green-area tags
- Error handling for common Overpass failures (504, timeouts)
- Retry mechanism with exponential backoff
"""

import requests
import time
from requests.exceptions import HTTPError, Timeout, ConnectionError
from config import OVERPASS_URL, CITY_BBOX


def build_overpass_query(bbox):
    """
    Build Overpass query to retrieve green areas within a bounding box.

    Parameters
    ----------
    bbox : tuple
        Bounding box in format (south, west, north, east)

    Returns
    -------
    str
        Overpass QL query string
    """
    south, west, north, east = bbox

    query = f"""
    [out:json][timeout:120];
    (
      way["leisure"~"park|garden|playground|nature_reserve"]({south},{west},{north},{east});
      relation["leisure"~"park|garden|playground|nature_reserve"]({south},{west},{north},{east});

      way["landuse"~"grass|forest|recreation_ground|meadow|village_green"]({south},{west},{north},{east});
      relation["landuse"~"grass|forest|recreation_ground|meadow|village_green"]({south},{west},{north},{east});

      way["natural"~"wood|grassland|heath"]({south},{west},{north},{east});
      relation["natural"~"wood|grassland|heath"]({south},{west},{north},{east});
    );
    out geom;
    """
    return query


def extract_green_spaces(max_retries=3):
    """
    Extract green areas from Overpass API with retry logic.

    Parameters
    ----------
    max_retries : int
        Maximum number of retry attempts in case of failure

    Returns
    -------
    dict
        JSON response from Overpass API

    Raises
    ------
    Exception
        If all retries fail
    """

    query = build_overpass_query(CITY_BBOX)

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt}: Sending request to Overpass API...")

            response = requests.post(
                OVERPASS_URL,
                data={"data": query},
                timeout=180
            )

            response.raise_for_status()

            print("Data successfully retrieved from Overpass.")
            return response.json()

        except HTTPError as e:
            print(f"HTTP error occurred: {e}")

            if response.status_code == 504:
                print("Server timeout (504). Overpass may be overloaded.")
            elif response.status_code == 429:
                print("Too many requests (429). Rate limit exceeded.")

        except Timeout:
            print("Request timed out.")

        except ConnectionError:
            print("Connection error occurred.")

        except Exception as e:
            print(f"Unexpected error: {e}")

        # Retry logic
        if attempt < max_retries:
            wait_time = attempt * 5
            print(f"Retrying in {wait_time} seconds...\n")
            time.sleep(wait_time)
        else:
            print("Max retries reached. Extraction failed.")
            raise Exception("Failed to retrieve data from Overpass API.")
