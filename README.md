<div align="center">

![banner](github-header-banner.png)

A lightweight desktop timer for 3×3 Rubik's Cube solves, built with Python.

[![Version](https://img.shields.io/badge/Version-2.0-00ff00?style=for-the-badge)](https://github.com/L3gitFoxy/3x3_timer)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://microsoft.com/windows)
[![Stars](https://img.shields.io/github/stars/L3gitFoxy/3x3_timer?style=for-the-badge)](https://github.com/L3gitFoxy/3x3_timer/stargazers)
[![Issues](https://img.shields.io/github/issues/L3gitFoxy/3x3_timer?style=for-the-badge)](https://github.com/L3gitFoxy/3x3_timer/issues)

Simple. Fast. Offline.

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Running](#running)
- [Project Structure](#project-structure)
- [Data Storage](#data-storage)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)

---

## Overview

**3x3 Timer** is a minimal desktop timer designed for recording Rubik's Cube solves without unnecessary complexity.

Solve history is stored locally, making the application completely offline with no external services or accounts required.

---

## Features

- High-precision solve timer with inspection & grace period
- WCA-style scramble generator (20 random moves)
- Isometric 3D cube visualizer (step through scrambles with arrow keys)
- Local solve history with scramble tracking
- Persistent JSON storage
- Lightweight multi-file modular application
- No internet connection required
- No external database
- Easy to modify and extend
- Cross-platform (Windows, macOS, Linux)

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

---

## Project Structure

```text
3x3_timer/
│
├── src/
│   ├── __init__.py          # Package marker
│   ├── scramble.py          # Cube simulation & scramble generation
│   ├── timer.py             # Pure timer logic & state machine
│   ├── storage.py           # JSON persistence & validation
│   ├── ui.py                # Tkinter graphical interface
│   └── visualizer.py        # Isometric 3D cube visualizer
├── data/
│   └── times.json           # Solve history (gitignored)
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── README.md
└── SECURITY.md
```

---

## Data Storage

Solve times are stored locally in `data/times.json`.

No cloud services, analytics, or user accounts are used.

---

## Requirements

- Python 3.10 or newer
- Tkinter (included with most Python installations)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Security

See [SECURITY.md](SECURITY.md).

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.