from extract import extract_green_spaces
from transform import transform_to_geodataframe
from load import load_to_postgis


def run():
    print("Starting ETL process...")

    print("Extracting data...")
    raw_data = extract_green_spaces()

    print("Transforming data...")
    gdf = transform_to_geodataframe(raw_data)

    print(f"Loaded {len(gdf)} green areas.")

    print("Loading into PostGIS...")
    load_to_postgis(gdf)

    print("ETL completed successfully.")


if __name__ == "__main__":
    run()
