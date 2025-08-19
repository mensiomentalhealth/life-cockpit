#!/usr/bin/env python3
"""
Simple test script for Life Cockpit setup
"""

import sys
from pathlib import Path

def test_basic_setup():
    """Test basic project setup."""
    print("🧪 Testing Life Cockpit Setup...")
    print("=" * 40)
    
    # Test Python version
    print(f"✅ Python version: {sys.version}")
    
    # Test project structure
    project_root = Path(".")
    required_dirs = ["auth", "dataverse", "utils", "logs", "tests"]
    
    print("\n📁 Checking project structure:")
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"  ✅ {dir_name}/")
        else:
            print(f"  ❌ {dir_name}/ (missing)")
    
    # Test required files
    required_files = ["README.md", "requirements.txt", "env.example", ".gitignore"]
    
    print("\n📄 Checking required files:")
    for file_name in required_files:
        file_path = project_root / file_name
        if file_path.exists():
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} (missing)")
    
    print("\n🎉 Basic setup test completed!")
    print("\n💡 Next steps:")
    print("  1. Copy env.example to .env")
    print("  2. Fill in your Microsoft 365 credentials")
    print("  3. Install dependencies: pip install -r requirements.txt")
    print("  4. Start building your automation scripts!")

if __name__ == "__main__":
    test_basic_setup()
