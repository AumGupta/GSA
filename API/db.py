import psycopg

def get_connection():
    return psycopg.connect(
        host="localhost",
        dbname="gsa_db",
        user="postgres",
        password="postgres",
        port=5432
    )
