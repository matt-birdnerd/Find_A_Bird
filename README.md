### Find a Bird App

## Setup Instructions

### Database setup
Install Postgresql-16

By default apt installs postgresql 14. We want 16 so we'll need to add the official postgres repository to our apt.
Update our apt first
        
    sudo apt update

Add the Postgres security keys to our trusted keys list

    wget -qO - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg

Add the postgres repository while referencing our security keys

    echo "deb [signed-by=/etc/apt/trusted.gpg.d/postgresql.gpg] http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list

Update your repositories list

    sudo apt-get update

Install posgresql-16

    sudo apt-get install postgresql-16

Ensure it starts the service on boot

    sudo systemctl start postgresql@16-main
    sudo systemctl enable postgresql@16-main

    
Install PostGIS for latitude and longitude geometry queries

    sudo apt-get install postgis postgresql-contrib


Log into postgresql

    sudo -u postgres psql


Create a user for the scripts to use

    CREATE USER find_a_bird WITH PASSWORD 'secure_password_goes_here';

Give permissions to the script user

    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO find_a_bird;

Create the database

    CREATE DATABASE findabird;

Switch to your database

    \c findabird

Enable PostGIS extension

    CREATE EXTENSION postgis;
    CREATE EXTENSION postgis_topology;

Verify PostGIS installation with:

    SELECT PostGIS_full_version();

Use the ```findabird_db_tables.sql``` file to initialize the database tables and columns.


