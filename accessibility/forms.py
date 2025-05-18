"""
Forms for the accessibility app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

class AccessibilitySettingsForm(forms.Form):
    """Form for accessibility settings."""
    # Display options
    HIGH_CONTRAST_CHOICES = [
        (False, _('Default')),
        (True, _('High Contrast'))
    ]
    
    FONT_SIZE_CHOICES = [
        ('small', _('Small')),
        ('medium', _('Medium')),
        ('large', _('Large')),
        ('xlarge', _('Extra Large')),
    ]
    
    COLOR_BLIND_CHOICES = [
        ('none', _('None')),
        ('protanopia', _('Protanopia (red-weak)')),
        ('deuteranopia', _('Deuteranopia (green-weak)')),
        ('tritanopia', _('Tritanopia (blue-weak)')),
    ]
    
    # Form fields
    high_contrast = forms.ChoiceField(
        label=_('Color Contrast'),
        choices=HIGH_CONTRAST_CHOICES,
        widget=forms.RadioSelect,
        required=False,
    )
    
    dyslexia_font = forms.BooleanField(
        label=_('Use dyslexia-friendly font'),
        required=False,
        help_text=_('Uses OpenDyslexic font for better readability')
    )
    
    font_size = forms.ChoiceField(
        label=_('Font Size'),
        choices=FONT_SIZE_CHOICES,
        widget=forms.RadioSelect,
        required=True,
    )
    
    color_blind = forms.ChoiceField(
        label=_('Color Blindness'),
        choices=COLOR_BLIND_CHOICES,
        widget=forms.RadioSelect,
        required=True,
    )
    
    keyboard_nav = forms.BooleanField(
        label=_('Keyboard Navigation'),
        required=False,
        help_text=_('Enhance keyboard navigation support')
    )
    
    screen_reader = forms.BooleanField(
        label=_('Screen Reader Mode'),
        required=False,
        help_text=_('Optimize for screen readers')
    )
    
    animations = forms.BooleanField(
        label=_('Animations'),
        required=False,
        help_text=_('Enable animations and transitions')
    )
    
    reduced_motion = forms.BooleanField(
        label=_('Reduced Motion'),
        required=False,
        help_text=_('Reduce animations and transitions')
    )
    
    def __init__(self, *args, **kwargs):
        """Initialize the form with user preferences if available."""
        self.user = kwargs.pop('user', None)
        initial = kwargs.get('initial', {})
        
        # Set initial values from user preferences
        if self.user and hasattr(self.user, 'accessibility_settings'):
            user_settings = self.user.accessibility_settings
            for field in self.fields:
                if field in user_settings:
                    initial[field] = user_settings[field]
        
        kwargs['initial'] = initial
        super().__init__(*args, **kwargs)
    
    def save(self):
        """Save the accessibility settings for the user."""
        if not self.user or not hasattr(self.user, 'accessibility_settings'):
            return False
            
        cleaned_data = self.cleaned_data
        self.user.accessibility_settings = {
            'high_contrast': cleaned_data.get('high_contrast') == 'True',
            'dyslexia_font': cleaned_data.get('dyslexia_font', False),
            'font_size': cleaned_data.get('font_size', 'medium'),
            'color_blind': cleaned_data.get('color_blind', 'none'),
            'keyboard_nav': cleaned_data.get('keyboard_nav', False),
            'screen_reader': cleaned_data.get('screen_reader', False),
            'animations': cleaned_data.get('animations', True),
            'reduced_motion': cleaned_data.get('reduced_motion', False),
        }
        self.user.save()
        return True
