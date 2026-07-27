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

- `src/timer.py` — Pure timer logic (no UI imports).
- `src/storage.py` — JSON load/save.
- `src/ui.py` — Tkinter interface.
- `data/times.json` — User solve data (gitignored).

## Running Locally

```bash
python -m src.ui
```

## Reporting Issues

Open an issue on GitHub with:

- What you expected to happen
- What actually happened
- Steps to reproduce
- Python version and OS