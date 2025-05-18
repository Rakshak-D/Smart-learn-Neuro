"""
NLP Service for SmartLearn Neuro
Handles all natural language processing tasks including text analysis, summarization, and more.
"""
import logging
from typing import List, Dict, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class NLPService:
    """Service for handling NLP tasks."""
    
    def __init__(self):
        """Initialize the NLP service with required models."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._load_models()
    
    def _load_models(self):
        """Load NLP models."""
        try:
            # Load spaCy model
            self.nlp = spacy.load('en_core_web_sm')
            
            # Load sentence transformer model
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize TF-IDF vectorizer
            self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
            
            self.logger.info("NLP models loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading NLP models: {e}")
            raise
    
    def get_text_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for a given text.
        
        Args:
            text: Input text
            
        Returns:
            Numpy array containing the text embedding
        """
        try:
            return self.sentence_model.encode(text, convert_to_numpy=True)
        except Exception as e:
            self.logger.error(f"Error generating text embedding: {e}")
            return np.zeros(384)  # Default dimension for all-MiniLM-L6-v2
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Get embeddings for both texts
            embedding1 = self.get_text_embedding(text1)
            embedding2 = self.get_text_embedding(text2)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(
                embedding1.reshape(1, -1),
                embedding2.reshape(1, -1)
            )[0][0]
            
            return float(similarity)
            
        except Exception as e:
            self.logger.error(f"Error calculating text similarity: {e}")
            return 0.0
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[Dict[str, float]]:
        """
        Extract keywords from text using TF-IDF.
        
        Args:
            text: Input text
            top_n: Number of keywords to return
            
        Returns:
            List of dictionaries with keywords and their scores
        """
        try:
            # Fit the vectorizer
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text])
            
            # Get feature names (words)
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            
            # Get TF-IDF scores
            scores = tfidf_matrix.toarray().flatten()
            
            # Sort by score
            sorted_indices = np.argsort(scores)[::-1][:top_n]
            
            # Return top N keywords with scores
            return [
                {'keyword': feature_names[i], 'score': float(scores[i])}
                for i in sorted_indices if scores[i] > 0
            ]
            
        except Exception as e:
            self.logger.error(f"Error extracting keywords: {e}")
            return []
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of a given text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with sentiment scores
        """
        try:
            # This is a simple implementation
            # In production, you might want to use a pre-trained sentiment analysis model
            doc = self.nlp(text)
            
            # Count positive and negative words (simplified example)
            positive_words = ['good', 'great', 'excellent', 'awesome', 'amazing']
            negative_words = ['bad', 'poor', 'terrible', 'awful', 'worst']
            
            pos_count = sum(1 for token in doc if token.text.lower() in positive_words)
            neg_count = sum(1 for token in doc if token.text.lower() in negative_words)
            
            total_words = len(doc)
            
            # Calculate sentiment scores (simplified)
            positive_score = pos_count / total_words if total_words > 0 else 0
            negative_score = neg_count / total_words if total_words > 0 else 0
            
            return {
                'positive': positive_score,
                'negative': negative_score,
                'neutral': max(0, 1 - (positive_score + negative_score)),
                'compound': (positive_score - negative_score)
            }
            
        except Exception as e:
            self.logger.error(f"Error in sentiment analysis: {e}")
            return {
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0,
                'compound': 0.0,
                'error': str(e)
            }

# Singleton instance
nlp_service = NLPService()
