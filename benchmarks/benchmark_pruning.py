"""Benchmark script for pruning performance (T22).

Measures median time and iterations for puzzle generation with/without pruning.
"""
import time
import statistics
from generate.generator import Generator


def benchmark_pruning(num_seeds=10, size=7, difficulty="medium"):
    """Benchmark pruning vs legacy removal.
    
    Args:
        num_seeds: Number of different seeds to test
        size: Puzzle size
        difficulty: Target difficulty
    
    Returns:
        Dict with timing statistics
    """
    results = {
        "legacy": {"times": [], "clue_counts": [], "iterations": []},
        "pruning": {"times": [], "clue_counts": [], "iterations": []}
    }
    
    print(f"\n{'='*60}")
    print(f"Benchmarking: {size}x{size} {difficulty} puzzles")
    print(f"Seeds: {num_seeds}")
    print(f"{'='*60}\n")
    
    # Note: Currently pruning is enabled by default in config
    # This benchmark assumes pruning_enabled flag is respected
    
    for seed in range(1000, 1000 + num_seeds):
        print(f"Seed {seed}...", end=" ")
        
        # Generate with pruning enabled (default)
        start = time.time()
        try:
            result = Generator.generate_puzzle(
                size=size,
                difficulty=difficulty,
                seed=seed,
                allow_diagonal=True,
                path_mode="serpentine"
            )
            elapsed = (time.time() - start) * 1000
            
            results["pruning"]["times"].append(elapsed)
            results["pruning"]["clue_counts"].append(result.clue_count)
            results["pruning"]["iterations"].append(result.attempts_used)
            
            print(f"✓ {elapsed:.0f}ms, {result.clue_count} clues, {result.attempts_used} iterations")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    # Compute statistics
    stats = {}
    for mode in ["pruning"]:  # Only testing pruning for now
        if results[mode]["times"]:
            stats[mode] = {
                "median_time_ms": statistics.median(results[mode]["times"]),
                "mean_time_ms": statistics.mean(results[mode]["times"]),
                "median_clues": statistics.median(results[mode]["clue_counts"]),
                "median_iterations": statistics.median(results[mode]["iterations"]),
                "min_time_ms": min(results[mode]["times"]),
                "max_time_ms": max(results[mode]["times"]),
            }
    
    return stats


def print_benchmark_results(stats):
    """Print formatted benchmark results."""
    print(f"\n{'='*60}")
    print("BENCHMARK RESULTS")
    print(f"{'='*60}\n")
    
    for mode, data in stats.items():
        print(f"{mode.upper()}:")
        print(f"  Median Time:       {data['median_time_ms']:.1f} ms")
        print(f"  Mean Time:         {data['mean_time_ms']:.1f} ms")
        print(f"  Range:             {data['min_time_ms']:.1f} - {data['max_time_ms']:.1f} ms")
        print(f"  Median Clues:      {data['median_clues']:.0f}")
        print(f"  Median Iterations: {data['median_iterations']:.0f}")
        print()


if __name__ == "__main__":
    import sys
    
    # Parse args
    num_seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    size = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    difficulty = sys.argv[3] if len(sys.argv) > 3 else "medium"
    
    stats = benchmark_pruning(num_seeds, size, difficulty)
    print_benchmark_results(stats)
    
    # Success criteria check (SC-001: Hard 9x9 ≤6.0s median)
    if size == 9 and difficulty == "hard":
        if "pruning" in stats:
            median_time_s = stats["pruning"]["median_time_ms"] / 1000
            target_time_s = 6.0
            
            print(f"{'='*60}")
            print(f"SC-001 Check: Hard 9x9 median time")
            print(f"  Target:   ≤{target_time_s:.1f}s")
            print(f"  Achieved: {median_time_s:.2f}s")
            
            if median_time_s <= target_time_s:
                print(f"  Result:   ✓ PASS")
            else:
                print(f"  Result:   ✗ FAIL")
            print(f"{'='*60}\n")
