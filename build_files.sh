#!/bin/bash

# Build script for Vercel deployment

echo "========================================="
echo "Starting Vercel Build Process..."
echo "========================================="

# Install dependencies
echo ""
echo "Step 1: Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Run migrations
echo ""
echo "Step 2: Running database migrations..."
python manage.py migrate --run-syncdb
echo "✅ Database migrations completed"

# Collect static files
echo ""
echo "Step 3: Collecting static files..."
python manage.py collectstatic --noinput --clear
echo "✅ Static files collected"

# Verify static files exist
echo ""
echo "Step 4: Verifying static files..."
if [ -d "staticfiles" ]; then
    echo "✅ staticfiles directory exists"
    ls -la staticfiles/
else
    echo "⚠️ staticfiles directory not found"
fi

echo ""
echo "========================================="
echo "✅ Build completed successfully!"
echo "========================================="
