"""Tests for the core timer state machine."""

from __future__ import annotations

import time
from collections.abc import Generator

import pytest

from timer import SpeedCubeTimer, TimerPhase, format_time


@pytest.fixture
def timer() -> Generator[SpeedCubeTimer, None, None]:
    """Provide a fresh timer instance for each test."""
    yield SpeedCubeTimer()


class TestTimerInitialState:
    """Timer should start in IDLE phase with zero elapsed time."""

    def test_initial_phase(self, timer: SpeedCubeTimer) -> None:
        assert timer.phase == TimerPhase.IDLE

    def test_initial_elapsed(self, timer: SpeedCubeTimer) -> None:
        assert timer.elapsed_ms == 0

    def test_initial_running(self, timer: SpeedCubeTimer) -> None:
        assert timer.running is False

    def test_initial_display(self, timer: SpeedCubeTimer) -> None:
        assert timer.display_ms == 0

    def test_initial_status_key(self, timer: SpeedCubeTimer) -> None:
        assert timer.status_key == "idle"


class TestTimerInspection:
    """Inspection phase: 15-second countdown."""

    def test_start_inspection_sets_phase(self, timer: SpeedCubeTimer) -> None:
        timer.start_inspection()
        assert timer.phase == TimerPhase.INSPECTION

    def test_inspection_display_countdown(self, timer: SpeedCubeTimer) -> None:
        timer.start_inspection()
        timer.tick()
        # After a tick, display should be close to 15_000 ms
        assert 14_000 <= timer.display_ms <= 15_000

    def test_inspection_transitions_to_grace(self, timer: SpeedCubeTimer) -> None:
        timer.start_inspection()
        # Simulate 15 seconds passing
        timer._phase_start = time.time() - 16  # 16 seconds ago
        timer.tick()
        assert timer.phase == TimerPhase.GRACE

    def test_cancel_during_inspection(self, timer: SpeedCubeTimer) -> None:
        timer.start_inspection()
        timer.cancel()
        assert timer.phase == TimerPhase.IDLE
        assert timer.display_ms == 0


class TestTimerGrace:
    """Grace phase: 3-second window before READY."""

    def test_grace_transitions_to_ready(self, timer: SpeedCubeTimer) -> None:
        timer.start_inspection()
        timer._phase_start = time.time() - 16  # Skip inspection
        timer.tick()
        assert timer.phase == TimerPhase.GRACE

        # Simulate 3 seconds passing
        timer._phase_start = time.time() - 4  # 4 seconds ago
        timer.tick()
        assert timer.phase == TimerPhase.READY

    def test_cancel_during_grace(self, timer: SpeedCubeTimer) -> None:
        timer.start_inspection()
        timer._phase_start = time.time() - 16  # Skip to grace
        timer.tick()
        assert timer.phase == TimerPhase.GRACE

        timer.cancel()
        assert timer.phase == TimerPhase.IDLE


class TestTimerSolve:
    """Solve phase: timing a solve."""

    def test_start_solve_from_ready(self, timer: SpeedCubeTimer) -> None:
        # Manually set to READY (normally transitions from grace)
        timer.phase = TimerPhase.READY
        timer.start_solve()
        assert timer.phase == TimerPhase.SOLVING
        assert timer.running is True

    def test_solve_accumulates_time(self, timer: SpeedCubeTimer) -> None:
        timer.phase = TimerPhase.READY
        timer.start_solve()
        # Simulate 1 second of solving
        timer._start_time = time.time() - 1
        timer.tick()
        assert 900 <= timer.elapsed_ms <= 1100  # ~1000ms

    def test_stop_solve_returns_elapsed(self, timer: SpeedCubeTimer) -> None:
        timer.phase = TimerPhase.READY
        timer.start_solve()
        timer._start_time = time.time() - 2  # 2 seconds
        timer.tick()
        elapsed = timer.stop_solve()
        assert 1900 <= elapsed <= 2100
        assert timer.phase == TimerPhase.IDLE
        assert timer.running is False

    def test_reset_during_solve(self, timer: SpeedCubeTimer) -> None:
        timer.phase = TimerPhase.READY
        timer.start_solve()
        timer.reset()
        assert timer.phase == TimerPhase.IDLE
        assert timer.running is False
        assert timer.elapsed_ms == 0


class TestTimerEdgeCases:
    """Edge cases and boundary conditions."""

    def test_double_start_inspection(self, timer: SpeedCubeTimer) -> None:
        timer.start_inspection()
        timer.start_inspection()  # Should not crash
        assert timer.phase == TimerPhase.INSPECTION

    def test_stop_solve_when_not_solving(self, timer: SpeedCubeTimer) -> None:
        elapsed = timer.stop_solve()
        assert elapsed == 0
        assert timer.phase == TimerPhase.IDLE

    def test_reset_when_idle(self, timer: SpeedCubeTimer) -> None:
        timer.reset()  # Should not crash
        assert timer.phase == TimerPhase.IDLE

    def test_full_flow(self, timer: SpeedCubeTimer) -> None:
        """Simulate a complete solve cycle."""
        timer.start_inspection()
        assert timer.phase == TimerPhase.INSPECTION

        timer.cancel()
        assert timer.phase == TimerPhase.IDLE

        timer.start_inspection()
        timer._phase_start = time.time() - 16
        timer.tick()
        assert timer.phase == TimerPhase.GRACE

        timer._phase_start = time.time() - 4
        timer.tick()
        assert timer.phase == TimerPhase.READY

        timer.start_solve()
        assert timer.phase == TimerPhase.SOLVING

        timer._start_time = time.time() - 3
        timer.tick()
        elapsed = timer.stop_solve()
        assert 2900 <= elapsed <= 3100
        assert timer.phase == TimerPhase.IDLE


class TestFormatTime:
    """format_time utility function."""

    def test_zero(self) -> None:
        assert format_time(0) == "00:00.00"

    def test_seconds_only(self) -> None:
        assert format_time(5_000) == "00:05.00"

    def test_minutes_and_seconds(self) -> None:
        assert format_time(65_000) == "01:05.00"

    def test_centiseconds(self) -> None:
        assert format_time(1_234) == "00:01.23"

    def test_large_value(self) -> None:
        assert format_time(3_600_000) == "60:00.00"

    def test_negative_value(self) -> None:
        assert format_time(-5_000) == "00:05.00"

    def test_rounding(self) -> None:
        assert format_time(1_239) == "00:01.23"
        assert format_time(1_240) == "00:01.24"
