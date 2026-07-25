<div align="center">

![banner](github-header-banner.png)

A lightweight desktop timer for 3×3 Rubik's Cube solves, built with Python.

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://microsoft.com/windows)
[![License](https://img.shields.io/github/license/L3gitFoxy/3x3_timer?style=for-the-badge)](LICENSE)
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
- [License](#license)

---

## Overview

**3x3 Timer** is a minimal desktop timer designed for recording Rubik's Cube solves without unnecessary complexity.

Solve history is stored locally, making the application completely offline with no external services or accounts required.

---

## Features

- High-precision solve timer
- Local solve history
- Persistent JSON storage
- Lightweight single-file application
- No internet connection required
- No external database
- Easy to modify and extend

---

## Installation

Clone the repository:

```bash
git clone https://github.com/L3gitFoxy/3x3_timer.git
```

Enter the project directory:

```bash
cd 3x3_timer
```

---

## Running

```bash
python "3x3 interactive timer.py"
```

---

## Project Structure

```text
3x3_timer/
│
├── 3x3 interactive timer.py    # Main application
├── 3x3_times.json              # Stored solve history
└── README.md
```

---

## Data Storage

Solve times are stored locally inside

```text
3x3_times.json
```

No cloud services, analytics, or user accounts are used.

---

## Requirements

- Python 3.13 or newer
- Windows (currently tested)

---

## Contributing

Contributions are welcome.

If you find a bug or have an improvement:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a Pull Request.

---

## License

This project is licensed under the MIT License.

See the `LICENSE` file for details.
