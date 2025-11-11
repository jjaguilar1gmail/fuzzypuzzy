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

# Puzzle Generation (NEW: Uniqueness-Preserving Generator)
python hidato.py --generate --size 5 --difficulty easy --seed 123
python hidato.py --generate --size 7 --difficulty hard --seed 42
python hidato.py --generate --size 6 --percent-fill 0.40 --seed 99
python hidato.py --generate --size 5 --blocked '1,1;2,2' --seed 200
python hidato.py --generate --size 6 --symmetry rotational --seed 777 --print-seed

# NEW: Smart Path Modes (Fast, Diverse Generation)
python hidato.py --generate --size 9 --difficulty hard --path-mode backbite_v1 --seed 42
python hidato.py --generate --size 7 --difficulty medium --path-mode random_walk_v2 --seed 123
python hidato.py --generate --size 8 --path-mode backbite_v1 --path-time-ms 5000 --seed 99

# Partial Coverage Acceptance (for challenging configurations)
python hidato.py --generate --size 9 --allow-partial-paths --min-cover 0.85 --path-time-ms 4000 --seed 42

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

- **Uniqueness-Preserving Generator**: Generate puzzles with guaranteed single solutions
  - **Difficulty Bands**: Easy, medium, hard, extreme with automatic assessment
  - **Smart Path Modes**: Choose from 4 path-building algorithms (see below)
  - **Partial Coverage**: Accept high-coverage partial paths for challenging configs
  - **Deterministic**: Same seed produces identical puzzles
  - **Blocked Cells**: Support for custom grid layouts
  - **Symmetry Options**: Rotational and horizontal symmetry
  - **Metrics Reporting**: Clue density, logic ratio, search depth, path build time
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

### 🛤️ Smart Path Modes

The generator supports four path-building algorithms with different characteristics:

| Mode | Description | Performance | Use Case |
|------|-------------|-------------|----------|
| `serpentine` | Deterministic snake pattern | Instant | Testing, predictable layouts |
| `random_walk` | Legacy random exploration | Variable | **Deprecated** - use random_walk_v2 |
| `backbite_v1` | Hamiltonian path refinement | ~38ms (9x9) | **Recommended** - fast & diverse |
| `random_walk_v2` | Smart random with Warnsdorff | ~50-200ms | Max variety, controlled retries |

**Path Mode Features**:
- ✅ **Bounded Execution**: All modes respect `--path-time-ms` budgets
- ✅ **Deterministic**: Same seed produces identical paths
- ✅ **Diversity**: backbite_v1 and random_walk_v2 produce varied layouts
- ✅ **Partial Coverage**: Accept high-coverage paths (≥85%) with `--allow-partial-paths`

**Usage Examples:**
```bash
# Recommended: Fast diverse generation
python hidato.py --generate --size 9 --path-mode backbite_v1 --seed 42

# Maximum variety (slower)
python hidato.py --generate --size 7 --path-mode random_walk_v2 --seed 123

# Challenging configs with partial acceptance
python hidato.py --generate --size 9 --allow-partial-paths --min-cover 0.85 --seed 99

# Set time budget for path building
python hidato.py --generate --size 8 --path-mode backbite_v1 --path-time-ms 5000
```

**Partial Coverage Acceptance**:
- When enabled with `--allow-partial-paths`, generator accepts paths covering ≥ `min-cover` ratio (default 85%)
- Uncovered cells are blocked, and puzzle constraints adjusted
- Useful for difficult configurations (heavy blocking, extreme constraints)
- Output includes `path_coverage` and acceptance reason in metrics

### 🎯 Adaptive Turn Anchors

The generator uses intelligent anchor selection to enable truly minimal-clue puzzles while preserving uniqueness:

| Difficulty | Anchor Strategy | Goal |
|------------|----------------|------|
| **Easy** | Endpoints + 2-3 hard anchors | Preserve structure and clarity |
| **Medium** | Endpoints + 1 soft anchor (droppable) | Balance challenge with hints |
| **Hard** | Endpoints only | Minimize clues for maximum challenge |
| **Extreme** | Endpoints only | Ultra-minimal with repair-only anchors |

**Adaptive Features**:
- ✅ **Policy-Driven**: `adaptive_v1` policy adjusts anchors by difficulty
- ✅ **Soft Anchors**: Medium difficulty may drop redundant anchors
- ✅ **Repair Anchors**: Hard/Extreme add anchors only as last resort for uniqueness
- ✅ **Legacy Fallback**: Use `--anchor-policy legacy` for old behavior
- ✅ **Metrics**: Track anchor counts, types, positions, and selection reason

**Usage Examples:**
```bash
# Default: Adaptive anchors (fewer clues on hard puzzles)
python hidato.py --generate --size 7 --difficulty hard --seed 42 --verbose

# Legacy mode: More anchors (traditional behavior)
python hidato.py --generate --size 7 --difficulty hard --seed 42 --anchor-policy legacy --verbose

# Quick disable: Use flag to turn off adaptive anchors
python hidato.py --generate --size 6 --difficulty medium --no-adaptive-turn-anchors

# View anchor metrics with verbose flag
python hidato.py --generate --size 5 --difficulty easy --seed 99 --verbose
# Output includes:
#   Anchor Policy: adaptive_v1
#   Anchor Count: 5 (hard: 3, soft: 0, repair: 0)
#   Anchor Reason: policy
```

**Anchor Types**:
- **Hard**: Must-keep structural anchors for easy difficulty
- **Soft**: Optional anchors for medium that may be dropped if redundant
- **Repair**: Last-resort anchors added when uniqueness verification fails
- **Endpoint**: Always kept (start and end of path)

**Impact on Generation**:
- Adaptive mode enables lower clue counts on hard/extreme difficulties
- Legacy mode maintains backward compatibility with higher anchor counts
- Same seed + same policy = deterministic anchor placement
- Metrics visibility helps tune puzzle generation parameters

### 📁 Project Structure

```
core/          # Domain model (Position, Cell, Grid, Puzzle)
generate/      # Puzzle generation pipeline
  anchor_policy.py  # Adaptive anchor selection (NEW)
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
- **NEW**: [Generator Specification](specs/001-unique-puzzle-gen/spec.md) - Uniqueness-preserving generator requirements
- **NEW**: [Adaptive Turn Anchors](specs/001-adaptive-turn-anchors/spec.md) - Intelligent anchor selection by difficulty
```
- **NEW**: [Generator Quickstart](specs/001-unique-puzzle-gen/quickstart.md) - How to generate puzzles
- **NEW**: [Smart Path Modes Quickstart](specs/001-smart-path-modes/quickstart.md) - Path mode options and examples
 - **NEW**: [Uniqueness Improvements](docs/uniqueness_improvements.md) - Structural guardrails & pruning strategy

### 🧪 Uniqueness & Guardrail Tests

Run the test suite (includes uniqueness engine & guardrail regression tests):

```powershell
cd tests; pytest -k uniqueness -v; cd ..
```

Key tests:
- `test_uniqueness_engines.py` – classic vs staged engine sanity checks
- `test_uniqueness_seed42_regression.py` – ensures seed 42 no longer produces ambiguous sparse puzzle
- `test_uniqueness_guard_metrics.py` – guard helper metric stability across seeds

All uniqueness-sensitive tests tolerate minor density variance while enforcing structural constraints (max gap ≤ 12, quartile coverage, dispersion).

