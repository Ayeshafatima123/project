"""
Vercel Serverless Entry Point for Django
"""
import os
import sys

# Add project root to Python path
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_path)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'survey_rewards_site.settings')

# Setup Django
import django
from django.conf import settings

# Initialize Django
django.setup()

# Run migrations (required for serverless on each cold start)
try:
    from django.core.management import call_command
    call_command('migrate', '--run-syncdb', verbosity=0)
except Exception as e:
    # Log but don't fail - migrations might already be applied
    print(f"Migration info: {e}")

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

# Custom error handler for debugging
def handler(request, context):
    try:
        return application(request, context)
    except Exception as e:
        # Return detailed error for debugging
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR: {error_details}")
        raise
