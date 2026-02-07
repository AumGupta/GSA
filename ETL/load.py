# module responsible for loading data into PostGIS.


from sqlalchemy import create_engine
from geoalchemy2 import Geometry
from config import DB_CONFIG


def get_engine():
    """Create SQLAlchemy engine using database configuration."""
    connection_string = (
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    return create_engine(connection_string)


def load_to_postgis(gdf, table_name="green_areas"):
    """Load GeoDataFrame into PostGIS table."""

    engine = get_engine()

    gdf.to_postgis(
        name=table_name,
        con=engine,
        if_exists="replace",
        index=False
    )
