""
AI Configuration Settings
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Model paths
MODEL_DIR = BASE_DIR / 'ai_models'
MODEL_DIR.mkdir(exist_ok=True)

# Model file paths
RECOMMENDATION_MODEL_PATH = MODEL_DIR / 'recommendation_model.h5'
ENGAGEMENT_MODEL_PATH = MODEL_DIR / 'engagement_model.h5'
SENTENCE_MODEL_NAME = 'all-MiniLM-L6-v2'

# NLP Settings
NLP = {
    'spacy_model': 'en_core_web_sm',
    'sentence_model': 'all-MiniLM-L6-v2',
    'max_seq_length': 128,
    'batch_size': 32
}

# Computer Vision Settings
COMPUTER_VISION = {
    'face_detection_confidence': 0.7,
    'min_face_size': (30, 30),
    'max_face_size': (300, 300),
    'detection_interval': 5  # Process every 5th frame
}

# Adaptive Learning Settings
ADAPTIVE_LEARNING = {
    'default_learning_rate': 0.001,
    'max_learning_rate': 0.01,
    'min_learning_rate': 0.0001,
    'difficulty_adjustment_rate': 0.1,
    'max_difficulty': 1.0,
    'min_difficulty': 0.1
}

# Recommendation Settings
RECOMMENDATION = {
    'similarity_threshold': 0.7,
    'max_recommendations': 5,
    'diversity_weight': 0.3,
    'popularity_weight': 0.2,
    'relevance_weight': 0.5
}

# Engagement Analysis Settings
ENGAGEMENT = {
    'attention_span': 20,  # minutes
    'high_engagement_threshold': 0.7,
    'low_engagement_threshold': 0.3,
    'decay_rate': 0.95,
    'update_interval': 60  # seconds
}

# Caching
CACHING = {
    'enabled': True,
    'default_timeout': 3600,  # 1 hour
    'max_entries': 1000
}

# Logging
LOGGING = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'ai_service.log'
}

def get_model_path(model_name: str) -> str:
    """Get the full path for a model file."""
    return str(MODEL_DIR / model_name)

def ensure_model_directories():
    """Ensure all required model directories exist."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    return MODEL_DIR
