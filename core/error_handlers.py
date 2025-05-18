"""
Custom error handlers for the application.
"""
import logging
import json
from django.http import JsonResponse, HttpResponseServerError
from django.template import loader
from django.views.defaults import ERROR_400_TEMPLATE_NAME, ERROR_403_TEMPLATE_NAME, \
    ERROR_404_TEMPLATE_NAME, ERROR_500_TEMPLATE_NAME
from django.conf import settings

logger = logging.getLogger(__name__)

def custom_400(request, exception=None, template_name=ERROR_400_TEMPLATE_NAME):
    """Handle 400 Bad Request errors."""
    context = {
        'status_code': 400,
        'message': 'Bad Request',
        'details': str(exception) if exception else 'The request could not be understood by the server.'
    }
    return render_error_response(request, context, template_name, 400)

def custom_403(request, exception=None, template_name=ERROR_403_TEMPLATE_NAME):
    """Handle 403 Forbidden errors."""
    context = {
        'status_code': 403,
        'message': 'Permission Denied',
        'details': str(exception) if exception else 'You do not have permission to access this resource.'
    }
    return render_error_response(request, context, template_name, 403)

def custom_404(request, exception=None, template_name=ERROR_404_TEMPLATE_NAME):
    """Handle 404 Not Found errors."""
    context = {
        'status_code': 404,
        'message': 'Page Not Found',
        'details': 'The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.'
    }
    return render_error_response(request, context, template_name, 404)

def custom_500(request, template_name=ERROR_500_TEMPLATE_NAME):
    """Handle 500 Server Error."""
    context = {
        'status_code': 500,
        'message': 'Server Error',
        'details': 'An unexpected error occurred. Our team has been notified.'
    }
    return render_error_response(request, context, template_name, 500)

def render_error_response(request, context, template_name, status_code):
    """Render error response based on the request type (API or HTML)."""
    # Log the error for debugging
    logger.error(
        'Error %d: %s - %s',
        status_code,
        context.get('message', ''),
        context.get('details', ''),
        exc_info=True if status_code >= 500 else None
    )
    
    # For API requests, return JSON
    if request.content_type == 'application/json' or 'application/json' in request.META.get('HTTP_ACCEPT', ''):
        return JsonResponse(context, status=status_code)
    
    # For regular requests, render HTML
    template = loader.get_template(template_name)
    return HttpResponseServerError(template.render(context, request), content_type='text/html')


def handle_uncaught_exception(request, exception):
    """Handle uncaught exceptions in views.
    
    Args:
        request: The request object
        exception: The exception that was raised
        
    Returns:
        HttpResponse: The error response
    """
    logger.critical(
        'Unhandled exception in view: %s',
        str(exception),
        exc_info=True,
        extra={
            'status_code': 500,
            'request': request
        }
    )
    
    # Only send error emails in production
    if not settings.DEBUG:
        from django.views.debug.technical_500_response import get_traceback
        from django.core.mail import mail_admins
        
        try:
            tb = get_traceback(None, None, None, sys.exc_info())
            mail_admins(
                'Unhandled Exception',
                f'An unhandled exception occurred: {exception}\n\n{tb}',
                fail_silently=True
            )
        except Exception as mail_exc:
            logger.error('Failed to send error email: %s', str(mail_exc), exc_info=True)
    
    return custom_500(request)
