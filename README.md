### Find a Bird App

## Setup Instructions

### Database setup
Install Postgresql
    sudo apt update
    sudo apt install postgresql postgresql-contrib

Log into postgresql

    sudo -u postgres psql

Create a user for the scripts to use

    CREATE USER find_a_bird WITH PASSWORD 'secure_password_goes_here';


