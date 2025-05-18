"""
Configuration file for pytest.

This file contains fixtures and hooks that are available to all tests.
"""
import os
import shutil
import tempfile
from pathlib import Path

import pytest
from django.conf import settings
from django.test import override_settings

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent


def pytest_configure():
    """Configure pytest with Django settings for tests."""
    # Set up test settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test"
    )

    # Configure Django settings for tests
    settings.configure(
        DEBUG=True,
        TESTING=True,
        SECRET_KEY="test-secret-key",
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
            "rest_framework",
            "rest_framework.authtoken",
            "drf_yasg",
            "ai",
            "users",
            "lessons",
            "assessments",
        ],
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
        ],
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                },
            },
        ],
        REST_FRAMEWORK={
            "DEFAULT_AUTHENTICATION_CLASSES": (
                "rest_framework_simplejwt.authentication.JWTAuthentication",
                "rest_framework.authentication.SessionAuthentication",
            ),
            "DEFAULT_PERMISSION_CLASSES": [
                "rest_framework.permissions.IsAuthenticated",
            ],
            "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
            "PAGE_SIZE": 10,
            "TEST_REQUEST_DEFAULT_FORMAT": "json",
        },
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "unique-snowflake",
            }
        },
        STATIC_URL="/static/",
        MEDIA_URL="/media/",
        MEDIA_ROOT=os.path.join(PROJECT_ROOT, "test_media"),
        STATIC_ROOT=os.path.join(PROJECT_ROOT, "test_static"),
        # Add any other settings you need for testing
    )

    # Create test media directory
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)


def pytest_unconfigure():
    """Clean up after tests."""
    # Clean up test media directory
    if os.path.exists(settings.MEDIA_ROOT):
        shutil.rmtree(settings.MEDIA_ROOT)


@pytest.fixture(scope="session")
def django_db_setup():
    """Set up test database."""
    # This ensures Django's test database is set up once per test session
    pass


@pytest.fixture
def temp_media_root(settings):
    """Temporary media root for file upload tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        settings.MEDIA_ROOT = temp_dir
        yield temp_dir


@pytest.fixture
def api_client():
    """Return an API client for testing."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def admin_client(admin_user):
    """Return a client logged in as an admin user."""
    from rest_framework.test import APIClient
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture
def user(django_user_model):
    """Create and return a test user."""
    return django_user_model.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def auth_client(user):
    """Return an authenticated API client."""
    from rest_framework.test import APIClient
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def nlp_test_data():
    """Return test data for NLP tests."""
    return {
        "text": "This is a test sentence for NLP processing.",
        "similarity_text1": "The quick brown fox jumps over the lazy dog.",
        "similarity_text2": "A quick brown fox jumps over the sleeping dog.",
        "keywords_text": "Python is a popular programming language for data science and machine learning.",
        "sentiment_text_positive": "I love this product! It's amazing!",
        "sentiment_text_negative": "This is terrible. I hate it!",
        "sentiment_text_neutral": "This is a neutral statement.",
    }


@pytest.fixture
def cv_test_image():
    """Return a test image for computer vision tests."""
    # Create a simple 100x100 black image
    from PIL import Image
    import io
    
    img = Image.new('RGB', (100, 100), color='black')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    return img_io


@pytest.fixture
def mock_ai_services(monkeypatch):
    """Mock AI services for testing."""
    # Mock NLP service
    def mock_process_text(self, text):
        return {"processed": True, "text": f"Processed: {text}"}
    
    # Mock computer vision service
    def mock_process_image(self, image):
        return {"processed": True, "result": "face_detected"}
    
    # Mock speech service
    def mock_text_to_speech(self, text):
        return b"mock_audio_data"
    
    # Apply mocks
    from ai.services import NLPService, ComputerVisionService, SpeechService
    monkeypatch.setattr(NLPService, "process_text", mock_process_text)
    monkeypatch.setattr(ComputerVisionService, "process_image", mock_process_image)
    monkeypatch.setattr(SpeechService, "text_to_speech", mock_text_to_speech)


@pytest.fixture
def test_settings():
    """Test settings context manager."""
    return override_settings(
        DEBUG=True,
        TESTING=True,
        SECRET_KEY="test-secret-key",
    )


# Add custom markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test (deselect with '-m "
        "not integration')",
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
