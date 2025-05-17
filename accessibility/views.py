from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import AccessibilitySettings

@login_required
def accessibility_settings(request):
    # Get or create the AccessibilitySettings instance for the logged-in user
    settings, created = AccessibilitySettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update use_dyslexia_font based on form submission checkbox
        settings.use_dyslexia_font = 'use_dyslexia_font' in request.POST
        settings.save()
        # Redirect to user profile or any other page after saving
        return redirect('profile')
    
    # Render the settings form with current settings
    return render(request, 'accessibility/settings.html', {'settings': settings})
