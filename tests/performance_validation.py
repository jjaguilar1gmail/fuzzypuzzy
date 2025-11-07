#!/usr/bin/env python3
"""Performance validation and benchmarking suite for advanced solvers."""

import time
import statistics
from typing import Dict, List, Tuple
from core.puzzle import Puzzle
from core.grid import Grid
from core.constraints import Constraints
from core.position import Position
from solve.solver import Solver
from hidato_io.exporters import ascii_print

class PerformanceBenchmark:
    """Performance benchmarking and validation for solver modes."""
    
    def __init__(self):
        self.results = {}
        self.test_cases = self._generate_test_cases()
    
    def _generate_test_cases(self) -> List[Tuple[str, Puzzle]]:
        """Generate standardized test cases for benchmarking."""
        cases = []
        
        # Case 1: Simple linear (baseline)
        grid1 = Grid(1, 6, allow_diagonal=False)
        constraints1 = Constraints(1, 6, allow_diagonal=False)
        puzzle1 = Puzzle(grid1, constraints1)
        grid1.get_cell(Position(0, 0)).value = 1
        grid1.get_cell(Position(0, 0)).given = True
        grid1.get_cell(Position(0, 5)).value = 6
        grid1.get_cell(Position(0, 5)).given = True
        cases.append(("Linear_1x6", puzzle1))
        
        # Case 2: Small square
        grid2 = Grid(3, 3, allow_diagonal=False)
        constraints2 = Constraints(1, 6, allow_diagonal=False)
        puzzle2 = Puzzle(grid2, constraints2)
        grid2.get_cell(Position(0, 0)).value = 1
        grid2.get_cell(Position(0, 0)).given = True
        grid2.get_cell(Position(2, 2)).value = 6
        grid2.get_cell(Position(2, 2)).given = True
        cases.append(("Square_3x3", puzzle2))
        
        # Case 3: L-shaped layout
        grid3 = Grid(2, 4, allow_diagonal=False)
        constraints3 = Constraints(1, 6, allow_diagonal=False)
        puzzle3 = Puzzle(grid3, constraints3)
        grid3.get_cell(Position(0, 0)).value = 1
        grid3.get_cell(Position(0, 0)).given = True
        grid3.get_cell(Position(1, 3)).value = 6
        grid3.get_cell(Position(1, 3)).given = True
        cases.append(("L_Shape_2x4", puzzle3))
        
        # Case 4: Constraint-rich case
        grid4 = Grid(2, 3, allow_diagonal=False)
        constraints4 = Constraints(1, 6, allow_diagonal=False)
        puzzle4 = Puzzle(grid4, constraints4)
        grid4.get_cell(Position(0, 0)).value = 1
        grid4.get_cell(Position(0, 0)).given = True
        grid4.get_cell(Position(0, 1)).value = 2
        grid4.get_cell(Position(0, 1)).given = True
        grid4.get_cell(Position(1, 2)).value = 6
        grid4.get_cell(Position(1, 2)).given = True
        cases.append(("Constrained_2x3", puzzle4))
        
        return cases
    
    def benchmark_mode(self, mode: str, runs: int = 5) -> Dict:
        """Benchmark a specific solver mode across all test cases."""
        print(f"🔧 Benchmarking {mode} ({runs} runs per case)")
        
        mode_results = {}
        
        for case_name, puzzle in self.test_cases:
            print(f"  Testing {case_name}...")
            
            times = []
            steps = []
            success_count = 0
            
            for run in range(runs):
                # Use copy to avoid state contamination
                from copy import deepcopy
                test_puzzle = deepcopy(puzzle)
                
                # Configure based on mode
                config = {}
                if mode == "logic_v3":
                    config.update({
                        'max_nodes': 1000,
                        'max_depth': 15,
                        'timeout_ms': 5000
                    })
                
                # Time the solve
                start_time = time.perf_counter()
                result = Solver.solve(test_puzzle, mode=mode, **config)
                end_time = time.perf_counter()
                
                times.append((end_time - start_time) * 1000)  # Convert to ms
                steps.append(len(result.steps))
                if result.solved:
                    success_count += 1
            
            # Calculate statistics
            mode_results[case_name] = {
                'success_rate': success_count / runs,
                'avg_time_ms': statistics.mean(times),
                'median_time_ms': statistics.median(times),
                'min_time_ms': min(times),
                'max_time_ms': max(times),
                'stddev_time_ms': statistics.stdev(times) if len(times) > 1 else 0,
                'avg_steps': statistics.mean(steps),
                'runs': runs
            }
        
        return mode_results
    
    def run_full_benchmark(self) -> None:
        """Run complete performance benchmark across all modes."""
        print("🚀 ADVANCED SOLVER PERFORMANCE BENCHMARK")
        print("=" * 60)
        
        modes = ["logic_v0", "logic_v1", "logic_v2", "logic_v3"]
        
        for mode in modes:
            self.results[mode] = self.benchmark_mode(mode, runs=3)
        
        self._print_summary_report()
        self._validate_performance_requirements()
    
    def _print_summary_report(self) -> None:
        """Print comprehensive performance report."""
        print("\n📊 PERFORMANCE SUMMARY REPORT")
        print("=" * 60)
        
        # Header
        print(f"{'Case':<15} {'Mode':<10} {'Success':<8} {'Avg(ms)':<10} {'Steps':<8} {'Status'}")
        print("-" * 60)
        
        # Results for each case
        for case_name, _ in self.test_cases:
            for mode in ["logic_v0", "logic_v1", "logic_v2", "logic_v3"]:
                if mode in self.results and case_name in self.results[mode]:
                    data = self.results[mode][case_name]
                    success = f"{data['success_rate']:.0%}"
                    avg_time = f"{data['avg_time_ms']:.1f}"
                    avg_steps = f"{data['avg_steps']:.1f}"
                    
                    # Determine status
                    if data['success_rate'] == 1.0:
                        if data['avg_time_ms'] < 100:
                            status = "✅ Fast"
                        elif data['avg_time_ms'] < 1000:
                            status = "✅ Good"
                        else:
                            status = "⚠️ Slow"
                    elif data['success_rate'] > 0:
                        status = "⚠️ Partial"
                    else:
                        status = "❌ Failed"
                    
                    print(f"{case_name:<15} {mode:<10} {success:<8} {avg_time:<10} {avg_steps:<8} {status}")
        
        print()
        
        # Mode comparison
        print("📈 MODE COMPARISON")
        print("-" * 30)
        for mode in ["logic_v0", "logic_v1", "logic_v2", "logic_v3"]:
            if mode in self.results:
                # Calculate overall metrics
                all_times = []
                all_successes = []
                
                for case_data in self.results[mode].values():
                    all_times.append(case_data['avg_time_ms'])
                    all_successes.append(case_data['success_rate'])
                
                avg_time = statistics.mean(all_times)
                avg_success = statistics.mean(all_successes)
                
                print(f"{mode:<12}: {avg_success:.0%} success, {avg_time:.1f}ms avg")
    
    def _validate_performance_requirements(self) -> None:
        """Validate that performance meets requirements."""
        print("\n🎯 PERFORMANCE VALIDATION")
        print("=" * 40)
        
        requirements = {
            "logic_v0": {"max_time_ms": 50, "min_success": 0.5},
            "logic_v1": {"max_time_ms": 200, "min_success": 0.7},
            "logic_v2": {"max_time_ms": 500, "min_success": 0.8},
            "logic_v3": {"max_time_ms": 2000, "min_success": 0.9}
        }
        
        all_passed = True
        
        for mode, req in requirements.items():
            if mode in self.results:
                # Calculate mode metrics
                times = []
                successes = []
                
                for case_data in self.results[mode].values():
                    times.append(case_data['avg_time_ms'])
                    successes.append(case_data['success_rate'])
                
                max_time = max(times)
                avg_success = statistics.mean(successes)
                
                # Check requirements
                time_ok = max_time <= req["max_time_ms"]
                success_ok = avg_success >= req["min_success"]
                
                status = "✅ PASS" if (time_ok and success_ok) else "❌ FAIL"
                
                print(f"{mode:<12}: {status}")
                if not time_ok:
                    print(f"  ⚠️  Max time {max_time:.1f}ms > {req['max_time_ms']}ms")
                    all_passed = False
                if not success_ok:
                    print(f"  ⚠️  Success {avg_success:.1%} < {req['min_success']:.0%}")
                    all_passed = False
        
        print()
        if all_passed:
            print("🎉 ALL PERFORMANCE REQUIREMENTS MET!")
        else:
            print("⚠️  Some performance requirements not met")
            print("   Consider optimization or requirement adjustment")
    
    def memory_profile_test(self) -> None:
        """Basic memory usage profiling."""
        print("\n💾 MEMORY USAGE ANALYSIS")
        print("=" * 30)
        
        import tracemalloc
        
        for mode in ["logic_v1", "logic_v2", "logic_v3"]:
            print(f"\nTesting {mode} memory usage...")
            
            # Use a moderately complex case
            case_name, puzzle = self.test_cases[1]  # Square_3x3
            
            tracemalloc.start()
            
            from copy import deepcopy
            test_puzzle = deepcopy(puzzle)
            
            config = {}
            if mode == "logic_v3":
                config.update({'max_nodes': 500, 'timeout_ms': 2000})
            
            result = Solver.solve(test_puzzle, mode=mode, **config)
            
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            print(f"  Current: {current / 1024:.1f} KB")
            print(f"  Peak: {peak / 1024:.1f} KB")
            print(f"  Result: {'✅' if result.solved else '❌'}")


def main():
    """Run the performance validation suite."""
    benchmark = PerformanceBenchmark()
    
    # Run full benchmark
    benchmark.run_full_benchmark()
    
    # Memory profiling
    benchmark.memory_profile_test()
    
    print("\n🏁 PERFORMANCE VALIDATION COMPLETE")
    print("See results above for detailed analysis")


if __name__ == "__main__":
    main()