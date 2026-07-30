<div align="center">

![banner](github-header-banner.png)

A modern desktop timer for 3×3 Rubik's Cube solves, built with Python & CustomTkinter.

[![Version](https://img.shields.io/badge/Version-2.3-00ff00?style=for-the-badge)](https://github.com/L3gitFoxy/3x3_timer)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://microsoft.com/windows)
[![Stars](https://img.shields.io/github/stars/L3gitFoxy/3x3_timer?style=for-the-badge)](https://github.com/L3gitFoxy/3x3_timer/stargazers)
[![Issues](https://img.shields.io/github/issues/L3gitFoxy/3x3_timer?style=for-the-badge)](https://github.com/L3gitFoxy/3x3_timer/issues)

Simple. Fast. Offline.

</div>

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Data Storage](#data-storage)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)

## Overview

**3x3 Timer** is a modern desktop timer for recording Rubik's Cube solves with a sleek CustomTkinter dark-theme UI.

Solve history is stored locally, making the application completely offline with no external services or accounts required.

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
- No internet connection required
- No external database
- Lightweight multi-file modular application

## Installation

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
├── data/
│   └── times.json           # Solve history (gitignored)
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── SECURITY.md
└── 3x3.py                   # Full length code without any divisions
```

## Data Storage

Solve times are stored locally in `data/times.json`.

No cloud services, analytics, or user accounts are used.

## Requirements

- Python 3.10 or newer
- CustomTkinter >= 5.2.2 (installed automatically via pip)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

See [SECURITY.md](SECURITY.md).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
