from django.db import models

class Gesture(models.Model):
    user_id = models.IntegerField()
    gesture_type = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gesture {self.gesture_type} by user {self.user_id}"
