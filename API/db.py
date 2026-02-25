# Database connection module for the Green Spaces Accessibility API

import os
import psycopg

# Load the full connection URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set!")
    # Connect to Supabase Postgres using SSL
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require"
    )