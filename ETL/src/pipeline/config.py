"""
Configuration file for the ETL pipeline, containing database connection details and Overpass API settings.
"""
from os import environ

POSTGRES_PASSWORD = environ.get('POSTGRES_PASSWORD')

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "gsa_db",
    "user": "postgres",
    "password": POSTGRES_PASSWORD 
}

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# bounding box format: south, west, north, east
CITY_BBOX = (38.691, -9.229, 38.796, -9.091) # Lisbon bounding box for main extraction
# CITY_BBOX = (38.72, -9.16, 38.74, -9.14) #small area in Lisbon to test
# CITY_BBOX = (36.95, -9.50, 42.16, -6.18) # Portugal bounding box for future use