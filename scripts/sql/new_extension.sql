CREATE USER otm_kdp ENCRYPTED PASSWORD 'postgres';

\c template1
CREATE EXTENSION IF NOT EXISTS hstore;
\c template1
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
\c template1
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE DATABASE otm_kdp OWNER otm_kdp;