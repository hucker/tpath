"""
Main test runner for TPath modular tests.

This file runs all the individual test modules in the correct order
and provides a summary of test results.
"""

import os
import sys
import importlib.util

# Add the src directory to the path so we can import tpath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def run_test_module(module_name, file_path):
    """Run a test module and capture any errors."""
    print(f"\n{'='*60}")
    print(f"Running {module_name}")
    print(f"{'='*60}")
    
    try:
        # Import and run the test module
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        print(f"✅ {module_name} completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ {module_name} failed with error:")
        print(f"   {type(e).__name__}: {e}")
        return False


def main():
    """Run all test modules."""
    print("TPath Modular Test Suite")
    print("Testing structure matches the class file organization")
    
    # Define test modules in order of dependencies
    test_modules = [
        ("Core Tests", "test_core.py"),
        ("Size Tests", "test_size.py"),
        ("Age Tests", "test_age.py"),
        ("Time Tests", "test_time.py"),
        ("Integration Tests", "test_integration.py"),
    ]
    
    # Get the test directory
    test_dir = os.path.dirname(__file__)
    
    # Run each test module
    results = []
    for module_name, file_name in test_modules:
        file_path = os.path.join(test_dir, file_name)
        
        if os.path.exists(file_path):
            success = run_test_module(module_name, file_path)
            results.append((module_name, success))
        else:
            print(f"⚠️  Warning: Test file {file_name} not found")
            results.append((module_name, False))
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for module_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{module_name:<20} {status}")
    
    print(f"\nTotal: {passed}/{total} test modules passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)