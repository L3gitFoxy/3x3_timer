# Contributing to 3x3 Timer

Thanks for your interest in contributing!

## How to Contribute

1. **Fork** the repository.
2. **Create a feature branch** (`git checkout -b feature/your-feature`).
3. **Commit your changes** with clear messages.
4. **Push** to your fork and open a **Pull Request**.

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/).
- Use **type hints** on all function signatures.
- Keep functions small and focused — one responsibility per function.

## Project Structure

- `src/scramble.py` — Cube simulation & WCA scramble generation (parallel-face prevention per WCA 4b3).
- `src/timer.py` — Pure timer logic & state machine (no UI imports).
- `src/storage.py` — JSON load/save with validation.
- `src/ui.py` — CustomTkinter graphical interface (inline scramble, times graph, CSV export, responsive layout).
- `src/visualizer.py` — Isometric 3D cube visualizer with arrow key navigation.
- `data/times.json` — User solve data (gitignored).

## Running Locally

```bash
python run.py
```

## Installing Dependencies

```bash
pip install customtkinter>=5.2.2
```

## Reporting Issues

Open an issue on GitHub with:

- What you expected to happen
- What actually happened
- Steps to reproduce
- Python version and OS