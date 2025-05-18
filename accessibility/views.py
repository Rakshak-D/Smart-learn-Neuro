"""
Views for the accessibility app.
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from django.conf import settings
from .forms import AccessibilitySettingsForm
from .models import (
    AccessibilitySettings,
    DyslexiaSettings,
    ADHDSettings,
    RewardSystem
)

class AccessibilitySettingsView(View):
    """View for managing accessibility settings."""
    template_name = 'accessibility/settings.html'
    form_class = AccessibilitySettingsForm
    
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        """Handle GET requests: display the settings form."""
        # Get user's current settings
        accessibility_settings = getattr(request.user, 'accessibilitysettings', None)
        dyslexia_settings = getattr(request.user, 'dyslexiasettings', None)
        adhd_settings = getattr(request.user, 'adhdsettings', None)
        
        # Prepare initial data
        initial = {}
        if accessibility_settings:
            initial.update({
                'high_contrast': accessibility_settings.high_contrast,
                'keyboard_nav': accessibility_settings.keyboard_nav,
                'screen_reader': accessibility_settings.screen_reader,
                'animations': accessibility_settings.animations,
                'reduced_motion': accessibility_settings.reduced_motion,
            })
        
        if dyslexia_settings:
            initial.update({
                'dyslexia_font': dyslexia_settings.font_family == 'open_dyslexic',
                'font_size': dyslexia_settings.font_size,
                'line_spacing': dyslexia_settings.line_spacing,
                'letter_spacing': dyslexia_settings.letter_spacing,
                'word_spacing': dyslexia_settings.word_spacing,
                'enable_text_to_speech': dyslexia_settings.enable_text_to_speech,
                'enable_spelling_assistance': dyslexia_settings.enable_spelling_assistance,
                'enable_grammar_assistance': dyslexia_settings.enable_grammar_assistance,
                'simplified_language': dyslexia_settings.simplified_language,
            })
        
        if adhd_settings:
            initial.update({
                'enable_focus_mode': adhd_settings.enable_focus_mode,
                'enable_white_noise': adhd_settings.enable_white_noise,
                'enable_break_reminders': adhd_settings.enable_break_reminders,
                'show_visual_timers': adhd_settings.show_visual_timers,
                'show_progress_bars': adhd_settings.show_progress_bars,
                'enable_task_chunking': adhd_settings.enable_task_chunking,
                'reduce_animations': adhd_settings.reduce_animations,
            })
        
        form = self.form_class(initial=initial, user=request.user)
        return render(request, self.template_name, {'form': form})
    
    @method_decorator(login_required)
    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        """Handle POST requests: process the form submission."""
        form = self.form_class(request.POST, user=request.user)
        
        if form.is_valid():
            self._save_settings(request, form.cleaned_data)
            messages.success(request, _('Your accessibility settings have been saved.'))
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('accessibility:settings')
        
        # Form is invalid
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        
        return render(request, self.template_name, {'form': form})
    
    def _save_settings(self, request, cleaned_data):
        """Save the accessibility settings to the database and session."""
        # Save to database
        self._save_to_database(request.user, cleaned_data)
        
        # Save to session for immediate effect
        self._save_to_session(request, cleaned_data)
    
    def _save_to_database(self, user, data):
        """Save settings to the database."""
        # Save to AccessibilitySettings
        if hasattr(user, 'accessibilitysettings'):
            settings = user.accessibilitysettings
        else:
            settings = AccessibilitySettings(user=user)
        
        # Update settings
        settings.high_contrast = data.get('high_contrast', False)
        settings.keyboard_nav = data.get('keyboard_nav', False)
        settings.screen_reader = data.get('screen_reader', False)
        settings.animations = data.get('animations', True)
        settings.reduced_motion = data.get('reduced_motion', False)
        settings.save()
        
        # Save to DyslexiaSettings if exists
        if hasattr(user, 'dyslexiasettings'):
            dys_settings = user.dyslexiasettings
            dys_settings.font_family = 'open_dyslexic' if data.get('dyslexia_font') else 'default'
            dys_settings.font_size = data.get('font_size', 16)
            dys_settings.line_spacing = data.get('line_spacing', 1.5)
            dys_settings.letter_spacing = data.get('letter_spacing', 0.12)
            dys_settings.word_spacing = data.get('word_spacing', 0.16)
            dys_settings.enable_text_to_speech = data.get('enable_text_to_speech', False)
            dys_settings.enable_spelling_assistance = data.get('enable_spelling_assistance', False)
            dys_settings.enable_grammar_assistance = data.get('enable_grammar_assistance', False)
            dys_settings.simplified_language = data.get('simplified_language', False)
            dys_settings.save()
        
        # Save to ADHDSettings if exists
        if hasattr(user, 'adhdsettings'):
            adhd_settings = user.adhdsettings
            adhd_settings.enable_focus_mode = data.get('enable_focus_mode', False)
            adhd_settings.enable_white_noise = data.get('enable_white_noise', False)
            adhd_settings.enable_break_reminders = data.get('enable_break_reminders', False)
            adhd_settings.show_visual_timers = data.get('show_visual_timers', True)
            adhd_settings.show_progress_bars = data.get('show_progress_bars', True)
            adhd_settings.enable_task_chunking = data.get('enable_task_chunking', True)
            adhd_settings.reduce_animations = data.get('reduce_animations', False)
            adhd_settings.save()
    
    def _save_to_session(self, request, data):
        """Save settings to the session."""
        for key, value in data.items():
            request.session[key] = value
        
        # Set session expiry to 1 year
        request.session.set_expiry(31536000)  # 1 year in seconds
        
        # Mark session as modified to ensure it gets saved
        request.session.modified = True


@method_decorator(login_required, name='dispatch')
@method_decorator(require_http_methods(["POST"]), name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ToggleSettingView(View):
    """API endpoint to toggle a specific accessibility setting."""
    # List of valid boolean settings that can be toggled
    valid_boolean_settings = [
        'high_contrast', 'dyslexia_font', 'keyboard_nav', 'screen_reader',
        'animations', 'reduced_motion', 'enable_focus_mode', 'enable_white_noise',
        'enable_break_reminders', 'show_visual_timers', 'show_progress_bars',
        'enable_task_chunking', 'enable_text_to_speech', 'enable_spelling_assistance',
        'enable_grammar_assistance', 'simplified_language', 'dark_mode', 'enable_toolbar'
    ]
    
    def post(self, request, setting_name, *args, **kwargs):
        """Handle POST request to toggle a setting."""
        if setting_name not in self.valid_boolean_settings:
            return JsonResponse(
                {'success': False, 'message': 'Invalid setting'}, 
                status=400
            )
        
        try:
            # Get the value from the request body if it's a JSON request
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body)
                    new_value = data.get('value')
                    if new_value is None:
                        raise ValueError("Value not provided")
                except (json.JSONDecodeError, ValueError):
                    return JsonResponse(
                        {'success': False, 'message': 'Invalid request data'}, 
                        status=400
                    )
            else:
                # For form data, toggle the current value
                current_value = request.session.get(setting_name, False)
                new_value = not current_value
            
            # Update the setting in session
            request.session[setting_name] = new_value
            
            # Save to database
            self._save_to_database(request.user, setting_name, new_value)
            
            # Set session expiry to 1 year
            request.session.set_expiry(31536000)  # 1 year in seconds
            request.session.modified = True
            
            # Return success response
            return JsonResponse({
                'success': True, 
                'message': f'Setting {setting_name} updated successfully',
                'setting': setting_name, 
                'value': new_value
            })
            
        except Exception as e:
            return JsonResponse(
                {'success': False, 'message': str(e)}, 
                status=500
            )
    
    def _save_to_database(self, user, setting_name, value):
        """Save the setting to the appropriate model in the database."""
        try:
            # Check which model this setting belongs to
            if hasattr(user, 'accessibilitysettings') and hasattr(user.accessibilitysettings, setting_name):
                setattr(user.accessibilitysettings, setting_name, value)
                user.accessibilitysettings.save()
            elif hasattr(user, 'dyslexiasettings'):
                # Handle dyslexia-specific settings
                dys_settings = user.dyslexiasettings
                if setting_name == 'dyslexia_font':
                    dys_settings.font_family = 'open_dyslexic' if value else 'default'
                    dys_settings.save()
                elif hasattr(dys_settings, setting_name):
                    setattr(dys_settings, setting_name, value)
                    dys_settings.save()
            elif hasattr(user, 'adhdsettings') and hasattr(user.adhdsettings, setting_name):
                setattr(user.adhdsettings, setting_name, value)
                user.adhdsettings.save()
            else:
                # If setting doesn't exist in any model, create it in AccessibilitySettings
                if not hasattr(user, 'accessibilitysettings'):
                    settings = AccessibilitySettings(user=user)
                else:
                    settings = user.accessibilitysettings
                
                if hasattr(settings, setting_name):
                    setattr(settings, setting_name, value)
                    settings.save()
                    
        except Exception as e:
            # Log the error but don't fail the request
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error saving setting {setting_name}: {str(e)}")
            
        # Handle dyslexia settings separately if not already handled
        if hasattr(user, 'dyslexiasettings') and hasattr(user.dyslexiasettings, setting_name):
            try:
                setattr(user.dyslexiasettings, setting_name, value)
                user.dyslexiasettings.save()
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Error saving dyslexia setting {setting_name}: {str(e)}")
        elif hasattr(user, 'adhdsettings') and hasattr(user.adhdsettings, setting_name):
            setattr(user.adhdsettings, setting_name, value)
            user.adhdsettings.save()


@method_decorator(login_required, name='dispatch')
@method_decorator(require_http_methods(["POST"]), name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class UpdateSettingView(View):
    """API endpoint to update a specific accessibility setting with a value."""
    # Define valid settings and their validation functions
    valid_settings = {
        'font_size': (lambda x: x in ['small', 'medium', 'large', 'xlarge'], 'dyslexiasettings'),
        'text_size': (lambda x: isinstance(x, (int, float)) and 0.5 <= float(x) <= 2.0, 'dyslexiasettings'),
        'color_theme': (lambda x: x in ['default', 'dark', 'light', 'high_contrast', 'sepia', 'blue_light'], 'accessibilitysettings'),
        'font_family': (lambda x: x in ['default', 'open_dyslexic', 'arial', 'verdana', 'tahoma', 'comic_sans', 'times'], 'dyslexiasettings'),
        'line_spacing': (lambda x: isinstance(x, (int, float)) and 1.0 <= float(x) <= 3.0, 'dyslexiasettings'),
        'letter_spacing': (lambda x: isinstance(x, (int, float)) and 0 <= float(x) <= 1.0, 'dyslexiasettings'),
        'word_spacing': (lambda x: isinstance(x, (int, float)) and 0 <= float(x) <= 1.0, 'dyslexiasettings'),
        'tts_voice': (lambda x: isinstance(x, str) and len(x) > 0, 'dyslexiasettings'),
        'tts_speed': (lambda x: isinstance(x, (int, float)) and 0.5 <= float(x) <= 2.0, 'dyslexiasettings'),
        'break_interval': (lambda x: isinstance(x, (int, float)) and x > 0, 'adhdsettings'),
        'break_duration': (lambda x: isinstance(x, (int, float)) and x > 0, 'adhdsettings'),
        'max_task_duration': (lambda x: isinstance(x, (int, float)) and x > 0, 'adhdsettings'),
        'reward_frequency': (lambda x: isinstance(x, (int, float)) and x > 0, 'adhdsettings'),
    }
            
    def post(self, request, setting_name, *args, **kwargs):
        """Handle POST request to update a setting."""
        if setting_name not in self.valid_settings:
            return JsonResponse(
                {'success': False, 'message': 'Invalid setting'}, 
                status=400
            )
            
        try:
            # Get the value from the request
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body)
                    value = data.get('value')
                except json.JSONDecodeError:
                    return JsonResponse(
                        {'success': False, 'message': 'Invalid JSON data'}, 
                        status=400
                    )
            else:
                value = request.POST.get('value')
                
            if value is None:
                return JsonResponse(
                    {'success': False, 'message': 'Value not provided'}, 
                    status=400
                )
                
            # Convert numeric values
            validator, model_name = self.valid_settings[setting_name]
            try:
                if setting_name in ['line_spacing', 'letter_spacing', 'word_spacing', 'tts_speed', 
                                  'break_interval', 'break_duration', 'max_task_duration', 'reward_frequency']:
                    value = float(value)
                elif setting_name in ['font_size'] and isinstance(value, str) and value.replace('.', '').isdigit():
                    value = float(value)
            except (ValueError, TypeError):
                pass
                
            # Validate the value
            if not validator(value):
                return JsonResponse(
                    {'success': False, 'message': f'Invalid value for {setting_name}'}, 
                    status=400
                )
                
            # Update the setting in session
            request.session[setting_name] = value
                
            # Set session expiry to 1 year
            request.session.set_expiry(31536000)
            request.session.modified = True
                
            # Save to database
            self._save_to_database(request.user, setting_name, value, model_name)
                
            return JsonResponse({
                'success': True, 
                'message': f'Setting {setting_name} updated successfully',
                'setting': setting_name, 
                'value': value
            })
                
        except Exception as e:
            # Log the error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating setting {setting_name}: {str(e)}")
                
            return JsonResponse(
                {'success': False, 'message': f'Failed to update setting: {str(e)}'}, 
                status=500
            )
            
    def _save_to_database(self, user, setting_name, value, model_name):
        """Save the setting to the appropriate model in the database."""
        try:
            # Get or create the model instance
            if not hasattr(user, model_name):
                if model_name == 'accessibilitysettings':
                    model = AccessibilitySettings(user=user)
                elif model_name == 'dyslexiasettings':
                    model = DyslexiaSettings(user=user)
                elif model_name == 'adhdsettings':
                    model = ADHDSettings(user=user)
                else:
                    return
            else:
                model = getattr(user, model_name)
                    
            # Special handling for font_family vs dyslexia_font
            if setting_name == 'font_family' and hasattr(model, 'font_family'):
                setattr(model, 'font_family', value)
                setattr(model, 'dyslexia_font', value == 'open_dyslexic')
            else:
                setattr(model, setting_name, value)
                    
            model.save()
                    
            # Update related settings if needed
            if setting_name == 'font_family' and value == 'open_dyslexic':
                user.dyslexiasettings.dyslexia_font = True
                user.dyslexiasettings.save()
                    
        except Exception as e:
            # Log the error but don't fail the request
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error saving settings: {str(e)}")
            
            return JsonResponse({
                'success': False,
                'message': f'Failed to save settings: {str(e)}'
            }, status=500)
    
    def _update_database_settings(self, user, settings_data):
        """Update database with the provided settings."""
        try:
            # Update AccessibilitySettings
            if hasattr(user, 'accessibilitysettings'):
                acc_settings = user.accessibilitysettings
                
                # Boolean fields
                for field in ['high_contrast', 'keyboard_nav', 'screen_reader', 
                             'animations', 'reduced_motion']:
                    if field in settings_data:
                        setattr(acc_settings, field, settings_data[field])
                
                # Special fields
                if 'dark_mode' in settings_data:
                    acc_settings.dark_mode = settings_data['dark_mode']
                
                acc_settings.save()
            
            # Update DyslexiaSettings
            if hasattr(user, 'dyslexiasettings'):
                dys_settings = user.dyslexiasettings
                
                # Font settings
                if 'font_family' in settings_data:
                    dys_settings.font_family = settings_data['font_family']
                    dys_settings.dyslexia_font = (settings_data['font_family'] == 'open_dyslexic')
                
                # Spacing settings
                for field in ['font_size', 'line_spacing', 'letter_spacing', 'word_spacing', 'tts_speed']:
                    if field in settings_data:
                        setattr(dys_settings, field, settings_data[field])
                
                dys_settings.save()
            
            # Update ADHDSettings if they exist
            if hasattr(user, 'adhdsettings'):
                adhd_settings = user.adhdsettings
                
                # ADHD-specific settings
                for field in ['enable_focus_mode', 'enable_white_noise', 'enable_break_reminders',
                             'show_visual_timers', 'show_progress_bars', 'enable_task_chunking',
                             'reduce_animations']:
                    if field in settings_data:
                        setattr(adhd_settings, field, settings_data[field])
                
                adhd_settings.save()
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating database settings: {str(e)}")
            raise


@method_decorator(login_required, name='dispatch')
class GetSettingsView(View):
    """View to get all current settings."""
    
    def get(self, request, *args, **kwargs):
        """Handle GET request to retrieve all settings."""
        try:
            # Get settings from session
            settings = {
                'high_contrast': request.session.get('high_contrast', False),
                'dark_mode': request.session.get('dark_mode', False),
                'text_size': request.session.get('text_size', '1'),
                'dyslexia_font': request.session.get('dyslexia_font', False),
                'keyboard_nav': request.session.get('keyboard_nav', True),
                'screen_reader': request.session.get('screen_reader', False),
                'animations': request.session.get('animations', True),
                'reduced_motion': request.session.get('reduced_motion', False),
                'enable_toolbar': request.session.get('enable_toolbar', True),
                'color_blind': request.session.get('color_blind', 'none'),
                'font_family': request.session.get('font_family', 'default'),
                'line_spacing': float(request.session.get('line_spacing', 1.5)),
                'letter_spacing': float(request.session.get('letter_spacing', 0.12)),
                'word_spacing': float(request.session.get('word_spacing', 0.16)),
                'tts_speed': float(request.session.get('tts_speed', 1.0)),
            }
            
            # If no settings in session, try to get from database
            if not any(settings.values()):
                settings = self._get_settings_from_database(request.user, settings)
                
                # Save to session for future use
                for key, value in settings.items():
                    request.session[key] = value
                
                request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'settings': settings
            })
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error retrieving settings: {str(e)}")
            
            return JsonResponse({
                'success': False,
                'message': f'Failed to retrieve settings: {str(e)}'
            }, status=500)
    
    def _get_settings_from_database(self, user, default_settings):
        """Get settings from the database."""
        settings = default_settings.copy()
        
        try:
            # Get from AccessibilitySettings
            if hasattr(user, 'accessibilitysettings'):
                acc_settings = user.accessibilitysettings
                settings.update({
                    'high_contrast': acc_settings.high_contrast,
                    'dark_mode': getattr(acc_settings, 'dark_mode', False),
                    'keyboard_nav': acc_settings.keyboard_nav,
                    'screen_reader': acc_settings.screen_reader,
                    'animations': acc_settings.animations,
                    'reduced_motion': acc_settings.reduced_motion,
                })
            
            # Get from DyslexiaSettings
            if hasattr(user, 'dyslexiasettings'):
                dys_settings = user.dyslexiasettings
                settings.update({
                    'dyslexia_font': dys_settings.dyslexia_font,
                    'font_family': dys_settings.font_family,
                    'font_size': dys_settings.font_size,
                    'line_spacing': float(dys_settings.line_spacing),
                    'letter_spacing': float(dys_settings.letter_spacing),
                    'word_spacing': float(dys_settings.word_spacing),
                    'tts_speed': float(getattr(dys_settings, 'tts_speed', 1.0)),
                })
            
            # Get from ADHDSettings if they exist
            if hasattr(user, 'adhdsettings'):
                adhd_settings = user.adhdsettings
                settings.update({
                    'enable_focus_mode': adhd_settings.enable_focus_mode,
                    'enable_white_noise': adhd_settings.enable_white_noise,
                    'enable_break_reminders': adhd_settings.enable_break_reminders,
                    'show_visual_timers': adhd_settings.show_visual_timers,
                    'show_progress_bars': adhd_settings.show_progress_bars,
                    'enable_task_chunking': adhd_settings.enable_task_chunking,
                    'reduce_animations': adhd_settings.reduce_animations,
                })
            
            return settings
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting settings from database: {str(e)}")
            return default_settings


@method_decorator(login_required, name='get')
class QuickAccessPanelView(View):
    """Renders the quick access accessibility panel."""
    template_name = 'accessibility/quick_access_panel.html'
    
    def get(self, request, *args, **kwargs):
        """Handle GET request."""
        # Initialize context with default settings
        context = {
            'settings': {
                # General settings
                'high_contrast': request.session.get('high_contrast', False),
                'dark_mode': request.session.get('dark_mode', False),
                'dyslexia_font': request.session.get('dyslexia_font', False),
                'text_size': request.session.get('text_size', '1'),
                'enable_toolbar': request.session.get('enable_toolbar', True),
                'keyboard_nav': request.session.get('keyboard_nav', True),
                'screen_reader': request.session.get('screen_reader', False),
                'animations': request.session.get('animations', True),
                'reduced_motion': request.session.get('reduced_motion', False),
                'color_blind': request.session.get('color_blind', 'none'),
                
                # Font and spacing
                'font_family': request.session.get('font_family', 'default'),
                'line_spacing': float(request.session.get('line_spacing', 1.5)),
                'letter_spacing': float(request.session.get('letter_spacing', 0.12)),
                'word_spacing': float(request.session.get('word_spacing', 0.16)),
                'tts_speed': float(request.session.get('tts_speed', 1.0)),
                
                # Dyslexia settings
                'enable_text_to_speech': request.session.get('enable_text_to_speech', False),
                'enable_spelling_assistance': request.session.get('enable_spelling_assistance', False),
                'enable_grammar_assistance': request.session.get('enable_grammar_assistance', False),
                'simplified_language': request.session.get('simplified_language', False),
                
                # ADHD settings
                'enable_focus_mode': request.session.get('enable_focus_mode', False),
                'enable_white_noise': request.session.get('enable_white_noise', False),
                'enable_break_reminders': request.session.get('enable_break_reminders', False),
                'show_visual_timers': request.session.get('show_visual_timers', True),
                'show_progress_bars': request.session.get('show_progress_bars', True),
                'enable_task_chunking': request.session.get('enable_task_chunking', True),
                'reduce_animations': request.session.get('reduce_animations', False),
            }
        }
        
        # If no settings in session, try to get from database
        if not any(context['settings'].values()):
            context['settings'].update(self._get_settings_from_database(request.user))
            
            # Save to session for future use
            for key, value in context['settings'].items():
                request.session[key] = value
            request.session.modified = True
            
        return render(request, self.template_name, context)
    
    def _get_settings_from_database(self, user):
        """Get settings from database models."""
        settings = {}
        
        # Get from AccessibilitySettings
        if hasattr(user, 'accessibilitysettings'):
            acc_settings = user.accessibilitysettings
            settings.update({
                'high_contrast': acc_settings.high_contrast,
                'dark_mode': getattr(acc_settings, 'dark_mode', False),
                'keyboard_nav': acc_settings.keyboard_nav,
                'screen_reader': acc_settings.screen_reader,
                'animations': acc_settings.animations,
                'reduced_motion': acc_settings.reduced_motion,
            })
        
        # Get from DyslexiaSettings
        if hasattr(user, 'dyslexiasettings'):
            dys_settings = user.dyslexiasettings
            settings.update({
                'dyslexia_font': dys_settings.dyslexia_font,
                'font_family': dys_settings.font_family,
                'font_size': dys_settings.font_size,
                'line_spacing': float(dys_settings.line_spacing),
                'letter_spacing': float(dys_settings.letter_spacing),
                'word_spacing': float(dys_settings.word_spacing),
                'tts_speed': float(getattr(dys_settings, 'tts_speed', 1.0)),
                'enable_text_to_speech': getattr(dys_settings, 'enable_text_to_speech', False),
                'enable_spelling_assistance': getattr(dys_settings, 'enable_spelling_assistance', False),
                'enable_grammar_assistance': getattr(dys_settings, 'enable_grammar_assistance', False),
                'simplified_language': getattr(dys_settings, 'simplified_language', False),
            })
        
        # Get from ADHDSettings if they exist
        if hasattr(user, 'adhdsettings'):
            adhd_settings = user.adhdsettings
            settings.update({
                'enable_focus_mode': adhd_settings.enable_focus_mode,
                'enable_white_noise': adhd_settings.enable_white_noise,
                'enable_break_reminders': adhd_settings.enable_break_reminders,
                'show_visual_timers': adhd_settings.show_visual_timers,
                'show_progress_bars': adhd_settings.show_progress_bars,
                'enable_task_chunking': adhd_settings.enable_task_chunking,
                'reduce_animations': adhd_settings.reduce_animations,
            })
            
        return settings


class AccessibilityStatementView(View):
    """Renders the accessibility statement page."""
    template_name = 'accessibility/accessibility_statement.html'
    
    def get(self, request, *args, **kwargs):
        """Handle GET request."""
        return render(request, self.template_name)