from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Lesson, LessonProgress

class LessonTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser', password='testpass', prefers_chunked=True
        )
        self.lesson = Lesson.objects.create(title='Test Lesson', content='Line1\nLine2')

    def test_get_chunks(self):
        chunks = self.lesson.get_chunks(self.user)
        self.assertEqual(chunks, ['Line1', 'Line2'])

    def test_lesson_progress(self):
        progress = LessonProgress.objects.create(user=self.user, lesson=self.lesson, progress=50.0)
        self.assertEqual(progress.progress, 50.0)
        self.assertEqual(str(progress), f"{self.user.username} - {self.lesson.title}")