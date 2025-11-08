# fuzzypuzzy
A collection of puzzle games with terminal interfaces and solving capabilities.

## Current Feature: Hidato Terminal MVP ✅

A fully functional terminal-playable Hidato puzzle game with generation, solving, and ASCII rendering.

### 🚀 Quick Start

```bash
# Main entry point (recommended)
python hidato.py               # Start interactive REPL
python hidato.py --demo        # Run full feature demonstration
python hidato.py --trace       # Run solver with detailed trace (for debugging/learning)
python hidato.py --version     # Show version information
python hidato.py --help        # Show all CLI options

# Alternative entry points
python app/api.py              # Direct REPL access
python complete_demo.py        # Comprehensive feature showcase

# Advanced solver modes (available in REPL):
solve --mode logic_v0          # Basic consecutive logic (default)
solve --mode logic_v1          # Enhanced two-ended propagation
solve --mode logic_v2          # Region-aware spatial reasoning  
solve --mode logic_v3          # Bounded search with backtracking

# Available commands in REPL:
generate 5x5           # Create a 5x5 puzzle
generate 7x7 --seed 42 # Create reproducible 7x7 puzzle
show                   # Display current puzzle
move 2 3 15           # Place number 15 at position (2,3)
hint                  # Get a solving hint (default: logic_v0)
hint --mode logic_v1   # Get hint using enhanced logic solver
solve                 # Auto-solve the puzzle (default: logic_v0)
solve --mode logic_v2  # Solve using region-aware techniques
solve --mode logic_v3  # Solve using bounded search with backtracking
export puzzle.json    # Save puzzle to file
import puzzle.json    # Load puzzle from file
help                  # Show all commands
quit                  # Exit
```

### ✨ Features

- **Puzzle Generation**: 5x5 and 7x7 Hidato puzzles with serpentine paths
- **Interactive Play**: Move validation with adjacency constraints
- **Advanced Solving**: 4 progressive solver modes from basic to bounded search
- **Intelligent Hints**: Context-aware solving suggestions with mode selection
- **Detailed Tracing**: Step-by-step solver trace with strategy breakdown and validation
- **Solution Validation**: Automatic verification (givens preserved, contiguous path, all values)
- **Visual Display**: Clean ASCII rendering with highlighted moves
- **Save/Load**: JSON export/import with metadata preservation
- **Performance**: Sub-second generation, deterministic solving, real-time timing feedback

### 🎯 Example Session

```
$ python hidato.py
🎯 Welcome to Hidato Terminal MVP!
Type 'help' for commands or 'quit' to exit.

hidato> generate 5x5 --seed 42
⏱️  Generate 5x5: 1.0ms
Seed: 42, Givens: 5

[ 1] .  .  .  .
 .  .  . [ 7] .
 .  . [13] .  .
 . [19] .  .  .
 .  .  .  . [25]

hidato> move 1 2 2
✅ Placed 2 at (1, 2)

[ 1]* 2* .  .  .
 .  .  . [ 7] .
 .  . [13] .  .
 . [19] .  .  .
 .  .  .  . [25]

hidato> export my-puzzle
✅ Puzzle exported to my-puzzle.json

hidato> hint --mode logic_v1
💡 Hint (logic_v1): Place 3 at (2, 1): Only possible value for this cell

hidato> solve --mode logic_v2
🔍 Attempting to solve puzzle using logic_v2...
⏱️  Solve puzzle (logic_v2): 15.2ms
✅ Puzzle solved successfully!
🎯 Solution found in 8 steps
```

### 🎮 Entry Points

| Command | Purpose | Features |
|---------|---------|----------|
| `python hidato.py` | **Main entry point** | CLI options, help, version info |
| `python hidato.py --demo` | Feature demonstration | Automated showcase of all capabilities |
| `python app/api.py` | Direct REPL | Immediate access to puzzle interface |
| `python complete_demo.py` | Comprehensive test | Full phase-by-phase feature validation |

### 🧠 Solver Modes

| Mode | Description | Capabilities | Performance |
|------|-------------|--------------|-------------|
| `logic_v0` | Basic consecutive logic | Single-cell deduction | <1ms |
| `logic_v1` | Enhanced two-ended propagation | Bidirectional reasoning | <5ms |
| `logic_v2` | Region-aware spatial reasoning | Corridor/degree/island elimination | ~15ms, ≥1 elimination |
| `logic_v3` | Bounded search with backtracking | MRV by value, LCV/frontier ordering | ~160ms, 25 nodes, depth 14 |

**Recent Improvements (001-fix-v2-v3-solvers)**:
- ✅ **v2 (logic_v2)**: Now reaches fixpoint with corridor bridging, degree pruning, and island elimination
- ✅ **v3 (logic_v3)**: Fixed in-place logic application and MRV-by-value heuristic
  - **Performance**: Solves canonical 5x5 in ~160ms with 25 nodes and depth 14 (87% node reduction from baseline)
  - **Correctness**: 100% deterministic, full solution validation
  - **Tracing**: Use `python hidato.py --trace` to see detailed solving steps

**Usage Examples:**
```bash
# In REPL, try different modes for challenging puzzles
solve --mode logic_v1    # Try enhanced logic first
solve --mode logic_v2    # If stuck, use spatial reasoning (fast)
solve --mode logic_v3    # For puzzles requiring search (deterministic)

# See detailed solving trace with validation
python hidato.py --trace  # Shows strategy breakdown and step-by-step trace
```

### 📁 Project Structure

```
core/          # Domain model (Position, Cell, Grid, Puzzle)
generate/      # Puzzle generation pipeline
solve/         # Solving algorithms and strategies  
hidato_io/     # ASCII rendering and JSON serialization
app/           # REPL interface and move validation
util/          # Profiling and utilities
tests/         # Contract tests for core functionality
```

**Documentation**:
- [Feature Specification](specs/001-hidato-terminal-mvp/spec.md) - Requirements and user stories
- [Implementation Plan](specs/001-hidato-terminal-mvp/plan.md) - Technical approach and architecture  
- [Quickstart Guide](specs/001-hidato-terminal-mvp/quickstart.md) - How to run the MVP
- [Solver Improvements](specs/001-fix-v2-v3-solvers/spec.md) - v2/v3 solver fixes and enhancements
- [Solver Implementation](specs/001-fix-v2-v3-solvers/plan.md) - Technical details of solver improvements

