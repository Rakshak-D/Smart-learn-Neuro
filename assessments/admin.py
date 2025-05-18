from django.contrib import admin
from django.apps import apps

# Get models using string references to avoid circular imports
Assessment = apps.get_model('assessments', 'Assessment')
UserResponse = apps.get_model('assessments', 'UserResponse')

# Register Assessment and UserResponse models with the Django admin site
admin.site.register(Assessment)
admin.site.register(UserResponse)
