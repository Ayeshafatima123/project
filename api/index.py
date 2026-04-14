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

# Now try to load Django
try:
    from django.core.wsgi import get_wsgi_application
    django_app = get_wsgi_application()
    
    # Django loaded successfully - use it
    application = django_app
    
    # Run migrations in background (don't block requests)
    try:
        from django.core.management import call_command
        call_command('migrate', '--run-syncdb', verbosity=0)
    except:
        pass
        
except Exception as e:
    # Django failed - show detailed error
    import traceback
    error_html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Django Error</title></head>
    <body style="font-family: monospace; padding: 40px;">
        <h1 style="color: red;">Django Failed to Load</h1>
        <h2>Exception:</h2>
        <pre>{str(e)}</pre>
        <h2>Traceback:</h2>
        <pre>{traceback.format_exc()}</pre>
    </body>
    </html>
    """.encode('utf-8')
    
    def error_app(environ, start_response):
        status = '500 Internal Server Error'
        response_headers = [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Content-Length', str(len(error_html))),
        ]
        start_response(status, response_headers)
        return [error_html]
    
    application = error_app

# Vercel looks for 'app'
app = application
