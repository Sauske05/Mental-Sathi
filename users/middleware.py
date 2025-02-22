from django.shortcuts import redirect
from django.conf import settings
import re
import logging
logger = logging.getLogger(__name__)
class RedirectUnauthorizedHttpMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for a static file
        print(f'The static url is: {settings.STATIC_URL}')
        # if settings.STATIC_URL in request.path:
        #     if request.user.is_authenticated:
        #         return redirect('/admin_dashboard/')  # Redirect authenticated users to the dashboard
        #     else:
        #         return redirect('/')  # Redirect unauthenticated users to the landing page

        if request.path.endswith('.html'):
            #logger.info(f"Static file detected: {request.path}")  # Log static file access

            if request.user.is_authenticated:
                return redirect('/admin_dashboard/')
            else:
                return redirect('/')
        return self.get_response(request)
