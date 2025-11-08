#!/usr/bin/env python3
"""Hidato Terminal MVP - Main Entry Point

A command-line interface for the Hidato puzzle game.
"""

import sys
import os
import argparse

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app.api import API, HidatoREPL


def run_trace_demo():
    """Run solver on canonical 5x5 with detailed trace output."""
    import json
    from pathlib import Path
    from core.position import Position
    from core.grid import Grid
    from core.constraints import Constraints
    from core.puzzle import Puzzle
    from solve.solver import Solver, validate_solution
    from util.trace import TraceFormatter, format_steps_summary, format_validation_report
    
    # Load canonical 5x5
    fixture_path = Path(__file__).parent / "tests" / "integration" / "fixtures" / "canonical_5x5.json"
    if not fixture_path.exists():
        print(f"❌ Fixture not found: {fixture_path}")
        print("Run from project root directory.")
        return
    
    with open(fixture_path, 'r') as f:
        data = json.load(f)
    
    print("="*70)
    print("🧩 Puzzle: Canonical 5x5 Hidato")
    print("="*70)
    print(f"Size: {data['rows']}x{data['cols']}")
    print(f"Values: {data['min_value']}-{data['max_value']}")
    print(f"Adjacency: {data['adjacency']}-way")
    print(f"Givens: {len(data['givens'])}")
    print()
    
    # Build puzzle
    grid = Grid(data['rows'], data['cols'], allow_diagonal=(data['adjacency'] == '8'))
    constraints = Constraints(data['min_value'], data['max_value'], data['adjacency'])
    puzzle = Puzzle(grid, constraints)
    
    original_givens = {}
    for given in data['givens']:
        pos = Position(given['row'], given['col'])
        grid.set_cell_value(pos, given['value'])
        grid.get_cell(pos).given = True
        original_givens[pos] = given['value']
    
    # Solve with v3
    print("🔧 Solving with logic_v3 (bounded search)...")
    result = Solver.solve(puzzle, mode='logic_v3')
    
    print(f"\n✓ Result: {'SOLVED' if result.solved else 'UNSOLVED'}")
    print(f"  Nodes explored: {result.nodes}")
    print(f"  Max depth: {result.depth}")
    print(f"  Total steps: {len(result.steps)}")
    print()
    
    # Show trace summary
    print("="*70)
    print("📋 Step Summary")
    print("="*70)
    summary = format_steps_summary(result.steps, group_by_strategy=True)
    print(summary)
    print()
    
    # Show detailed trace (limited)
    print("="*70)
    print("🔍 Detailed Trace (first 50 steps)")
    print("="*70)
    formatter = TraceFormatter(group_similar=False, max_lines=50)
    trace = formatter.format_steps(result.steps)
    print(trace)
    print()
    
    # Validate solution
    if result.solved:
        print("="*70)
        print("✅ Final Validation")
        print("="*70)
        report = validate_solution(puzzle, original_givens)
        formatted_report = format_validation_report(report)
        print(formatted_report)


def main():
    """Main entry point with optional command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Hidato Terminal MVP - Interactive puzzle game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python hidato.py                    # Start interactive REPL
  python hidato.py --demo            # Run feature demonstration
  python hidato.py --version         # Show version info

Interactive Commands:
  generate 5x5 --seed 42             # Create reproducible puzzle
  move 2 3 15                        # Place number at position
  hint                               # Get solving hint
  solve                              # Auto-solve puzzle
  export puzzle.json                 # Save to file
  import puzzle.json                 # Load from file
  help                               # Show all commands
        """
    )
    
    parser.add_argument(
        '--demo', 
        action='store_true',
        help='Run a demonstration of all features'
    )
    
    parser.add_argument(
        '--trace',
        action='store_true',
        help='Run solver with detailed trace output (for debugging/learning)'
    )
    
    parser.add_argument(
        '--version', 
        action='store_true',
        help='Show version information'
    )
    
    args = parser.parse_args()
    
    if args.version:
        print("Hidato Terminal MVP v1.0")
        print("Feature: 001-hidato-terminal-mvp")
        print("Python 3.11+ compatible")
        return
    
    if args.trace:
        print("🔍 Running Solver with Detailed Trace...")
        print()
        run_trace_demo()
        return
    
    if args.demo:
        print("🎯 Starting Hidato Terminal MVP Demo...")
        print("(Running complete_demo.py)")
        print()
        import complete_demo
        complete_demo.main()
        return
    
    # Default: start interactive REPL
    print("🎯 Welcome to Hidato Terminal MVP!")
    print("Type 'help' for commands or 'quit' to exit.")
    print()
    
    try:
        API.start_repl()
    except KeyboardInterrupt:
        print("\n👋 Thanks for playing Hidato!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()