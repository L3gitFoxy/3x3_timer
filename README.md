<div align="center">

![banner](github-header-banner.png)

A modern desktop timer for 3×3 Rubik's Cube solves, built with Python & CustomTkinter.

[![Version](https://img.shields.io/badge/Version-2.3-00ff00?style=for-the-badge)](https://github.com/L3gitFoxy/3x3_timer)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://microsoft.com/windows)
[![CI](https://img.shields.io/github/actions/workflow/status/L3gitFoxy/3x3_timer/ci.yml?branch=main&style=for-the-badge&logo=github&label=CI)](https://github.com/L3gitFoxy/3x3_timer/actions)
[![Tests](https://img.shields.io/badge/Tests-65%20passing-00cc00?style=for-the-badge&logo=pytest)](https://github.com/L3gitFoxy/3x3_timer)
[![Ruff](https://img.shields.io/badge/Linted%20with-Ruff-ffcc00?style=for-the-badge&logo=ruff)](https://github.com/astral-sh/ruff)
[![Mypy](https://img.shields.io/badge/Type%20checked-Mypy-2a6db2?style=for-the-badge&logo=python)](https://mypy-lang.org/)
[![Stars](https://img.shields.io/github/stars/L3gitFoxy/3x3_timer?style=for-the-badge)](https://github.com/L3gitFoxy/3x3_timer/stargazers)
[![Issues](https://img.shields.io/github/issues/L3gitFoxy/3x3_timer?style=for-the-badge)](https://github.com/L3gitFoxy/3x3_timer/issues)

Simple. Fast. Offline.

</div>

---

## Table of Contents

- [Quick Start](#quick-start)
- [Overview](#overview)
- [Features](#features)
- [Changelog](#changelog)
- [Installation](#installation)
- [Running](#running)
- [Project Structure](#project-structure)
- [Data Storage](#data-storage)
- [Development](#development)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)

---

## Quick Start

**30 seconds to your first solve:**

```bash
# Option 1: One-command install (requires Python 3.10+)
pip install git+https://github.com/L3gitFoxy/3x3_timer.git && 3x3_timer

# Option 2: Run directly (no install)
git clone https://github.com/L3gitFoxy/3x3_timer.git
cd 3x3_timer
python run.py

# Option 3: Double-click (Windows)
run.bat
```

On first launch, a welcome dialog explains the timer flow. Press **ANY KEY** to start inspection, then follow the on-screen prompts.

---

## Overview

**3x3 Timer** is a modern desktop timer for recording Rubik's Cube solves with a sleek CustomTkinter dark-theme UI.

Solve history is stored locally, making the application completely offline with no external services or accounts required.

---

## Features

- **Modern UI** — CustomTkinter dark theme with rounded widgets, hover effects, and dynamic font scaling
- **High-precision solve timer** with inspection (15s) & grace period (3s)
- **WCA-compliant scramble generator** (20 random moves, no parallel-face sequences per WCA 4b3)
- **Inline scramble display** — scramble always visible, no reveal/hide pattern
- **Isometric 3D cube visualizer** — step through scrambles with arrow keys
- **Solve time graph** — line chart with best/worst/average markers in the times window
- **Local solve history** with scramble tracking and persistent JSON storage
- **Ao5 / Ao12 / Ao100** — sliding-window averages calculated automatically
- **CSV export** — export all solve times to CSV for external analysis
- **Responsive layout** — window resizes proportionally, timer font scales
- **Cross-platform** (Windows, macOS, Linux)
- **First-run welcome dialog** — explains the timer flow for new users
- **One-click launchers** — `run.bat` (Windows) and `run.sh` (macOS/Linux) auto-create virtual environments
- No internet connection required
- No external database
- Lightweight multi-file modular application

---

## Installation & Running

### One-command install (requires Python 3.10+)

```bash
pip install git+https://github.com/L3gitFoxy/3x3_timer.git && 3x3_timer
```

Or install, then run whenever:

```bash
pip install git+https://github.com/L3gitFoxy/3x3_timer.git
3x3_timer
```

### Run directly without installing

```bash
git clone https://github.com/L3gitFoxy/3x3_timer.git
cd 3x3_timer
python run.py
```

### One-click launchers (auto-create virtual environment)

**Windows:** Double-click `run.bat`  
**macOS/Linux:** Run `./run.sh` in the terminal

These scripts automatically create a Python virtual environment, install dependencies, and launch the app — no manual setup required.

### Install with pipx (recommended for isolation)

```bash
pipx install git+https://github.com/L3gitFoxy/3x3_timer.git
3x3_timer
```

[pipx](https://pypa.github.io/pipx/) installs the app in an isolated environment so it doesn't interfere with other Python packages.

---

## Project Structure

```text
3x3_timer/
│
├── src/
│   ├── __init__.py          # Package marker
│   ├── scramble.py          # Cube simulation & WCA scramble generation
│   ├── timer.py             # Pure timer logic & state machine
│   ├── storage.py           # JSON persistence & validation
│   ├── ui.py                # CustomTkinter graphical interface
│   └── visualizer.py        # Isometric 3D cube visualizer
├── tests/
│   ├── __init__.py          # Test suite marker
│   ├── test_timer.py        # Timer state machine tests (20 tests)
│   ├── test_scramble.py     # Scramble generation tests (22 tests)
│   └── test_storage.py      # JSON persistence tests (23 tests)
├── data/
│   └── times.json           # Solve history (gitignored)
├── .github/workflows/
│   └── ci.yml               # CI pipeline (lint, type-check, test)
├── .pre-commit-config.yaml  # Git hooks (ruff, mypy, formatting)
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── SECURITY.md
├── pyproject.toml           # Project config & tool settings
├── run.bat                  # Windows one-click launcher
├── run.sh                   # Unix one-click launcher
└── run.py                   # Entry point
```

---

## Data Storage

Solve times are stored locally in `data/times.json`.

No cloud services, analytics, or user accounts are used.

---

## Development

### Setup

```bash
# Clone the repo
git clone https://github.com/L3gitFoxy/3x3_timer.git
cd 3x3_timer

# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Run tests

```bash
pytest --cov=src
```

### Lint & format

```bash
ruff check src/ tests/
ruff format src/ tests/
```

### Type check

```bash
mypy src/ tests/
```

### Pre-commit hooks

The project uses [pre-commit](https://pre-commit.com/) to automatically run ruff (lint + format) and mypy before every commit. After installing dev dependencies, run:

```bash
pre-commit install
```

---

## Requirements

- Python 3.10 or newer
- CustomTkinter >= 5.2.2 (installed automatically via pip)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Security

See [SECURITY.md](SECURITY.md).

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
