#!/usr/bin/env python3
"""
Demo script to showcase the AI Healer capabilities
"""

import os
import sys
import time
import subprocess
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def print_banner():
    """Print demo banner"""
    banner = """
🤖 AI-Driven Self-Healing CI/CD Platform Demo
=============================================

This demo will showcase the self-healing capabilities by:
1. Creating a failing test
2. Running the AI Healer Agent
3. Showing the generated fix

Note: This is a simulation - no actual PRs will be created.
"""
    print(banner)

def create_demo_failing_test():
    """Create a demo failing test file"""
    failing_test_content = '''import pytest
from app.main import add, subtract

def test_add():
    """Test the add function"""
    assert add(2, 3) == 5

def test_subtract():
    """Test the subtract function"""
    assert subtract(5, 3) == 2

def test_demo_failing_case():
    """This test will fail to demonstrate healing"""
    # Intentionally wrong assertion
    assert add(10, 5) == 20  # Should be 15
'''
    
    # Create temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='_test.py', delete=False, dir='tests') as f:
        f.write(failing_test_content)
        return f.name

def run_failing_tests(test_file):
    """Run tests and capture the failure"""
    print("🧪 Running tests to generate failure...")
    
    try:
        result = subprocess.run(
            ['python', '-m', 'pytest', test_file, '-v'],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        # Save output to log file
        log_file = 'demo_test_output.log'
        with open(log_file, 'w') as f:
            f.write(result.stdout)
            f.write(result.stderr)
        
        print(f"📝 Test output saved to: {log_file}")
        print("Test Output Preview:")
        print("-" * 40)
        print(result.stdout[-500:])  # Show last 500 characters
        print("-" * 40)
        
        return log_file
    
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return None

def demonstrate_log_parsing(log_file):
    """Demonstrate log parsing capabilities"""
    print("\n🔍 Demonstrating Log Parsing...")
    
    try:
        from healer.log_parser import LogParser
        
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        parser = LogParser()
        error_info = parser.parse_failure(log_content)
        
        if error_info:
            print("✅ Log Parser Results:")
            print(f"   📁 File: {error_info['file_path']}")
            print(f"   📍 Line: {error_info.get('line_number', 'Unknown')}")
            print(f"   ❌ Error: {error_info['error_message']}")
            print(f"   🏷️  Type: {error_info.get('error_type', 'Unknown')}")
            return error_info
        else:
            print("❌ No error found in logs")
            return None
    
    except Exception as e:
        print(f"❌ Log parsing failed: {e}")
        return None

def demonstrate_ai_analysis(error_info, test_file):
    """Demonstrate AI analysis (simulation)"""
    print("\n🧠 Demonstrating AI Analysis...")
    
    if not error_info:
        print("❌ No error info available for AI analysis")
        return None
    
    # Read the failing file
    try:
        with open(test_file, 'r') as f:
            file_content = f.read()
        
        print("📖 Original failing code:")
        print("-" * 40)
        print(file_content)
        print("-" * 40)
        
        # Simulate AI fix (in real scenario, this would call OpenAI)
        print("\n🤖 AI Analysis (Simulated):")
        print("   The test expects add(10, 5) to equal 20, but add(10, 5) = 15")
        print("   The assertion should be: assert add(10, 5) == 15")
        
        # Generate simulated fix
        fixed_content = file_content.replace(
            "assert add(10, 5) == 20  # Should be 15",
            "assert add(10, 5) == 15  # Fixed: correct expected value"
        )
        
        print("\n✅ AI-Generated Fix:")
        print("-" * 40)
        print(fixed_content)
        print("-" * 40)
        
        return fixed_content
    
    except Exception as e:
        print(f"❌ AI analysis simulation failed: {e}")
        return None

def demonstrate_git_operations():
    """Demonstrate git operations (simulation)"""
    print("\n🔄 Demonstrating Git Operations (Simulated)...")
    
    print("🌿 Would create branch: fix/ai-heal-demo123")
    print("📝 Would commit changes with message: 'fix: AI repair for assertion error'")
    print("🚀 Would push to remote repository")
    print("📋 Would create PR with title: '🤖 AI Fix: Assertion Error in test_demo_failing_case'")
    
    pr_body = """## 🔧 Automated Fix Summary

**Error Type**: assertion
**File**: `tests/demo_test.py`
**Line**: 12

### 🐛 Original Error
```
assert 15 == 20
```

### 🤖 AI Analysis
The test was expecting add(10, 5) to equal 20, but the correct result is 15.
Fixed the assertion to use the correct expected value.

### 🧪 Testing
Please verify that:
- [ ] All existing tests still pass
- [ ] The specific failing test now passes
- [ ] No new regressions are introduced
"""
    
    print("\n📋 PR Body Preview:")
    print("-" * 40)
    print(pr_body)
    print("-" * 40)

def cleanup_demo_files():
    """Clean up demo files"""
    print("\n🧹 Cleaning up demo files...")
    
    files_to_remove = [
        'demo_test_output.log',
    ]
    
    for file_path in files_to_remove:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"   🗑️  Removed: {file_path}")
        except Exception as e:
            print(f"   ⚠️  Failed to remove {file_path}: {e}")
    
    # Remove any temporary test files
    tests_dir = Path('tests')
    for test_file in tests_dir.glob('tmp*.py'):
        try:
            test_file.unlink()
            print(f"   🗑️  Removed: {test_file}")
        except Exception as e:
            print(f"   ⚠️  Failed to remove {test_file}: {e}")

def main():
    """Run the demo"""
    print_banner()
    
    try:
        # Step 1: Create failing test
        print("📝 Step 1: Creating failing test...")
        test_file = create_demo_failing_test()
        print(f"   Created: {test_file}")
        
        # Step 2: Run tests and capture failure
        print("\n🧪 Step 2: Running tests to capture failure...")
        log_file = run_failing_tests(test_file)
        
        if not log_file:
            print("❌ Demo failed: Could not generate test failure")
            return 1
        
        # Step 3: Demonstrate log parsing
        error_info = demonstrate_log_parsing(log_file)
        
        # Step 4: Demonstrate AI analysis
        fixed_content = demonstrate_ai_analysis(error_info, test_file)
        
        # Step 5: Demonstrate git operations
        demonstrate_git_operations()
        
        # Success message
        print("\n🎉 Demo completed successfully!")
        print("\nIn a real scenario, this would:")
        print("1. ✅ Parse the actual test failure")
        print("2. 🤖 Call OpenAI GPT-4 for analysis")
        print("3. 🔧 Generate and apply the fix")
        print("4. 🌿 Create a git branch and commit")
        print("5. 🚀 Push changes and create a PR")
        print("6. 📧 Notify the team of the fix")
        
        return 0
    
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
        return 1
    
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        return 1
    
    finally:
        # Always cleanup
        cleanup_demo_files()

if __name__ == "__main__":
    sys.exit(main())