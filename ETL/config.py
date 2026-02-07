# configuration file for ETL.
# stores database connection and Overpass parameters.

import os

POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "gsa_db",
    "user": "postgres",
    "password": POSTGRES_PASSWORD 
}

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
# OVERPASS_URL = "https://lz4.overpass-api.de/api/interpreter" #mirror1
# OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter" #mirror2


# bounding box format: south, west, north, east
# CITY_BBOX = (38.70, -9.25, 38.80, -9.10)  #  Lisbon
# CITY_BBOX = (38.72, -9.16, 38.74, -9.14) #small area in Lisbon to test
CITY_BBOX = (38.691, -9.229, 38.796, -9.091)


