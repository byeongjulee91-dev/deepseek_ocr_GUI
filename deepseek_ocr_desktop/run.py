#!/usr/bin/env python3
"""
DeepSeek-OCR Desktop Application Launcher
"""
import sys
import os
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent
src_dir = project_root / "src"

# Add project root to Python path (not src!)
sys.path.insert(0, str(project_root))

# Change to src directory for resource loading
os.chdir(src_dir)

# Import and run the main application as a module
if __name__ == "__main__":
    # Import main from src package
    from src.main import main
    main()
