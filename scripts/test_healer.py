#!/usr/bin/env python3
"""
Test script for the AI Healer Agent
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def create_test_log():
    """Create a test log file with a failing test"""
    test_log_content = """
============================= test session starts ==============================
platform linux -- Python 3.11.0, pytest-7.4.3, pluggy-1.3.0
rootdir: /workspace
collected 3 items

tests/test_main.py ..F                                                   [100%]

=================================== FAILURES ===================================
______________________________ test_failing_case _______________________________

    def test_failing_case():
        # This test is designed to fail to trigger the self-healing agent
>       assert add(2, 2) == 5
E       assert 4 == 5
E        +  where 4 = add(2, 2)

tests/test_main.py:12: AssertionError
=========================== short test summary info ============================
FAILED tests/test_main.py::test_failing_case - assert 4 == 5
========================= 1 failed, 2 passed in 0.10s ============================
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        f.write(test_log_content.strip())
        return f.name

def test_log_parser():
    """Test the log parser functionality"""
    print("🧪 Testing Log Parser...")
    
    from healer.log_parser import LogParser
    
    log_file = create_test_log()
    
    try:
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        parser = LogParser()
        error_info = parser.parse_failure(log_content)
        
        if error_info:
            print(f"✅ Log parser found error: {error_info}")
            return True
        else:
            print("❌ Log parser failed to find error")
            return False
    
    finally:
        os.unlink(log_file)

def test_config():
    """Test configuration loading"""
    print("🧪 Testing Configuration...")
    
    try:
        from healer.config import config
        
        # Test that config loads without error
        print(f"✅ Config loaded successfully")
        print(f"   - OpenAI Model: {config.openai_model}")
        print(f"   - Max Retries: {config.max_retry_attempts}")
        print(f"   - Branch Prefix: {config.branch_prefix}")
        
        return True
    
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_environment():
    """Test environment setup"""
    print("🧪 Testing Environment...")
    
    required_vars = ['OPENAI_API_KEY', 'GITHUB_TOKEN', 'GITHUB_REPOSITORY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   Set these in your .env file for full functionality")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def test_dependencies():
    """Test that all dependencies are installed"""
    print("🧪 Testing Dependencies...")
    
    required_packages = [
        'flask',
        'pytest',
        'openai',
        'requests',
        'gitpython'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed")
        return True

def test_flask_app():
    """Test Flask application"""
    print("🧪 Testing Flask Application...")
    
    try:
        from app.main import app
        
        with app.test_client() as client:
            # Test main endpoint
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Flask app main endpoint working")
            else:
                print(f"❌ Flask app main endpoint failed: {response.status_code}")
                return False
            
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Flask app health endpoint working")
            else:
                print(f"❌ Flask app health endpoint failed: {response.status_code}")
                return False
        
        return True
    
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def run_unit_tests():
    """Run the actual unit tests"""
    print("🧪 Running Unit Tests...")
    
    try:
        result = subprocess.run(
            ['python', '-m', 'pytest', 'tests/', '-v'],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        print("Test Output:")
        print(result.stdout)
        
        if result.stderr:
            print("Test Errors:")
            print(result.stderr)
        
        # We expect some tests to fail (by design)
        if result.returncode != 0:
            print("⚠️  Some tests failed (this is expected for the demo)")
        else:
            print("✅ All tests passed")
        
        return True
    
    except Exception as e:
        print(f"❌ Unit test execution failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🤖 AI Healer Agent Test Suite")
    print("=" * 40)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Configuration", test_config),
        ("Environment", test_environment),
        ("Flask Application", test_flask_app),
        ("Log Parser", test_log_parser),
        ("Unit Tests", run_unit_tests)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The AI Healer is ready to go!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())