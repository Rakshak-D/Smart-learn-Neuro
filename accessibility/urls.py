from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'profiles', views.AccessibilityProfileViewSet, basename='accessibility_profile')

# Text Settings
text_settings_patterns = [
    path('', views.TextSettingsView.as_view(), name='text_settings'),
    path('fonts/', views.FontListView.as_view(), name='font_list'),
    path('themes/', views.ThemeListView.as_view(), name='theme_list'),
    path('contrast/', views.ContrastSettingsView.as_view(), name='contrast_settings'),
]

# Reading Tools
reading_tools_patterns = [
    path('reader/', views.ReadingToolsView.as_view(), name='reading_tools'),
    path('bookmarks/', views.BookmarkViewSet.as_view(), name='bookmarks'),
    path('highlights/', views.HighlightViewSet.as_view(), name='highlights'),
    path('notes/', views.NoteViewSet.as_view(), name='notes'),
]

# Assistive Technologies
assistive_tech_patterns = [
    path('screen-reader/', views.ScreenReaderView.as_view(), name='screen_reader'),
    path('voice-control/', views.VoiceControlView.as_view(), name='voice_control'),
    path('keyboard-nav/', views.KeyboardNavigationView.as_view(), name='keyboard_nav'),
]

# Learning Support
learning_support_patterns = [
    path('dyslexia/', views.DyslexiaSupportView.as_view(), name='dyslexia_support'),
    path('adhd/', views.ADHDSupportView.as_view(), name='adhd_support'),
    path('visual-impairment/', views.VisualImpairmentView.as_view(), name='visual_impairment'),
    path('hearing-impairment/', views.HearingImpairmentView.as_view(), name='hearing_impairment'),
]

# User Preferences
preferences_patterns = [
    path('save/', views.SavePreferencesView.as_view(), name='save_preferences'),
    path('reset/', views.ResetPreferencesView.as_view(), name='reset_preferences'),
    path('export/', views.ExportPreferencesView.as_view(), name='export_preferences'),
    path('import/', views.ImportPreferencesView.as_view(), name='import_preferences'),
]

# URL Patterns
urlpatterns = [
    # API Endpoints
    path('api/', include(router.urls)),
    
    # Text and Display Settings
    path('text/', include(text_settings_patterns)),
    
    # Reading Tools
    path('reading/', include(reading_tools_patterns)),
    
    # Assistive Technologies
    path('assistive/', include(assistive_tech_patterns)),
    
    # Learning Support
    path('support/', include(learning_support_patterns)),
    
    # User Preferences
    path('preferences/', include(preferences_patterns)),
    
    # Quick Access
    path('quick-access/', include([
        path('toggle-dyslexic-font/', views.ToggleDyslexicFontView.as_view(), name='toggle_dyslexic_font'),
        path('toggle-high-contrast/', views.ToggleHighContrastView.as_view(), name='toggle_high_contrast'),
        path('toggle-tts/', views.ToggleTTSView.as_view(), name='toggle_tts'),
        path('toggle-stt/', views.ToggleSTTView.as_view(), name='toggle_stt'),
        path('toggle-keyboard-nav/', views.ToggleKeyboardNavView.as_view(), name='toggle_keyboard_nav'),
    ])),
    
    # Settings
    path('settings/', views.AccessibilitySettingsView.as_view(), name='accessibility_settings'),
    
    # Help and Documentation
    path('help/', include([
        path('', views.HelpCenterView.as_view(), name='help_center'),
        path('tutorials/', views.TutorialsView.as_view(), name='tutorials'),
        path('faq/', views.FAQView.as_view(), name='faq'),
        path('contact/', views.ContactSupportView.as_view(), name='contact_support'),
    ])),
]
