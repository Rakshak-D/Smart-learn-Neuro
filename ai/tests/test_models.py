"""
Tests for AI models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from ai.models import (
    LearningProfile,
    LearningSession,
    EngagementData,
    PerformanceData,
    ContentRecommendation,
)


class TestLearningProfileModel(TestCase):
    """Tests for the LearningProfile model."""

    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.learning_profile = LearningProfile.objects.create(
            user=self.user,
            learning_style="visual",
            proficiency_level=1,
            interests=["programming", "machine learning"],
            goals=["learn python", "build ai applications"],
        )

    def test_learning_profile_creation(self):
        """Test LearningProfile creation and string representation."""
        self.assertEqual(str(self.learning_profile), f"{self.user.username}'s Learning Profile")
        self.assertEqual(self.learning_profile.learning_style, "visual")
        self.assertEqual(self.learning_profile.proficiency_level, 1)
        self.assertEqual(self.learning_profile.interests, ["programming", "machine learning"])
        self.assertEqual(self.learning_profile.goals, ["learn python", "build ai applications"])

    def test_learning_profile_update(self):
        """Test updating LearningProfile."""
        self.learning_profile.learning_style = "auditory"
        self.learning_profile.proficiency_level = 2
        self.learning_profile.save()
        
        updated_profile = LearningProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.learning_style, "auditory")
        self.assertEqual(updated_profile.proficiency_level, 2)


class TestLearningSessionModel(TestCase):
    """Tests for the LearningSession model."""

    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.learning_session = LearningSession.objects.create(
            user=self.user,
            session_id="test_session_123",
            duration_minutes=30,
            content_type="lesson",
            content_id="lesson_1",
            engagement_metrics={"attention": 0.8, "participation": 0.7},
        )

    def test_learning_session_creation(self):
        """Test LearningSession creation and string representation."""
        self.assertEqual(str(self.learning_session), f"{self.user.username}'s session {self.learning_session.session_id}")
        self.assertEqual(self.learning_session.duration_minutes, 30)
        self.assertEqual(self.learning_session.content_type, "lesson")
        self.assertEqual(self.learning_session.content_id, "lesson_1")
        self.assertEqual(self.learning_session.engagement_metrics["attention"], 0.8)


class TestEngagementDataModel(TestCase):
    """Tests for the EngagementData model."""

    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.engagement_data = EngagementData.objects.create(
            user=self.user,
            session_id="test_session_123",
            timestamp=3600,  # 1 hour in seconds
            attention_score=0.85,
            emotion_scores={"happy": 0.7, "neutral": 0.3},
            interaction_events=[
                {"type": "click", "timestamp": 10, "target": "next_button"},
                {"type": "scroll", "timestamp": 20, "position": 50},
            ],
        )

    def test_engagement_data_creation(self):
        """Test EngagementData creation and string representation."""
        self.assertEqual(str(self.engagement_data), f"Engagement data for {self.user.username} at {self.engagement_data.timestamp}")
        self.assertEqual(self.engagement_data.attention_score, 0.85)
        self.assertEqual(self.engagement_data.emotion_scores["happy"], 0.7)
        self.assertEqual(len(self.engagement_data.interaction_events), 2)


class TestPerformanceDataModel(TestCase):
    """Tests for the PerformanceData model."""

    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.performance_data = PerformanceData.objects.create(
            user=self.user,
            assessment_id="assessment_1",
            score=85.5,
            total_questions=10,
            correct_answers=8,
            incorrect_answers=2,
            time_taken_seconds=1200,  # 20 minutes
            topic_scores={"python": 0.9, "django": 0.8, "ai": 0.7},
        )

    def test_performance_data_creation(self):
        """Test PerformanceData creation and string representation."""
        self.assertEqual(str(self.performance_data), f"Performance data for {self.user.username} on {self.performance_data.assessment_id}")
        self.assertEqual(self.performance_data.score, 85.5)
        self.assertEqual(self.performance_data.total_questions, 10)
        self.assertEqual(self.performance_data.correct_answers, 8)
        self.assertEqual(self.performance_data.incorrect_answers, 2)
        self.assertEqual(self.performance_data.time_taken_seconds, 1200)
        self.assertEqual(self.performance_data.topic_scores["python"], 0.9)


class TestContentRecommendationModel(TestCase):
    """Tests for the ContentRecommendation model."""

    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.recommendation = ContentRecommendation.objects.create(
            user=self.user,
            content_type="lesson",
            content_id="lesson_1",
            title="Introduction to Python",
            description="Learn the basics of Python programming",
            score=0.95,
            reason="Based on your interest in programming",
            metadata={"difficulty": "beginner", "duration": 30, "tags": ["python", "programming"]},
        )

    def test_content_recommendation_creation(self):
        """Test ContentRecommendation creation and string representation."""
        self.assertEqual(str(self.recommendation), f"Recommendation for {self.user.username}: {self.recommendation.title}")
        self.assertEqual(self.recommendation.content_type, "lesson")
        self.assertEqual(self.recommendation.content_id, "lesson_1")
        self.assertEqual(self.recommendation.title, "Introduction to Python")
        self.assertEqual(self.recommendation.score, 0.95)
        self.assertEqual(self.recommendation.reason, "Based on your interest in programming")
        self.assertEqual(self.recommendation.metadata["difficulty"], "beginner")
