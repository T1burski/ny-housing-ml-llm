import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import os

def load_csv_to_postgresql():
    try:
        # Read the CSV file
        df = pd.read_csv(f"{os.getcwd()}/dags/data/ny_house_dataset.csv")
        
        # Create the connection URL
        url = URL.create(
            drivername="postgresql",
            username=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME")
        )

        # Create engine
        engine = create_engine(url)
        
        schema_name = 'ny_datasets'
        table_name = 'original_data'
        
        # Create schema and table using SQLAlchemy
        create_schema = text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
        create_table = text(f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (
                BROKERTITLE VARCHAR(255),
                TYPE VARCHAR(100),
                PRICE DECIMAL(20,2),
                BEDS DECIMAL(10,2),
                BATH DECIMAL(10,2),
                PROPERTYSQFT DECIMAL(15,2),
                ADDRESS VARCHAR(255),
                STATE VARCHAR(255),
                MAIN_ADDRESS VARCHAR(255),
                ADMINISTRATIVE_AREA_LEVEL_2 VARCHAR(255),
                LOCALITY VARCHAR(255),
                SUBLOCALITY VARCHAR(255),
                STREET_NAME VARCHAR(255),
                LONG_NAME VARCHAR(255),
                FORMATTED_ADDRESS VARCHAR(255),
                LATITUDE DECIMAL(15,8),
                LONGITUDE DECIMAL(15,8)
            )
        """)
        
        with engine.begin() as connection:
            # Create schema and table
            connection.execute(create_schema)
            connection.execute(create_table)
            
            # Clear existing data
            connection.execute(text(f"TRUNCATE TABLE {schema_name}.{table_name}"))
            
            # Prepare the insert query
            columns = ', '.join(df.columns)
            placeholders = ', '.join([':' + col for col in df.columns])
            insert_query = text(f"INSERT INTO {schema_name}.{table_name} ({columns}) VALUES ({placeholders})")
            
            # Convert DataFrame to list of dictionaries
            records = df.to_dict('records')
            
            # Insert data in chunks
            chunk_size = 1000
            for i in range(0, len(records), chunk_size):
                chunk = records[i:i + chunk_size]
                connection.execute(insert_query, chunk)
                print(f"Inserted records {i} to {min(i + chunk_size, len(records))}")
        
        print(f"Successfully loaded all {len(records)} records into {schema_name}.{table_name}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        engine.dispose()
        print("Database connection closed.")