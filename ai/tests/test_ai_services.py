"""
Tests for AI services
"""
import os
import sys
import logging
import unittest
import numpy as np
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import AI services
try:
    from ai.orchestrator import AIOrchestrator, ai_orchestrator
    from ai.nlp_service import NLPService
    from ai.computer_vision import FaceDetector, EngagementAnalyzer
    from ai.enhanced_adaptive_engine import EnhancedAdaptiveEngine
    from ai.api_views import (
        TextSimilarityView,
        KeywordExtractionView,
        SentimentAnalysisView,
        EngagementAnalysisView,
        AdaptiveLearningView
    )
    AI_SERVICES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Could not import AI services: {e}")
    AI_SERVICES_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the User model
User = get_user_model()

@unittest.skipIf(not AI_SERVICES_AVAILABLE, "AI services not available")
class TestNLPService(TestCase):
    """Test cases for NLP Service"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.nlp_service = NLPService()
    
    def test_text_embedding(self):
        """Test text embedding generation"""
        text = "This is a test sentence for embedding"
        embedding = self.nlp_service.get_text_embedding(text)
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.shape, (384,))  # All-MiniLM-L6-v2 has 384 dimensions
    
    def test_text_similarity(self):
        """Test text similarity calculation"""
        text1 = "I love programming in Python"
        text2 = "Python programming is my favorite"
        text3 = "The weather is nice today"
        
        # Similar texts should have high similarity
        sim1 = self.nlp_service.calculate_similarity(text1, text2)
        self.assertGreaterEqual(sim1, 0.6)  # Should be quite similar
        
        # Dissimilar texts should have low similarity
        sim2 = self.nlp_service.calculate_similarity(text1, text3)
        self.assertLess(sim2, 0.5)  # Should be less similar
        
        # Similarity should be symmetric
        sim3 = self.nlp_service.calculate_similarity(text2, text1)
        self.assertAlmostEqual(sim1, sim3, places=5)
    
    def test_keyword_extraction(self):
        """Test keyword extraction"""
        text = """
        Machine learning is a subset of artificial intelligence that provides systems 
        the ability to automatically learn and improve from experience without being 
        explicitly programmed. Machine learning focuses on the development of computer 
        programs that can access data and use it to learn for themselves.
        """
        keywords = self.nlp_service.extract_keywords(text, top_n=5)
        
        self.assertIsInstance(keywords, list)
        self.assertLessEqual(len(keywords), 5)
        
        # Check that keywords have the expected structure
        for kw in keywords:
            self.assertIn('keyword', kw)
            self.assertIn('score', kw)
            self.assertIsInstance(kw['keyword'], str)
            self.assertIsInstance(kw['score'], float)
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis"""
        positive_text = "I love this product! It works perfectly and was delivered quickly."
        negative_text = "I'm very disappointed with this purchase. It broke after one day."
        neutral_text = "This is a neutral statement without strong sentiment."
        
        # Test positive sentiment
        pos_result = self.nlp_service.analyze_sentiment(positive_text)
        self.assertGreater(pos_result['positive'], pos_result['negative'])
        self.assertGreater(pos_result['compound'], 0.5)
        
        # Test negative sentiment
        neg_result = self.nlp_service.analyze_sentiment(negative_text)
        self.assertGreater(neg_result['negative'], neg_result['positive'])
        self.assertLess(neg_result['compound'], -0.5)
        
        # Test neutral sentiment
        neu_result = self.nlp_service.analyze_sentiment(neutral_text)
        self.assertGreater(neu_result['neutral'], 0.5)
        self.assertTrue(-0.2 < neu_result['compound'] < 0.2)


