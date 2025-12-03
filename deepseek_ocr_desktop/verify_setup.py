#!/usr/bin/env python3
"""
Setup Verification Script for DeepSeek-OCR Desktop
Checks if the project structure is correct
"""

import sys
from pathlib import Path

def verify_setup():
    """Verify project setup"""
    print("🔍 Verifying DeepSeek-OCR Desktop setup...\n")

    # Check 1: Project structure
    print("✓ Checking project structure...")
    required_files = [
        "run.py",
        "requirements.txt",
        "src/__init__.py",
        "src/main.py",
        "src/core/__init__.py",
        "src/ui/__init__.py",
        "src/ui/widgets/__init__.py",
        "src/ui/dialogs/__init__.py",
        "src/utils/__init__.py",
        "src/resources/__init__.py",
    ]

    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"  ❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("  ✅ All required files present")

    # Check 2: Python package structure
    print("\n✓ Checking Python package structure...")
    sys.path.insert(0, str(Path.cwd()))

    try:
        import src
        print("  ✅ src package importable")
    except ImportError as e:
        print(f"  ❌ Cannot import src package: {e}")
        return False

    # Check 3: Dependencies (optional check)
    print("\n✓ Checking dependencies...")
    missing_deps = []

    dependencies = [
        ("PySide6", "PySide6"),
        ("torch", "torch"),
        ("transformers", "transformers"),
        ("PIL", "Pillow"),
    ]

    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f"  ✅ {package_name} installed")
        except ImportError:
            print(f"  ⚠️  {package_name} not installed")
            missing_deps.append(package_name)

    if missing_deps:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("   Install with: uv pip install -r requirements.txt")

    # Check 4: Virtual environment
    print("\n✓ Checking virtual environment...")
    if hasattr(sys, 'prefix') and sys.prefix != sys.base_prefix:
        print(f"  ✅ Virtual environment active: {sys.prefix}")
    else:
        print("  ⚠️  No virtual environment active")
        print("   Recommended: uv venv && source .venv/bin/activate")

    # Final summary
    print("\n" + "="*60)
    if missing_deps:
        print("⚠️  Setup partially complete - install missing dependencies")
        print("\n📝 Next steps:")
        print("   1. uv venv (if not done)")
        print("   2. source .venv/bin/activate")
        print("   3. uv pip install -r requirements.txt")
        print("   4. uv run run.py")
    else:
        print("✅ Setup complete! Ready to run.")
        print("\n🚀 Run the application:")
        print("   uv run run.py")
        print("   # or")
        print("   python run.py")
    print("="*60)

    return True

if __name__ == "__main__":
    success = verify_setup()
    sys.exit(0 if success else 1)
