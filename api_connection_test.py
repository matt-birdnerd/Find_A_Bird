import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Get the API key from the .env file
api_key = os.getenv('EBIRD_API_KEY')

# Define the eBird API endpoint you want to access, for example, a sample endpoint
url = 'https://api.ebird.org/v2/data/obs/geo/recent?lat=42.0&lng=-76.0'

# Set up the headers with your API key
headers = {
    'X-eBirdApiToken': api_key
}

# Make the GET request to the eBird API
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Process the response here - example: print the response JSON
    print(response.json())
else:
    print(f"Failed to retrieve data: {response.status_code}")
