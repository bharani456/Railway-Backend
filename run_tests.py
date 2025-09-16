#!/usr/bin/env python3
"""
Test runner script for QR Track Fittings System
Runs all tests with proper configuration and reporting
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run all tests with proper configuration"""
    
    # Set environment variables for testing
    os.environ["TESTING"] = "true"
    os.environ["MONGODB_DATABASE"] = "qr_track_fittings_test"
    
    # Test configuration
    test_args = [
        "python", "-m", "pytest",
        "tests/",
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker handling
        "--disable-warnings",  # Disable warnings
        "--cov=app",  # Coverage reporting
        "--cov-report=html",  # HTML coverage report
        "--cov-report=term-missing",  # Terminal coverage report
        "--cov-fail-under=80",  # Fail if coverage below 80%
        "--junitxml=test-results.xml",  # JUnit XML output
        "--html=test-report.html",  # HTML test report
        "--self-contained-html",  # Self-contained HTML report
    ]
    
    print("🚀 Starting QR Track Fittings System Test Suite")
    print("=" * 60)
    
    try:
        # Run tests
        result = subprocess.run(test_args, check=True)
        
        print("\n✅ All tests passed successfully!")
        print(f"📊 Coverage report generated: htmlcov/index.html")
        print(f"📋 Test report generated: test-report.html")
        print(f"📄 JUnit XML: test-results.xml")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return e.returncode
    except Exception as e:
        print(f"\n💥 Error running tests: {e}")
        return 1

def run_specific_tests(test_pattern):
    """Run specific tests based on pattern"""
    
    os.environ["TESTING"] = "true"
    os.environ["MONGODB_DATABASE"] = "qr_track_fittings_test"
    
    test_args = [
        "python", "-m", "pytest",
        f"tests/{test_pattern}",
        "-v",
        "--tb=short",
        "--disable-warnings"
    ]
    
    print(f"🔍 Running tests matching: {test_pattern}")
    print("=" * 60)
    
    try:
        result = subprocess.run(test_args, check=True)
        print("\n✅ Tests completed successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return e.returncode

def run_performance_tests():
    """Run performance tests"""
    
    os.environ["TESTING"] = "true"
    os.environ["MONGODB_DATABASE"] = "qr_track_fittings_test"
    
    test_args = [
        "python", "-m", "pytest",
        "tests/test_performance.py",
        "-v",
        "--tb=short",
        "--disable-warnings",
        "-s"  # Don't capture output for performance tests
    ]
    
    print("⚡ Running Performance Tests")
    print("=" * 60)
    
    try:
        result = subprocess.run(test_args, check=True)
        print("\n✅ Performance tests completed successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Performance tests failed with exit code {e.returncode}")
        return e.returncode

def main():
    """Main function"""
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "all":
            return run_tests()
        elif command == "auth":
            return run_specific_tests("test_auth.py")
        elif command == "users":
            return run_specific_tests("test_users.py")
        elif command == "qr":
            return run_specific_tests("test_qr_codes.py")
        elif command == "installations":
            return run_specific_tests("test_installations.py")
        elif command == "performance":
            return run_performance_tests()
        elif command == "help":
            print("QR Track Fittings System Test Runner")
            print("=" * 40)
            print("Usage: python run_tests.py [command]")
            print("\nCommands:")
            print("  all          - Run all tests (default)")
            print("  auth         - Run authentication tests")
            print("  users        - Run user management tests")
            print("  qr           - Run QR code tests")
            print("  installations - Run installation tests")
            print("  performance  - Run performance tests")
            print("  help         - Show this help message")
            return 0
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python run_tests.py help' for available commands")
            return 1
    else:
        # Default: run all tests
        return run_tests()

if __name__ == "__main__":
    sys.exit(main())
