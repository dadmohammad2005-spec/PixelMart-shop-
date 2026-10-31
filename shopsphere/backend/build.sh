#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

if [ -f "manage.py" ]; then
    MANAGE_CMD="python manage.py"
    REQ_FILE="requirements.txt"
elif [ -f "shopsphere/backend/manage.py" ]; then
    MANAGE_CMD="python shopsphere/backend/manage.py"
    REQ_FILE="shopsphere/backend/requirements.txt"
elif [ -f "backend/manage.py" ]; then
    MANAGE_CMD="python backend/manage.py"
    REQ_FILE="backend/requirements.txt"
else
    echo "manage.py not found!"
    exit 1
fi

echo "==> Upgrading pip..."
pip install --upgrade pip

echo "==> Installing requirements from $REQ_FILE..."
pip install -r "$REQ_FILE"

echo "==> Running collectstatic..."
$MANAGE_CMD collectstatic --no-input

echo "==> Running migrations..."
$MANAGE_CMD migrate

echo "==> Seeding sample data (PixelMart catalog)..."
$MANAGE_CMD seed_sample_data

echo "==> Build complete!"
