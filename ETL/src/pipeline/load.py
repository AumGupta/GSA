import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine, text
from src.helpers import info, die
from src.pipeline import DB_CONFIG

def get_engine():
    conn_str = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    return create_engine(conn_str)

def load_data(engine, df, table_name):
    """
    Generalized loader that detects if a dataframe is spatial or standard.
    """
    if df is None or df.empty:
        die(f"Dataframe for '{table_name}' is empty or None. Skipping load")
        return

    # Check if it's a GeoDataFrame with a valid geometry column
    if isinstance(df, gpd.GeoDataFrame) and 'geometry' in df.columns:
        if 'osm_id' in df.columns:
            df['osm_id'] = pd.to_numeric(df['osm_id'], errors='coerce').fillna(0).astype('int64')
        
        df.to_postgis(
            name=table_name,
            con=engine,
            if_exists='append',
            index=False
        )
        info(f"LOAD: GeoDatFrame with {len(df)} records in '{table_name}' table")
    else:
        # Load standard tabular data
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists='append',
            index=False
        )
        info(f"LOAD: DataFrame with {len(df)} records in '{table_name}' table")
        
def truncate_tables(engine, table_names):
    """Cleans tables before a fresh load using the text() wrapper"""
    with engine.begin() as conn:
        for table in reversed(table_names):
            conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))
            info(f"LOAD: '{table}' table truncated successfully")