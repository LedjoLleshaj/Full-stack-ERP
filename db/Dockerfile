# Use the official PostgreSQL image from Docker Hub
FROM REDACTED:latest

# Copy the SQL script to initialize the database
COPY schema.sql /docker-entrypoint-initdb.d/

ENV POSTGRES_USER REDACTED
ENV POSTGRES_PASSWORD REDACTED
ENV POSTGRES_DB selita_fish

EXPOSE 5432