import os
import sys
from io import StringIO

import psycopg2
from dotenv import load_dotenv
import requests
import pandas as pd
import geopandas as gpd
import sqlalchemy as sa

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

# Define the eBird API endpoint you want to access
url = "https://api.ebird.org/v2/ref/hotspot/US"

# Set up the headers with your API key
headers = {
    'X-eBirdApiToken': api_key
}

# define column names in preperation for import

column_names = ['ebird_id', 
                'country', 
                'subnational1', 
                'subnational2', 
                'latitude', 
                'longitude', 
                'display_name', 
                'create_date', 
                'unknown']

    # GET hotspots list from eBird API
try:
    # Make the GET request to the eBird API
    api_response = requests.get(url, headers=headers)

    api_response.raise_for_status()  # will raise an exception for HTTP error codes
    hotspot_data = StringIO(api_response.text)
    hotspot_data_df = pd.read_csv(hotspot_data, names=column_names)
    print("API data retrieved successfully.")
    #clean out unneeded columns
    hotspot_data_df.drop(columns=['unknown', 'country', 'subnational1'], inplace=True)
except requests.RequestException as e:
    print(f"API request failed: {e}")
    hotspot_data = []  # to avoid further processing

# The eBird database contains a few hotspots with NaN values in the subnational2 columns
# Cleaning NaN values from the dataframe
    
hotspot_data_df.dropna(subset=['subnational2'], inplace=True)

# Initialize a column for the subnational2 id number which will become a foreign key in the DB
hotspot_data_df[['subnational2_id']] = None

# populate the subnational2_id column with the primary key from the subnational_2 table
try:
    conn = psycopg2.connect(
        dbname=db_name, 
        user=db_user, 
        password=db_password, 
        host=db_host, 
        port=db_port
        )
    cursor = conn.cursor()

    # Fetch all mappings from subnational2_code to id
    cursor.execute("SELECT subnational2_code, id FROM subnational2")
    mappings = cursor.fetchall()
    mappings_dict = {code: id for code, id in mappings}
    print("subnational2_code mapped successfully.")
except psycopg2.Error as e:
    print(f"Database operation failed: {e}")

finally:
    if conn:
        cursor.close()
        conn.close()

# Map subnational2 id's to submational2_codes
hotspot_data_df['subnational2_id'] = hotspot_data_df['subnational2'].map(mappings_dict)
# remove the subnational_2 code column as it is not present in the database       
hotspot_data_df.drop(columns='subnational2', inplace=True)
print("Mapping subnational2 code to id successful")

# extract existing hotspots to check for duplicates
try:
    # Connect to your database
    conn = psycopg2.connect(
        dbname=db_name, 
        user=db_user, 
        password=db_password, 
        host=db_host, 
        port=db_port
    )

    # Create a new cursor
    cursor = conn.cursor()

    # Execute the query to fetch existing ebird_id values
    cursor.execute("SELECT ebird_id FROM hotspots")
    
    # Fetch all results
    existing_ids_tuples = cursor.fetchall()
    
    # Convert the list of tuples to a list
    existing_ids_list = [item[0] for item in existing_ids_tuples]
    print("Existing hotspots retrieved successfully.")
except psycopg2.Error as e:
    print(f"Database operation failed: {e}")
    conn.close()
    sys.exit(1)  # Exit the script with a non-zero status code
finally:
    # Close the cursor and connection
    if conn:
        cursor.close()
        conn.close()

# filter retrevied data with data already in the database
hotspot_data_df = hotspot_data_df[~hotspot_data_df['ebird_id'].isin(existing_ids_list)]


# Connect to the database to insert data
try:
    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"
    engine = sa.create_engine(connection_string)

    hotspot_data_df.to_sql('hotspots', engine, if_exists='append', index=False, method='multi')
    print("Data inserted successfully.")

except sa.exc.SQLAlchemyError as e:
    print(f"Database connection failed: {e}")
    sys.exit(1)  # Exit the script with a non-zero status code

# Populate geometry column in database
    
try:
    conn = psycopg2.connect(
        dbname=db_name, 
        user=db_user, 
        password=db_password, 
        host=db_host, 
        port=db_port
    )
    cursor = conn.cursor()

    update_geometry_query = """
    UPDATE hotspots
    SET geometry = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
    WHERE geometry IS NULL;
    """
    cursor.execute(update_geometry_query)

    conn.commit()

except psycopg2.Error as e:
    print(f"Database operation failed: {e}")

finally:
    if conn:
        cursor.close()
        conn.close()