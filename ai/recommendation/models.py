from django.db import models

class Recommendation(models.Model):
    user_id = models.IntegerField()
    lesson_id = models.IntegerField()
    score = models.FloatField()

    def __str__(self):
        return f"Recommendation for user {self.user_id}"
