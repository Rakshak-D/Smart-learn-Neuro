"""
Accessibility utilities and middleware for SmartLearnNeuro.
"""
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class AccessibilityMiddleware(MiddlewareMixin):
    """
    Middleware to handle accessibility settings for users.
    """
    def process_request(self, request):
        """Process the request and apply accessibility settings."""
        # Initialize default accessibility settings
        accessibility_settings = {
            'high_contrast': False,
            'dyslexia_font': False,
            'font_size': 'medium',  # small, medium, large, xlarge
            'color_blind': 'none',  # none, protanopia, deuteranopia, tritanopia
            'keyboard_nav': False,
            'screen_reader': False,
            'animations': True,
            'reduced_motion': False,
        }
        
        # Get user's saved settings if authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                user_settings = request.user.accessibility_settings
                if user_settings:
                    accessibility_settings.update(user_settings)
            except AttributeError:
                # User model doesn't have accessibility_settings attribute
                pass
        
        # Check for session overrides
        for key in accessibility_settings.keys():
            if key in request.session:
                accessibility_settings[key] = request.session[key]
        
        # Check for URL parameters to override settings
        for key in accessibility_settings.keys():
            if key in request.GET:
                value = request.GET.get(key)
                if value.lower() in ('true', '1', 'on'):
                    accessibility_settings[key] = True
                    request.session[key] = True
                elif value.lower() in ('false', '0', 'off'):
                    accessibility_settings[key] = False
                    request.session[key] = False
                else:
                    accessibility_settings[key] = value
                    request.session[key] = value
        
        # Add to request
        request.accessibility_settings = accessibility_settings
        
        return None
    
    def process_template_response(self, request, response):
        """Add accessibility settings to template context."""
        if hasattr(request, 'accessibility_settings') and hasattr(response, 'context_data'):
            if response.context_data is None:
                response.context_data = {}
            response.context_data['accessibility'] = request.accessibility_settings
        return response


def get_contrast_ratio(hex1, hex2):
    """Calculate the contrast ratio between two colors in hex format."""
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    
    def get_luminance(rgb):
        # Convert RGB to relative luminance
        def adjust_channel(c):
            if c <= 0.03928:
                return c / 12.92
            return ((c + 0.055) / 1.055) ** 2.4
            
        r, g, b = [adjust_channel(c) for c in rgb]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    # Convert hex to RGB and calculate luminance
    rgb1 = hex_to_rgb(hex1)
    rgb2 = hex_to_rgb(hex2)
    
    l1 = get_luminance(rgb1) + 0.05
    l2 = get_luminance(rgb2) + 0.05
    
    # Ensure l1 is the lighter color
    if l1 < l2:
        l1, l2 = l2, l1
    
    contrast_ratio = l1 / l2
    return round(contrast_ratio, 2)


def is_high_contrast(hex1, hex2, min_ratio=4.5):
    """Check if two colors have sufficient contrast."""
    return get_contrast_ratio(hex1, hex2) >= min_ratio


def get_accessible_color(background_hex, light_color='#ffffff', dark_color='#000000', min_ratio=4.5):
    """Get a text color that has sufficient contrast with the background."""
    light_contrast = get_contrast_ratio(background_hex, light_color)
    dark_contrast = get_contrast_ratio(background_hex, dark_color)
    
    if light_contrast >= min_ratio and light_contrast > dark_contrast:
        return light_color
    elif dark_contrast >= min_ratio:
        return dark_color
    else:
        # Fallback to the higher contrast option
        return light_color if light_contrast > dark_contrast else dark_color
