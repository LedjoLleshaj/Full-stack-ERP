#!/bin/sh

echo "Waiting for REDACTED..."

while ! nc -z db 5432; do
  sleep 1
done

echo "PostgreSQL started"

exec "$@"
