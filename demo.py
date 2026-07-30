"""Combined 3x3 Speed Cube Timer & Visualizer Application.

Includes:
- Rubik's cube state simulation and WCA-style scramble generation.
- JSON-based persistence for solve times.
- Core timer logic state machine.
- Tkinter-based isometric 3D cube visualizer.
- CustomTkinter graphical user interface.
"""

from __future__ import annotations

import csv
import json
import random
import time
import tkinter as tk
import tkinter.messagebox as mb
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from tkinter import filedialog
from typing import Any

import customtkinter as ctk

# ── Theme & appearance ───────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# ── Storage Configuration ────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_FILE = DATA_DIR / "times.json"


def get_data_path(filename: str = "times.json") -> Path:
    """Return the full path to a data file, ensuring the *data/* directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR / filename


def load_times(path: Path = DEFAULT_FILE) -> list[dict[str, Any]]:
    """Load solve times from *path*.

    Returns an empty list if the file is missing, empty, or contains corrupt data.
    """
    if not path.exists() or path.stat().st_size == 0:
        return []

    try:
        with path.open(encoding="utf-8") as f:
            data: Any = json.load(f)
        if isinstance(data, list) and all(
            isinstance(e, dict) and "time" in e and "date" in e for e in data
        ):
            return data
        return []
    except (json.JSONDecodeError, OSError):
        return []


def save_times(times: list[dict[str, Any]], path: Path = DEFAULT_FILE) -> None:
    """Persist *times* to *path* as pretty-printed JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(times, f, indent=2)


# ── Cube Constants & Helpers ─────────────────────────────────────────

MOVES: list[str] = ["U", "D", "L", "R", "F", "B"]
MODIFIERS: list[str] = ["", "'", "2"]

FACE_COLORS: dict[str, str] = {
    "U": "#ffffff",  # white
    "D": "#ffff00",  # yellow
    "F": "#00aa00",  # green
    "B": "#0055ff",  # blue
    "L": "#ff8800",  # orange
    "R": "#ff0000",  # red
}

CubeState = dict[str, list[str]]
OPPOSITES: dict[str, str] = {"U": "D", "D": "U", "R": "L", "L": "R", "F": "B", "B": "F"}


def make_solved_cube() -> CubeState:
    """Return a cube with every face solid."""
    return {f: [f] * 9 for f in "UDFBLR"}


def _rotate_face_cw(cube: CubeState, face: str) -> None:
    """Rotate a single face 90° clockwise in-place."""
    s = cube[face]
    cube[face] = [
        s[6], s[3], s[0],
        s[7], s[4], s[1],
        s[8], s[5], s[2],
    ]


def _do_move(cube: CubeState, face: str) -> None:
    """Apply a single quarter-turn to *face* (updates *cube* in-place)."""
    _rotate_face_cw(cube, face)
    U, D, F, B, L, R = (cube[x] for x in "UDFBLR")

    if face == "U":
        tmp = [F[0], F[1], F[2]]
        F[0], F[1], F[2] = R[0], R[1], R[2]
        R[0], R[1], R[2] = B[0], B[1], B[2]
        B[0], B[1], B[2] = L[0], L[1], L[2]
        L[0], L[1], L[2] = tmp
    elif face == "D":
        tmp = [F[6], F[7], F[8]]
        F[6], F[7], F[8] = L[6], L[7], L[8]
        L[6], L[7], L[8] = B[6], B[7], B[8]
        B[6], B[7], B[8] = R[6], R[7], R[8]
        R[6], R[7], R[8] = tmp
    elif face == "F":
        tmp = [U[6], U[7], U[8]]
        U[6], U[7], U[8] = L[8], L[5], L[2]
        L[2], L[5], L[8] = D[0], D[1], D[2]
        D[0], D[1], D[2] = R[6], R[3], R[0]
        R[0], R[3], R[6] = tmp
    elif face == "B":
        tmp = [U[0], U[1], U[2]]
        U[0], U[1], U[2] = R[2], R[5], R[8]
        R[2], R[5], R[8] = D[8], D[7], D[6]
        D[6], D[7], D[8] = L[0], L[3], L[6]
        L[0], L[3], L[6] = tmp[::-1]
    elif face == "L":
        tmp = [U[0], U[3], U[6]]
        U[0], U[3], U[6] = B[8], B[5], B[2]
        B[2], B[5], B[8] = D[6], D[3], D[0]
        D[0], D[3], D[6] = F[0], F[3], F[6]
        F[0], F[3], F[6] = tmp
    elif face == "R":
        tmp = [U[2], U[5], U[8]]
        U[2], U[5], U[8] = F[2], F[5], F[8]
        F[2], F[5], F[8] = D[2], D[5], D[8]
        D[2], D[5], D[8] = B[6], B[3], B[0]
        B[0], B[3], B[6] = tmp[::-1]


