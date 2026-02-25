# Database connection module for the Green Spaces Accessibility API

import os
import psycopg

# Load the full connection URL from environment variable
#DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = os.environ.get("DB_PORT")
    DB_NAME = os.environ.get("DB_NAME")
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")

    if not DB_HOST:
        raise RuntimeError("DB_HOST environment variable not found")

    return psycopg.connect(
        host='db.uqayijuvmanqhyjvjcwb.supabase.co',
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode="require"
    )