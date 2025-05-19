#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE core_db;
    CREATE DATABASE chat_db;
    
    \c core_db
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    \c chat_db
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOSQL 