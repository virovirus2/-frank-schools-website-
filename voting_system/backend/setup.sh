#!/bin/bash

echo "Starting Voting System Setup..."

# Create necessary directories
mkdir -p logs
mkdir -p media
mkdir -p staticfiles

echo "Directories created"

# Database migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Migrations completed"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Setup completed successfully!"
