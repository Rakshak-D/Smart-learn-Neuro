from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import AccessibilitySettings

class AccessibilitySettingsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')

    def test_create_accessibility_settings(self):
        settings = AccessibilitySettings.objects.create(user=self.user, use_dyslexia_font=True)
        self.assertTrue(settings.use_dyslexia_font)
        self.assertEqual(str(settings), f"Settings for {self.user.username}")