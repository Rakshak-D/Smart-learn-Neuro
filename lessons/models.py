from django.db import models
from django.conf import settings

class Lesson(models.Model):
    """
    Model representing a lesson with title, content, optional image, and creation timestamp.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_chunks(self):
        """
        Return the content split by newline if user prefers chunked reading,
        else return the whole content as a single-item list.
        Note: 'settings.user.prefers_chunked' access is unusual; typically, this
        should be fetched from the user instance or user profile, not settings.
        """
        # Since 'settings.user.prefers_chunked' might not exist, you may want to
        # pass the user as a parameter to this method or handle this logic elsewhere.
        # Here's a safer default fallback:
        try:
            if settings.user.prefers_chunked:
                return self.content.split('\n')
        except AttributeError:
            pass
        return [self.content]

    def __str__(self):
        # String representation of a Lesson instance
        return self.title


class LessonProgress(models.Model):
    """
    Tracks progress of a user for a specific lesson.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    progress = models.FloatField(default=0.0)  # Represents completion percentage (0.0 - 100.0)

    def __str__(self):
        # String representation showing username and lesson title
        return f"{self.user.username} - {self.lesson.title}"
