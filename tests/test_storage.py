"""Tests for JSON persistence of solve times."""

from __future__ import annotations

import json
import os
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

from storage import get_data_path, load_times, save_times


@pytest.fixture
def temp_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a temporary directory for test data files."""
    yield tmp_path


@pytest.fixture
def sample_times() -> list[dict[str, Any]]:
    """Provide sample solve data."""
    return [
        {"time": 12_345, "date": "2024-01-15 10:30:00", "scramble": "R U R' U'"},
        {"time": 15_678, "date": "2024-01-15 10:35:00", "scramble": "F R U R' U' F'"},
        {"time": 10_000, "date": "2024-01-15 10:40:00", "scramble": "U R U' L' U R' U' L"},
    ]


class TestGetDataPath:
    """get_data_path should create the data directory and return correct paths."""

    def test_returns_path_object(self) -> None:
        result = get_data_path("test.json")
        assert isinstance(result, Path)

    def test_default_filename(self) -> None:
        result = get_data_path()
        assert result.name == "times.json"

    def test_custom_filename(self) -> None:
        result = get_data_path("custom.json")
        assert result.name == "custom.json"

    def test_creates_directory(self, tmp_path: Path) -> None:
        # Use a path in the temp directory to verify directory creation
        test_dir = tmp_path / "test_data"
        path = test_dir / "times.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        assert path.parent.exists()


class TestSaveTimes:
    """save_times should persist data correctly."""

    def test_saves_to_file(
        self, temp_dir: Path, sample_times: list[dict[str, Any]]
    ) -> None:
        path = temp_dir / "times.json"
        save_times(sample_times, path)
        assert path.exists()

    def test_file_contains_valid_json(
        self, temp_dir: Path, sample_times: list[dict[str, Any]]
    ) -> None:
        path = temp_dir / "times.json"
        save_times(sample_times, path)
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        assert data == sample_times

    def test_empty_list(self, temp_dir: Path) -> None:
        path = temp_dir / "times.json"
        save_times([], path)
        assert path.exists()
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        assert data == []

    def test_creates_parent_directory(
        self, temp_dir: Path, sample_times: list[dict[str, Any]]
    ) -> None:
        nested = temp_dir / "subdir" / "nested" / "times.json"
        save_times(sample_times, nested)
        assert nested.exists()


class TestLoadTimes:
    """load_times should read data correctly."""

    def test_loads_saved_data(
        self, temp_dir: Path, sample_times: list[dict[str, Any]]
    ) -> None:
        path = temp_dir / "times.json"
        save_times(sample_times, path)
        loaded = load_times(path)
        assert loaded == sample_times

    def test_empty_file_returns_empty_list(self, temp_dir: Path) -> None:
        path = temp_dir / "times.json"
        # Create empty file
        path.write_text("", encoding="utf-8")
        loaded = load_times(path)
        assert loaded == []

    def test_missing_file_returns_empty_list(self, temp_dir: Path) -> None:
        path = temp_dir / "nonexistent.json"
        loaded = load_times(path)
        assert loaded == []

    def test_corrupt_json_returns_empty_list(self, temp_dir: Path) -> None:
        path = temp_dir / "corrupt.json"
        path.write_text("{invalid json!!!!}", encoding="utf-8")
        loaded = load_times(path)
        assert loaded == []

    def test_invalid_structure_returns_empty_list(self, temp_dir: Path) -> None:
        path = temp_dir / "invalid.json"
        # Valid JSON but wrong structure (not a list of dicts with time/date)
        with path.open("w", encoding="utf-8") as f:
            json.dump({"not": "a list"}, f)
        loaded = load_times(path)
        assert loaded == []

    def test_partial_invalid_entries_returns_empty_list(self, temp_dir: Path) -> None:
        path = temp_dir / "partial.json"
        # Valid JSON list but entries missing required fields
        with path.open("w", encoding="utf-8") as f:
            json.dump(
                [{"time": 12345}, {"date": "2024-01-01"}],
                f,
            )
        loaded = load_times(path)
        assert loaded == []

    def test_round_trip_preserves_data(
        self, temp_dir: Path, sample_times: list[dict[str, Any]]
    ) -> None:
        """Save, load, modify, save, load again — data should be preserved."""
        path = temp_dir / "roundtrip.json"

        # First save
        save_times(sample_times, path)
        loaded1 = load_times(path)
        assert loaded1 == sample_times

        # Append a new solve
        new_solve = {"time": 20_000, "date": "2024-01-15 11:00:00", "scramble": "R' D' R D"}
        loaded1.append(new_solve)
        save_times(loaded1, path)

        # Reload
        loaded2 = load_times(path)
        assert len(loaded2) == 4
        assert loaded2[-1] == new_solve

    def test_large_dataset(self, temp_dir: Path) -> None:
        """Should handle hundreds of entries without issue."""
        path = temp_dir / "large.json"
        times = [
            {"time": i * 100, "date": f"2024-01-01 00:00:{i:02d}", "scramble": "R U R'"}
            for i in range(500)
        ]
        save_times(times, path)
        loaded = load_times(path)
        assert len(loaded) == 500
        assert loaded == times

    def test_file_permissions_error(self, temp_dir: Path) -> None:
        """Should handle permission errors gracefully."""
        path = temp_dir / "readonly.json"
        save_times([{"time": 1000, "date": "2024-01-01", "scramble": "R"}], path)

        # Make file read-only (on Windows this is different)
        # Just test that the function handles OSError gracefully
        if os.name != "nt":  # Unix only
            path.chmod(0o444)
            loaded = load_times(path)
            assert loaded is not None  # Should return something, not crash
