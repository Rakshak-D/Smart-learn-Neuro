"""
Tests for API serializers.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from ai.models import LearningProfile, LearningSession, EngagementData
from ai.serializers import (
    UserSerializer,
    LearningProfileSerializer,
    LearningSessionSerializer,
    EngagementDataSerializer,
    TextAnalysisSerializer,
    SpeechToTextSerializer,
    ContentModerationSerializer,
    AssessmentSerializer,
    RecommendationSerializer,
    FeedbackSerializer
)

class TestUserSerializer(TestCase):
    """Tests for the UserSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.serializer = UserSerializer

    def test_serialize_user(self):
        """Test serializing a user."""
        user = get_user_model().objects.create_user(**self.user_data)
        serializer = self.serializer(user)
        
        self.assertEqual(serializer.data['username'], self.user_data['username'])
        self.assertEqual(serializer.data['email'], self.user_data['email'])
        self.assertNotIn('password', serializer.data)

    def test_deserialize_user(self):
        """Test deserializing user data."""
        serializer = self.serializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))

    def test_invalid_email(self):
        """Test validation of invalid email."""
        self.user_data['email'] = 'invalid-email'
        serializer = self.serializer(data=self.user_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


class TestLearningProfileSerializer(TestCase):
    """Tests for the LearningProfileSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile_data = {
            'user': self.user.id,
            'learning_style': 'visual',
            'proficiency_level': 2,
            'interests': ['programming', 'ai'],
            'goals': ['learn python', 'build projects']
        }
        self.serializer = LearningProfileSerializer

    def test_serialize_profile(self):
        """Test serializing a learning profile."""
        profile = LearningProfile.objects.create(
            user=self.user,
            learning_style='visual',
            proficiency_level=2,
            interests=['programming', 'ai'],
            goals=['learn python', 'build projects']
        )
        
        serializer = self.serializer(profile)
        self.assertEqual(serializer.data['learning_style'], 'visual')
        self.assertEqual(serializer.data['proficiency_level'], 2)
        self.assertEqual(serializer.data['interests'], ['programming', 'ai'])
        self.assertEqual(serializer.data['goals'], ['learn python', 'build projects'])

    def test_deserialize_profile(self):
        """Test deserializing profile data."""
        serializer = self.serializer(data=self.profile_data)
        self.assertTrue(serializer.is_valid())
        
        profile = serializer.save()
        self.assertEqual(profile.learning_style, 'visual')
        self.assertEqual(profile.proficiency_level, 2)
        self.assertEqual(profile.interests, ['programming', 'ai'])
        self.assertEqual(profile.goals, ['learn python', 'build projects'])

    def test_invalid_learning_style(self):
        """Test validation of invalid learning style."""
        self.profile_data['learning_style'] = 'invalid-style'
        serializer = self.serializer(data=self.profile_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('learning_style', serializer.errors)


class TestTextAnalysisSerializer(TestCase):
    """Tests for the TextAnalysisSerializer."""

    def setUp(self):
        """Set up test data."""
        self.valid_data = {
            'text': 'This is a test sentence for text analysis.',
            'language': 'en',
            'options': {
                'extract_keywords': True,
                'analyze_sentiment': True
            }
        }
        self.serializer = TextAnalysisSerializer

    def test_valid_data(self):
        """Test validation with valid data."""
        serializer = self.serializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_missing_required_field(self):
        """Test validation with missing required field."""
        invalid_data = self.valid_data.copy()
        del invalid_data['text']
        
        serializer = self.serializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('text', serializer.errors)

    def test_invalid_language(self):
        """Test validation with invalid language."""
        invalid_data = self.valid_data.copy()
        invalid_data['language'] = 'invalid-lang'
        
        serializer = self.serializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('language', serializer.errors)


class TestAssessmentSerializer(TestCase):
    """Tests for the AssessmentSerializer."""

    def setUp(self):
        """Set up test data."""
        self.valid_data = {
            'assessment_id': 'test_assessment_1',
            'questions': [
                {
                    'id': 'q1',
                    'question': 'What is 2+2?',
                    'options': ['3', '4', '5', '6'],
                    'correct_answer': '4',
                    'user_answer': '4',
                    'is_correct': True
                },
                {
                    'id': 'q2',
                    'question': 'What is the capital of France?',
                    'options': ['London', 'Berlin', 'Paris', 'Madrid'],
                    'correct_answer': 'Paris',
                    'user_answer': 'London',
                    'is_correct': False
                }
            ],
            'score': 50.0,
            'passed': False
        }
        self.serializer = AssessmentSerializer

    def test_valid_assessment(self):
        """Test validation of valid assessment data."""
        serializer = self.serializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_question_format(self):
        """Test validation of invalid question format."""
        invalid_data = self.valid_data.copy()
        invalid_data['questions'][0].pop('question')
        
        serializer = self.serializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('questions', serializer.errors)

    def test_missing_required_field(self):
        """Test validation with missing required field."""
        invalid_data = self.valid_data.copy()
        del invalid_data['assessment_id']
        
        serializer = self.serializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('assessment_id', serializer.errors)


class TestRecommendationSerializer(TestCase):
    """Tests for the RecommendationSerializer."""

    def setUp(self):
        """Set up test data."""
        self.valid_data = {
            'content_id': 'lesson_1',
            'content_type': 'lesson',
            'title': 'Introduction to Python',
            'description': 'Learn the basics of Python programming',
            'score': 0.95,
            'reason': 'Based on your interest in programming',
            'metadata': {
                'difficulty': 'beginner',
                'duration': 30,
                'tags': ['python', 'programming']
            }
        }
        self.serializer = RecommendationSerializer

    def test_valid_recommendation(self):
        """Test validation of valid recommendation data."""
        serializer = self.serializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_missing_required_field(self):
        """Test validation with missing required field."""
        invalid_data = self.valid_data.copy()
        del invalid_data['content_id']
        
        serializer = self.serializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('content_id', serializer.errors)

    def test_invalid_score_range(self):
        """Test validation of score range."""
        invalid_data = self.valid_data.copy()
        invalid_data['score'] = 1.5  # Invalid, should be between 0 and 1
        
        serializer = self.serializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('score', serializer.errors)
