from django.db import models
from django.conf import settings

class Assessment(models.Model):
    """
    Model representing an assessment with an optional audio file.
    """
    title = models.CharField(max_length=200)
    audio_file = models.FileField(upload_to='audio/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Response(models.Model):
    """
    Model representing a user's response to an assessment.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    response_text = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.assessment.title}"
