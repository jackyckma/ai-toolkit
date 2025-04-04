#!/usr/bin/env python3
"""
Simple script to run the AI-Native Development Toolkit directly.
This avoids Python module import issues when running from the project root.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from ai_toolkit.cli.main import main

if __name__ == "__main__":
    sys.exit(main()) 