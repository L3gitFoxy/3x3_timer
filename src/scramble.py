"""Rubik's cube state simulation and WCA-style scramble generation.

Provides a pure-data-structure representation of a 3×3 cube and
functions to apply moves and generate random scrambles.
No UI dependencies — can be used from any frontend.
"""

from __future__ import annotations

import random
from typing import Dict, List

# ── Constants ────────────────────────────────────────────────────────

MOVES: List[str] = ["U", "D", "L", "R", "F", "B"]
MODIFIERS: List[str] = ["", "'", "2"]

# Standard Western colour scheme
FACE_COLORS: Dict[str, str] = {
    "U": "#ffffff",  # white
    "D": "#ffff00",  # yellow
    "F": "#00aa00",  # green
    "B": "#0055ff",  # blue
    "L": "#ff8800",  # orange
    "R": "#ff0000",  # red
}

CubeState = Dict[str, List[str]]
"""Maps face letter → list of 9 sticker colours (reading order)."""


# ── Cube helpers ─────────────────────────────────────────────────────

def make_solved_cube() -> CubeState:
    """Return a cube with every face solid."""
    return {f: [f] * 9 for f in "UDFBLR"}


def _rotate_face_cw(cube: CubeState, face: str) -> None:
    """Rotate a single face 90° clockwise in-place."""
    s = cube[face]
    cube[face] = [s[6], s[3], s[0],
                  s[7], s[4], s[1],
                  s[8], s[5], s[2]]


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


def compute_states(scramble: str) -> List[CubeState]:
    """Return a list of cube states from solved → after each move.

    Useful for stepping through a scramble visually.
    """
    states: List[CubeState] = [make_solved_cube()]
    for m in scramble.split():
        nxt = {f: list(states[-1][f]) for f in "UDFBLR"}
        apply_move(nxt, m)
        states.append(nxt)
    return states


# ── Opposing face pairs (WCA regulation 4b3) ─────────────────────────

OPPOSITES: Dict[str, str] = {"U": "D", "D": "U", "R": "L", "L": "R", "F": "B", "B": "F"}

# ── Scramble generation ──────────────────────────────────────────────

def generate_scramble(length: int = 20) -> str:
    """Generate a random WCA-style scramble of *length* moves.

    - No move appears twice consecutively on the same face.
    - No move on the *opposite* face after a move on its parallel face
      (WCA regulation 4b3 — e.g. R is never followed by L, U never by D).
    """
    scramble: List[str] = []
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
