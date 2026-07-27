"""JSON-based persistence for solve times."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, List, Dict


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_FILE = DATA_DIR / "times.json"


def get_data_path(filename: str = "times.json") -> Path:
    """Return the full path to a data file, ensuring the *data/* directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR / filename


def load_times(path: Path = DEFAULT_FILE) -> List[Dict[str, Any]]:
    """Load solve times from *path*.

    Returns an empty list if the file is missing, empty, or contains corrupt data.
    """
    if not path.exists() or path.stat().st_size == 0:
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data: Any = json.load(f)
        # Validate — we expect a list of objects with 'time' and 'date'
        if isinstance(data, list) and all(
            isinstance(e, dict) and "time" in e and "date" in e for e in data
        ):
            return data
        return []
    except (json.JSONDecodeError, OSError):
        return []


def save_times(times: List[Dict[str, Any]], path: Path = DEFAULT_FILE) -> None:
    """Persist *times* to *path* as pretty-printed JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(times, f, indent=2)