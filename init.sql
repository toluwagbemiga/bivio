-- Initial database setup
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database if it doesn't exist
CREATE DATABASE pos_financial_db;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE pos_financial_db TO pos_user;
