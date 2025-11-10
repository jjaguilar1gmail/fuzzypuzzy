from core.grid import Grid
from core.constraints import Constraints 
from core.position import Position
"""Core domain model: Puzzle

Contains the Puzzle class representing a puzzle instance.
"""

class Puzzle:
    """So the Puzzle class is a container that represents one entire Hidato instance — 
    the grid layout, the rules, and maybe a few convenience methods.
    .grid — your Grid instance
    .constraints — your Constraints instance
    .difficulty - setting the difficulty level of the puzzle
    .givens() — a helper that lists which positions have fixed numbers
    .to_dict() — an exporter that turns it into a JSON-safe dictionary
    .from_dict() — the inverse, builds a puzzle back from JSON
    .occupied_positions() / empty_positions() -> Iterable[Position]- Forwarders to grid, often filtering out blocked cells.
    .value_positions() -> dict[int, Position] - Reverse index of placed numbers (useful for solvers).
    .is_complete() -> bool - True if all playable cells have valid values in min_value..max_value with no duplicates.
    .is_valid_partial() -> bool - Lightweight sanity check: values in range, no duplicate values, givens untouched.
    .verify_path_contiguity() -> bool - If must_be_connected, confirm that for each k, k and k+1 are neighbors (for all placed consecutive pairs).
    For partial boards, you can check only the placed consecutive pairs to prune invalid states.
    .clone(replacements: dict[Position, int] | None = None) -> Puzzle - Returns a shallow copy with optional value updates (never mutates givens).
    .clear_non_givens() -> None - Reset the board to its initial state.
    .summary() -> str - Human-friendly one-liner (rows×cols, blocked count, clues, rules)."""
    def __init__(self, grid: Grid, constraints: Constraints, difficulty="medium"):
        self.grid = grid  # Grid instance
        self.constraints = constraints  # Constraints instance
        self.difficulty = difficulty  # Difficulty level of the puzzle
    def givens(self):
        """Returns a list of positions that have given values."""
        givens_list = []
        for row in self.grid.cells:
            for cell in row:
                if cell.given:
                    givens_list.append(cell.pos)
        return givens_list
    def to_dict(self):
        """Exports the puzzle to a JSON-safe dictionary."""
        puzzle_dict = {
            "grid": {
                "rows": self.grid.rows,
                "cols": self.grid.cols,
                "cells": [
                    [
                        {
                            "row": cell.pos.row,
                            "col": cell.pos.col,
                            "value": cell.value,
                            "blocked": cell.blocked,
                            "given": cell.given,
                        }
                        for cell in row
                    ]
                    for row in self.grid.cells
                ],
            },
            "constraints": {
                "min_value": self.constraints.min_value,
                "max_value": self.constraints.max_value,
                "allow_diagonal": self.constraints.allow_diagonal,
                "must_be_connected": self.constraints.must_be_connected,
            },
            "difficulty": self.difficulty,
        }
        return puzzle_dict
    def from_dict(self, puzzle_dict):
        """Builds a puzzle back from a JSON-safe dictionary."""
        grid_info = puzzle_dict["grid"]
        constraints_info = puzzle_dict["constraints"]
        self.grid = Grid(grid_info["rows"], grid_info["cols"], constraints_info["allow_diagonal"])
        for r, row in enumerate(grid_info["cells"]):
            for c, cell_info in enumerate(row):
                cell = self.grid.get_cell(Position(r, c))
                cell.value = cell_info["value"]
                cell.blocked = cell_info["blocked"]
                cell.given = cell_info["given"]
        self.constraints = Constraints(
            min_value=constraints_info["min_value"],
            max_value=constraints_info["max_value"],
            allow_diagonal=constraints_info["allow_diagonal"],
            must_be_connected=constraints_info["must_be_connected"],
        )
        self.difficulty = puzzle_dict.get("difficulty", "medium")
    def occupied_positions(self):
        """Returns an iterator of all positions that currently have a value (either givens or solver/generator placements)."""
        return self.grid.filled_positions()
    def empty_positions(self):
        """Returns an iterator of all positions that have no value assigned (i.e., not given, not filled)."""
        return self.grid.empty_positions()
    def value_positions(self):
        """Returns a dictionary mapping placed numbers to their positions."""
        value_pos_dict = {}
        for cell in self.grid.iter_cells():
            if cell.value is not None and not cell.blocked:
                value_pos_dict[cell.value] = cell.pos
        return value_pos_dict
    def is_complete(self):
        """Returns True if all playable cells have valid values in min_value..max_value with no duplicates."""
        placed_values = set()
        for cell in self.grid.iter_cells():
            if not cell.blocked:
                if cell.value is None:
                    return False
                if not self.constraints.valid_value(cell.value):
                    return False
                if cell.value in placed_values:
                    return False
                placed_values.add(cell.value)
        return True
    def is_valid_partial(self):
        """Lightweight sanity check: values in range, no duplicate values, givens untouched."""
        placed_values = set()
        for cell in self.grid.iter_cells():
            if cell.value is not None and not cell.blocked:
                if not self.constraints.valid_value(cell.value):
                    return False
                if cell.value in placed_values:
                    return False
                placed_values.add(cell.value)
        return True
    def verify_path_contiguity(self):
        """If must_be_connected, confirm that for each k, k and k+1 are neighbors (for all placed consecutive pairs).
        For partial boards, you can check only the placed consecutive pairs to prune invalid states."""
        if not self.constraints.must_be_connected:
            return True
        value_pos = self.value_positions()
        for k in range(self.constraints.min_value, self.constraints.max_value):
            if k in value_pos and (k + 1) in value_pos:
                pos_a = value_pos[k]
                pos_b = value_pos[k + 1]
                if not self.constraints.valid_transition(pos_a, pos_b, self.grid.rows, self.grid.cols):
                    return False
        return True
    def clone(self, replacements: dict[Position, int] | None = None) -> "Puzzle":
        """Returns a shallow copy with optional value updates (never mutates givens)."""
        new_grid = Grid(self.grid.rows, self.grid.cols, allow_diagonal=self.constraints.allow_diagonal)
        for cell in self.grid.iter_cells():
            new_cell = new_grid.get_cell(cell.pos)
            new_cell.value = cell.value
            new_cell.blocked = cell.blocked
            new_cell.given = cell.given
        if replacements:
            for pos, value in replacements.items():
                cell = new_grid.get_cell(pos)
                if not cell.given and not cell.blocked:
                    cell.value = value
        new_puzzle = Puzzle(new_grid, self.constraints, self.difficulty)
        return new_puzzle
    def clear_non_givens(self) -> None:
        """Reset the board to its initial state."""
        for cell in self.grid.iter_cells():
            if not cell.given and not cell.blocked:
                cell.value = None
    def summary(self) -> str:
        """Human-friendly one-liner (rows×cols, blocked count, clues, rules)."""
        blocked_count = sum(1 for cell in self.grid.iter_cells() if cell.blocked)
        clue_count = sum(1 for cell in self.grid.iter_cells() if cell.given)
        rules = []
        if self.constraints.allow_diagonal:
            rules.append("8-neighbors")
        else:
            rules.append("4-neighbors")
        if self.constraints.must_be_connected:
            rules.append("must be connected")
        summary_str = (f"Puzzle: {self.grid.rows}x{self.grid.cols}, "
                       f"Blocked: {blocked_count}, "
                       f"Givens: {clue_count}, "
                       f"Rules: {', '.join(rules)}")
        return summary_str

