# Use PostgreSQL 16 Alpine for smaller image size
FROM REDACTED:16-alpine

# Copy the SQL script to initialize the database
COPY schema.sql /docker-entrypoint-initdb.d/

# Credentials are passed via docker-compose environment variables
# Do NOT hardcode credentials here

EXPOSE 5432