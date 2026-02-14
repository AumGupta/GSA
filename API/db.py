# Database connection module for the Green Spaces Accessibility API
# This module provides a function to establish a connection to the PostgreSQL database.

# Importing necessary libraries
import os
import psycopg

# Load database password from environment variable for security
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

# Function to get a connection to the PostgreSQL database
def get_connection():
    return psycopg.connect(
        host="localhost",
        dbname="gsa_db",
        user="postgres",
        password=POSTGRES_PASSWORD,
        port=5432
    )

