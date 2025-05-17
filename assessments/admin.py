from django.contrib import admin
from .models import Assessment, Response

# Register Assessment and Response models with the Django admin site
admin.site.register(Assessment)
admin.site.register(Response)
