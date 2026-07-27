#!/usr/bin/env python3
"""Entry point — run this file to start the timer."""

import sys
from pathlib import Path

# Ensure the project root is on sys.path so 'src' is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.ui import main

if __name__ == "__main__":
    main()