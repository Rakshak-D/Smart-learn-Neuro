"""
Tests for AI services.
"""
import pytest
from unittest.mock import MagicMock, patch

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

from ai.services import (
    NLPService,
    ComputerVisionService,
    SpeechService,
    AdaptiveLearningService,
    ContentModerationService,
)


class TestNLPService(TestCase):
    """Tests for the NLP service."""

    def setUp(self):
        """Set up test data."""
        self.nlp_service = NLPService()
        self.test_text = "This is a test sentence for NLP processing."
        self.test_text2 = "Another test sentence for comparison."

    def test_extract_keywords(self):
        """Test keyword extraction."""
        keywords = self.nlp_service.extract_keywords(self.test_text)
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
        self.assertTrue(all(isinstance(kw, str) for kw in keywords))

    def test_analyze_sentiment(self):
        """Test sentiment analysis."""
        sentiment = self.nlp_service.analyze_sentiment("I love this!")
        self.assertIn("sentiment", sentiment)
        self.assertIn("score", sentiment)
        self.assertIn(sentiment["sentiment"], ["positive", "neutral", "negative"])

    def test_calculate_similarity(self):
        """Test text similarity calculation."""
        similarity = self.nlp_service.calculate_similarity(
            self.test_text, self.test_text2
        )
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)


class TestComputerVisionService(TestCase):
    """Tests for the Computer Vision service."""

    def setUp(self):
        """Set up test data."""
        self.cv_service = ComputerVisionService()
        # Create a simple black image for testing
        from PIL import Image
        import io
        
        self.test_image = Image.new('RGB', (100, 100), color='black')
        self.img_io = io.BytesIO()
        self.test_image.save(self.img_io, format='JPEG')
        self.img_io.seek(0)

    def test_detect_faces(self):
        """Test face detection."""
        result = self.cv_service.detect_faces(self.img_io.getvalue())
        self.assertIsInstance(result, list)
        # In this case, we expect no faces in a black image
        self.assertEqual(len(result), 0)

    def test_analyze_engagement(self):
        """Test engagement analysis."""
        result = self.cv_service.analyze_engagement(self.img_io.getvalue())
        self.assertIsInstance(result, dict)
        self.assertIn("engagement_score", result)
        self.assertIsInstance(result["engagement_score"], float)


class TestSpeechService(TestCase):
    """Tests for the Speech service."""

    def setUp(self):
        """Set up test data."""
        self.speech_service = SpeechService()
        self.test_text = "This is a test sentence for text-to-speech."

    def test_text_to_speech(self):
        """Test text-to-speech conversion."""
        audio_data = self.speech_service.text_to_speech(self.test_text)
        self.assertIsInstance(audio_data, bytes)
        self.assertGreater(len(audio_data), 0)

    def test_get_available_voices(self):
        """Test getting available voices."""
        voices = self.speech_service.get_available_voices()
        self.assertIsInstance(voices, list)
        self.assertGreater(len(voices), 0)
        self.assertTrue(all(isinstance(v, dict) for v in voices))


class TestAdaptiveLearningService(TestCase):
    """Tests for the Adaptive Learning service."""

    def setUp(self):
        """Set up test data."""
        self.learning_service = AdaptiveLearningService()
        self.user_id = "test_user_123"
        self.lesson_data = {
            "lesson_id": "lesson_1",
            "difficulty": "beginner",
            "topics": ["programming", "python"],
            "duration_minutes": 30,
        }

    def test_update_learning_profile(self):
        """Test updating learning profile."""
        result = self.learning_service.update_learning_profile(
            self.user_id, {"preferred_learning_style": "visual"}
        )
        self.assertTrue(result["success"])

    def test_get_recommendations(self):
        """Test getting learning recommendations."""
        recommendations = self.learning_service.get_recommendations(
            self.user_id, limit=3
        )
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 3)


class TestContentModerationService(TestCase):
    """Tests for the Content Moderation service."""

    def setUp(self):
        """Set up test data."""
        self.moderation_service = ContentModerationService()

    def test_moderate_text(self):
        """Test text moderation."""
        # Test with clean text
        result = self.moderation_service.moderate_text("This is a clean text.")
        self.assertIsInstance(result, dict)
        self.assertIn("is_approved", result)
        self.assertTrue(result["is_approved"])
        
        # Test with inappropriate text
        result = self.moderation_service.moderate_text("This is an inappropriate text with bad words.")
        self.assertIsInstance(result, dict)
        self.assertIn("is_approved", result)

    
    def test_moderate_image(self):
        """Test image moderation."""
        # Create a simple black image for testing
        from PIL import Image
        import io
        
        img = Image.new('RGB', (100, 100), color='black')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        result = self.moderation_service.moderate_image(img_io.getvalue())
        self.assertIsInstance(result, dict)
        self.assertIn("is_approved", result)


class TestAIViews(APITestCase):
    """Tests for AI API views."""

    def setUp(self):
        """Set up test data."""
        from django.contrib.auth import get_user_model
        
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get("/api/ai/health/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertEqual(response.data["status"], "healthy")

    @patch("ai.services.NLPService.analyze_sentiment")
    def test_sentiment_analysis(self, mock_analyze):
        """Test sentiment analysis endpoint."""
        mock_analyze.return_value = {"sentiment": "positive", "score": 0.8}
        
        response = self.client.post(
            "/api/ai/text/sentiment/",
            {"text": "I love this!"},
            format="json",
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["sentiment"], "positive")
        mock_analyze.assert_called_once_with("I love this!")

    @patch("ai.services.SpeechService.text_to_speech")
    def test_text_to_speech(self, mock_tts):
        """Test text-to-speech endpoint."""
        mock_tts.return_value = b"mock_audio_data"
        
        response = self.client.post(
            "/api/ai/speech/tts/convert/",
            {"text": "Test text to speech."},
            format="json",
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b"mock_audio_data")
        mock_tts.assert_called_once_with("Test text to speech.")
