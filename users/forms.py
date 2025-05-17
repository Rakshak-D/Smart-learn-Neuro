from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, LEARNING_CONDITIONS, FONT_FAMILIES

# Enhanced signup form with all necessary fields
class CustomUserCreationForm(UserCreationForm):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    class_level = forms.CharField(max_length=20, required=True)
    learning_condition = forms.ChoiceField(choices=LEARNING_CONDITIONS, required=True)
    
    class Meta:
        model = CustomUser
        fields = (
            'username', 'name', 'email', 'password1', 'password2',
            'class_level', 'learning_condition'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

# Comprehensive settings form for personalization
class UserSettingsForm(forms.ModelForm):
    font_family = forms.ChoiceField(choices=FONT_FAMILIES, required=False)
    background_color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}), required=False)
    text_color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}), required=False)
    
    class Meta:
        model = CustomUser
        fields = (
            'font_size', 'font_family', 'prefers_audio', 'prefers_chunked',
            'background_color', 'text_color', 'contrast_mode',
            'letter_spacing', 'word_spacing', 'line_height',
            'focus_timer', 'break_duration'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['font_size'].widget.attrs.update({'class': 'form-control', 'min': '12', 'max': '32'})
        self.fields['letter_spacing'].widget.attrs.update({'class': 'form-control', 'step': '0.1'})
        self.fields['word_spacing'].widget.attrs.update({'class': 'form-control', 'step': '0.1'})
        self.fields['line_height'].widget.attrs.update({'class': 'form-control', 'step': '0.1'})
        self.fields['focus_timer'].widget.attrs.update({'class': 'form-control', 'min': '5', 'max': '60'})
        self.fields['break_duration'].widget.attrs.update({'class': 'form-control', 'min': '1', 'max': '15'})
