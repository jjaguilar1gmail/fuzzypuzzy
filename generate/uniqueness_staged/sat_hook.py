"""Optional SAT/CP solver hook interface."""

from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.puzzle import Puzzle


class SolverInterface(ABC):
    """Abstract interface for external SAT/CP solvers.
    
    Implementers provide one-solution + blocking-clause verification.
    """
    
    @abstractmethod
    def find_solution(self, puzzle: 'Puzzle', timeout_ms: int) -> Optional['Puzzle']:
        """Find one valid solution to the puzzle.
        
        Args:
            puzzle: Puzzle to solve
            timeout_ms: Time budget for this query
            
        Returns:
            Completed puzzle if found, None if no solution or timeout
        """
        pass
    
    @abstractmethod
    def find_second_solution(
        self, 
        puzzle: 'Puzzle', 
        first_solution: 'Puzzle',
        timeout_ms: int
    ) -> Optional['Puzzle']:
        """Find a second solution different from the first.
        
        Args:
            puzzle: Original puzzle
            first_solution: First solution to exclude
            timeout_ms: Time budget for this query
            
        Returns:
            Second solution if found, None if unique or timeout
        """
        pass


# Global registry for optional SAT solver
_SAT_SOLVER: Optional[SolverInterface] = None


def register_sat_solver(solver: SolverInterface) -> None:
    """Register an external SAT/CP solver.
    
    Args:
        solver: Solver implementing SolverInterface
    """
    global _SAT_SOLVER
    _SAT_SOLVER = solver


def get_sat_solver() -> Optional[SolverInterface]:
    """Get the registered SAT solver, if any.
    
    Returns:
        Registered solver or None
    """
    return _SAT_SOLVER


def has_sat_solver() -> bool:
    """Check if a SAT solver is registered.
    
    Returns:
        True if solver available
    """
    return _SAT_SOLVER is not None


def clear_sat_solver() -> None:
    """Clear the registered solver (mainly for testing)."""
    global _SAT_SOLVER
    _SAT_SOLVER = None
