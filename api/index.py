"""
Vercel Serverless Entry Point for Django
"""
import os
import sys

# Add project root to Python path
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_path)
sys.path.insert(0, os.path.join(project_path, 'survey_rewards_site'))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'survey_rewards_site.settings')
os.environ.setdefault('VERCEL', '1')

# Now try to load Django
try:
    import django
    django.setup()
    
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
    <head><title>Django Error</title>
    <style>
        body {{ font-family: monospace; padding: 40px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #e53e3e; }}
        h2 {{ color: #2d3748; margin-top: 20px; }}
        pre {{ background: #f7fafc; padding: 15px; border-radius: 4px; overflow-x: auto; }}
        .solution {{ background: #c6f6d5; padding: 15px; border-radius: 4px; margin: 20px 0; }}
    </style>
    </head>
    <body>
        <div class="container">
            <h1>🚨 Django Failed to Load</h1>
            <h2>Exception:</h2>
            <pre>{str(e)}</pre>
            <h2>Traceback:</h2>
            <pre>{traceback.format_exc()}</pre>
            <div class="solution">
                <h3>💡 Quick Fix:</h3>
                <ol>
                    <li>Check Vercel deployment logs for details</li>
                    <li>Make sure all dependencies are in requirements.txt</li>
                    <li>Verify environment variables are set</li>
                    <li>Try redeploying the app</li>
                </ol>
            </div>
        </div>
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
