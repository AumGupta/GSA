import src.pipeline as p
import src.helpers as h

def extract()-> list:
    h.info("EXTRACT: Data from Overpass API...")
    try:
        green_areas_data = p.extract_green_areas_data()
        if green_areas_data is None:
            h.die("No data extracted for green areas. Exiting")
            return
        routing_data = p.extract_routing_data()
    except Exception as e:
        h.die(f"Extraction failed:  {e}")
    raw_data = [green_areas_data, routing_data]
    return raw_data

def transform(raw_data)-> list:
    h.info("TRANSFORM: Raw data...")
    try:
        dfs = p.transform_green_areas_data(raw_data[0])
        routing_dfs = p.transform_routing_data(raw_data[1])
        dfs = list(dfs)
        dfs.extend(list(routing_dfs))
        for df in dfs:
            if df is None or df.empty:
                h.die(f'{df} is empty or None. Exiting.')
                return
    except Exception as e:
        h.die(f"Transformation failed: {e}")
    return dfs

def load(dfs: list)-> None:
    engine = p.get_engine()
    
    # Define order carefully: 'types' must be loaded before 'green_areas'
    target_tables = ['types', 'green_areas', 'ways', 'vertices']
    
    h.info("LOAD: Data into database...")
    h.info(f"LOAD: Cleaning existing data from target tables: {', '.join(target_tables[:-1])} and {target_tables[-1]}")
    try:
        p.truncate_tables(engine, target_tables)
    except Exception as e:
        h.die(f"Failed to clean target tables: {e}")

    try:
        for i in range(len(target_tables)):
            p.load_data(engine, dfs[i], target_tables[i])
    except Exception as e:
        h.die(f"Error loading data into '{target_tables[i]}' table: {e}")
    engine.dispose()
    
def main():
    h.info("START: ETL Process...")
    raw_data, t1, m1 = h.time_this_function(extract)
    h.info(m1)
    dfs, t2, m2 = h.time_this_function(transform, raw_data=raw_data)
    h.info(m2)
    r3 = h.time_this_function(load, dfs=dfs)
    h.info(r3[-1])
    h.done(f"ETL COMPLETED IN {t1+t2+r3[-2]:.3f} SECONDS")

if __name__ == "__main__":
    main()