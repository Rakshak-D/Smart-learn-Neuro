"""
Custom middleware for the core app.
"""
import sys
import logging
from django.conf import settings
from django.http import HttpResponseServerError
from .error_handlers import handle_uncaught_exception

logger = logging.getLogger(__name__)

class ExceptionLoggingMiddleware:
    """
    Middleware that logs exceptions and provides custom error handling.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Process exceptions raised by views.
        """
        # Don't log 404 errors
        from django.http import Http404
        from django.core.exceptions import PermissionDenied
        
        if isinstance(exception, Http404):
            return None
            
        if isinstance(exception, PermissionDenied):
            return None
            
        # Log the exception
        logger.error(
            'Unhandled exception while processing request: %s',
            request.path,
            exc_info=sys.exc_info(),
            extra={
                'status_code': 500,
                'request': request,
            }
        )
        
        # Return the appropriate error response
        return handle_uncaught_exception(request, exception)


class SecurityHeadersMiddleware:
    """
    Middleware to set security headers for all responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Security Headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'same-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # CSP Header - Update this to match your specific requirements
        csp = """
            default-src 'self';
            script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://code.jquery.com https://cdnjs.cloudflare.com;
            style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com;
            img-src 'self' data: https:;
            font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com;
            connect-src 'self' https://api.example.com;
            media-src 'self' https:;
            object-src 'none';
            frame-ancestors 'none';
            base-uri 'self';
            form-action 'self';
        """
        response['Content-Security-Policy'] = ' '.join(csp.split())
        
        # HSTS Header - Only enable this if you're using HTTPS
        # response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        return response
