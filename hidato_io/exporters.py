"""I/O adapters: Exporters

Contains the Exporters class for exporting puzzles to text/SVG/PDF formats.
"""

def ascii_render(puzzle, highlight_move=None):
    """Returns an ASCII string representation of the puzzle grid.
    
    Args:
        puzzle: The puzzle to render
        highlight_move: Optional tuple (row, col) to highlight a cell with *
    """
    lines = []
    for row_idx, row in enumerate(puzzle.grid.cells):
        row_str = ""
        for col_idx, cell in enumerate(row):
            is_highlighted = highlight_move and highlight_move == (row_idx, col_idx)
            
            if cell.blocked:
                row_str += " X "
            elif cell.value is not None:
                if cell.given:
                    if is_highlighted:
                        row_str += f"*{cell.value:2}*"  # Highlight given with *
                    else:
                        row_str += f"[{cell.value:2}]"
                else:
                    if is_highlighted:
                        row_str += f"*{cell.value:2}*"  # Highlight user move with *
                    else:
                        row_str += f" {cell.value:2} "
            else:
                if is_highlighted:
                    row_str += " *. "  # Highlight empty cell
                else:
                    row_str += " . "
        lines.append(row_str)
    return "\n".join(lines)

def ascii_print(puzzle, highlight_move=None):
    """Prints an ASCII representation of the puzzle to the console.
    
    Args:
        puzzle: The puzzle to print
        highlight_move: Optional tuple (row, col) to highlight a cell with *
    """
    print(ascii_render(puzzle, highlight_move))

class Exporters:
    """A placeholder Exporters class for export adapters."""
    pass
