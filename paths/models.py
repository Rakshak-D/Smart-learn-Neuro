from django.db import models
from django.conf import settings

class LearningPath(models.Model):
    title = models.CharField(max_length=200)
    lessons = models.ManyToManyField('lessons.Lesson')  # Many lessons can belong to one path
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class UserPath(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    customized_order = models.JSONField(null=True, blank=True)  # Store custom lesson order as JSON

    def __str__(self):
        return f"{self.user.username} - {self.path.title}"
