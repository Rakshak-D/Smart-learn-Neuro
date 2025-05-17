from django.contrib import admin
from .models import Lesson, LessonProgress

# Register the Lesson model with the Django admin site
admin.site.register(Lesson)

# Register the LessonProgress model with the Django admin site
admin.site.register(LessonProgress)
