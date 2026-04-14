"""
Vercel Serverless Entry Point for Django - MINIMAL VERSION FOR TESTING
"""
import os
import sys

# Add project root to Python path
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_path)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'survey_rewards_site.settings')

# Try to import Django and see what happens
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    # Return a simple error page to see what's wrong
    import traceback
    error_html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Django Import Error</title></head>
    <body style="font-family: monospace; padding: 40px;">
        <h1 style="color: red;">Django Failed to Load</h1>
        <pre>{traceback.format_exc()}</pre>
        <h2>Error:</h2>
        <pre>{str(e)}</pre>
    </body>
    </html>
    """
    
    def simple_app(environ, start_response):
        status = '500 Internal Server Error'
        response_headers = [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Content-Length', str(len(error_html.encode('utf-8')))),
        ]
        start_response(status, response_headers)
        return [error_html.encode('utf-8')]
    
    application = simple_app

# Vercel also looks for 'app'
app = application
