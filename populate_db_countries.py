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

# Define the eBird API endpoint you want to access, for example, a sample endpoint
url = 'https://api.ebird.org/v2/ref/region/list/country/world'

# Set up the headers with your API key
headers = {
    'X-eBirdApiToken': api_key
}

# GET countries list from eBird API
try:
    # Make the GET request to the eBird API
    api_response = requests.get(url, headers=headers)

    api_response.raise_for_status()  # will raise an exception for HTTP error codes
    countries_data = api_response.json()
except requests.RequestException as e:
    print(f"API request failed: {e}")
    countries_data = []  # to avoid further processing

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

    # Insert data into the database
    for country in countries_data:
        country_code = country['code']  
        country_name = country['name'] 

        # Check for duplicates
        cursor.execute('SELECT * FROM countries WHERE country_code = %s', (country_code,))
        if cursor.fetchone() is None:  # Only insert if the country_code doesn't exist
            cursor.execute('INSERT INTO countries (country_code, display_name) VALUES (%s, %s)',
                           (country_code, country_name))

    conn.commit()

except psycopg2.Error as e:
    print(f"Database operation failed: {e}")

finally:
    if conn:
        cursor.close()
        conn.close()