def apply_move(cube: CubeState, move: str) -> None:
    """Apply a full move (e.g. ``"R2"``, ``"U'"``) to *cube* in-place."""
    face = move[0]
    mod = move[1:]
    times = 3 if mod == "'" else (2 if mod == "2" else 1)
    for _ in range(times):
        _do_move(cube, face)


def apply_scramble(cube: CubeState, scramble: str) -> None:
    """Apply a space-separated scramble string to *cube* in-place."""
    for m in scramble.split():
        apply_move(cube, m)


def compute_states(scramble: str) -> list[CubeState]:
    """Return a list of cube states from solved → after each move."""
    states: list[CubeState] = [make_solved_cube()]
    for m in scramble.split():
        nxt = {f: list(states[-1][f]) for f in "UDFBLR"}
        apply_move(nxt, m)
        states.append(nxt)
    return states


def generate_scramble(length: int = 20) -> str:
    """Generate a random WCA-style scramble of *length* moves."""
    scramble: list[str] = []
    last: str | None = None
    for _ in range(length):
        available = [
            m for m in MOVES
            if m != last and (last is None or m != OPPOSITES[last])
        ]
        move = random.choice(available)
        mod = random.choice(MODIFIERS)
        scramble.append(move + mod)
        last = move
    return " ".join(scramble)


# ── Timer Logic ──────────────────────────────────────────────────────

class TimerPhase(Enum):
    """Represents the current state of the timer."""
    IDLE = auto()
    INSPECTION = auto()
    GRACE = auto()
    READY = auto()
    SOLVING = auto()


class SpeedCubeTimer:
    """Pure-logic timer for 3x3 speed solves."""

    INSPECTION_MS: int = 15_000
    GRACE_MS: int = 3_000

    def __init__(self) -> None:
        self.phase: TimerPhase = TimerPhase.IDLE
        self.running: bool = False
        self.elapsed_ms: int = 0
        self._start_time: float | None = None
        self._phase_start: float = 0.0

    def start_inspection(self) -> None:
        self.phase = TimerPhase.INSPECTION
        self._phase_start = time.time()
        self._start_time = None

    def cancel(self) -> None:
        self.phase = TimerPhase.IDLE
        self._phase_start = 0.0
        self._start_time = None

    def start_solve(self) -> None:
        self.phase = TimerPhase.SOLVING
        self.running = True
        self.elapsed_ms = 0
        self._start_time = time.time()

    def stop_solve(self) -> int:
        self.running = False
        self.phase = TimerPhase.IDLE
        elapsed = self.elapsed_ms
        self.elapsed_ms = 0
        self._start_time = None
        return elapsed

    def reset(self) -> None:
        self.running = False
        self.phase = TimerPhase.IDLE
        self.elapsed_ms = 0
        self._start_time = None
        self._phase_start = 0.0

    def tick(self) -> None:
        now = time.time()
        if self.phase == TimerPhase.INSPECTION:
            elapsed = int((now - self._phase_start) * 1000)
            if self.INSPECTION_MS - elapsed <= 0:
                self.phase = TimerPhase.GRACE
                self._phase_start = now
        elif self.phase == TimerPhase.GRACE:
            elapsed = int((now - self._phase_start) * 1000)
            if self.GRACE_MS - elapsed <= 0:
                self.phase = TimerPhase.READY
                self._phase_start = now
        elif self.phase == TimerPhase.SOLVING and self.running:
            self.elapsed_ms = int((now - self._start_time) * 1000)

    @property
    def display_ms(self) -> int:
        now = time.time()
        if self.phase == TimerPhase.INSPECTION:
            return max(0, self.INSPECTION_MS - int((now - self._phase_start) * 1000))
        if self.phase == TimerPhase.GRACE:
            return max(0, self.GRACE_MS - int((now - self._phase_start) * 1000))
        if self.phase in (TimerPhase.SOLVING, TimerPhase.READY):
            return self.elapsed_ms if self.running else 0
        return 0


