import os

import psycopg2
from dotenv import load_dotenv
import requests

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

# Get list of states/subnational2 values from the database
# Connect to the database
try:
        conn = psycopg2.connect(
            dbname=db_name, 
            user=db_user, 
            password=db_password, 
            host=db_host, 
            port=db_port
        )
        cursor = conn.cursor()

        # get all of the subnational1 values
        query = 'SELECT subnational1_code FROM subnational1'
        
        # execute the query
        cursor.execute(query)
        
        # Fetch the results
        results = cursor.fetchall()

        # turn results into a list
        subnational1_codes = [item[0] for item in results]

except psycopg2.Error as e:
    print(f"Database error: {e}")

finally:
    if conn:
        cursor.close()
        conn.close()

for code in subnational1_codes:
# Define the eBird API endpoint. This case its subnational2 which is 'county'
    
    url = f'https://api.ebird.org/v2/ref/region/list/subnational2/{code}'

    # Set up the headers with your API key
    headers = {
        'X-eBirdApiToken': api_key
    }

    # GET countries list from eBird API
    try:
        # Make the GET request to the eBird API
        api_response = requests.get(url, headers=headers)

        api_response.raise_for_status()  # will raise an exception for HTTP error codes
        subnational2_data = api_response.json()
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        subnational2_data = []  # to avoid further processing

    # Connect to the database
    try:
        conn = psycopg2.connect(
            dbname=db_name, 
            user=db_user, 
            password=db_password, 
            host=db_host, 
            port=db_port
        )
        cursor = conn.cursor()

        # get all of the subnational values

        # Insert data into the database
        cursor.execute("SELECT id FROM subnational1 WHERE subnational1_code = %s", (code,))
        subnational1_id = cursor.fetchone()[0]

        for subnational2 in subnational2_data:
            subnational2_code = subnational2['code']  
            subnational2_name = subnational2['name']
            

            # Check for duplicates
            cursor.execute('SELECT * FROM subnational2 WHERE subnational2_code = %s', (subnational2_code,))
            if cursor.fetchone() is None:  # Only insert if the country_code doesn't exist
                cursor.execute('INSERT INTO subnational2 (subnational2_code, display_name, country_id) VALUES (%s, %s, %s)',
                            (subnational2_code, subnational2_name, subnational1_id))

        conn.commit()

    except psycopg2.Error as e:
        print(f"Database operation failed: {e}")

    finally:
        if conn:
            cursor.close()
            conn.close()