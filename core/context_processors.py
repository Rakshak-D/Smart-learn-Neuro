"""Context processors for the core app."""


def accessibility_settings(request):
    """Add accessibility settings to the template context.
    
    Args:
        request: The request object
        
    Returns:
        dict: Dictionary containing accessibility settings
    """
    # Default accessibility settings
    accessibility = {
        'high_contrast': False,
        'dyslexia_font': False,
        'font_size': 'medium',
        'color_blind': 'none',
        'keyboard_nav': False,
        'screen_reader': False,
        'animations': True,
        'reduced_motion': False,
    }
    
    # Update with user's settings if available
    if hasattr(request, 'accessibility_settings'):
        accessibility.update(request.accessibility_settings)
    
    # Add body classes for accessibility
    body_classes = []
    
    if accessibility.get('high_contrast'):
        body_classes.append('high-contrast')
    
    if accessibility.get('dyslexia_font'):
        body_classes.append('dyslexia-font')
    
    if accessibility.get('reduced_motion'):
        body_classes.append('reduced-motion')
    
    if accessibility.get('color_blind') != 'none':
        body_classes.append(f'color-blind-{accessibility["color_blind"]}')
    
    if accessibility.get('font_size') != 'medium':
        body_classes.append(f'font-size-{accessibility["font_size"]}')
    
    accessibility['body_classes'] = ' '.join(body_classes)
    
    return {
        'accessibility': accessibility
    }
