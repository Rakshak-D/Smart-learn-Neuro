"""
Django settings for the SmartLearn project.

This module contains the base settings and imports environment-specific settings.
"""

# Import base settings
from .base import *  # noqa

# Import environment-specific settings
try:
    from .local import *  # noqa
except ImportError:
    pass

# Import test settings if running tests
import sys
if 'test' in sys.argv or 'test_coverage' in sys.argv:
    try:
        from .test import *  # noqa
    except ImportError:
        pass
