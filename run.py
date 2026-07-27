#!/usr/bin/env python3
"""Entry point — run this file to start the timer."""

import sys
from pathlib import Path

# Ensure src/ is on the path so imports work when running directly
SRC_DIR = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(SRC_DIR))

from ui import main


if __name__ == "__main__":
    main()
