from django.test import TestCase
from django.urls import reverse
from .models import CustomUser

class CustomUserTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', password='testpass', font_size=18, prefers_audio=True
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.font_size, 18)
        self.assertTrue(self.user.prefers_audio)

    def test_login_view(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to profile