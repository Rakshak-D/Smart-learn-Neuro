"""
Tests for utility functions and helpers.
"""
from django.test import TestCase
from datetime import datetime, timedelta

from ai.utils import (
    calculate_engagement_score,
    generate_session_id,
    validate_email,
    format_duration,
    sanitize_input,
    calculate_progress,
    get_learning_style_icon,
    get_difficulty_label,
    calculate_accuracy,
    format_date,
    generate_random_string,
    validate_url,
    calculate_average_rating,
    paginate_queryset,
    get_client_ip,
    is_valid_uuid,
    calculate_percentage
)

class TestUtils(TestCase):
    """Tests for utility functions."""

    def test_calculate_engagement_score(self):
        """Test engagement score calculation."""
        metrics = {
            'attention': 0.8,
            'participation': 0.7,
            'interaction': 0.6
        }
        score = calculate_engagement_score(metrics)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_generate_session_id(self):
        """Test session ID generation."""
        session_id = generate_session_id()
        self.assertIsInstance(session_id, str)
        self.assertEqual(len(session_id), 32)

    def test_validate_email(self):
        """Test email validation."""
        self.assertTrue(validate_email("test@example.com"))
        self.assertFalse(validate_email("invalid-email"))

    def test_format_duration(self):
        """Test duration formatting."""
        self.assertEqual(format_duration(90), "1h 30m")
        self.assertEqual(format_duration(45), "45m")
        self.assertEqual(format_duration(3720), "2h 2m")

    def test_sanitize_input(self):
        """Test input sanitization."""
        self.assertEqual(sanitize_input("<script>alert('xss')</script>"), "alert('xss')")
        self.assertEqual(sanitize_input("  trim  "), "trim")

    def test_calculate_progress(self):
        """Test progress calculation."""
        self.assertEqual(calculate_progress(5, 10), 50.0)
        self.assertEqual(calculate_progress(0, 10), 0.0)
        self.assertEqual(calculate_progress(10, 0), 0.0)

    def test_get_learning_style_icon(self):
        """Test learning style icon mapping."""
        self.assertEqual(get_learning_style_icon("visual"), "eye")
        self.assertEqual(get_learning_style_icon("auditory"), "volume-up")
        self.assertEqual(get_learning_style_icon("kinesthetic"), "hand-pointer")
        self.assertEqual(get_learning_style_icon("unknown"), "book")

    def test_get_difficulty_label(self):
        """Test difficulty label mapping."""
        self.assertEqual(get_difficulty_label(1), "Beginner")
        self.assertEqual(get_difficulty_label(2), "Intermediate")
        self.assertEqual(get_difficulty_label(3), "Advanced")
        self.assertEqual(get_difficulty_label(4), "Expert")
        self.assertEqual(get_difficulty_label(5), "Master")

    def test_calculate_accuracy(self):
        """Test accuracy calculation."""
        self.assertEqual(calculate_accuracy(8, 2), 80.0)
        self.assertEqual(calculate_accuracy(0, 0), 0.0)
        self.assertEqual(calculate_accuracy(10, 0), 100.0)

    def test_format_date(self):
        """Test date formatting."""
        test_date = datetime(2023, 5, 15, 14, 30, 0)
        self.assertEqual(format_date(test_date), "May 15, 2023")

    def test_generate_random_string(self):
        """Test random string generation."""
        random_str = generate_random_string(10)
        self.assertEqual(len(random_str), 10)
        self.assertTrue(isinstance(random_str, str))

    def test_validate_url(self):
        """Test URL validation."""
        self.assertTrue(validate_url("https://example.com"))
        self.assertFalse(validate_url("not-a-url"))

    def test_calculate_average_rating(self):
        """Test average rating calculation."""
        ratings = [4, 5, 3, 4, 5]
        self.assertEqual(calculate_average_rating(ratings), 4.2)
        self.assertIsNone(calculate_average_rating([]))

    def test_paginate_queryset(self):
        """Test queryset pagination."""
        queryset = list(range(1, 26))  # 1-25
        page = 2
        page_size = 10
        
        result = paginate_queryset(queryset, page, page_size)
        self.assertEqual(result['results'], list(range(11, 21)))
        self.assertEqual(result['total_pages'], 3)
        self.assertEqual(result['total_items'], 25)
        self.assertEqual(result['current_page'], 2)

    def test_get_client_ip(self):
        """Test client IP extraction."""
        request = type('Request', (), {
            'META': {'HTTP_X_FORWARDED_FOR': '192.168.1.1, 10.0.0.1'}
        })
        self.assertEqual(get_client_ip(request), '192.168.1.1')

    def test_is_valid_uuid(self):
        """Test UUID validation."""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        invalid_uuid = "not-a-uuid"
        self.assertTrue(is_valid_uuid(valid_uuid))
        self.assertFalse(is_valid_uuid(invalid_uuid))

    def test_calculate_percentage(self):
        """Test percentage calculation."""
        self.assertEqual(calculate_percentage(25, 100), 25.0)
        self.assertEqual(calculate_percentage(1, 3), 33.33)
        self.assertEqual(calculate_percentage(0, 0), 0.0)
