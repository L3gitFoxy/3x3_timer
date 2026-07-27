"""Tkinter-based graphical interface for the 3x3 speed cube timer."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from typing import List, Dict, Any

from timer import SpeedCubeTimer, TimerPhase, format_time
from storage import load_times, save_times
from scramble import generate_scramble
from visualizer import open_visualizer

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
    "idle": "Press ANY KEY to reveal scramble",
    "scramble_revealed": "Press ANY KEY again to start inspection",
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
        self.current_scramble: str = generate_scramble()
        self._scramble_revealed: bool = False
        self._times_window: tk.Toplevel | None = None

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

        # Scramble row
        self._scramble_frame = tk.Frame(main, bg=BG)
        self._scramble_frame.pack(pady=(0, 5))

        self._scramble_label = tk.Label(
            self._scramble_frame, text="",
            font=("Courier", 13, "bold"), bg=BG, fg="#00cfff",
            wraplength=1200, justify=tk.CENTER,
        )

        self._new_scramble_btn = tk.Button(
            self._scramble_frame, text="New Scramble",
            command=self._new_scramble,
            font=("Arial", 10), bg="#333333", fg="#00cfff",
            padx=6, pady=3, cursor="hand2", relief="flat",
        )

        self._visualize_btn = tk.Button(
            self._scramble_frame, text="Visualize Scramble",
            command=lambda: open_visualizer(self.root, self.current_scramble),
            font=("Arial", 10), bg="#333333", fg="#ff9900",
            padx=6, pady=3, cursor="hand2", relief="flat",
        )

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
            if not self._scramble_revealed:
                # Reveal scramble
                self._scramble_revealed = True
                self._scramble_label.config(text=self.current_scramble)
                self._scramble_label.pack(pady=(4, 0))
                self._new_scramble_btn.pack(side="left", padx=6, pady=4)
                self._visualize_btn.pack(side="left", padx=6, pady=4)
                self._status_label.config(
                    text=STATUS_TEXTS["scramble_revealed"], fg=FG_YELLOW,
                )
            else:
                # Start inspection
                self._scramble_label.pack_forget()
                self._new_scramble_btn.pack_forget()
                self._visualize_btn.pack_forget()
                self._scramble_revealed = False
                self.timer.start_inspection()

        elif phase == TimerPhase.INSPECTION:
            # Pressing during inspection cancels
            self._hide_scramble()
            self.timer.cancel()

        elif phase == TimerPhase.GRACE:
            # Pressing during grace cancels
            self._hide_scramble()
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
            self._ask_show_times(elapsed)

    def _on_escape(self, _event: tk.Event) -> None:
        phase = self.timer.phase
        if phase in (TimerPhase.INSPECTION, TimerPhase.GRACE):
            self._hide_scramble()
            self.timer.cancel()
        elif phase == TimerPhase.SOLVING:
            self._hide_scramble()
            self.timer.reset()
            self._status_label.config(text=STATUS_TEXTS["idle"], fg=FG_YELLOW)
        else:
            self.root.quit()

    # ── Scramble helpers ────────────────────────────────────────────

    def _hide_scramble(self) -> None:
        self._scramble_label.pack_forget()
        self._new_scramble_btn.pack_forget()
        self._visualize_btn.pack_forget()
        self._scramble_revealed = False

    def _new_scramble(self) -> None:
        self.current_scramble = generate_scramble()
        self._scramble_label.config(text=self.current_scramble)

    # ── Update loop (called every 10 ms) ───────────────────────────

    def _update(self) -> None:
        self.timer.tick()
        self._refresh_display()
        self.root.after(10, self._update)

    def _refresh_display(self) -> None:
        ms = self.timer.display_ms
        phase = self.timer.phase

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

        if self._times_window is not None and self._times_window.winfo_exists():
            self._times_window.lift()
            self._times_window.focus()
            return

        self._times_window = tk.Toplevel(self.root)
        self._times_window.title("3x3 Solve Times")
        self._times_window.geometry("800x600")
        self._times_window.configure(bg=BG)

        def on_close() -> None:
            self._times_window.destroy()
            self._times_window = None

        self._times_window.protocol("WM_DELETE_WINDOW", on_close)

        tk.Label(
            self._times_window, text="Your Solve Times",
            font=("Arial", 18, "bold"), bg=BG, fg=FG_GREEN,
        ).pack(pady=10)

        # Scrollable area
        container = tk.Frame(self._times_window, bg=BG)
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
        if s["count"] > 0:
            self._stat_label(stats_frame, f"Best:   {format_time(s['best'])}", FG_GREEN)
            self._stat_label(stats_frame, f"Worst:  {format_time(s['worst'])}", FG_RED)
            self._stat_label(stats_frame, f"Average: {format_time(s['average'])}", FG_YELLOW)
        self._stat_label(stats_frame, "═" * 50, FG_DARK)

        # ── Solve entries ──
        tk.Label(
            scrollable, text="All Solves:", font=("Arial", 12, "bold"),
            bg=CANVAS_BG, fg=FG_WHITE,
        ).pack(anchor="w", padx=10, pady=(10, 5))

        best = s.get("best")
        worst = s.get("worst")

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

            # Show scramble if available
            scr = entry.get("scramble", "")
            if scr:
                tk.Label(
                    row, text=scr,
                    font=("Courier", 9), bg="#1a1a1a", fg="#888888", anchor="w",
                ).pack(side="left", fill=tk.X, expand=True, padx=(8, 0))

            tk.Button(
                row, text="✕",
                command=lambda i=idx: self._delete_solve(i),
                font=("Arial", 10), bg="#ff4444", fg="white",
                padx=5, pady=0, cursor="hand2", bd=0,
            ).pack(side="right", padx=5)

    @staticmethod
    def _stat_label(parent: tk.Frame, text: str, colour: str) -> None:
        tk.Label(
            parent, text=text,
            font=("Arial", 12, "bold") if "═" not in text else ("Arial", 10),
            bg=CANVAS_BG, fg=colour,
        ).pack(anchor="w")

    # ── Delete & Clear ──────────────────────────────────────────────

    def _delete_solve(self, index: int) -> None:
        if index < 0 or index >= len(self.times):
            return
        if messagebox.askyesno(
            "Delete Solve",
            f"Delete solve: {format_time(self.times[index]['time'])}?",
        ):
            del self.times[index]
            save_times(self.times)
            if self._times_window and self._times_window.winfo_exists():
                self._times_window.destroy()
                self._times_window = None
            self._view_times()

    def _clear_times(self) -> None:
        if messagebox.askyesno("Clear Times", "Are you sure you want to clear all times?"):
            self.times.clear()
            save_times(self.times)
            self.timer.reset()
            self._hide_scramble()
            self._status_label.config(text=STATUS_TEXTS["idle"], fg=FG_YELLOW)
            if self._times_window and self._times_window.winfo_exists():
                self._times_window.destroy()
                self._times_window = None
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