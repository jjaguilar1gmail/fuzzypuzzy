import copy

from generate.generator import Generator
from generate.uniqueness import count_solutions
from core.grid import Grid
from core.constraints import Constraints
from core.puzzle import Puzzle
from core.position import Position


SEED = 12345


def build_puzzle_from_generated(gen):
    grid = Grid(gen.size, gen.size, allow_diagonal=gen.allow_diagonal)
    for r, c in gen.blocked_cells:
        grid.get_cell(Position(r, c)).blocked = True
    constraints = Constraints(
        1,
        gen.size * gen.size,
        allow_diagonal=gen.allow_diagonal,
        must_be_connected=True,
    )
    puzzle = Puzzle(grid, constraints)
    for r, c, v in gen.givens:
        cell = grid.get_cell(Position(r, c))
        cell.value = v
        cell.given = True
    return puzzle


def generate_base():
    gen = Generator.generate_puzzle(size=5, difficulty="easy", seed=SEED)
    return build_puzzle_from_generated(gen)


def test_count_solutions_unique_puzzle():
    puzzle = generate_base()
    result = count_solutions(puzzle, cap=2, node_cap=5000, timeout_ms=10000)
    assert result.solutions_found == 1
    assert result.nodes > 0
    assert result.depth > 0


def test_count_solutions_ambiguous_after_removal():
    puzzle = generate_base()
    ambig = copy.deepcopy(puzzle)
    for cell in ambig.grid.iter_cells():
        if cell.given and cell.value not in (
            ambig.constraints.min_value,
            ambig.constraints.max_value,
        ):
            cell.given = False
            cell.value = None
            break
    result = count_solutions(ambig, cap=2, node_cap=5000, timeout_ms=10000)
    assert result.solutions_found >= 2


def test_count_solutions_unsolvable_after_duplicate():
    puzzle = generate_base()
    unsat = copy.deepcopy(puzzle)
    givens = [cell for cell in unsat.grid.iter_cells() if cell.given]
    # Corrupt the puzzle by duplicating a value
    val = givens[0].value
    target = givens[1]
    target.value = val
    result = count_solutions(unsat, cap=2, node_cap=5000, timeout_ms=10000)
    assert result.solutions_found == 0
