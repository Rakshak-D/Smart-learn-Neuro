from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

# This form extends Django's built-in UserCreationForm
# It allows new users to register with our CustomUser model
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser  # Use the custom user model instead of default
        fields = ('username', 'email', 'password1', 'password2')  # Fields to display on registration form


# This form is used for updating user preferences in settings (font size, audio, chunking)
class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = CustomUser  # Again, our custom user model
        fields = ('font_size', 'prefers_audio', 'prefers_chunked')  # Settings related to accessibility and learning preference
