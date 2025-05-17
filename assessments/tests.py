from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Assessment, Response

class AssessmentTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.assessment = Assessment.objects.create(title='Test Assessment')

    def test_create_response(self):
        response = Response.objects.create(
            user=self.user, assessment=self.assessment, response_text='Test response'
        )
        self.assertEqual(response.response_text, 'Test response')
        self.assertEqual(str(response), f"{self.user.username} - {self.assessment.title}")