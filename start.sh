#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to start..."
while ! nc -z postgres 5432; do
    sleep 1
done
echo "PostgreSQL is ready."

# Apply database migrations
echo "Applying database migrations"
python manage.py migrate

# Apply database fixtures
echo "Applying database fixtures"
python commands.py

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000