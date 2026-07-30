"""Tests for the scramble generator and cube simulation."""

from __future__ import annotations

import re

import pytest

from scramble import (
    FACE_COLORS,
    MOVES,
    OPPOSITES,
    CubeState,
    apply_move,
    apply_scramble,
    compute_states,
    generate_scramble,
    make_solved_cube,
)


@pytest.fixture
def solved_cube() -> CubeState:
    """Provide a fresh solved cube for each test."""
    return make_solved_cube()


class TestMakeSolvedCube:
    """A solved cube should have uniform faces."""

    def test_all_faces_present(self, solved_cube: CubeState) -> None:
        assert set(solved_cube.keys()) == {"U", "D", "F", "B", "L", "R"}

    def test_each_face_has_9_stickers(self, solved_cube: CubeState) -> None:
        for face in "UDFBLR":
            assert len(solved_cube[face]) == 9

    def test_each_face_is_solid(self, solved_cube: CubeState) -> None:
        for face in "UDFBLR":
            assert all(s == face for s in solved_cube[face])


class TestApplyMove:
    """Applying a single move should change the cube state."""

    def test_r_move_changes_state(self, solved_cube: CubeState) -> None:
        original = {f: list(solved_cube[f]) for f in "UDFBLR"}
        apply_move(solved_cube, "R")
        # R move should change U, F, D, B faces
        assert solved_cube["U"] != original["U"]
        assert solved_cube["F"] != original["F"]
        assert solved_cube["D"] != original["D"]
        assert solved_cube["B"] != original["B"]

    def test_r2_returns_to_original_after_4(self, solved_cube: CubeState) -> None:
        original = {f: list(solved_cube[f]) for f in "UDFBLR"}
        for _ in range(4):
            apply_move(solved_cube, "R2")
        assert solved_cube == original

    def test_r_prime_undoes_r(self, solved_cube: CubeState) -> None:
        original = {f: list(solved_cube[f]) for f in "UDFBLR"}
        apply_move(solved_cube, "R")
        apply_move(solved_cube, "R'")
        assert solved_cube == original

    def test_all_moves_are_valid(self, solved_cube: CubeState) -> None:
        """Each base move should not crash and should change state."""
        for move in MOVES:
            cube = make_solved_cube()
            apply_move(cube, move)
            assert cube != make_solved_cube()

    def test_all_modifiers_work(self, solved_cube: CubeState) -> None:
        """Test each move with each modifier."""
        for move in MOVES:
            for mod in ["", "'", "2"]:
                cube = make_solved_cube()
                apply_move(cube, move + mod)  # Should not crash


class TestApplyScramble:
    """Applying a full scramble string."""

    def test_scramble_changes_state(self, solved_cube: CubeState) -> None:
        scramble = "R U R' U'"
        apply_scramble(solved_cube, scramble)
        assert solved_cube != make_solved_cube()

    def test_scramble_is_reversible(self, solved_cube: CubeState) -> None:
        scramble = "R U R' U'"
        apply_scramble(solved_cube, scramble)
        # Reverse the scramble
        reverse_moves = scramble.split()[::-1]
        reverse = " ".join(
            m + "'" if "'" not in m and "2" not in m else
            m.replace("'", "") if "'" in m else
            m
            for m in reverse_moves
        )
        apply_scramble(solved_cube, reverse)
        assert solved_cube == make_solved_cube()


class TestComputeStates:
    """Step-by-step state computation."""

    def test_returns_list(self) -> None:
        states = compute_states("R U R'")
        assert isinstance(states, list)

    def test_first_state_is_solved(self) -> None:
        states = compute_states("R U R'")
        assert states[0] == make_solved_cube()

    def test_length_is_moves_plus_one(self) -> None:
        moves = "R U R' U' R' F R2 U' R' U'"
        states = compute_states(moves)
        assert len(states) == len(moves.split()) + 1

    def test_each_state_differs(self) -> None:
        states = compute_states("R U R' U'")
        for i in range(1, len(states)):
            assert states[i] != states[i - 1]


class TestGenerateScramble:
    """Scramble generation should follow WCA rules."""

    def test_default_length(self) -> None:
        scramble = generate_scramble()
        assert len(scramble.split()) == 20

    def test_custom_length(self) -> None:
        scramble = generate_scramble(length=10)
        assert len(scramble.split()) == 10

    def test_no_consecutive_same_face(self) -> None:
        for _ in range(100):
            scramble = generate_scramble()
            moves = scramble.split()
            for i in range(1, len(moves)):
                assert moves[i][0] != moves[i - 1][0], (
                    f"Consecutive same face: {moves[i-1]} {moves[i]}"
                )

    def test_no_parallel_face_sequences(self) -> None:
        """WCA regulation 4b3: no move on opposite face after parallel face."""
        for _ in range(100):
            scramble = generate_scramble()
            moves = scramble.split()
            for i in range(1, len(moves)):
                prev_face = moves[i - 1][0]
                curr_face = moves[i][0]
                assert curr_face != OPPOSITES[prev_face], (
                    f"Parallel face sequence: {moves[i-1]} {moves[i]} "
                    f"({prev_face} → {curr_face})"
                )

    def test_only_valid_moves(self) -> None:
        for _ in range(50):
            scramble = generate_scramble()
            for move in scramble.split():
                assert move[0] in MOVES
                assert move[1:] in ("", "'", "2")

    def test_scramble_is_deterministic_length(self) -> None:
        """Scrambles of same length should all be that length."""
        for length in [5, 10, 15, 20, 25]:
            scramble = generate_scramble(length=length)
            assert len(scramble.split()) == length


class TestFaceColors:
    """Face color definitions."""

    def test_all_faces_have_colors(self) -> None:
        for face in "UDFBLR":
            assert face in FACE_COLORS

    def test_colors_are_valid_hex(self) -> None:
        for color in FACE_COLORS.values():
            assert re.match(r"^#[0-9a-f]{6}$", color), f"Invalid color: {color}"
