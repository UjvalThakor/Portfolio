#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "==> Upgrading pip..."
pip install --upgrade pip

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Collecting static assets..."
python manage.py collectstatic --no-input

echo "==> Running database migrations..."
python manage.py migrate

echo "==> Seeding initial portfolio records..."
python manage.py seed_portfolio

echo "==> Build finished successfully!"
