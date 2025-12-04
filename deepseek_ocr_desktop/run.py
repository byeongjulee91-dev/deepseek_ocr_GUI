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

# Add src directory to Python path (for absolute imports)
sys.path.insert(0, str(src_dir))

# Change to src directory for resource loading
os.chdir(src_dir)

# Import and run the main application
if __name__ == "__main__":
    from main import main
    main()
