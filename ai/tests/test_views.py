"""
Tests for AI API views.
"""
import json
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from ai.models import LearningProfile


class TestHealthCheckView(APITestCase):
    """Tests for the HealthCheckView."""

    def test_health_check(self):
        """Test the health check endpoint."""
        url = reverse('health_check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertIn('timestamp', response.data)
        self.assertIn('version', response.data)


class TestTextAnalysisViews(APITestCase):
    """Tests for text analysis views."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)
        
        # Test data
        self.text_data = {
            'text': 'This is a test sentence for text analysis.'
        }
        self.similarity_data = {
            'text1': 'The quick brown fox jumps over the lazy dog.',
            'text2': 'A quick brown fox jumps over the sleeping dog.'
        }

    @patch('ai.services.NLPService.analyze_sentiment')
    def test_sentiment_analysis(self, mock_analyze):
        """Test sentiment analysis endpoint."""
        # Mock the sentiment analysis result
        mock_analyze.return_value = {
            'sentiment': 'positive',
            'score': 0.85,
            'confidence': 0.95
        }
        
        url = reverse('analyze_sentiment')
        response = self.client.post(url, self.text_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['sentiment'], 'positive')
        self.assertEqual(response.data['score'], 0.85)
        mock_analyze.assert_called_once_with(self.text_data['text'])

    @patch('ai.services.NLPService.extract_keywords')
    def test_keyword_extraction(self, mock_extract):
        """Test keyword extraction endpoint."""
        # Mock the keyword extraction result
        mock_extract.return_value = ['test', 'sentence', 'text', 'analysis']
        
        url = reverse('extract_keywords')
        response = self.client.post(url, self.text_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('keywords', response.data)
        self.assertEqual(len(response.data['keywords']), 4)
        mock_extract.assert_called_once_with(self.text_data['text'])

    @patch('ai.services.NLPService.calculate_similarity')
    def test_text_similarity(self, mock_similarity):
        """Test text similarity endpoint."""
        # Mock the similarity calculation result
        mock_similarity.return_value = 0.75
        
        url = reverse('text_similarity')
        response = self.client.post(url, self.similarity_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('similarity_score', response.data)
        self.assertEqual(response.data['similarity_score'], 0.75)
        mock_similarity.assert_called_once_with(
            self.similarity_data['text1'], 
            self.similarity_data['text2']
        )


class TestSpeechViews(APITestCase):
    """Tests for speech processing views."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)
        
        # Test data
        self.tts_data = {
            'text': 'This is a test for text-to-speech conversion.',
            'voice': 'en-US-Wavenet-D',
            'speed': 1.0
        }

    @patch('ai.services.SpeechService.text_to_speech')
    def test_text_to_speech(self, mock_tts):
        """Test text-to-speech endpoint."""
        # Mock the TTS result
        mock_tts.return_value = b'mock_audio_data'
        
        url = reverse('tts_convert')
        response = self.client.post(url, self.tts_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'mock_audio_data')
        self.assertEqual(response['Content-Type'], 'audio/mpeg')
        mock_tts.assert_called_once_with(
            text=self.tts_data['text'],
            voice=self.tts_data['voice'],
            speed=self.tts_data['speed']
        )

    @patch('ai.services.SpeechService.get_available_voices')
    def test_get_voices(self, mock_voices):
        """Test get available voices endpoint."""
        # Mock the voices list
        mock_voices.return_value = [
            {'name': 'en-US-Wavenet-A', 'language': 'en-US', 'gender': 'FEMALE'},
            {'name': 'en-US-Wavenet-B', 'language': 'en-US', 'gender': 'MALE'},
        ]
        
        url = reverse('tts_voices')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('voices', response.data)
        self.assertEqual(len(response.data['voices']), 2)
        mock_voices.assert_called_once()


class TestComputerVisionViews(APITestCase):
    """Tests for computer vision views."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)
        
        # Create a test image
        from PIL import Image
        import io
        
        self.image = Image.new('RGB', (100, 100), color='red')
        self.image_io = io.BytesIO()
        self.image.save(self.image_io, format='JPEG')
        self.image_io.seek(0)

    @patch('ai.services.ComputerVisionService.detect_faces')
    def test_face_detection(self, mock_detect):
        """Test face detection endpoint."""
        # Mock the face detection result
        mock_detect.return_value = [
            {'bounding_box': [10, 10, 50, 50], 'confidence': 0.99},
        ]
        
        url = reverse('face_detection')
        with open('test_image.jpg', 'wb') as f:
            f.write(self.image_io.getvalue())
        
        with open('test_image.jpg', 'rb') as img:
            response = self.client.post(url, {'image': img}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('faces', response.data)
        self.assertEqual(len(response.data['faces']), 1)
        mock_detect.assert_called_once()

    @patch('ai.services.ComputerVisionService.analyze_engagement')
    def test_engagement_analysis(self, mock_analyze):
        """Test engagement analysis endpoint."""
        # Mock the engagement analysis result
        mock_analyze.return_value = {
            'engagement_score': 0.85,
            'attention_level': 'high',
            'emotions': {'happy': 0.7, 'neutral': 0.3}
        }
        
        url = reverse('engagement_analysis')
        with open('test_image.jpg', 'wb') as f:
            f.write(self.image_io.getvalue())
        
        with open('test_image.jpg', 'rb') as img:
            response = self.client.post(url, {'image': img}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('engagement_score', response.data)
        self.assertEqual(response.data['engagement_score'], 0.85)
        mock_analyze.assert_called_once()


class TestAdaptiveLearningViews(APITestCase):
    """Tests for adaptive learning views."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)
        
        # Create a learning profile for the user
        self.learning_profile = LearningProfile.objects.create(
            user=self.user,
            learning_style='visual',
            proficiency_level=2,
            interests=['programming', 'ai'],
            goals=['learn python', 'build ai apps']
        )
        
        # Test data
        self.assessment_data = {
            'assessment_id': 'test_assessment_1',
            'score': 85.5,
            'total_questions': 10,
            'correct_answers': 8,
            'incorrect_answers': 2,
            'time_taken_seconds': 1200,
            'topic_scores': {
                'python': 0.9,
                'django': 0.7,
                'ai': 0.8
            }
        }

    @patch('ai.services.AdaptiveLearningService.get_recommendations')
    def test_get_recommendations(self, mock_recommend):
        """Test getting learning recommendations."""
        # Mock the recommendations
        mock_recommend.return_value = [
            {
                'content_id': 'lesson_1',
                'content_type': 'lesson',
                'title': 'Introduction to Python',
                'score': 0.95,
                'reason': 'Matches your interest in programming'
            },
            {
                'content_id': 'lesson_2',
                'content_type': 'lesson',
                'title': 'AI Fundamentals',
                'score': 0.88,
                'reason': 'Based on your learning goals'
            }
        ]
        
        url = reverse('learning_recommendations')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recommendations', response.data)
        self.assertEqual(len(response.data['recommendations']), 2)
        mock_recommend.assert_called_once_with(user_id=str(self.user.id), limit=10)

    def test_update_learning_profile(self):
        """Test updating learning profile."""
        url = reverse('update_learning_profile')
        update_data = {
            'learning_style': 'auditory',
            'proficiency_level': 3,
            'interests': ['programming', 'ai', 'machine learning'],
            'goals': ['learn python', 'build ai apps', 'get certified']
        }
        
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.learning_profile.refresh_from_db()
        self.assertEqual(self.learning_profile.learning_style, 'auditory')
        self.assertEqual(self.learning_profile.proficiency_level, 3)
        self.assertIn('machine learning', self.learning_profile.interests)
        self.assertIn('get certified', self.learning_profile.goals)

    @patch('ai.services.AdaptiveLearningService.submit_assessment')
    def test_submit_assessment(self, mock_submit):
        """Test submitting an assessment."""
        # Mock the submission result
        mock_submit.return_value = {
            'success': True,
            'assessment_id': 'test_assessment_1',
            'feedback': 'Good job!',
            'next_steps': ['Review topic X', 'Try practice Y']
        }
        
        url = reverse('submit_assessment')
        response = self.client.post(url, self.assessment_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['assessment_id'], 'test_assessment_1')
        mock_submit.assert_called_once_with(
            user_id=str(self.user.id),
            assessment_data=self.assessment_data
        )
