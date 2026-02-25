# Database connection module for the Green Spaces Accessibility API

import os
import psycopg

# Load the full connection URL from environment variable
#DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    """
    Returns a new connection to the Postgres database using the
    DATABASE_URL environment variable.
    """
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable not found")

    # Connect using psycopg (psycopg3)
    # sslmode is already included in the URL, so no need to pass separately
    try:
        conn = psycopg.connect(database_url)
        return conn
    except Exception as e:
        # Optional: wrap with a clear error for Render logs
        raise RuntimeError(f"Failed to connect to DB: {e}") from e