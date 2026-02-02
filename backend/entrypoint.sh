#!/bin/sh

echo "Waiting for REDACTED..."

while ! nc -z db 5432; do
  sleep 1
done

echo "PostgreSQL started"

# Run migrations
python manage.py migrate

# Create superuser from environment variables (only if doesn't exist)
python manage.py shell << EOF
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@localhost')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'changeme')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Created superuser: {username}")
else:
    print(f"Superuser {username} already exists")
EOF

exec "$@"

