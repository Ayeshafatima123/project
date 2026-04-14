#!/bin/bash

# Build script for Vercel deployment

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate --run-syncdb

# Collect static files
python manage.py collectstatic --noinput --clear

# Create cache table (if using database cache)
# python manage.py createcachetable

echo "Build completed successfully!"
