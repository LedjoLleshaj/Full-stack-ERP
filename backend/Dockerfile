# Use slim Python 3.11 base image
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# ✅ Add wait-for-db script
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Default command — you can override this in docker-compose
# CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8080"]

ENTRYPOINT [ "./entrypoint.sh" ]

# ✅ Default command using wait_for_db
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8080"]
