"""CustomTkinter-based graphical interface for the 3x3 speed cube timer."""

from __future__ import annotations

import csv
import tkinter as tk  # for Canvas (no CTkCanvas in customtkinter 5.x)
import tkinter.messagebox as mb
from datetime import datetime
from pathlib import Path
from tkinter import filedialog
from typing import Any

import customtkinter as ctk

from scramble import generate_scramble
from storage import get_data_path, load_times, save_times
from timer import SpeedCubeTimer, TimerPhase, format_time
from visualizer import open_visualizer

# ── Theme & appearance ───────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


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

    # ── UI construction ─────────────────────────────────────────────

    def _build_ui(self) -> None:
        # Main container — expandable grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        main = ctk.CTkFrame(self.root)
        main.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main.grid_rowconfigure(3, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # ── Title ──
        ctk.CTkLabel(
            main, text="3x3 Speed Cube Timer",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).grid(row=0, column=0, pady=(0, 10))

        # ── Scramble panel (always visible — inline) ──
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

        # ── Timer display ──
        self._timer_label = ctk.CTkLabel(
            main, text="00:00.00",
            font=ctk.CTkFont(size=100, weight="bold"),
            text_color="#00ff00",
        )
        self._timer_label.grid(row=2, column=0, pady=10)

        # ── Status ──
        self._status_label = ctk.CTkLabel(
            main, text="Press ANY KEY to start inspection",
            font=ctk.CTkFont(size=16),
            text_color="#ffff00",
        )
        self._status_label.grid(row=3, column=0, pady=(0, 10))

        # ── Buttons row ──
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

        # ── Info footer ──
        ctk.CTkLabel(
            main,
            text="SPACE or ENTER to Start/Stop  ·  ESC to Exit",
            font=ctk.CTkFont(size=12),
            text_color="#888888",
        ).grid(row=5, column=0, pady=(10, 0))

        # ── Mount resize handler ──
        self.root.bind("<Configure>", self._on_resize)

    def _bind_keys(self) -> None:
        self.root.bind("<Key>", self._on_key)
        self.root.bind("<Escape>", self._on_escape)

    # ── Responsive layout ───────────────────────────────────────────

    def _on_resize(self, event: Any = None) -> None:
        """Scale timer font proportional to window width."""
        if not hasattr(self, "_timer_label"):
            return
        w = self.root.winfo_width()
        size = max(50, min(110, w // 6))
        self._timer_label.configure(font=ctk.CTkFont(size=size, weight="bold"))
        # Update scramble wrap width
        self._scramble_label.configure(wraplength=max(200, w - 80))
        # Adjust main frame padding
        pad = max(10, min(40, w // 18))
        for child in self.root.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                child.grid_configure(padx=pad, pady=pad)

    # ── Key handling ────────────────────────────────────────────────

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

    # ── Scramble helper ─────────────────────────────────────────────

    def _new_scramble(self) -> None:
        self.current_scramble = generate_scramble()
        self._scramble_label.configure(text=self.current_scramble)

    # ── Update loop (every 10 ms) ───────────────────────────────────

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
            self._status_label.configure(
                text=f"LOOKING TIME: {remain_s - 1} seconds",
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
        else:  # IDLE
            self._status_label.configure(
                text="Press ANY KEY to start inspection", text_color="#ffff00"
            )
            self._timer_label.configure(text="00:00.00", text_color="#00ff00")

    # ── Statistics ──────────────────────────────────────────────────

    @staticmethod
    def _sliding_avg(times_ms: list[int], window: int) -> int | None:
        """Return the most recent sliding-window average, or None if not enough solves."""
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

    # ── Times graph (canvas-based) ──────────────────────────────────

    def _draw_times_graph(self, canvas: tk.Canvas, times_ms: list[int]) -> None:
        """Draw a line chart of solve times on the given canvas."""
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

        # ── Axes ──
        canvas.create_line(
            margin_l, ch - margin_b, cw - margin_r, ch - margin_b,
            fill="#555555", width=1,
        )
        canvas.create_line(
            margin_l, margin_t, margin_l, ch - margin_b,
            fill="#555555", width=1,
        )

        # ── Y-axis labels ──
        for i in range(5):
            y_val = mx - (rng * i / 4)
            y = margin_t + (plot_h * i / 4)
            canvas.create_text(
                margin_l - 8, y, text=format_time(int(y_val)),
                fill="#888888", font=("Arial", 8), anchor="e",
            )
            # grid line
            canvas.create_line(
                margin_l, y, cw - margin_r, y,
                fill="#333333", width=1, dash=(2, 4),
            )

        # ── X-axis labels ──
        label_count = min(n, 10)
        for i in range(label_count + 1):
            idx = int(i * (n - 1) / label_count) if n > 1 else 0
            x = margin_l + (plot_w * idx / (n - 1)) if n > 1 else margin_l + plot_w // 2
            canvas.create_text(
                x, ch - margin_b + 12, text=str(idx + 1),
                fill="#888888", font=("Arial", 8), anchor="n",
            )

        # ── Data line ──
        points: list[float] = []
        for i, t in enumerate(times_ms):
            x = margin_l + (plot_w * i / (n - 1)) if n > 1 else margin_l + plot_w // 2
            y = margin_t + plot_h - (plot_h * (t - mn) / rng)
            points.extend([x, y])

        if len(points) >= 4:
            canvas.create_line(points, fill="#00ff00", width=2, smooth=True)

        # ── Data dots ──
        best = mn
        worst = mx
        for i, t in enumerate(times_ms):
            x = margin_l + (plot_w * i / (n - 1)) if n > 1 else margin_l + plot_w // 2
            y = margin_t + plot_h - (plot_h * (t - mn) / rng)
            color = "#00ff00" if t == best else "#ff4444" if t == worst else "#00cfff"
            r = 4 if t in (best, worst) else 2
            canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")

        # ── Avg reference line ──
        avg_val = sum(times_ms) / n
        avg_y = margin_t + plot_h - (plot_h * (avg_val - mn) / rng)
        canvas.create_line(
            margin_l, avg_y, cw - margin_r, avg_y,
            fill="#ffff00", width=1, dash=(4, 4),
        )
        canvas.create_text(
            cw - margin_r + 4, avg_y, text="avg",
            fill="#ffff00", font=("Arial", 8), anchor="w",
        )

    # ── View times window ───────────────────────────────────────────

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

        # Title row with export button
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

        # ── Graph ──
        graph_frame = ctk.CTkFrame(self._times_window, fg_color="#0a0a0a", height=180)
        graph_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))
        graph_frame.grid_propagate(False)

        graph_canvas = tk.Canvas(
            graph_frame, bg="#0a0a0a", highlightthickness=0, height=180,
        )
        graph_canvas.pack(fill="both", expand=True)

        times_ms = [e["time"] for e in self.times]
        # Draw after a short delay to let canvas compute geometry
        self._times_window.after(
            50,
            lambda: self._draw_times_graph(graph_canvas, times_ms),
        )
        # Redraw on resize
        graph_canvas.bind(
            "<Configure>",
            lambda _e: self._draw_times_graph(graph_canvas, times_ms),
        )

        # ── Scrollable content ──
        scroll_container = ctk.CTkScrollableFrame(self._times_window, fg_color="transparent")
        scroll_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        scroll_container.grid_columnconfigure(0, weight=1)

        # ── Statistics ──
        s = self._stats()
        stats_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        stats_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkLabel(
            stats_frame, text=f"Total Solves: {s['count']}",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, sticky="w", pady=2)

        if s["count"] > 0:
            ctk.CTkLabel(
                stats_frame, text=f"Best:   {format_time(s['best'])}",
                font=ctk.CTkFont(size=13), text_color="#00ff00",
            ).grid(row=1, column=0, sticky="w", pady=1)
            ctk.CTkLabel(
                stats_frame, text=f"Worst:  {format_time(s['worst'])}",
                font=ctk.CTkFont(size=13), text_color="#ff4444",
            ).grid(row=2, column=0, sticky="w", pady=1)
            ctk.CTkLabel(
                stats_frame, text=f"Average: {format_time(int(s['average']))}",
                font=ctk.CTkFont(size=13), text_color="#ffff00",
            ).grid(row=3, column=0, sticky="w", pady=1)

            # ── Sliding averages ──
            row_offset = 4
            for label, key in [("Ao5", "ao5"), ("Ao12", "ao12"), ("Ao100", "ao100")]:
                val = s.get(key)
                if val is not None:
                    ctk.CTkLabel(
                        stats_frame, text=f"{label}: {format_time(val)}",
                        font=ctk.CTkFont(size=13), text_color="#00cfff",
                    ).grid(row=row_offset, column=0, sticky="w", pady=1)
                    row_offset += 1

        ctk.CTkLabel(
            stats_frame, text="─" * 50,
            font=ctk.CTkFont(size=11), text_color="#555555",
        ).grid(row=10, column=0, sticky="w", pady=4)

        # ── Solve entries ──
        ctk.CTkLabel(
            scroll_container, text="All Solves:",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=1, column=0, sticky="w", pady=(0, 4))

        best = s.get("best")
        worst = s.get("worst")

        for idx, entry in enumerate(self.times):
            t = entry["time"]
            colour = "#00ff00" if t == best else "#ff4444" if t == worst else \
                     "#8B4513" if t >= 40_000 else "#ffff7c"

            row = ctk.CTkFrame(scroll_container, fg_color="#1e1e1e")
            row.grid(row=idx + 2, column=0, sticky="ew", pady=2)
            row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                row, text=f"{idx + 1}. {format_time(t)}  ·  {entry['date']}",
                font=ctk.CTkFont(size=12), text_color=colour, anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=8, pady=4)

            scr = entry.get("scramble", "")
            if scr:
                ctk.CTkLabel(
                    row, text=scr,
                    font=ctk.CTkFont(size=9, family="Courier"),
                    text_color="#666666", anchor="w",
                ).grid(row=1, column=0, sticky="w", padx=8, pady=(0, 4))

            ctk.CTkButton(
                row, text="✕",
                command=lambda i=idx: self._delete_solve(i),
                width=30, height=24, fg_color="#cc0000", hover_color="#990000",
                font=ctk.CTkFont(size=12),
            ).grid(row=0, column=1, rowspan=2, padx=6, sticky="e")

    # ── CSV Export ──────────────────────────────────────────────────

    def _export_csv(self) -> None:
        """Export all solve times to a CSV file."""
        if not self.times:
            parent_win: Any = self._times_window
            mb.showinfo("Export", "No times to export!", parent=parent_win)
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
            mb.showinfo(
                "Export Successful",
                f"Exported {len(self.times)} solves to:\n{filename}",
                parent=self._times_window,  # type: ignore[arg-type]
            )
        except (OSError, PermissionError) as e:
            mb.showerror("Export Failed", str(e), parent=self._times_window)  # type: ignore[arg-type]

    # ── Delete & Clear ──────────────────────────────────────────────

    def _delete_solve(self, index: int) -> None:
        if index < 0 or index >= len(self.times):
            return
        parent_win: ctk.CTkToplevel | ctk.CTk = (
            self._times_window if self._times_window else self.root
        )
        if mb.askyesno(
            "Delete Solve",
            f"Delete solve: {format_time(self.times[index]['time'])}?",
            parent=parent_win,
        ):
            del self.times[index]
            save_times(self.times)
            if self._times_window and self._times_window.winfo_exists():
                self._times_window.destroy()
                self._times_window = None
            self._view_times()

    def _clear_times(self) -> None:
        if mb.askyesno("Clear Times", "Are you sure you want to clear all times?"):
            self.times.clear()
            save_times(self.times)
            self.timer.reset()
            self._status_label.configure(
                text="Press ANY KEY to start inspection", text_color="#ffff00"
            )
            if self._times_window and self._times_window.winfo_exists():
                self._times_window.destroy()
                self._times_window = None
            mb.showinfo("Success", "All times cleared!")

    # ── Dialog after solve ──────────────────────────────────────────

    def _show_welcome_if_first_run(self) -> None:
        """Show a welcome dialog on first launch to explain the timer flow."""
        welcome_flag = get_data_path(".welcome_shown")
        if welcome_flag.exists():
            return

        mb.showinfo(
            "Welcome to 3x3 Speed Cube Timer!",
            "Here's how to get started:\n\n"
            "1. Press ANY KEY to start the 15-second inspection (look at the scramble)\n"
            "2. After inspection, you have 3 seconds of grace time\n"
            "3. Press ANY KEY again to start solving\n"
            "4. Press ANY KEY to stop the timer\n"
            "5. View your times with the 'View Times' button\n\n"
            "Keyboard shortcuts:\n"
            "  SPACE / ENTER  — Start/Stop\n"
            "  ESC            — Cancel / Quit\n\n"
            "Happy cubing! 🧩",
            parent=self.root,
        )
        # Mark welcome as shown
        welcome_flag.parent.mkdir(parents=True, exist_ok=True)
        welcome_flag.touch()

    def _ask_show_times(self, elapsed: int) -> None:
        if mb.askyesno(
            "Solve Complete!",
            f"Solve Time: {format_time(elapsed)}\n\nView your times?",
        ):
            self._view_times()


def main() -> None:
    """Entry point for the application."""
    root = ctk.CTk()
    root.minsize(600, 500)
    root.geometry("700x580")
    Application(root)
    root.mainloop()
