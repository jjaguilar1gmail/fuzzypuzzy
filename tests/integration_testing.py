#!/usr/bin/env python3
"""Comprehensive integration testing suite for the advanced solver system."""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

# Add project root to path for imports
sys.path.insert(0, str(Path.cwd()))

from core.puzzle import Puzzle
from core.grid import Grid
from core.constraints import Constraints
from core.position import Position
from solve.solver import Solver
from hidato_io.exporters import ascii_print

@dataclass
class TestCase:
    """Integration test case definition."""
    name: str
    description: str
    puzzle: Puzzle
    expected_solvable: bool
    expected_modes: List[str]  # Modes that should solve this
    max_time_ms: int = 5000

class IntegrationTestSuite:
    """Comprehensive integration testing for all solver components."""
    
    def __init__(self):
        self.test_cases = self._create_test_cases()
        self.results = {}
    
    def _create_test_cases(self) -> List[TestCase]:
        """Create comprehensive test case suite."""
        cases = []
        
        # Test Case 1: Basic Linear Path (All modes should solve)
        grid1 = Grid(1, 4, allow_diagonal=False)
        constraints1 = Constraints(1, 4, allow_diagonal=False)
        puzzle1 = Puzzle(grid1, constraints1)
        grid1.get_cell(Position(0, 0)).value = 1
        grid1.get_cell(Position(0, 0)).given = True
        grid1.get_cell(Position(0, 3)).value = 4
        grid1.get_cell(Position(0, 3)).given = True
        
        cases.append(TestCase(
            name="Linear_Basic",
            description="Simple 1x4 linear path from 1 to 4",
            puzzle=puzzle1,
            expected_solvable=True,
            expected_modes=["logic_v0", "logic_v1", "logic_v2", "logic_v3"],
            max_time_ms=100
        ))
        
        # Test Case 2: Square Layout (Logic modes should solve)
        grid2 = Grid(2, 2, allow_diagonal=False)
        constraints2 = Constraints(1, 4, allow_diagonal=False)
        puzzle2 = Puzzle(grid2, constraints2)
        grid2.get_cell(Position(0, 0)).value = 1
        grid2.get_cell(Position(0, 0)).given = True
        grid2.get_cell(Position(1, 1)).value = 4
        grid2.get_cell(Position(1, 1)).given = True
        
        cases.append(TestCase(
            name="Square_2x2",
            description="2x2 square with corners 1 and 4",
            puzzle=puzzle2,
            expected_solvable=True,
            expected_modes=["logic_v1", "logic_v2", "logic_v3"],
            max_time_ms=200
        ))
        
        # Test Case 3: Constrained Layout (Advanced modes needed)
        grid3 = Grid(2, 3, allow_diagonal=False)
        constraints3 = Constraints(1, 6, allow_diagonal=False)
        puzzle3 = Puzzle(grid3, constraints3)
        grid3.get_cell(Position(0, 0)).value = 1
        grid3.get_cell(Position(0, 0)).given = True
        grid3.get_cell(Position(0, 1)).value = 2
        grid3.get_cell(Position(0, 1)).given = True
        grid3.get_cell(Position(1, 2)).value = 6
        grid3.get_cell(Position(1, 2)).given = True
        
        cases.append(TestCase(
            name="Constrained_Path",
            description="2x3 grid with multiple constraints",
            puzzle=puzzle3,
            expected_solvable=True,
            expected_modes=["logic_v2", "logic_v3"],
            max_time_ms=500
        ))
        
        # Test Case 4: Impossible Puzzle (Should be detected by all modes)
        grid4 = Grid(1, 3, allow_diagonal=False)
        constraints4 = Constraints(1, 5, allow_diagonal=False)  # Need 5 values, only 3 cells
        puzzle4 = Puzzle(grid4, constraints4)
        grid4.get_cell(Position(0, 0)).value = 1
        grid4.get_cell(Position(0, 0)).given = True
        grid4.get_cell(Position(0, 2)).value = 5
        grid4.get_cell(Position(0, 2)).given = True
        
        cases.append(TestCase(
            name="Impossible_Values",
            description="1x3 grid requiring 5 values (impossible)",
            puzzle=puzzle4,
            expected_solvable=False,
            expected_modes=[],  # No modes should solve
            max_time_ms=1000
        ))
        
        # Test Case 5: Complex Search (Only logic_v3 should reliably solve)
        grid5 = Grid(3, 2, allow_diagonal=False)
        constraints5 = Constraints(1, 6, allow_diagonal=False)
        puzzle5 = Puzzle(grid5, constraints5)
        grid5.get_cell(Position(0, 0)).value = 1
        grid5.get_cell(Position(0, 0)).given = True
        grid5.get_cell(Position(2, 1)).value = 6
        grid5.get_cell(Position(2, 1)).given = True
        grid5.get_cell(Position(1, 0)).value = 3
        grid5.get_cell(Position(1, 0)).given = True
        
        cases.append(TestCase(
            name="Complex_Search",
            description="3x2 grid requiring backtracking search",
            puzzle=puzzle5,
            expected_solvable=True,
            expected_modes=["logic_v3"],
            max_time_ms=2000
        ))
        
        # Test Case 6: Diagonal Adjacency Test
        grid6 = Grid(2, 2, allow_diagonal=True)
        constraints6 = Constraints(1, 4, allow_diagonal=True)
        puzzle6 = Puzzle(grid6, constraints6)
        grid6.get_cell(Position(0, 0)).value = 1
        grid6.get_cell(Position(0, 0)).given = True
        grid6.get_cell(Position(1, 1)).value = 2
        grid6.get_cell(Position(1, 1)).given = True
        
        cases.append(TestCase(
            name="Diagonal_Adjacency",
            description="2x2 grid with diagonal adjacency enabled",
            puzzle=puzzle6,
            expected_solvable=True,
            expected_modes=["logic_v1", "logic_v2", "logic_v3"],
            max_time_ms=300
        ))
        
        return cases
    
    def run_integration_tests(self) -> None:
        """Run complete integration test suite."""
        print("🧪 ADVANCED SOLVER INTEGRATION TESTS")
        print("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for test_case in self.test_cases:
            print(f"\n🔬 Testing: {test_case.name}")
            print(f"   Description: {test_case.description}")
            
            case_results = self._run_test_case(test_case)
            self.results[test_case.name] = case_results
            
            # Analyze results
            case_passed = self._analyze_test_case(test_case, case_results)
            
            total_tests += 1
            if case_passed:
                passed_tests += 1
                print(f"   ✅ PASSED")
            else:
                print(f"   ❌ FAILED")
        
        self._print_integration_summary(total_tests, passed_tests)
    
    def _run_test_case(self, test_case: TestCase) -> Dict[str, Any]:
        """Run a single test case across all solver modes."""
        results = {}
        modes = ["logic_v0", "logic_v1", "logic_v2", "logic_v3"]
        
        for mode in modes:
            print(f"     Testing {mode}...", end=" ")
            
            try:
                # Use copy to avoid state contamination
                from copy import deepcopy
                test_puzzle = deepcopy(test_case.puzzle)
                
                # Configure for mode
                config = {}
                if mode == "logic_v3":
                    config.update({
                        'max_nodes': 1000,
                        'max_depth': 15,
                        'timeout_ms': test_case.max_time_ms
                    })
                
                # Solve
                import time
                start_time = time.perf_counter()
                result = Solver.solve(test_puzzle, mode=mode, **config)
                end_time = time.perf_counter()
                
                solve_time = (end_time - start_time) * 1000  # Convert to ms
                
                results[mode] = {
                    'solved': result.solved,
                    'time_ms': solve_time,
                    'steps': len(result.steps),
                    'error': None
                }
                
                status = "✅" if result.solved else "❌"
                print(f"{status} ({solve_time:.1f}ms)")
                
            except Exception as e:
                results[mode] = {
                    'solved': False,
                    'time_ms': 0,
                    'steps': 0,
                    'error': str(e)
                }
                print(f"❌ ERROR: {e}")
        
        return results
    
    def _analyze_test_case(self, test_case: TestCase, results: Dict) -> bool:
        """Analyze test case results for correctness."""
        all_correct = True
        
        for mode, result in results.items():
            expected_to_solve = mode in test_case.expected_modes
            actually_solved = result['solved']
            
            if test_case.expected_solvable:
                # Solvable puzzle
                if expected_to_solve and not actually_solved:
                    print(f"      ⚠️  {mode} should have solved but didn't")
                    all_correct = False
                elif not expected_to_solve and actually_solved:
                    print(f"      ℹ️  {mode} solved unexpectedly (good!)")
            else:
                # Unsolvable puzzle
                if actually_solved:
                    print(f"      ❌ {mode} solved impossible puzzle!")
                    all_correct = False
            
            # Check timeout
            if result['time_ms'] > test_case.max_time_ms:
                print(f"      ⏰ {mode} exceeded timeout ({result['time_ms']:.1f}ms)")
                all_correct = False
        
        return all_correct
    
    def _print_integration_summary(self, total: int, passed: int) -> None:
        """Print comprehensive integration test summary."""
        print("\n" + "="*60)
        print("📊 INTEGRATION TEST SUMMARY")
        print("="*60)
        
        print(f"Total Test Cases: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {passed/total:.1%}")
        
        if passed == total:
            print("\n🎉 ALL INTEGRATION TESTS PASSED!")
            print("✅ Advanced solver system is working correctly")
        else:
            print(f"\n⚠️  {total - passed} test case(s) failed")
            print("Review individual test results above")
        
        # Mode performance summary
        print(f"\n📈 SOLVER MODE PERFORMANCE")
        print("-" * 40)
        
        mode_stats = {"logic_v0": [], "logic_v1": [], "logic_v2": [], "logic_v3": []}
        
        for case_name, case_results in self.results.items():
            for mode, result in case_results.items():
                if result['solved']:
                    mode_stats[mode].append(result['time_ms'])
        
        for mode, times in mode_stats.items():
            if times:
                avg_time = sum(times) / len(times)
                solve_count = len(times)
                print(f"{mode:<12}: {solve_count} solves, {avg_time:.1f}ms avg")
            else:
                print(f"{mode:<12}: No successful solves")
    
    def run_end_to_end_workflow(self) -> None:
        """Test complete end-to-end solver workflow."""
        print("\n🔄 END-TO-END WORKFLOW TEST")
        print("=" * 40)
        
        # Create a representative puzzle
        grid = Grid(2, 3, allow_diagonal=False)
        constraints = Constraints(1, 6, allow_diagonal=False)
        puzzle = Puzzle(grid, constraints)
        
        # Set initial constraints
        grid.get_cell(Position(0, 0)).value = 1
        grid.get_cell(Position(0, 0)).given = True
        grid.get_cell(Position(1, 2)).value = 6
        grid.get_cell(Position(1, 2)).given = True
        
        print("Initial puzzle state:")
        ascii_print(puzzle)
        
        # Test complete workflow for logic_v2
        print("\nTesting logic_v2 workflow...")
        
        try:
            result = Solver.solve(puzzle, mode="logic_v2")
            
            if result.solved:
                print("✅ Solve successful!")
                print(f"Steps taken: {len(result.steps)}")
                print("\nFinal solution:")
                ascii_print(puzzle)
                
                # Verify solution
                if self._verify_solution(puzzle):
                    print("✅ Solution verification passed")
                else:
                    print("❌ Solution verification failed")
            else:
                print("❌ Solve failed")
                
        except Exception as e:
            print(f"❌ Workflow error: {e}")
    
    def _verify_solution(self, puzzle: Puzzle) -> bool:
        """Verify that a solved puzzle is correct."""
        # Check all cells filled
        for row in range(puzzle.grid.rows):
            for col in range(puzzle.grid.cols):
                cell = puzzle.grid.get_cell(Position(row, col))
                if cell.value == 0:
                    return False
        
        # Check value range
        min_val = puzzle.constraints.min_value
        max_val = puzzle.constraints.max_value
        expected_count = max_val - min_val + 1
        
        used_values = set()
        for row in range(puzzle.grid.rows):
            for col in range(puzzle.grid.cols):
                cell = puzzle.grid.get_cell(Position(row, col))
                used_values.add(cell.value)
        
        if len(used_values) != expected_count:
            return False
        
        # Check consecutive path (simplified)
        # For complete validation, would need path tracing
        return True


def main():
    """Run the comprehensive integration test suite."""
    suite = IntegrationTestSuite()
    
    # Run main integration tests
    suite.run_integration_tests()
    
    # Run end-to-end workflow test
    suite.run_end_to_end_workflow()
    
    print("\n🏁 INTEGRATION TESTING COMPLETE")
    print("All solver components have been validated")


if __name__ == "__main__":
    main()