def format_time(milliseconds: int) -> str:
    """Convert milliseconds to ``MM:SS.MS`` format."""
    ms = abs(milliseconds)
    seconds = ms // 1000
    minutes = seconds // 60
    seconds %= 60
    centiseconds = (ms % 1000) // 10
    return f"{minutes:02d}:{seconds:02d}.{centiseconds:02d}"


# ── Visualizer Window ────────────────────────────────────────────────

def open_visualizer(parent: tk.Tk | tk.Toplevel, scramble_str: str) -> None:
    """Open a popup window to step through *scramble_str* move by move."""
    moves = scramble_str.split()
    if not moves:
        return

    win = tk.Toplevel(parent)
    win.title("Scramble Visualizer")
    win.configure(bg="#1a1a1a")
    win.geometry("600x540")

    move_label = tk.Label(win, text="", font=("Arial", 16, "bold"), bg="#1a1a1a", fg="#ff9900")
    move_label.pack(pady=(12, 2))

    seq_label = tk.Label(win, text="", font=("Courier", 11), bg="#1a1a1a", fg="#555555", wraplength=560, justify="center")
    seq_label.pack(pady=(0, 4))

    tk.Label(win, text="← →  arrow keys to step through moves", font=("Arial", 10), bg="#1a1a1a", fg="#666666").pack(pady=(0, 6))

    canvas = tk.Canvas(win, bg="#1a1a1a", highlightthickness=0, width=600, height=340)
    canvas.pack()

    cube_states: list[CubeState] = compute_states(scramble_str)
    step_idx: list[int] = [0]

    def shade(color: str, factor: float) -> str:
        r = int(int(color[1:3], 16) * factor)
        g = int(int(color[3:5], 16) * factor)
        b = int(int(color[5:7], 16) * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    def draw_cube(cube: CubeState) -> None:
        canvas.delete("all")
        S = 36
        CX, CY = 300, 220

        def add(p1, p2):
            return (p1[0] + p2[0], p1[1] + p2[1])

        def scale(v, f):
            return (v[0] * f, v[1] * f)

        vec_UR = (S, -S / 2)
        vec_UL = (-S, -S / 2)
        vec_DR = (S, S / 2)
        vec_DL = (-S, S / 2)
        vec_D = (0, S)

        def draw_face(face_name, origin, vec_c, vec_r, darken):
            for row in range(3):
                for col in range(3):
                    idx = row * 3 + col
                    p0 = add(origin, add(scale(vec_c, col), scale(vec_r, row)))
                    p1 = add(p0, vec_c)
                    p2 = add(p1, vec_r)
                    p3 = add(p0, vec_r)
                    color = FACE_COLORS[cube[face_name][idx]]
                    if darken != 1.0:
                        color = shade(color, darken)
                    canvas.create_polygon([p0, p1, p2, p3], fill=color, outline="#111", width=2)

        draw_face("R", (CX, CY), vec_UR, vec_D, 0.75)
        draw_face("F", add((CX, CY), scale(vec_UL, 3)), vec_DR, vec_D, 0.88)
        draw_face("U", (CX, CY - 3 * S), vec_DR, vec_DL, 1.0)

    def refresh() -> None:
        idx = step_idx[0]
        draw_cube(cube_states[idx])
        if idx == 0:
            move_label.config(text="Solved state", fg="#aaaaaa")
            seq_label.config(text=" ".join(moves))
        elif idx == len(moves):
            move_label.config(text="Done!", fg="#00ff00")
            seq_label.config(text=" ".join(moves))
        else:
            move_label.config(text=f"Move {idx}/{len(moves)}: {moves[idx-1]}", fg="#ff9900")
            parts = [f"[{m}]" if i == idx - 1 else m for i, m in enumerate(moves)]
            seq_label.config(text=" ".join(parts))

    def on_key(event: tk.Event) -> None:
        if event.keysym == "Right" and step_idx[0] < len(moves):
            step_idx[0] += 1
            refresh()
        elif event.keysym == "Left" and step_idx[0] > 0:
            step_idx[0] -= 1
            refresh()

    win.bind("<Key>", on_key)
    refresh()


# ── Main Application GUI ─────────────────────────────────────────────

class Application:
    """Main application window with CustomTkinter."""

    def __init__(self, root: ctk.CTk) -> None:
        self.root = root
        self.root.title("3x3 Speed Cube Timer")
        self.root.minsize(600, 500)
        self.root.geometry("700x580")

        self.timer = SpeedCubeTimer()
        self.times: list[dict[str, Any]] = load_times()
        self.current_scramble: str = generate_scramble()
        self._times_window: ctk.CTkToplevel | None = None

        self._build_ui()
        self._bind_keys()
        self._update()
        self._show_welcome_if_first_run()

    def _build_ui(self) -> None:
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        main = ctk.CTkFrame(self.root)
        main.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main.grid_rowconfigure(3, weight=1)
        main.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            main, text="3x3 Speed Cube Timer",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).grid(row=0, column=0, pady=(0, 10))

        scramble_frame = ctk.CTkFrame(main, fg_color="transparent")
        scramble_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        scramble_frame.grid_columnconfigure(0, weight=1)

        self._scramble_label = ctk.CTkLabel(
            scramble_frame,
            text=self.current_scramble,
            font=ctk.CTkFont(size=13, family="Courier"),
            wraplength=600,
            justify="center",
            text_color="#00cfff",
        )
        self._scramble_label.grid(row=0, column=0, columnspan=3, pady=(4, 6), sticky="ew")

        btn_row = ctk.CTkFrame(scramble_frame, fg_color="transparent")
        btn_row.grid(row=1, column=0)

        ctk.CTkButton(
            btn_row, text="New Scramble",
            command=self._new_scramble,
            width=120, height=28,
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            btn_row, text="Visualize Scramble",
            command=lambda: open_visualizer(self.root, self.current_scramble),
            width=140, height=28, fg_color="#b8860b", hover_color="#8b6508",
        ).pack(side="left", padx=6)

        self._timer_label = ctk.CTkLabel(
            main, text="00:00.00",
            font=ctk.CTkFont(size=100, weight="bold"),
            text_color="#00ff00",
        )
        self._timer_label.grid(row=2, column=0, pady=10)

        self._status_label = ctk.CTkLabel(
            main, text="Press ANY KEY to start inspection",
            font=ctk.CTkFont(size=16),
            text_color="#ffff00",
        )
        self._status_label.grid(row=3, column=0, pady=(0, 10))

        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.grid(row=4, column=0, pady=10)

        ctk.CTkButton(
            btn_frame, text="View Times", command=self._view_times,
            width=130, height=36,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame, text="Clear Times", command=self._clear_times,
            width=130, height=36, fg_color="#cc0000", hover_color="#990000",
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            main,
            text="SPACE or ENTER to Start/Stop  ·  ESC to Exit",
            font=ctk.CTkFont(size=12),
            text_color="#888888",
        ).grid(row=5, column=0, pady=(10, 0))

        self.root.bind("<Configure>", self._on_resize)

    def _bind_keys(self) -> None:
        self.root.bind("<Key>", self._on_key)
        self.root.bind("<Escape>", self._on_escape)

    def _on_resize(self, event: Any = None) -> None:
        if not hasattr(self, "_timer_label"):
            return
        w = self.root.winfo_width()
        size = max(50, min(110, w // 6))
        self._timer_label.configure(font=ctk.CTkFont(size=size, weight="bold"))
        self._scramble_label.configure(wraplength=max(200, w - 80))

    def _on_key(self, event: tk.Event) -> None:
        if event.keysym == "Escape":
            return

        phase = self.timer.phase

        if phase == TimerPhase.IDLE:
            self.timer.start_inspection()
        elif phase in (TimerPhase.INSPECTION, TimerPhase.GRACE):
            self.timer.cancel()
        elif phase == TimerPhase.READY:
            self.timer.start_solve()
        elif phase == TimerPhase.SOLVING:
            elapsed = self.timer.stop_solve()
            self.times.append({
                "time": elapsed,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "scramble": self.current_scramble,
            })
            save_times(self.times)
            self.current_scramble = generate_scramble()
            self._scramble_label.configure(text=self.current_scramble)
            self._ask_show_times(elapsed)

    def _on_escape(self, _event: tk.Event) -> None:
        phase = self.timer.phase
        if phase in (TimerPhase.INSPECTION, TimerPhase.GRACE):
            self.timer.cancel()
        elif phase == TimerPhase.SOLVING:
            self.timer.reset()
            self._status_label.configure(
                text="Press ANY KEY to start inspection", text_color="#ffff00"
            )
        else:
            self.root.quit()

    def _new_scramble(self) -> None:
        self.current_scramble = generate_scramble()
        self._scramble_label.configure(text=self.current_scramble)

    def _update(self) -> None:
        self.timer.tick()
        self._refresh_display()
        self.root.after(10, self._update)

    def _refresh_display(self) -> None:
        ms = self.timer.display_ms
        phase = self.timer.phase

        if phase == TimerPhase.INSPECTION:
            remain_s = ms // 1000
            self._status_label.configure(
                text=f"LOOKING TIME: {remain_s} seconds",
                text_color="#00ff00",
            )
            self._timer_label.configure(text=format_time(ms), text_color="#ffaa00")
        elif phase == TimerPhase.GRACE:
            self._status_label.configure(text="READY TO SOLVE: 3 seconds", text_color="#0099ff")
            self._timer_label.configure(text=format_time(ms), text_color="#0099ff")
        elif phase == TimerPhase.READY:
            self._status_label.configure(
                text="PRESS ANY KEY TO START SOLVING", text_color="#ff0000"
            )
            self._timer_label.configure(text="00:00.00", text_color="#00ff00")
        elif phase == TimerPhase.SOLVING:
            self._status_label.configure(
                text="SOLVING... Press ANY KEY to STOP",
                text_color="#00ff00",
            )
            self._timer_label.configure(text=format_time(ms), text_color="#00ff00")
        else:
            self._status_label.configure(
                text="Press ANY KEY to start inspection", text_color="#ffff00"
            )
            self._timer_label.configure(text="00:00.00", text_color="#00ff00")

    @staticmethod
    def _sliding_avg(times_ms: list[int], window: int) -> int | None:
        if len(times_ms) < window:
            return None
        recent = times_ms[-window:]
        return int(sum(recent) / window)

    def _stats(self) -> dict[str, Any]:
        times_ms = [e["time"] for e in self.times]
        if not times_ms:
            return {"count": 0}
        return {
            "count": len(times_ms),
            "best": min(times_ms),
            "worst": max(times_ms),
            "average": sum(times_ms) / len(times_ms),
            "ao5": self._sliding_avg(times_ms, 5),
            "ao12": self._sliding_avg(times_ms, 12),
            "ao100": self._sliding_avg(times_ms, 100),
        }

    def _draw_times_graph(self, canvas: tk.Canvas, times_ms: list[int]) -> None:
        canvas.delete("all")
        n = len(times_ms)
        if n == 0:
            return

        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        if cw < 10 or ch < 10:
            cw, ch = 600, 200

        margin_l, margin_r, margin_t, margin_b = 60, 20, 15, 35
        plot_w = cw - margin_l - margin_r
        plot_h = ch - margin_t - margin_b

        if plot_w < 20 or plot_h < 20:
            return

        mn = min(times_ms)
        mx = max(times_ms)
        rng = mx - mn if mx != mn else 1

        canvas.create_line(margin_l, ch - margin_b, cw - margin_r, ch - margin_b, fill="#555555", width=1)
        canvas.create_line(margin_l, margin_t, margin_l, ch - margin_b, fill="#555555", width=1)

        for i in range(5):
            y_val = mx - (rng * i / 4)
            y = margin_t + (plot_h * i / 4)
            canvas.create_text(
                margin_l - 8, y, text=format_time(int(y_val)),
                fill="#888888", font=("Arial", 8), anchor="e",
            )
            canvas.create_line(margin_l, y, cw - margin_r, y, fill="#333333", width=1, dash=(2, 4))

        points: list[float] = []
        for i, t in enumerate(times_ms):
            x = margin_l + (plot_w * i / (n - 1)) if n > 1 else margin_l + plot_w // 2
            y = margin_t + plot_h - (plot_h * (t - mn) / rng)
            points.extend([x, y])

        if len(points) >= 4:
            canvas.create_line(points, fill="#00ff00", width=2, smooth=True)

    def _view_times(self) -> None:
        if not self.times:
            mb.showinfo("Times", "No times recorded yet!", parent=self.root)
            return

        if self._times_window is not None and self._times_window.winfo_exists():
            self._times_window.lift()
            self._times_window.focus()
            return

        self._times_window = ctk.CTkToplevel(self.root)
        self._times_window.title("3x3 Solve Times")
        self._times_window.minsize(700, 500)
        self._times_window.geometry("900x650")

        def on_close() -> None:
            if self._times_window is not None:
                self._times_window.destroy()
            self._times_window = None

        self._times_window.protocol("WM_DELETE_WINDOW", on_close)
        self._times_window.grid_rowconfigure(2, weight=1)
        self._times_window.grid_columnconfigure(0, weight=1)

        title_frame = ctk.CTkFrame(self._times_window, fg_color="transparent")
        title_frame.grid(row=0, column=0, pady=(12, 2))
        title_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            title_frame, text="Your Solve Times",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, padx=(0, 20))

        ctk.CTkButton(
            title_frame, text="Export CSV",
            command=self._export_csv,
            width=100, height=28, fg_color="#2b5b84", hover_color="#1a3f5c",
        ).grid(row=0, column=1)

        graph_frame = ctk.CTkFrame(self._times_window, fg_color="#0a0a0a", height=180)
        graph_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))
        graph_frame.grid_propagate(False)

        graph_canvas = tk.Canvas(graph_frame, bg="#0a0a0a", highlightthickness=0, height=180)
        graph_canvas.pack(fill="both", expand=True)

        times_ms = [e["time"] for e in self.times]
        self._times_window.after(50, lambda: self._draw_times_graph(graph_canvas, times_ms))

        scroll_container = ctk.CTkScrollableFrame(self._times_window, fg_color="transparent")
        scroll_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        scroll_container.grid_columnconfigure(0, weight=1)

        s = self._stats()
        stats_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        stats_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkLabel(
            stats_frame, text=f"Total Solves: {s['count']}",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, sticky="w", pady=2)

        if s["count"] > 0:
            ctk.CTkLabel(stats_frame, text=f"Best:   {format_time(s['best'])}", text_color="#00ff00").grid(row=1, column=0, sticky="w")
            ctk.CTkLabel(stats_frame, text=f"Worst:  {format_time(s['worst'])}", text_color="#ff4444").grid(row=2, column=0, sticky="w")
            ctk.CTkLabel(stats_frame, text=f"Average: {format_time(int(s['average']))}", text_color="#ffff00").grid(row=3, column=0, sticky="w")

    def _export_csv(self) -> None:
        if not self.times:
            mb.showinfo("Export", "No times to export!", parent=self._times_window)
            return

        filename = filedialog.asksaveasfilename(
            parent=self._times_window,
            title="Export Times as CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not filename:
            return

        try:
            with Path(filename).open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["#", "Time (ms)", "Time (formatted)", "Date", "Scramble"])
                for idx, entry in enumerate(self.times):
                    writer.writerow([
                        idx + 1,
                        entry["time"],
                        format_time(entry["time"]),
                        entry["date"],
                        entry.get("scramble", ""),
                    ])
            mb.showinfo("Export Successful", f"Exported {len(self.times)} solves.", parent=self._times_window)
        except (OSError, PermissionError) as e:
            mb.showerror("Export Failed", str(e), parent=self._times_window)

    def _clear_times(self) -> None:
        if mb.askyesno("Clear Times", "Are you sure you want to clear all times?"):
            self.times.clear()
            save_times(self.times)
            self.timer.reset()
            self._status_label.configure(text="Press ANY KEY to start inspection", text_color="#ffff00")
            if self._times_window and self._times_window.winfo_exists():
                self._times_window.destroy()
                self._times_window = None
            mb.showinfo("Success", "All times cleared!")

    def _show_welcome_if_first_run(self) -> None:
        welcome_flag = get_data_path(".welcome_shown")
        if welcome_flag.exists():
            return
        mb.showinfo(
            "Welcome to 3x3 Speed Cube Timer!",
            "1. Press ANY KEY to start inspection\n"
            "2. Press ANY KEY again to start solving\n"
            "3. Press ANY KEY to stop the timer\n\nHappy cubing! 🧩",
            parent=self.root,
        )
        welcome_flag.parent.mkdir(parents=True, exist_ok=True)
        welcome_flag.touch()

    def _ask_show_times(self, elapsed: int) -> None:
        if mb.askyesno("Solve Complete!", f"Solve Time: {format_time(elapsed)}\n\nView your times?"):
            self._view_times()


def main() -> None:
    """Entry point for the application."""
    root = ctk.CTk()
    Application(root)
    root.mainloop()


if __name__ == "__main__":
    main()