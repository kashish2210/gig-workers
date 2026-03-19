#!/usr/bin/env bash
# Render build script for GigShield
# This runs during every deploy on Render

set -o errexit  # exit on error

echo "==> Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Running migrations..."
python manage.py migrate --no-input

echo "==> Seeding initial data..."
python manage.py seed_data || echo "Seed data already exists or skipped."

echo "==> Build complete!"
