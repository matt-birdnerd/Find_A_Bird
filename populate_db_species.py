import os
from io import StringIO
import sys

import sqlalchemy as sa
from dotenv import load_dotenv
import requests
import pandas as pd

# Load environment variables
load_dotenv()

# Get the API key from the .env file
api_key = os.getenv('EBIRD_API_KEY')

# Database credentials from .env file
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')

# Define the eBird API endpoint you want to access, for example, a sample endpoint
url = 'https://api.ebird.org/v2/ref/taxonomy/ebird'

# Set up the headers with your API key
headers = {
    'X-eBirdApiToken': api_key
}

# GET species list from eBird API
try:
    # Make the GET request to the eBird API
    api_response = requests.get(url, headers=headers)

    api_response.raise_for_status()  # will raise an exception for HTTP error codes
    species_data = StringIO(api_response.text)
    species_df = pd.read_csv(species_data)
except requests.RequestException as e:
    print(f"Request failed: {e}")
except pd.errors.EmptyDataError as e:
    print(f"No data: {e}")

# Rename columns to match database
column_rename_map = {'TAXON_ORDER': 'taxonomic_order', 
                     'COMMON_NAME': 'common_name', 
                     'SCIENTIFIC_NAME': 'sci_name', 
                     'ORDER': 'order', 
                     'FAMILY_COM_NAME': 'family_common', 
                     'CATEGORY': 'category', 
                     'COM_NAME_CODES': 'alpha_code',
                     'SPECIES_CODE': 'species_code'}

species_df.rename(columns=column_rename_map, inplace=True)

# Select columns to insert and keep
columns_to_insert = list(column_rename_map.values())

species_import_df = species_df[columns_to_insert]

# Connect to the database
try:
    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"
    engine = sa.create_engine(connection_string)

    metadata = sa.MetaData()
    metadata.bind = engine
    table = sa.Table('species', metadata, autoload_with=engine)

    for index, row in species_import_df.iterrows():
        with engine.connect() as conn:
            try:
                stmt = sa.select(table).where(table.c.species_code == row['species_code'])
                result = conn.execute(stmt)
                if result.fetchone() is None:
                    pd.DataFrame([row]).to_sql('species', conn, if_exists='append', index=False, method='multi')
                    conn.commit()
                    print(f"INSERT {index}")
                
                else:
                    print("exists already")

            except sa.exc.SQLAlchemyError as e:
                print(f"Error: {e}")
                sys.exit(1)  # Exit the script with a non-zero status code

except sa.exc.SQLAlchemyError as e:
    print(f"Database connection failed: {e}")
    sys.exit(1)  # Exit the script with a non-zero status code

finally:
    conn.close()