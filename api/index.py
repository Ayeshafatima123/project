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
django.setup()

# Run migrations on each cold start (necessary for serverless)
from django.core.management import call_command
try:
    # Check if database exists, if not create it and run migrations
    from django.conf import settings
    db_path = settings.DATABASES['default'].get('NAME', '')
    
    # For SQLite, check if database file exists or if using /tmp
    is_sqlite = 'sqlite' in settings.DATABASES['default']['ENGINE']
    needs_migration = not is_sqlite or (is_sqlite and '/tmp' in str(db_path))
    
    if needs_migration:
        call_command('migrate', '--run-syncdb', verbosity=0)
except Exception as e:
    # If migrations fail, log but continue (will show error page)
    print(f"Migration warning: {e}")

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
