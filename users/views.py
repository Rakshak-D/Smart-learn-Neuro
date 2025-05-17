from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils import timezone
from django.db.models import Q
from .models import CustomUser, LEARNING_CONDITIONS
from .forms import CustomUserCreationForm, UserSettingsForm
from .serializers import CustomUserSerializer
from SmartLearnNeuro.ai.models import LearningPath, AssessmentResult
from SmartLearnNeuro.ai.utils import AdaptiveLearningEngine, TextToSpeechConverter
from SmartLearnNeuro.lessons.models import Lesson, Topic
from SmartLearnNeuro.assessments.models import Assessment, AssessmentQuestion
from SmartLearnNeuro.accessibility.models import AccessibilitySettings
import json

def login_view(request):
    """
    Handle user login with accessibility support.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Update last active time
            user.last_active = timezone.now()
            user.save()
            return redirect('profile')
        messages.error(request, "Invalid username or password.")
    return render(request, 'users/login.html', {
        'title': 'Login',
        'page_description': 'Welcome back! Please login to continue.'
    })

def register_view(request):
    """
    Handle user registration with personalized settings.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Initialize default settings based on learning condition
            if user.learning_condition == 'DYSLEXIA':
                user.font_family = 'OpenDyslexic'
                user.letter_spacing = 1.2
                user.word_spacing = 1.2
                user.line_height = 1.8
            elif user.learning_condition == 'ADHD':
                user.focus_timer = 20
                user.break_duration = 5
            user.save()
            
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {
        'form': form,
        'title': 'Register',
        'page_description': 'Create your personalized learning profile'
    })

@login_required
def profile_view(request):
    """
    Render the profile page with personalized learning dashboard.
    """
    user = request.user
    
    # Get recent assessments and progress
    recent_assessments = AssessmentResult.objects.filter(
        user=user
    ).order_by('-created_at')[:5]
    
    # Get current learning path
    learning_path = LearningPath.objects.filter(user=user).first()
    current_topic = None
    if learning_path:
        current_topic = learning_path.current_topic
    
    # Get recommended settings based on learning condition
    recommendations = {
        'font_size': user.font_size,
        'font_family': user.font_family,
        'background_color': user.background_color,
        'text_color': user.text_color,
        'letter_spacing': user.letter_spacing,
        'word_spacing': user.word_spacing,
        'line_height': user.line_height,
        'focus_timer': user.focus_timer,
        'break_duration': user.break_duration
    }
    
    return render(request, 'users/profile.html', {
        'user': user,
        'recent_assessments': recent_assessments,
        'current_topic': current_topic,
        'recommendations': recommendations,
        'title': 'Learning Dashboard',
        'page_description': f"Welcome {user.name}, your personalized learning dashboard"
    })

@login_required
def settings_view(request):
    """
    Allow users to update their accessibility and learning preferences.
    """
    user = request.user
    
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Settings updated successfully.")
            # Update user's learning path based on new settings
            if user.learning_condition == 'DYSLEXIA':
                if user.font_family == 'OpenDyslexic':
                    messages.info(request, "Font optimized for dyslexia")
            elif user.learning_condition == 'ADHD':
                if user.focus_timer < 20:
                    messages.warning(request, "Reduced focus time may affect learning")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserSettingsForm(instance=user)
    
    return render(request, 'users/settings.html', {
        'form': form,
        'title': 'Personal Settings',
        'page_description': 'Customize your learning experience'
    })

@login_required
def logout_view(request):
    """
    Handle user logout and save session data.
    """
    user = request.user
    if user.is_authenticated:
        # Save any unsaved progress
        if hasattr(user, 'current_learning_path'):
            user.current_learning_path.save()
        user.last_active = timezone.now()
        user.save()
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

class CustomUserViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for CustomUser model.
    Provides CRUD actions for CustomUser.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]