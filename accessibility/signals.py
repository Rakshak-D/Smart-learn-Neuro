"""
Signals for the accessibility app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import (
    AccessibilitySettings,
    DyslexiaSettings,
    ADHDSettings,
    RewardSystem
)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_accessibility_settings(sender, instance, created, **kwargs):
    """
    Create default accessibility settings when a new user is created.
    """
    if created:
        # Create base accessibility settings
        AccessibilitySettings.objects.create(user=instance)
        
        # Check if user has dyslexia or ADHD
        has_dyslexia = getattr(instance, 'has_dyslexia', False)
        has_adhd = getattr(instance, 'has_adhd', False)
        
        # Create dyslexia-specific settings
        DyslexiaSettings.objects.create(
            user=instance,
            font_family='open_dyslexic' if has_dyslexia else 'default',
            font_size=16,
            font_weight='normal',
            line_spacing=1.5,
            letter_spacing=0.12,
            word_spacing=0.16,
            color_theme='default',
            use_custom_colors=False,
            text_color='#000000',
            background_color='#FFFFFF',
            reading_guide='none',
            reading_guide_color='#FFFF00',
            enable_text_to_speech=has_dyslexia,
            tts_voice='default',
            tts_speed=1.0,
            enable_speech_to_text=False,
            enable_content_chunking=True,
            enable_spelling_assistance=has_dyslexia,
            enable_grammar_assistance=has_dyslexia,
            simplified_language=has_dyslexia
        )
        
        # Create ADHD-specific settings
        ADHDSettings.objects.create(
            user=instance,
            enable_focus_mode=has_adhd,
            focus_level=1,
            enable_white_noise=has_adhd,
            white_noise_type='white',
            enable_break_reminders=has_adhd,
            break_interval=15,
            break_duration=3,
            show_visual_timers=has_adhd,
            show_progress_bars=has_adhd,
            enable_task_chunking=has_adhd,
            max_task_duration=10,
            enable_rewards_system=has_adhd,
            reward_frequency=3,
            reward_animations=True,
            reduce_animations=not has_adhd,
            use_simplified_interface=has_adhd
        )
        
        # Create reward system
        RewardSystem.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_accessibility_settings(sender, instance, **kwargs):
    """
    Save the user's accessibility settings.
    """
    if hasattr(instance, 'accessibilitysettings'):
        instance.accessibilitysettings.save()
    if hasattr(instance, 'dyslexiasettings'):
        instance.dyslexiasettings.save()
    if hasattr(instance, 'adhdsettings'):
        instance.adhdsettings.save()
    if hasattr(instance, 'rewardsystem'):
        instance.rewardsystem.save()
