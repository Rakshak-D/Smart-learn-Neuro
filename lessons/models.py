from django.db import models
from django.conf import settings

class Lesson(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    audio_file = models.FileField(upload_to='audio/', null=True, blank=True)  # Optional lesson audio
    created_at = models.DateTimeField(auto_now_add=True)

    def get_chunks(self, user):
        """
        Return lesson content as chunks if the user prefers chunked reading,
        otherwise return full content.
        """
        if hasattr(user, 'prefers_chunked') and user.prefers_chunked:
            return self.content.split('\n')
        return [self.content]

    def __str__(self):
        return self.title


class LessonProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    progress = models.FloatField(default=0.0)  # Progress as percentage (0 to 100)

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} ({self.progress}%)"
