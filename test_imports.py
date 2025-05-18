import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartLearnNeuro.settings')
django.setup()

# Try to import models
try:
    from ai.models import Topic, LearningPath, LearningSession
    print("Successfully imported AI models!")
except Exception as e:
    print(f"Error importing AI models: {e}")

try:
    from assessments.models import Assessment
    print("Successfully imported Assessment model!")
except Exception as e:
    print(f"Error importing Assessment model: {e}")
