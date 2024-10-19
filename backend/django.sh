#!/bin/bash
echo "Creating Migrations"
python manage.py makemigrations backend
echo "================================="

echo "Migrating"
python manage.py migrate
echo "================================="

echo "Starting Django Server"
python manage.py runserver 0.0.0.0:8080
echo "================================="