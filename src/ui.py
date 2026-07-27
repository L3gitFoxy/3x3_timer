"""Tkinter-based graphical interface for the 3×3 speed cube timer."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from typing import List, Dict, Any

from timer import SpeedCubeTimer, TimerPhase, format_time
from storage import load_times, save_times

# ── Colour palette ──────────────────────────────────────────────────
BG = "#1a1a1a"
FG_GREEN = "#00ff00"
FG_YELLOW = "#ffff00"
FG_BLUE = "#0099ff"
FG_RED = "#ff0000"
FG_GREY = "#cccccc"
FG_WHITE = "#ffffff"
FG_DARK = "#666666"
FG_BROWN = "#8B4513"
CANVAS_BG = "#0a0a0a"
BUTTON_BLUE = "#0066ff"
BUTTON_RED = "#ff0000"

# ── Status text keyed to timer phase ────────────────────────────────
STATUS_TEXTS = {
    "idle": "Press ANY KEY to start looking time",
    "inspection": "LOOKING TIME:",
    "grace": "READY TO SOLVE:",
    "ready": "PRESS ANY KEY TO START SOLVING",
    "solving": "SOLVING... Press ANY KEY to STOP",
}


class Application:
    """Main application window."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("3x3 Speed Cube Timer")
        self.root.geometry("600x500")
        self.root.configure(bg=BG)

        self.timer = SpeedCubeTimer()
        self.times: List[Dict[str, Any]] = load_times()

        self._build_ui()
        self._bind_keys()
        self._update()

    # ── UI construction ─────────────────────────────────────────────

    def _build_ui(self) -> None:
        main = tk.Frame(self.root, bg=BG)
        main.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        # Title
        tk.Label(
            main, text="3x3 Speed Cube Timer",
            font=("Arial", 24, "bold"), bg=BG, fg=FG_GREEN,
        ).pack(pady=10)

        # Timer display
        self._timer_label = tk.Label(
            main, text="00:00.00",
            font=("Arial", 100, "bold"), bg=BG, fg=FG_GREEN,
        )
        self._timer_label.pack(pady=20)

        # Status
        self._status_label = tk.Label(
            main, text=STATUS_TEXTS["idle"],
            font=("Arial", 16), bg=BG, fg=FG_YELLOW,
        )
        self._status_label.pack(pady=10)

        # Buttons
        btn_frame = tk.Frame(main, bg=BG)
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame, text="View Times", command=self._view_times,
            font=("Arial", 12), bg=BUTTON_BLUE, fg="white",
            padx=10, pady=10, cursor="hand2",
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            btn_frame, text="Clear Times", command=self._clear_times,
            font=("Arial", 12), bg=BUTTON_RED, fg="white",
            padx=10, pady=10, cursor="hand2",
        ).grid(row=0, column=1, padx=10)

        # Info
        tk.Label(
            main,
            text="Press ANY KEY to Start\nPress ANY KEY to Stop\nPress ESC to Exit",
            font=("Arial", 12), bg=BG, fg=FG_GREY, justify=tk.CENTER,
        ).pack(pady=20)

    def _bind_keys(self) -> None:
        self.root.bind("<Key>", self._on_key)
        self.root.bind("<Escape>", self._on_escape)

    # ── Key handling ────────────────────────────────────────────────

    def _on_key(self, event: tk.Event) -> None:
        if event.keysym == "Escape":
            return

        phase = self.timer.phase

        if phase == TimerPhase.IDLE:
            self.timer.start_inspection()

        elif phase == TimerPhase.INSPECTION:
            self.timer.cancel()

        elif phase == TimerPhase.GRACE:
            self.timer.cancel()

        elif phase == TimerPhase.READY:
            self.timer.start_solve()

        elif phase == TimerPhase.SOLVING:
            elapsed = self.timer.stop_solve()
            self.times.append({
                "time": elapsed,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
            save_times(self.times)
            self._ask_show_times(elapsed)

    def _on_escape(self, _event: tk.Event) -> None:
        self.root.quit()

    # ── Update loop (called every 10 ms) ───────────────────────────

    def _update(self) -> None:
        self.timer.tick()
        self._refresh_display()
        self.root.after(10, self._update)

    def _refresh_display(self) -> None:
        ms = self.timer.display_ms
        phase = self.timer.phase

        # Timer text
        if phase == TimerPhase.INSPECTION:
            remain_s = ms // 1000
            if remain_s <= 0:
                remain_s = 1
            self._status_label.config(
                text=f"LOOKING TIME: {remain_s - 1} seconds", fg=FG_GREEN,
            )
            self._timer_label.config(text=format_time(ms), fg="#ffaa00")
        elif phase == TimerPhase.GRACE:
            self._status_label.config(text="READY TO SOLVE: 3 seconds", fg=FG_BLUE)
            self._timer_label.config(text=format_time(ms), fg=FG_BLUE)
        elif phase == TimerPhase.READY:
            self._status_label.config(text="PRESS ANY KEY TO START SOLVING", fg=FG_RED)
            self._timer_label.config(text="00:00.00", fg=FG_GREEN)
        elif phase == TimerPhase.SOLVING:
            self._status_label.config(text="SOLVING... Press ANY KEY to STOP", fg=FG_GREEN)
            self._timer_label.config(text=format_time(ms), fg=FG_GREEN)
        else:  # IDLE
            self._status_label.config(text=STATUS_TEXTS["idle"], fg=FG_YELLOW)
            self._timer_label.config(text="00:00.00", fg=FG_GREEN)

    # ── Statistics helper ───────────────────────────────────────────

    def _stats(self) -> Dict[str, Any]:
        times_ms = [e["time"] for e in self.times]
        if not times_ms:
            return {"count": 0}
        return {
            "count": len(times_ms),
            "best": min(times_ms),
            "worst": max(times_ms),
            "average": sum(times_ms) / len(times_ms),
        }

    # ── View times window ───────────────────────────────────────────

    def _view_times(self) -> None:
        if not self.times:
            messagebox.showinfo("Times", "No times recorded yet!")
            return

        win = tk.Toplevel(self.root)
        win.title("3x3 Solve Times")
        win.geometry("700x600")
        win.configure(bg=BG)

        tk.Label(
            win, text="Your Solve Times",
            font=("Arial", 18, "bold"), bg=BG, fg=FG_GREEN,
        ).pack(pady=10)

        # Scrollable area
        container = tk.Frame(win, bg=BG)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(container, bg=CANVAS_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=CANVAS_BG)

        scrollable.bind(
            "<Configure>",
            lambda _: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # ── Statistics ──
        s = self._stats()
        stats_frame = tk.Frame(scrollable, bg=CANVAS_BG)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        self._stat_label(stats_frame, "═" * 50, FG_DARK)
        self._stat_label(stats_frame, f"Total Solves: {s['count']}", FG_WHITE)
        self._stat_label(stats_frame, f"Best:   {format_time(s['best'])}", FG_GREEN)
        self._stat_label(stats_frame, f"Worst:  {format_time(s['worst'])}", FG_RED)
        self._stat_label(stats_frame, f"Average: {format_time(s['average'])}", FG_YELLOW)
        self._stat_label(stats_frame, "═" * 50, FG_DARK)

        # ── Solve entries ──
        tk.Label(
            scrollable, text="All Solves:", font=("Arial", 12, "bold"),
            bg=CANVAS_BG, fg=FG_WHITE,
        ).pack(anchor="w", padx=10, pady=(10, 5))

        best = s["best"]
        worst = s["worst"]

        for idx, entry in enumerate(self.times):
            t = entry["time"]
            colour = FG_GREEN if t == best else FG_RED if t == worst else \
                     FG_BROWN if t >= 40_000 else "#ffff7c"

            row = tk.Frame(scrollable, bg="#1a1a1a")
            row.pack(fill=tk.X, padx=10, pady=3)

            tk.Label(
                row, text=f"{idx + 1}. {format_time(t)} - {entry['date']}",
                font=("Arial", 11), bg="#1a1a1a", fg=colour, anchor="w",
            ).pack(side="left", fill=tk.X, expand=True)

            tk.Button(
                row, text="✕",
                command=lambda i=idx: self._delete_solve(i, win),
                font=("Arial", 10), bg="#ff4444", fg="white",
                padx=5, pady=0, cursor="hand2", bd=0,
            ).pack(side="right", padx=5)

    @staticmethod
    def _stat_label(parent: tk.Frame, text: str, colour: str) -> None:
        tk.Label(
            parent, text=text, font=("Arial", 12, "bold") if "═" not in text else ("Arial", 10),
            bg=CANVAS_BG, fg=colour,
        ).pack(anchor="w")

    # ── Delete & Clear ──────────────────────────────────────────────

    def _delete_solve(self, index: int, window: tk.Toplevel) -> None:
        if messagebox.askyesno(
            "Delete Solve",
            f"Delete solve: {format_time(self.times[index]['time'])}?",
        ):
            del self.times[index]
            save_times(self.times)
            window.destroy()
            self._view_times()

    def _clear_times(self) -> None:
        if messagebox.askyesno("Clear Times", "Are you sure you want to clear all times?"):
            self.times.clear()
            save_times(self.times)
            self.timer.cancel()
            messagebox.showinfo("Success", "All times cleared!")

    # ── Dialog after solve ──────────────────────────────────────────

    def _ask_show_times(self, elapsed: int) -> None:
        if messagebox.askyesno(
            "Solve Complete!",
            f"Solve Time: {format_time(elapsed)}\n\nView your times?",
        ):
            self._view_times()


def main() -> None:
    """Entry point for the application."""
    root = tk.Tk()
    Application(root)
    root.mainloop()