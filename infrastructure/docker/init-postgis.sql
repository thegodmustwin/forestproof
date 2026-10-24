CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- The API migration owns application tables. Extensions are initialized here so
-- local Docker development has the same spatial primitives as deployment.
