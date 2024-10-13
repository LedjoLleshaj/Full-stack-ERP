# Use the official PostgreSQL image from Docker Hub
FROM postgres:latest

# Copy the SQL script to initialize the database
COPY schema.sql /docker-entrypoint-initdb.d/

ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD postgres
ENV POSTGRES_DB selita_fish

EXPOSE 5432