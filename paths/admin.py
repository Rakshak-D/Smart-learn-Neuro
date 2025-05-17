from django.contrib import admin
from .models import LearningPath, UserPath

# Register models to appear in Django admin
admin.site.register(LearningPath)
admin.site.register(UserPath)
