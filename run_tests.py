#!/usr/bin/env python3
"""
Test runner script for the Tasmota SML Parser project.
Provides convenient commands for running different types of tests.
"""

import subprocess
import sys
import argparse
import os

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True, capture_output=False)
    if result.returncode != 0:
        print(f"❌ {description} failed with exit code {result.returncode}")
        return False
    else:
        print(f"✅ {description} completed successfully")
        return True

def main():
    parser = argparse.ArgumentParser(description="Test runner for Tasmota SML Parser")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--functional", action="store_true", help="Run functional tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--html-report", action="store_true", help="Generate HTML coverage report")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--lint", action="store_true", help="Run linting tools")
    parser.add_argument("--install-deps", action="store_true", help="Install test dependencies")
    
    args = parser.parse_args()
    
    if args.install_deps:
        success = run_command(
            "pip install -r requirements-test.txt",
            "Installing test dependencies"
        )
        if not success:
            sys.exit(1)
    
    if args.lint:
        commands = [
            ("flake8 *.py", "Flake8 linting"),
            ("black --check *.py", "Black formatting check"),
            ("isort --check-only *.py", "Import sorting check"),
        ]
        
        for cmd, desc in commands:
            if not run_command(cmd, desc):
                print("❌ Linting failed")
                sys.exit(1)
        print("✅ All linting checks passed")
    
    # Determine which tests to run
    test_commands = []
    
    if args.unit or args.all:
        test_commands.append(("python -m pytest tests/test_sml_decoder.py -v", "Unit tests (unittest)"))
        test_commands.append(("python -m pytest tests/test_sml_decoder_pytest.py -v", "Unit tests (pytest)"))
    
    if args.integration or args.all:
        test_commands.append(("python -m pytest tests/test_integration.py -v", "Integration tests"))
    
    if args.functional or args.all:
        test_commands.append(("python -m pytest tests/test_app.py -v", "Functional tests (unittest)"))
        test_commands.append(("python -m pytest tests/test_app_pytest.py -v", "Functional tests (pytest)"))
    
    if args.performance:
        test_commands.append(("python -m pytest tests/test_performance.py -v -m slow", "Performance tests"))
    
    if args.coverage:
        coverage_cmd = "python -m pytest tests/ --cov=. --cov-report=term-missing"
        if args.html_report:
            coverage_cmd += " --cov-report=html"
        test_commands.append((coverage_cmd, "Tests with coverage"))
    
    # If no specific test type is selected, run basic tests
    if not any([args.unit, args.integration, args.functional, args.performance, args.coverage, args.all]):
        test_commands = [
            ("python -m unittest discover -s tests -v", "All unittest tests"),
            ("python -m pytest tests/test_sml_decoder_pytest.py tests/test_app_pytest.py -v", "All pytest tests"),
        ]
    
    # Run the tests
    all_passed = True
    for cmd, desc in test_commands:
        if not run_command(cmd, desc):
            all_passed = False
    
    if all_passed:
        print(f"\n{'='*60}")
        print("🎉 All tests passed!")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print("❌ Some tests failed!")
        print(f"{'='*60}")
        sys.exit(1)

if __name__ == "__main__":
    main()
