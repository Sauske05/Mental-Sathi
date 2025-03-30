from pydoc import resolve

from django.shortcuts import redirect
from django.conf import settings
import re
import logging

from django.urls import Resolver404

logger = logging.getLogger(__name__)
class RedirectUnauthorizedHttpMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for a static file
        #print(f'The static url is: {settings.STATIC_URL}')
        # if settings.STATIC_URL in request.path:
        #     if request.user.is_authenticated:
        #         return redirect('/admin_dashboard/')  # Redirect authenticated users to the dashboard
        #     else:
        #         return redirect('/')  # Redirect unauthenticated users to the landing page

        try:
           response = self.get_response(request)
           if response.status_code  == 404:
               return redirect('/')
        except Exception as e:
            return redirect('/')

        # if request.session.get('user_id') is None:
        #     return redirect('/login')

        if request.path.endswith('.html'):
            if request.session.get('user_id'):
                return redirect('/dashboard/')
            else:
                return redirect('/')
        return self.get_response(request)
