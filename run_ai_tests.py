#!/usr/bin/env python
"""
Test runner for AI services tests.
"""
import os
import sys
import unittest
import argparse
from unittest.runner import TextTestRunner
from django.conf import settings

def setup_django():
    """Configure Django settings for tests."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
    
    import django
    django.setup()

def run_tests(test_labels=None, verbosity=2, failfast=False, interactive=True):
    """Run the test suite.
    
    Args:
        test_labels: List of test labels to run (e.g., ['ai.tests.TestNLPService'])
        verbosity: Verbosity level (0=quiet, 1=normal, 2=verbose)
        failfast: Stop the test run after the first failure
        interactive: Enable interactive mode
    """
    setup_django()
    
    # Default to running all tests if none specified
    if not test_labels:
        test_labels = ['ai.tests']
    
    # Discover and run tests
    loader = unittest.TestLoader()
    test_suite = loader.loadTestsFromNames(test_labels)
    
    # Run tests
    runner = TextTestRunner(verbosity=verbosity, failfast=failfast)
    result = runner.run(test_suite)
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

def main():
    """Main entry point for running tests."""
    parser = argparse.ArgumentParser(description='Run AI service tests')
    parser.add_argument(
        'test_labels', nargs='*',
        help='Test labels to run (e.g., ai.tests.TestNLPService)'
    )
    parser.add_argument(
        '-v', '--verbosity', type=int, default=2,
        help='Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output'
    )
    parser.add_argument(
        '--failfast', action='store_true',
        help='Stop running tests after the first failure'
    )
    parser.add_argument(
        '--no-input', '--noinput', action='store_false', dest='interactive',
        help='Do NOT prompt the user for input of any kind.'
    )
    
    args = parser.parse_args()
    
    # Run tests
    sys.exit(run_tests(
        test_labels=args.test_labels,
        verbosity=args.verbosity,
        failfast=args.failfast,
        interactive=args.interactive
    ))

if __name__ == '__main__':
    main()
