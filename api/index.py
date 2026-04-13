"""
Vercel Serverless Entry Point for Django
"""
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'survey_rewards_site.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
