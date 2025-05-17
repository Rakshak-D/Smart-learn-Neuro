import os
from gtts import gTTS
import tempfile
from django.conf import settings
import json

class TextToSpeechConverter:
    @staticmethod
    def convert(text, user):
        """Convert text to speech with personalized settings"""
        # Get user's preferred audio settings
        settings = TextToSpeechConverter._get_user_settings(user)
        
        # Create temporary file for audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_file.close()
        
        # Convert text to speech
        tts = gTTS(
            text=text,
            lang='en',
            slow=settings['slow'],
            tld=settings['tld']
        )
        
        # Save audio
        tts.save(temp_file.name)
        
        # Return audio information
        return {
            'url': f'/media/audio/{os.path.basename(temp_file.name)}',
            'duration': TextToSpeechConverter._estimate_duration(text),
            'temp_file': temp_file.name
        }
    
    @staticmethod
    def process_gesture(gesture, user):
        """Process gesture and return appropriate audio response"""
        # Map gestures to responses
        gesture_responses = {
            'confused': "I see you're having trouble. Let me explain that again in a simpler way.",
            'stuck': "Take a deep breath. I'll break this down into smaller steps for you.",
            'bored': "Let's try a different approach. I'll make this more engaging for you.",
            'focused': "Great job! You're doing well. Keep going!"
        }
        
        # Get response text
        response_text = gesture_responses.get(gesture, "I'm here to help. What would you like to know?")
        
        # Convert to speech
        audio = TextToSpeechConverter.convert(response_text, user)
        
        return {
            'text': response_text,
            'audio_url': audio['url'],
            'duration': audio['duration']
        }
    
    @staticmethod
    def _get_user_settings(user):
        """Get personalized text-to-speech settings"""
        return {
            'slow': user.learning_condition == 'DYSLEXIA',  # Slower speech for dyslexia
            'tld': 'com' if user.learning_condition == 'NORMAL' else 'co.uk',  # UK accent for dyslexia
        }
    
    @staticmethod
    def _estimate_duration(text):
        """Estimate audio duration based on text length"""
        words = len(text.split())
        # Average speaking rate: 125-150 words per minute
        rate = 125 if user.learning_condition == 'DYSLEXIA' else 150
        return (words / rate) * 60  # Convert to seconds
