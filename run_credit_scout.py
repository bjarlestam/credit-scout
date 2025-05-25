#!/usr/bin/env python3
"""
Credit Scout Runner

Simple script to run Credit Scout from the project root.
This handles the Python path setup automatically.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Import and run the main CLI
from credit_scout.main import cli

if __name__ == "__main__":
    cli() 