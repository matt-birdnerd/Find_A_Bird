import os

from dotenv import load_dotenv
import psycopg2

# Loading the environment variables from the .env file
load_dotenv()

# Reading environment variables
dbname = os.getenv('DB_NAME')
dbuser = os.getenv('DB_USER')
dbpassword = os.getenv('DB_PASSWORD')
dbhost = os.getenv('DB_HOST')
dbport = os.getenv('DB_PORT')

# Check the connection

try:
    conn = psycopg2.connect(dbname=dbname, user=dbuser, password=dbpassword, host=dbhost, port=dbport)
    cur = conn.cursor()
    cur.execute('SELECT version();')
    db_version = cur.fetchone()
    print("Connected to the database successfully.")
    print("Database version:", db_version)
except psycopg2.Error as e:
    print("Unable to connect to the database:", e)
finally:
    if conn:
        cur.close()
        conn.close()