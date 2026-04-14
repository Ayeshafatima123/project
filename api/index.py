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

# Setup Django and run migrations
import django
from django.conf import settings

# Run migrations before loading Django
if not settings.DEBUG:
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb', '--verbosity=0'])
    except Exception as e:
        print(f"Migration note: {e}")

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
