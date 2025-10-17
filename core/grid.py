"""Core domain model: Grid

Contains the Grid class representing the puzzle grid.
"""
from core.position import Position
from core.cell import Cell
from core.adjacency import Adjacency

class Grid:
    """A grid is a basic board container. Fields:
    rows: int, cols: int, cells: List[List[Cell]], adjacency: Adjacency"""
    def __init__(self, rows: int, cols: int, allow_diagonal: bool = True):
        self.rows = rows
        self.cols = cols
        self.cells = [[Cell(Position(r, c)) for c in range(cols)] for r in range(rows)]
        self.adjacency = Adjacency(allow_diagonal=allow_diagonal)
    def get_cell(self, pos: Position) -> Cell:
        """Returns the cell at the given position."""
        if 0 <= pos.row < self.rows and 0 <= pos.col < self.cols:
            return self.cells[pos.row][pos.col]
        else:
            raise IndexError("Position out of grid bounds.")
    def set_cell_value(self, pos: Position, value: int):
        """Sets the value of the cell at the given position."""
        cell = self.get_cell(pos)
        if not cell.given and not cell.blocked:
            cell.value = value
        else:
            raise ValueError("Cannot set value of a blocked cell.")
    def clear_cell(self, pos: Position):
        """Clears the value of the cell at the given position, but leaves given alone."""
        cell = self.get_cell(pos)
        if not cell.given and not cell.blocked:
            cell.value = None
        else:
            raise ValueError("Cannot clear a given cell.")
    def iter_cells(self):
        """Yields every Cell in the grid, 
        in row-major order (top to bottom, left to right)."""
        for row in self.cells:
            for cell in row:
                yield cell
    def empty_positions(self):
        """Returns a list (or iterator) of all positions that have no value assigned (i.e., not given, not filled)."""
        for cell in self.iter_cells():
            if cell.is_empty():
                yield cell.pos
    def filled_positions(self):
        """Returns a list (or iterator) of all positions that currently have a value (either givens or solver/generator placements)."""
        for cell in self.iter_cells():
            if cell.is_filled():
                yield cell.pos
    def print_grid(self):
        """Prints a simple text representation of the grid to the console."""
        for row in self.cells:
            row_str = ""
            for cell in row:
                if cell.blocked:
                    row_str += " X "
                elif cell.value is not None:
                    row_str += f" {cell.value} "
                else:
                    row_str += " . "
            print(row_str)