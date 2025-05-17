from django.contrib import admin
from .models import CustomUser

# Register the CustomUser model to appear in the Django admin site
admin.site.register(CustomUser)
