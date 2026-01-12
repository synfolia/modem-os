#!/usr/bin/env python3
"""
Test runner for MoDEM OS unit tests.

Runs all unit tests and provides a summary of results.
"""

import unittest
import sys
from pathlib import Path


def run_tests(verbose=False):
    """
    Run all unit tests in the tests/ directory.

    Args:
        verbose: If True, show detailed test output

    Returns:
        True if all tests passed, False otherwise
    """
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent / "tests"
    suite = loader.discover(start_dir, pattern="test_*.py")

    # Run tests with appropriate verbosity
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("="*70)

    return result.wasSuccessful()


if __name__ == "__main__":
    # Check for verbose flag
    verbose = "-v" in sys.argv or "--verbose" in sys.argv

    success = run_tests(verbose)
    sys.exit(0 if success else 1)