class TestComputerVision(TestCase):
    """Test cases for Computer Vision services"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not AI_SERVICES_AVAILABLE:
            return
            
        cls.face_detector = FaceDetector()
        cls.engagement_analyzer = EngagementAnalyzer()
    
    def test_face_detection(self, image_path=None):
        """Test face detection"""
        if not AI_SERVICES_AVAILABLE:
            self.skipTest("AI services not available")
            
        # Skip if no test image is provided
        if not image_path:
            self.skipTest("No test image provided for face detection")
            return
            
        import cv2
        try:
            # Load test image
            image = cv2.imread(image_path)
            if image is None:
                self.skipTest(f"Could not load test image: {image_path}")
                return
                
            # Detect faces
            result = self.face_detector.detect_faces(image)
            
            # Check the result
            self.assertTrue(result.success)
            self.assertIsInstance(result.face_count, int)
            self.assertGreaterEqual(result.face_count, 0)
            
            if result.face_count > 0:
                self.assertIsNotNone(result.face_locations)
                self.assertEqual(len(result.face_locations), result.face_count)
                
        except Exception as e:
            self.fail(f"Face detection test failed: {str(e)}")
    
    def test_engagement_analysis(self, image_path=None):
        """Test engagement analysis"""
        if not AI_SERVICES_AVAILABLE:
            self.skipTest("AI services not available")
            
        # Skip if no test image is provided
        if not image_path:
            self.skipTest("No test image provided for engagement analysis")
            return
            
        import cv2
        try:
            # Load test image
            image = cv2.imread(image_path)
            if image is None:
                self.skipTest(f"Could not load test image: {image_path}")
                return
                
            # Analyze engagement
            result = self.engagement_analyzer.analyze_frame(image)
            
            # Check the result
            self.assertIn('success', result)
            self.assertIn('engagement_score', result)
            self.assertIsInstance(result['engagement_score'], float)
            self.assertTrue(0 <= result['engagement_score'] <= 1.0)
            
        except Exception as e:
            self.fail(f"Engagement analysis test failed: {str(e)}")


class TestAIOrchestrator(TestCase):
    """Test cases for AI Orchestrator"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not AI_SERVICES_AVAILABLE:
            return
            
        cls.orchestrator = AIOrchestrator()
        
        # Create a test user
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_get_adaptive_engine(self):
        """Test getting an adaptive learning engine instance"""
        if not AI_SERVICES_AVAILABLE:
            self.skipTest("AI services not available")
            
        engine = self.orchestrator.get_adaptive_engine(self.user)
        self.assertIsInstance(engine, EnhancedAdaptiveEngine)
    
    def test_text_processing(self):
        """Test text processing through the orchestrator"""
        if not AI_SERVICES_AVAILABLE:
            self.skipTest("AI services not available")
            
        text = "This is a test sentence."
        
        # Test text embedding
        embedding = self.orchestrator.get_text_embedding(text)
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.shape, (384,))
        
        # Test text similarity
        similar_text = "This is another test sentence."
        different_text = "The weather is nice today."
        
        sim1 = self.orchestrator.calculate_similarity(text, similar_text)
        sim2 = self.orchestrator.calculate_similarity(text, different_text)
        
        self.assertGreater(sim1, sim2)  # Similar texts should have higher similarity
        
        # Test keyword extraction
        keywords = self.orchestrator.extract_keywords("""
            Machine learning is a subset of artificial intelligence that provides systems 
            the ability to automatically learn and improve from experience.
        """, top_n=3)
        
        self.assertIsInstance(keywords, list)
        self.assertLessEqual(len(keywords), 3)
        
        # Test sentiment analysis
        sentiment = self.orchestrator.analyze_sentiment("I'm very happy with this product!")
        self.assertIn('positive', sentiment)
        self.assertIn('negative', sentiment)
        self.assertIn('neutral', sentiment)
        self.assertIn('compound', sentiment)


class TestAPIEndpoints(APITestCase):
    """Test cases for API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not AI_SERVICES_AVAILABLE:
            return
            
        # Set up test client
        cls.client = APIClient()
        
        # Create a test user
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Authenticate the test client
        cls.client.force_authenticate(user=cls.user)
    
    def test_health_check(self):
        """Test health check endpoint"""
        if not AI_SERVICES_AVAILABLE:
            self.skipTest("AI services not available")
            
        response = self.client.get('/api/ai/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'ok')
    
    def test_text_similarity_endpoint(self):
        """Test text similarity API endpoint"""
        if not AI_SERVICES_AVAILABLE:
            self.skipTest("AI services not available")
            
        data = {
            'text1': 'I love programming in Python',
            'text2': 'Python is my favorite programming language'
        }
        response = self.client.post(
            '/api/ai/text/similarity/', 
            data, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('similarity', response.data)
        self.assertIsInstance(response.data['similarity'], float)
        self.assertTrue(0 <= response.data['similarity'] <= 1.0)
    
    def test_keyword_extraction_endpoint(self):
        """Test keyword extraction API endpoint"""
        if not AI_SERVICES_AVAILABLE:
            self.skipTest("AI services not available")
            
        data = {
            'text': """
                Machine learning is a subset of artificial intelligence that provides systems 
                the ability to automatically learn and improve from experience without being 
                explicitly programmed.
            """,
            'top_n': 3
        }
        response = self.client.post(
            '/api/ai/text/keywords/', 
            data, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('keywords', response.data)
        self.assertIsInstance(response.data['keywords'], list)
        self.assertLessEqual(len(response.data['keywords']), 3)
        
        # Check each keyword has the expected structure
        for kw in response.data['keywords']:
            self.assertIn('keyword', kw)
            self.assertIn('score', kw)
    
    def test_sentiment_analysis_endpoint(self):
        """Test sentiment analysis API endpoint"""
        if not AI_SERVICES_AVAILABLE:
            self.skipTest("AI services not available")
            
        data = {
            'text': 'I am extremely happy with this service! The support team was amazing.'
        }
        response = self.client.post(
            '/api/ai/text/sentiment/', 
            data, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('positive', response.data)
        self.assertIn('negative', response.data)
        self.assertIn('neutral', response.data)
        self.assertIn('compound', response.data)
        
        # Should be positive sentiment
        self.assertGreater(response.data['positive'], response.data['negative'])
        self.assertGreater(response.data['compound'], 0)
    
    def test_adaptive_learning_endpoint(self):
        """Test adaptive learning recommendations endpoint"""
        if not AI_SERVICES_AVAILABLE:
            self.skipTest("AI services not available")
            
        response = self.client.get('/api/ai/learning/recommendations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response structure
        self.assertIn('status', response.data)
        self.assertIn('data', response.data)
        
        if isinstance(response.data['data'], list):
            # If we have recommendations, check their structure
            for rec in response.data['data']:
                self.assertIn('id', rec)
                self.assertIn('title', rec)
                self.assertIn('topic', rec)
                self.assertIn('difficulty', rec)
                self.assertIn('score', rec)
                self.assertIn('url', rec)


if __name__ == '__main__':
    unittest.main()
