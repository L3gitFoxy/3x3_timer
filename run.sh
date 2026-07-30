#!/usr/bin/env bash
# 3x3 Speed Cube Timer - Unix Launcher (macOS/Linux)
# Auto-creates a virtual environment and launches the app.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="$SCRIPT_DIR/.venv"

if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "[3x3 Timer] Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "[3x3 Timer] Installing dependencies..."
    "$VENV_DIR/bin/python" -m pip install -e . >/dev/null 2>&1
fi

echo "[3x3 Timer] Starting application..."
exec "$VENV_DIR/bin/python" run.py