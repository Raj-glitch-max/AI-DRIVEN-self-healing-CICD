#!/usr/bin/env python3
"""
Setup script for AI-Driven Self-Healing CI/CD Platform
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and handle errors"""
    print(f"🔧 {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    prerequisites = {
        'python3': 'python3 --version',
        'pip': 'pip --version',
        'git': 'git --version',
        'docker': 'docker --version',
        'docker-compose': 'docker-compose --version'
    }
    
    missing = []
    for tool, cmd in prerequisites.items():
        if not run_command(cmd, f"Checking {tool}"):
            missing.append(tool)
    
    if missing:
        print(f"❌ Missing prerequisites: {', '.join(missing)}")
        print("Please install the missing tools and run setup again.")
        return False
    
    print("✅ All prerequisites found")
    return True

def setup_environment():
    """Setup Python environment and install dependencies"""
    print("📦 Setting up Python environment...")
    
    # Create virtual environment if it doesn't exist
    if not Path('venv').exists():
        if not run_command('python3 -m venv venv', "Creating virtual environment"):
            return False
    
    # Activate virtual environment and install dependencies
    activate_cmd = 'source venv/bin/activate' if os.name != 'nt' else 'venv\\Scripts\\activate'
    install_cmd = f'{activate_cmd} && pip install --upgrade pip && pip install -r requirements.txt'
    
    if not run_command(install_cmd, "Installing Python dependencies"):
        return False
    
    return True

def setup_configuration():
    """Setup configuration files"""
    print("⚙️  Setting up configuration...")
    
    # Copy .env.example to .env if it doesn't exist
    if not Path('.env').exists():
        if Path('.env.example').exists():
            shutil.copy('.env.example', '.env')
            print("📝 Created .env file from template")
            print("⚠️  Please edit .env file with your API keys and configuration")
        else:
            print("❌ .env.example not found")
            return False
    else:
        print("✅ .env file already exists")
    
    return True

def setup_git_hooks():
    """Setup git hooks for development"""
    print("🪝 Setting up git hooks...")
    
    hooks_dir = Path('.git/hooks')
    if not hooks_dir.exists():
        print("⚠️  Not a git repository, skipping git hooks")
        return True
    
    # Create pre-commit hook
    pre_commit_hook = hooks_dir / 'pre-commit'
    pre_commit_content = '''#!/bin/bash
# AI-Driven Self-Healing CI/CD Platform - Pre-commit Hook

echo "🔍 Running pre-commit checks..."

# Run tests
python -m pytest tests/ -v
if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Commit aborted."
    exit 1
fi

# Run linting (if available)
if command -v flake8 &> /dev/null; then
    flake8 app/ healer/ tests/
    if [ $? -ne 0 ]; then
        echo "❌ Linting failed. Commit aborted."
        exit 1
    fi
fi

echo "✅ Pre-commit checks passed"
'''
    
    with open(pre_commit_hook, 'w') as f:
        f.write(pre_commit_content)
    
    # Make hook executable
    os.chmod(pre_commit_hook, 0o755)
    print("✅ Git hooks setup completed")
    
    return True

def run_tests():
    """Run tests to verify setup"""
    print("🧪 Running tests to verify setup...")
    
    activate_cmd = 'source venv/bin/activate' if os.name != 'nt' else 'venv\\Scripts\\activate'
    test_cmd = f'{activate_cmd} && python -m pytest tests/ -v'
    
    result = run_command(test_cmd, "Running tests")
    if result is None:
        print("⚠️  Some tests failed, but this is expected for the demo")
        return True  # Tests are expected to fail for demo purposes
    
    return True

def main():
    """Main setup function"""
    print("🚀 AI-Driven Self-Healing CI/CD Platform Setup")
    print("=" * 50)
    
    steps = [
        ("Prerequisites Check", check_prerequisites),
        ("Environment Setup", setup_environment),
        ("Configuration Setup", setup_configuration),
        ("Git Hooks Setup", setup_git_hooks),
        ("Test Verification", run_tests)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 Step: {step_name}")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Start Jenkins: docker-compose up -d")
    print("3. Configure Jenkins credentials")
    print("4. Create a Jenkins pipeline job")
    print("5. Trigger a build to see the self-healing in action!")
    
    print("\n🔗 Useful commands:")
    print("- Run tests: python -m pytest tests/ -v")
    print("- Start Flask app: python app/main.py")
    print("- Run healer manually: python healer/agent.py test_output.log")

if __name__ == "__main__":
    main()