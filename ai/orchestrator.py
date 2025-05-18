"""
AI Service Orchestrator for SmartLearn Neuro
Coordinates all AI services and provides a unified interface.
"""
import logging
from typing import Dict, Any, Optional, List
import numpy as np

from .nlp_service import NLPService
from .computer_vision import EngagementAnalyzer, FaceDetector
from .enhanced_adaptive_engine import EnhancedAdaptiveEngine
from .config import (
    MODEL_DIR, RECOMMENDATION_MODEL_PATH, ENGAGEMENT_MODEL_PATH,
    NLP, COMPUTER_VISION, ADAPTIVE_LEARNING, RECOMMENDATION, ENGAGEMENT
)
from users.models import CustomUser

logger = logging.getLogger(__name__)

class AIOrchestrator:
    """Orchestrates all AI services for SmartLearn Neuro."""
    
    _instance = None
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(AIOrchestrator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the AI orchestrator."""
        if self._initialized:
            return
            
        self._initialized = True
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all AI services."""
        try:
            logger.info("Initializing AI services...")
            
            # Initialize NLP service
            self.nlp = NLPService()
            
            # Initialize Computer Vision services
            self.face_detector = FaceDetector(
                min_detection_confidence=COMPUTER_VISION['face_detection_confidence']
            )
            self.engagement_analyzer = EngagementAnalyzer()
            
            logger.info("AI services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI services: {e}")
            raise
    
    def get_adaptive_engine(self, user: CustomUser) -> EnhancedAdaptiveEngine:
        """Get an adaptive learning engine instance for a user."""
        try:
            return EnhancedAdaptiveEngine(user)
        except Exception as e:
            logger.error(f"Failed to create adaptive engine: {e}")
            raise
    
    def analyze_engagement(self, video_frame: Optional[np.ndarray] = None, 
                          interaction_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze user engagement.
        
        Args:
            video_frame: Optional video frame for visual analysis
            interaction_data: Optional interaction metrics
            
        Returns:
            Engagement analysis results
        """
        try:
            if video_frame is not None:
                return self.engagement_analyzer.analyze_frame(video_frame)
            return {"success": False, "error": "No video frame provided"}
        except Exception as e:
            logger.error(f"Engagement analysis failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_text_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a given text."""
        return self.nlp.get_text_embedding(text)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        return self.nlp.calculate_similarity(text1, text2)
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[Dict[str, float]]:
        """Extract keywords from text."""
        return self.nlp.extract_keywords(text, top_n)
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of a given text."""
        return self.nlp.analyze_sentiment(text)

# Global instance
ai_orchestrator = AIOrchestrator()
