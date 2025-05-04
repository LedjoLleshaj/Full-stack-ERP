#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z db 5432; do
  sleep 1
done

echo "PostgreSQL started"

# Run migrations
python manage.py migrate

echo "from django.contrib.auth import get_user_model; \
User = get_user_model(); \
User.objects.filter(username='adminselita').exists() or \
User.objects.create_superuser('adminselita', 'admin@selita.com', 'adminpass')" | python manage.py shell


exec "$@"
