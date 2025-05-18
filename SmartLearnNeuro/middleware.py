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


class CsrfViewMiddleware:
    """
    Middleware to ensure CSRF protection is properly enforced.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip CSRF check for safe methods
        if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            return self.get_response(request)
            
        # Check for CSRF token in headers or form data
        csrf_token = request.META.get('HTTP_X_CSRFTOKEN', '')
        if not csrf_token:
            csrf_token = request.POST.get('csrfmiddlewaretoken', '')
            
        if not csrf_token or not request.COOKIES.get('csrftoken') == csrf_token:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied('CSRF verification failed. Request aborted.')
            
        return self.get_response(request)
