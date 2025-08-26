#!/usr/bin/env python3
"""
Test runner script for Skylyt TravelHub Backend
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*50}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"❌ {description} failed with return code {result.returncode}")
        return False
    else:
        print(f"✅ {description} completed successfully")
        return True

def main():
    """Main test runner function."""
    print("Skylyt TravelHub Backend Test Suite")
    print("=" * 50)
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Test commands
    test_commands = [
        ("pytest tests/unit/ -v --tb=short", "Unit Tests"),
        ("pytest tests/integration/ -v --tb=short", "Integration Tests"),
        ("pytest tests/performance/ -v --tb=short -m 'not slow'", "Performance Tests (Fast)"),
        ("pytest tests/ --cov=app --cov-report=term-missing", "Full Test Suite with Coverage"),
    ]
    
    # Run tests based on command line arguments
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "unit":
            commands = [test_commands[0]]
        elif test_type == "integration":
            commands = [test_commands[1]]
        elif test_type == "performance":
            commands = [test_commands[2]]
        elif test_type == "coverage":
            commands = [test_commands[3]]
        elif test_type == "all":
            commands = test_commands
        else:
            print(f"Unknown test type: {test_type}")
            print("Available options: unit, integration, performance, coverage, all")
            sys.exit(1)
    else:
        # Default: run unit and integration tests
        commands = test_commands[:2]
    
    # Run selected tests
    results = []
    for command, description in commands:
        success = run_command(command, description)
        results.append((description, success))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{description}: {status}")
    
    # Exit with error if any tests failed
    if not all(success for _, success in results):
        sys.exit(1)
    
    print("\n🎉 All tests passed!")

if __name__ == "__main__":
    main()