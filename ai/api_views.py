"""
API Views for AI Services
"""
import logging
import base64
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.files.base import ContentFile
from django.core.cache import cache

from .orchestrator import ai_orchestrator
from .serializers import (
    TextSimilaritySerializer,
    KeywordExtractionSerializer,
    SentimentAnalysisSerializer,
    EngagementAnalysisSerializer
)

logger = logging.getLogger(__name__)

class BaseAIView(APIView):
    """Base view for AI endpoints."""
    permission_classes = [IsAuthenticated]
    
    def handle_exception(self, exc):
        """Handle exceptions and return appropriate responses."""
        logger.error(f"Error in {self.__class__.__name__}: {str(exc)}", exc_info=True)
        return Response(
            {"error": "An error occurred while processing your request."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class TextSimilarityView(BaseAIView):
    """API endpoint for calculating text similarity."""
    
    def post(self, request):
        """Calculate similarity between two texts."""
        serializer = TextSimilaritySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        text1 = serializer.validated_data['text1']
        text2 = serializer.validated_data['text2']
        
        try:
            similarity = ai_orchestrator.calculate_similarity(text1, text2)
            return Response({"similarity": float(similarity)})
        except Exception as e:
            logger.error(f"Error calculating text similarity: {e}")
            return Response(
                {"error": "Failed to calculate text similarity"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class KeywordExtractionView(BaseAIView):
    """API endpoint for extracting keywords from text."""
    
    def post(self, request):
        """Extract keywords from text."""
        serializer = KeywordExtractionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        text = serializer.validated_data['text']
        top_n = serializer.validated_data.get('top_n', 10)
        
        try:
            keywords = ai_orchestrator.extract_keywords(text, top_n)
            return Response({"keywords": keywords})
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return Response(
                {"error": "Failed to extract keywords"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SentimentAnalysisView(BaseAIView):
    """API endpoint for analyzing text sentiment."""
    
    def post(self, request):
        """Analyze sentiment of the given text."""
        serializer = SentimentAnalysisSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        text = serializer.validated_data['text']
        
        try:
            sentiment = ai_orchestrator.analyze_sentiment(text)
            return Response(sentiment)
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return Response(
                {"error": "Failed to analyze sentiment"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class EngagementAnalysisView(BaseAIView):
    """API endpoint for analyzing user engagement."""
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def post(self, request):
        """Analyze user engagement from video frame and interaction data."""
        serializer = EngagementAnalysisSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        video_frame = None
        interaction_data = serializer.validated_data.get('interaction_data')
        
        # Process video frame if provided
        if 'video_frame' in request.FILES:
            try:
                # Read and decode the image
                image_file = request.FILES['video_frame']
                image_data = image_file.read()
                nparr = np.frombuffer(image_data, np.uint8)
                video_frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            except Exception as e:
                logger.error(f"Error processing video frame: {e}")
                return Response(
                    {"error": "Invalid image file"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            result = ai_orchestrator.analyze_engagement(
                video_frame=video_frame,
                interaction_data=interaction_data
            )
            return Response(result)
        except Exception as e:
            logger.error(f"Error analyzing engagement: {e}")
            return Response(
                {"error": "Failed to analyze engagement"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AdaptiveLearningView(BaseAIView):
    """API endpoint for adaptive learning features."""
    
    def get(self, request):
        """Get personalized learning recommendations."""
        try:
            adaptive_engine = ai_orchestrator.get_adaptive_engine(request.user)
            recommendations = adaptive_engine.get_personalized_lessons()
            return Response({"recommendations": recommendations})
        except Exception as e:
            logger.error(f"Error getting learning recommendations: {e}")
            return Response(
                {"error": "Failed to get learning recommendations"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TextToSpeechView(BaseAIView):
    """API endpoint for text-to-speech conversion."""
    
    def post(self, request):
        """Convert text to speech."""
        text = request.data.get('text', '')
        if not text:
            return Response(
                {"error": "Text is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Generate speech (placeholder - implement actual TTS)
            audio_data = b""  # Replace with actual TTS generation
            
            return Response({
                "audio": base64.b64encode(audio_data).decode('utf-8'),
                "format": "audio/mp3"
            })
        except Exception as e:
            logger.error(f"Error in text-to-speech conversion: {e}")
            return Response(
                {"error": "Failed to convert text to speech"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
