"""Tkinter-based isometric 3D cube visualizer for scramble inspection.

Opens a popup window showing an isometric projection of the 3×3 cube,
allowing the user to step through each move of a scramble with arrow keys.
"""

from __future__ import annotations

import tkinter as tk

from scramble import FACE_COLORS, CubeState, compute_states


def open_visualizer(parent: tk.Tk | tk.Toplevel, scramble_str: str) -> None:
    """Open a popup window to step through *scramble_str* move by move."""
    moves = scramble_str.split()
    if not moves:
        return

    win = tk.Toplevel(parent)
    win.title("Scramble Visualizer")
    win.configure(bg="#1a1a1a")
    win.geometry("600x540")

    # ── Labels ──────────────────────────────────────────────────────
    move_label = tk.Label(
        win, text="", font=("Arial", 16, "bold"),
        bg="#1a1a1a", fg="#ff9900",
    )
    move_label.pack(pady=(12, 2))

    seq_label = tk.Label(
        win, text="", font=("Courier", 11),
        bg="#1a1a1a", fg="#555555", wraplength=560, justify="center",
    )
    seq_label.pack(pady=(0, 4))

    nav_label = tk.Label(
        win, text="← →  arrow keys to step through moves",
        font=("Arial", 10), bg="#1a1a1a", fg="#666666",
    )
    nav_label.pack(pady=(0, 6))

    # ── Canvas ──────────────────────────────────────────────────────
    canvas = tk.Canvas(win, bg="#1a1a1a", highlightthickness=0, width=600, height=340)
    canvas.pack()

    # ── Pre-compute all cube states ─────────────────────────────────
    cube_states: list[CubeState] = compute_states(scramble_str)

    step_idx: list[int] = [0]

    # ── Drawing helpers ─────────────────────────────────────────────
    def shade(color: str, factor: float) -> str:
        r = int(int(color[1:3], 16) * factor)
        g = int(int(color[3:5], 16) * factor)
        b = int(int(color[5:7], 16) * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    def draw_cube(cube: CubeState) -> None:
        canvas.delete("all")

        S = 36
        CX, CY = 300, 220

        def add(p1: tuple[float, float], p2: tuple[float, float]) -> tuple[float, float]:
            return (p1[0] + p2[0], p1[1] + p2[1])

        def scale(v: tuple[float, float], f: float) -> tuple[float, float]:
            return (v[0] * f, v[1] * f)

        # Isometric basis vectors
        vec_UR = (S, -S / 2)   # Up-Right
        vec_UL = (-S, -S / 2)  # Up-Left
        vec_DR = (S, S / 2)    # Down-Right
        vec_DL = (-S, S / 2)   # Down-Left
        vec_D = (0, S)         # Down

        def draw_face(
            face_name: str,
            origin: tuple[float, float],
            vec_c: tuple[float, float],
            vec_r: tuple[float, float],
            darken: float,
        ) -> None:
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

                    canvas.create_polygon(
                        [p0, p1, p2, p3],
                        fill=color, outline="#111", width=2,
                    )

        # Right face (drawn first = behind)
        draw_face("R", (CX, CY), vec_UR, vec_D, 0.75)
        # Front face (left side)
        draw_face("F", add((CX, CY), scale(vec_UL, 3)), vec_DR, vec_D, 0.88)
        # Top face
        draw_face("U", (CX, CY - 3 * S), vec_DR, vec_DL, 1.0)

    # ── Refresh display ─────────────────────────────────────────────
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

    # ── Keyboard navigation ─────────────────────────────────────────
    def on_key(event: tk.Event) -> None:
        if event.keysym == "Right" and step_idx[0] < len(moves):
            step_idx[0] += 1
            refresh()
        elif event.keysym == "Left" and step_idx[0] > 0:
            step_idx[0] -= 1
            refresh()

    win.bind("<Key>", on_key)
    refresh()
