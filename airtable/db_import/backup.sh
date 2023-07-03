#!/bin/bash

# Define a timestamp function
#timestamp() {
#  date +"%T" # current time
#}

pg_dump -h localhost -U postgres -p 5433 -f psql_backup airtable_cache