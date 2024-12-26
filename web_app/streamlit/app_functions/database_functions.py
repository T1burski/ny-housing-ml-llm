import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import os


def extract_data_postgresql(select_query):

    try:
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

        with engine.begin() as connection:
            result = connection.execute(text(select_query))
            
            rows = result.fetchall()
            
            df = pd.DataFrame(rows, columns=result.keys())

        engine.dispose()
        print("Database connection closed.")

        return df
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        engine.dispose()
        print("Database connection closed.")

def load_data_postgresql(data):

    try:
    
        url = URL.create(
            drivername="postgresql",
            username=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME")
        )

        engine = create_engine(url)
        
        schema_name = 'ny_datasets'
        table_name = 'requests_results'
        
        create_schema = text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
        create_table = text(f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (
                SUBLOCALITY VARCHAR(255),
                PRED_PRICE DECIMAL(20,2),
                BEDS DECIMAL(10,2),
                BATH DECIMAL(10,2),
                PROPERTYSQFT DECIMAL(15,2),
                LATITUDE DECIMAL(15,8),
                LONGITUDE DECIMAL(15,8),
                MED_PRICE DECIMAL(20,2),
                MED_PROPERTYSQFT DECIMAL(15,2),
                N_HOUSES INTEGER,
                REVIEW INTEGER,
                CREATED_AT DATE
            )
        """)
        
        with engine.begin() as connection:
            # Create schema and table
            connection.execute(create_schema)
            connection.execute(create_table)
            
            data_columns = [i.upper() for i, _ in data[0].items()]
            # Prepare the insert query
            columns = ', '.join(data_columns)
            placeholders = ', '.join([':' + col for col in data_columns])
            insert_query = text(f"INSERT INTO {schema_name}.{table_name} ({columns}) VALUES ({placeholders})")
            
            #records = df.to_dict('records')
            connection.execute(insert_query, data)
        
        print(f"Successfully loaded new user request records into {schema_name}.{table_name}")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        engine.dispose()
        print("Database connection closed.")