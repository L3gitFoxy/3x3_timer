"""Core timer logic — state machine with no UI dependencies."""

from __future__ import annotations

import time
from enum import Enum, auto
from typing import Optional


class TimerPhase(Enum):
    """Represents the current state of the timer."""
    IDLE = auto()
    INSPECTION = auto()
    GRACE = auto()
    READY = auto()
    SOLVING = auto()


class SpeedCubeTimer:
    """Pure-logic timer for 3x3 speed solves.

    Manages the state machine: IDLE → INSPECTION → GRACE → READY → SOLVING.
    """

    INSPECTION_MS: int = 15_000   # 15 seconds
    GRACE_MS: int = 3_000         # 3 seconds

    def __init__(self) -> None:
        self.phase: TimerPhase = TimerPhase.IDLE
        self.running: bool = False
        self.elapsed_ms: int = 0
        self._start_time: Optional[float] = None
        self._phase_start: float = 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start_inspection(self) -> None:
        """Begin the inspection/looking phase."""
        self.phase = TimerPhase.INSPECTION
        self._phase_start = time.time()
        self._start_time = None

    def cancel(self) -> None:
        """Cancel any in-progress inspection or grace period."""
        self.phase = TimerPhase.IDLE
        self._phase_start = 0.0
        self._start_time = None

    def start_solve(self) -> None:
        """Begin the solve (triggered by key press during READY phase)."""
        self.phase = TimerPhase.SOLVING
        self.running = True
        self.elapsed_ms = 0
        self._start_time = time.time()

    def stop_solve(self) -> int:
        """End the solve and return the elapsed time in milliseconds."""
        self.running = False
        self.phase = TimerPhase.IDLE
        elapsed = self.elapsed_ms
        self.elapsed_ms = 0
        self._start_time = None
        return elapsed

    def tick(self) -> None:
        """Advance state — call every ~10 ms from the UI update loop."""

        now = time.time()

        if self.phase == TimerPhase.INSPECTION:
            elapsed = int((now - self._phase_start) * 1000)
            remaining = self.INSPECTION_MS - elapsed
            if remaining <= 0:
                self.phase = TimerPhase.GRACE
                self._phase_start = now

        elif self.phase == TimerPhase.GRACE:
            elapsed = int((now - self._phase_start) * 1000)
            remaining = self.GRACE_MS - elapsed
            if remaining <= 0:
                self.phase = TimerPhase.READY
                self._phase_start = now

        elif self.phase == TimerPhase.SOLVING and self.running:
            self.elapsed_ms = int((now - self._start_time) * 1000)  # type: ignore[operator]

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    @property
    def display_ms(self) -> int:
        """Milliseconds to show on the timer display, based on current phase."""
        now = time.time()

        if self.phase == TimerPhase.INSPECTION:
            return max(0, self.INSPECTION_MS - int((now - self._phase_start) * 1000))
        if self.phase == TimerPhase.GRACE:
            return max(0, self.GRACE_MS - int((now - self._phase_start) * 1000))
        if self.phase in (TimerPhase.SOLVING, TimerPhase.READY):
            return self.elapsed_ms if self.running else 0
        return 0

    @property
    def status_key(self) -> str:
        """Key for looking up the status text in i18n or UI strings."""
        mapping = {
            TimerPhase.IDLE: "idle",
            TimerPhase.INSPECTION: "inspection",
            TimerPhase.GRACE: "grace",
            TimerPhase.READY: "ready",
            TimerPhase.SOLVING: "solving",
        }
        return mapping.get(self.phase, "idle")


# ------------------------------------------------------------------
# Utility
# ------------------------------------------------------------------

def format_time(milliseconds: int) -> str:
    """Convert milliseconds to ``MM:SS.MS`` format."""
    ms = abs(milliseconds)
    seconds = ms // 1000
    minutes = seconds // 60
    seconds %= 60
    centiseconds = (ms % 1000) // 10
    return f"{minutes:02d}:{seconds:02d}.{centiseconds:02d}"