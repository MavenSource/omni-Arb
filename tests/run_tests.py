"""
Test runner - runs all tests
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import test modules
from tests import test_config
from tests import test_utils


def run_all_tests():
    """Run all test suites"""
    print("=" * 60)
    print("OMNI-ARB TEST SUITE")
    print("=" * 60)
    print()
    
    failed = False
    
    # Run configuration tests
    print("Configuration Tests")
    print("-" * 60)
    try:
        test_config.test_default_config()
        test_config.test_config_get()
        test_config.test_config_with_yaml()
    except Exception as e:
        print(f"❌ Configuration tests failed: {e}")
        failed = True
    print()
    
    # Run utility tests
    print("Utility Tests")
    print("-" * 60)
    try:
        test_utils.test_calculate_profit_percentage()
        test_utils.test_format_token_amount()
        test_utils.test_parse_token_amount()
        test_utils.test_is_address()
    except Exception as e:
        print(f"❌ Utility tests failed: {e}")
        failed = True
    print()
    
    # Summary
    print("=" * 60)
    if not failed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
    print("=" * 60)


if __name__ == '__main__':
    run_all_tests()
